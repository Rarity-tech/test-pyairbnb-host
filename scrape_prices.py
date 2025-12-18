import pyairbnb
import csv
import os
import re
import subprocess
import time
from datetime import datetime, timedelta

# ==============================================================================
# CONFIG
# ==============================================================================

ROOM_IDS_FILE = "room_ids.txt"
TIMESTAMP = datetime.now().strftime('%Y%m%d_%H%M%S')
OUTPUT_CSV_MATRIX = f"prices_matrix_{TIMESTAMP}.csv"
OUTPUT_CSV_DETAILS = f"prices_details_{TIMESTAMP}.csv"

MAX_DAYS = int(os.environ.get("MAX_DAYS", "0"))  # 0 = tous les jours dispo
CURRENCY = os.environ.get("CURRENCY", "AED")
LANGUAGE = "en"
PROXY_URL = ""

DELAY_BETWEEN_DETAILS = 1.5
DELAY_BETWEEN_LISTINGS = 3.0

# Période : 365 jours à partir d'aujourd'hui
START_DATE = datetime.now().date()
END_DATE = START_DATE + timedelta(days=365)


# ==============================================================================
# UTILITAIRES
# ==============================================================================

def load_room_ids():
    """Charge les room IDs depuis le fichier texte"""
    if not os.path.exists(ROOM_IDS_FILE):
        print(f"❌ ERREUR: Fichier '{ROOM_IDS_FILE}' non trouvé!")
        return []
    
    room_ids = []
    with open(ROOM_IDS_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                room_ids.append(line)
    
    return room_ids


def extract_prices(price_data):
    """Extrait les 3 prix : original, discounted, final (par nuit)"""
    result = {
        "price_original": None,
        "price_discounted": None,
        "price_final": None,
        "discount_amount": None,
    }
    
    if not price_data:
        return result
    
    details = price_data.get("details", {})
    main = price_data.get("main", {})
    
    # 1. Extraire prix original depuis "X nights x PRIX"
    for key, value in details.items():
        match = re.search(r'(\d+)\s*nights?\s*x\s*[^\d]*([\d,]+\.?\d*)', key, re.IGNORECASE)
        if match:
            nights = int(match.group(1))
            price_str = match.group(2).replace(',', '')
            try:
                total = float(price_str)
                result["price_original"] = round(total / nights, 2)
            except:
                pass
            break
    
    # 2. Extraire réduction depuis "discount"
    for key, value in details.items():
        if "discount" in key.lower() and isinstance(value, str):
            match = re.search(r'-?\s*[^\d]*([\d,]+\.?\d*)', value)
            if match:
                try:
                    result["discount_amount"] = float(match.group(1).replace(',', ''))
                except:
                    pass
            break
    
    # 3. Prix discounted depuis main.discountedPrice
    discounted = main.get("discountedPrice", "")
    if discounted and isinstance(discounted, str):
        match = re.search(r'([\d,]+\.?\d*)', discounted)
        if match:
            try:
                result["price_discounted"] = float(match.group(1).replace(',', ''))
            except:
                pass
    
    # 4. Prix original display depuis main.originalPrice
    original = main.get("originalPrice", "")
    if original and isinstance(original, str):
        match = re.search(r'([\d,]+\.?\d*)', original)
        if match:
            try:
                # C'est le total, pas par nuit - on garde le per night calculé plus haut
                pass
            except:
                pass
    
    # 5. Calculer prix final (par nuit)
    # Si on a discount et original, calculer le final
    if result["price_original"] and result["discount_amount"]:
        # Estimer le nombre de nuits depuis les détails
        for key in details.keys():
            match = re.search(r'(\d+)\s*nights?', key, re.IGNORECASE)
            if match:
                nights = int(match.group(1))
                discount_per_night = result["discount_amount"] / nights
                result["price_final"] = round(result["price_original"] - discount_per_night, 2)
                break
    
    # Fallback: si pas de réduction, final = original
    if result["price_final"] is None and result["price_original"]:
        result["price_final"] = result["price_original"]
    
    return result


def get_available_days(calendar_data):
    """Extrait tous les jours disponibles du calendrier"""
    available_days = {}
    
    if not isinstance(calendar_data, list):
        return available_days
    
    for month_data in calendar_data:
        if not isinstance(month_data, dict):
            continue
        
        days = month_data.get("days", [])
        for day in days:
            date_str = day.get("calendarDate", "")
            if date_str:
                available_days[date_str] = {
                    "available": day.get("available", False),
                    "min_nights": day.get("minNights", 1),
                    "max_nights": day.get("maxNights", 365),
                }
    
    return available_days


def generate_date_range():
    """Génère toutes les dates sur 365 jours"""
    dates = []
    current = START_DATE
    while current <= END_DATE:
        dates.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)
    return dates


def git_commit_and_push(message):
    """Commit et push vers GitHub"""
    try:
        subprocess.run(["git", "config", "user.name", "GitHub Actions"], check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "actions@github.com"], check=True, capture_output=True)
        subprocess.run(["git", "add", "-A"], check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", message], check=True, capture_output=True)
        subprocess.run(["git", "push"], check=True, capture_output=True)
        print(f"✅ Git commit: {message}", flush=True)
        return True
    except subprocess.CalledProcessError:
        return False


# ==============================================================================
# MAIN
# ==============================================================================

def main():
    print("=" * 80)
    print("🚀 SCRAPE PRICES — pyairbnb 2.1.1")
    print("=" * 80)
    print(f"📅 Date run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"💰 Devise: {CURRENCY}")
    print(f"📊 Période: {START_DATE} → {END_DATE} (365 jours)")
    print(f"📄 Fichiers: {OUTPUT_CSV_MATRIX} & {OUTPUT_CSV_DETAILS}")
    print("=" * 80)
    
    # Charger les room IDs
    room_ids = load_room_ids()
    
    if not room_ids:
        print("❌ Aucun room ID à traiter!")
        return
    
    print(f"\n📋 {len(room_ids)} room IDs à traiter:")
    for i, rid in enumerate(room_ids, 1):
        print(f"   {i}. {rid}")
    
    # Récupérer l'API key
    print("\n" + "-" * 80)
    print("📦 Récupération de l'API Key...")
    try:
        api_key = pyairbnb.get_api_key(PROXY_URL)
        print(f"✅ API Key OK")
    except Exception as e:
        print(f"❌ Erreur API Key: {e}")
        return
    
    # Structure de données :
    # all_data[room_id][date] = {price_original, price_discounted, price_final, ...}
    all_data = {rid: {} for rid in room_ids}
    all_details = []  # Liste plate pour CSV details
    
    # Générer toutes les dates
    all_dates = generate_date_range()
    print(f"📅 {len(all_dates)} dates générées")
    
    # Traiter chaque room ID
    for idx, room_id in enumerate(room_ids, 1):
        print("\n" + "=" * 80)
        print(f"🏠 [{idx}/{len(room_ids)}] Room ID: {room_id}")
        print("=" * 80)
        
        try:
            # 1. Récupérer le calendrier
            print("📅 Récupération du calendrier...", end=" ", flush=True)
            calendar_data = pyairbnb.get_calendar(
                api_key=api_key,
                room_id=str(room_id),
                proxy_url=PROXY_URL,
            )
            print("OK")
            
            # 2. Extraire disponibilités
            availability = get_available_days(calendar_data)
            available_dates = [d for d, info in availability.items() if info["available"]]
            print(f"📊 {len(available_dates)} jours disponibles")
            
            if not available_dates:
                print("⚠️ Aucun jour disponible")
                continue
            
            # 3. Limiter si demandé
            if MAX_DAYS > 0:
                available_dates = available_dates[:MAX_DAYS]
                print(f"📊 Limité à {MAX_DAYS} jours")
            
            # 4. Récupérer les prix pour chaque jour dispo
            print(f"\n💰 Récupération des prix...")
            
            for day_idx, check_in in enumerate(available_dates, 1):
                day_info = availability.get(check_in, {})
                min_nights = day_info.get("min_nights", 1)
                
                check_in_date = datetime.strptime(check_in, "%Y-%m-%d")
                check_out_date = check_in_date + timedelta(days=min_nights)
                check_out = check_out_date.strftime("%Y-%m-%d")
                
                print(f"   [{day_idx}/{len(available_dates)}] {check_in}...", end=" ", flush=True)
                
                try:
                    details = pyairbnb.get_details(
                        room_id=int(room_id),
                        check_in=check_in,
                        check_out=check_out,
                        currency=CURRENCY,
                        proxy_url=PROXY_URL,
                        adults=2,
                        language=LANGUAGE,
                    )
                    
                    price_data = details.get("price", {})
                    prices = extract_prices(price_data)
                    
                    title = details.get("title", "")
                    room_type = details.get("room_type", "")
                    
                    # Stocker dans all_data pour matrix
                    all_data[room_id][check_in] = prices
                    
                    # Stocker dans all_details pour CSV détaillé
                    all_details.append({
                        "date": check_in,
                        "room_id": room_id,
                        "available": True,
                        "nights": min_nights,
                        "price_original": prices["price_original"],
                        "price_discounted": prices["price_discounted"],
                        "price_final": prices["price_final"],
                        "discount_amount": prices["discount_amount"],
                        "currency": CURRENCY,
                        "title": title[:50] if title else "",
                        "room_type": room_type,
                    })
                    
                    if prices["price_final"]:
                        print(f"✅ {prices['price_final']} {CURRENCY}")
                    else:
                        print(f"⚠️ Prix non trouvé")
                    
                except Exception as e:
                    print(f"❌ {str(e)[:40]}")
                
                time.sleep(DELAY_BETWEEN_DETAILS)
        
        except Exception as e:
            print(f"❌ Erreur: {e}")
        
        if idx < len(room_ids):
            time.sleep(DELAY_BETWEEN_LISTINGS)
    
    # ===========================================================================
    # GÉNÉRER CSV 1 : MATRIX (simple)
    # ===========================================================================
    print("\n" + "=" * 80)
    print(f"📄 Génération de {OUTPUT_CSV_MATRIX}...")
    print("=" * 80)
    
    with open(OUTPUT_CSV_MATRIX, "w", newline="", encoding="utf-8") as f:
        # Header: date + room_ids
        header = ["date"] + room_ids
        writer = csv.writer(f)
        writer.writerow(header)
        
        # Une ligne par date
        for date in all_dates:
            row = [date]
            for room_id in room_ids:
                price = all_data[room_id].get(date, {}).get("price_final", "")
                row.append(price if price else "")
            writer.writerow(row)
    
    print(f"✅ {OUTPUT_CSV_MATRIX} créé ({len(all_dates)} lignes)")
    
    # ===========================================================================
    # GÉNÉRER CSV 2 : DETAILS (complet)
    # ===========================================================================
    print(f"\n📄 Génération de {OUTPUT_CSV_DETAILS}...")
    
    if all_details:
        # Trier par date puis room_id
        all_details.sort(key=lambda x: (x["date"], x["room_id"]))
        
        fieldnames = [
            "date",
            "room_id",
            "available",
            "nights",
            "price_original",
            "price_discounted",
            "price_final",
            "discount_amount",
            "currency",
            "title",
            "room_type",
        ]
        
        with open(OUTPUT_CSV_DETAILS, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_details)
        
        print(f"✅ {OUTPUT_CSV_DETAILS} créé ({len(all_details)} lignes)")
    
    # Git commit
    git_commit_and_push(f"Prices: {len(all_details)} records from {len(room_ids)} listings")
    
    # Résumé
    print("\n" + "=" * 80)
    print("🎉 TERMINÉ")
    print("=" * 80)
    print(f"📊 Listings: {len(room_ids)}")
    print(f"📊 Enregistrements: {len(all_details)}")
    print(f"📄 Matrix: {OUTPUT_CSV_MATRIX}")
    print(f"📄 Details: {OUTPUT_CSV_DETAILS}")
    print("=" * 80)


if __name__ == "__main__":
    main()
