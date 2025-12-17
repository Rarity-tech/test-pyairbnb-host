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
OUTPUT_CSV = f"prices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

MAX_DAYS = int(os.environ.get("MAX_DAYS", "30"))  # 0 = tous les jours dispo
CURRENCY = os.environ.get("CURRENCY", "AED")
LANGUAGE = "en"
PROXY_URL = ""

DELAY_BETWEEN_DETAILS = 1.5  # Délai entre chaque appel get_details
DELAY_BETWEEN_LISTINGS = 3.0  # Délai entre chaque listing


# ==============================================================================
# UTILITAIRES
# ==============================================================================

def load_room_ids():
    """Charge les room IDs depuis le fichier texte"""
    if not os.path.exists(ROOM_IDS_FILE):
        print(f"❌ ERREUR: Fichier '{ROOM_IDS_FILE}' non trouvé!")
        print(f"   → Crée un fichier '{ROOM_IDS_FILE}' avec un room_id par ligne")
        return []
    
    room_ids = []
    with open(ROOM_IDS_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            # Ignorer les lignes vides et les commentaires
            if line and not line.startswith('#'):
                room_ids.append(line)
    
    return room_ids


def extract_price_per_night(price_details):
    """Extrait le prix par nuit depuis les détails de prix"""
    if not price_details:
        return None, None
    
    details = price_details.get("details", {})
    
    # Chercher le pattern "X night(s) x PRIX"
    for key, value in details.items():
        # Pattern: "2 nights x ﺩ.ﺇ3,390.50" ou "1 night x $150.00"
        match = re.search(r'(\d+)\s*nights?\s*x\s*[^\d]*([\d,]+\.?\d*)', key, re.IGNORECASE)
        if match:
            nights = int(match.group(1))
            price_str = match.group(2).replace(',', '')
            try:
                total_price = float(price_str)
                price_per_night = total_price / nights
                return price_per_night, total_price
            except:
                pass
    
    # Fallback: essayer d'extraire depuis originalPrice ou discountedPrice
    main = price_details.get("main", {})
    
    for field in ["discountedPrice", "originalPrice"]:
        price_str = main.get(field, "")
        if price_str and isinstance(price_str, str):
            # Extraire le nombre
            match = re.search(r'([\d,]+\.?\d*)', price_str)
            if match:
                try:
                    return float(match.group(1).replace(',', '')), None
                except:
                    pass
    
    return None, None


def get_available_days(calendar_data):
    """Extrait tous les jours disponibles du calendrier"""
    available_days = []
    
    if not isinstance(calendar_data, list):
        return available_days
    
    for month_data in calendar_data:
        if not isinstance(month_data, dict):
            continue
        
        days = month_data.get("days", [])
        for day in days:
            if day.get("available", False):
                date_str = day.get("calendarDate", "")
                if date_str:
                    available_days.append({
                        "date": date_str,
                        "min_nights": day.get("minNights", 1),
                        "max_nights": day.get("maxNights", 365),
                    })
    
    return available_days


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
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"💰 Devise: {CURRENCY}")
    print(f"📊 Max jours par listing: {MAX_DAYS if MAX_DAYS > 0 else 'TOUS'}")
    print("=" * 80)
    
    # Charger les room IDs
    room_ids = load_room_ids()
    
    if not room_ids:
        print("❌ Aucun room ID à traiter!")
        return
    
    print(f"\n📋 {len(room_ids)} room IDs à traiter:")
    for i, rid in enumerate(room_ids[:10], 1):
        print(f"   {i}. {rid}")
    if len(room_ids) > 10:
        print(f"   ... et {len(room_ids) - 10} autres")
    
    # Récupérer l'API key une seule fois
    print("\n" + "-" * 80)
    print("📦 Récupération de l'API Key...")
    try:
        api_key = pyairbnb.get_api_key(PROXY_URL)
        print(f"✅ API Key OK")
    except Exception as e:
        print(f"❌ Erreur API Key: {e}")
        return
    
    # Préparer le CSV
    all_records = []
    
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
            
            # 2. Extraire les jours disponibles
            available_days = get_available_days(calendar_data)
            print(f"📊 {len(available_days)} jours disponibles trouvés")
            
            if not available_days:
                print("⚠️ Aucun jour disponible, on passe au suivant")
                continue
            
            # 3. Limiter le nombre de jours si demandé
            if MAX_DAYS > 0 and len(available_days) > MAX_DAYS:
                available_days = available_days[:MAX_DAYS]
                print(f"📊 Limité à {MAX_DAYS} jours")
            
            # 4. Pour chaque jour disponible, récupérer le prix
            print(f"\n💰 Récupération des prix pour {len(available_days)} jours...")
            
            for day_idx, day_info in enumerate(available_days, 1):
                check_in = day_info["date"]
                min_nights = day_info["min_nights"]
                
                # Calculer check_out (minimum nights requis)
                check_in_date = datetime.strptime(check_in, "%Y-%m-%d")
                check_out_date = check_in_date + timedelta(days=min_nights)
                check_out = check_out_date.strftime("%Y-%m-%d")
                
                print(f"   [{day_idx}/{len(available_days)}] {check_in} → {check_out} ({min_nights} nuit(s))...", end=" ", flush=True)
                
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
                    
                    # Extraire les prix
                    price_data = details.get("price", {})
                    price_per_night, total_price = extract_price_per_night(price_data)
                    
                    # Extraire autres infos utiles
                    title = details.get("title", "")
                    room_type = details.get("room_type", "")
                    
                    main_price = price_data.get("main", {})
                    original_price = main_price.get("originalPrice", "")
                    discounted_price = main_price.get("discountedPrice", "")
                    
                    record = {
                        "room_id": room_id,
                        "date": check_in,
                        "check_out": check_out,
                        "nights": min_nights,
                        "price_per_night": price_per_night,
                        "total_price": total_price,
                        "original_price_display": original_price if isinstance(original_price, str) else "",
                        "discounted_price_display": discounted_price if isinstance(discounted_price, str) else "",
                        "currency": CURRENCY,
                        "title": title[:50] if title else "",
                        "room_type": room_type,
                        "available": True,
                    }
                    
                    all_records.append(record)
                    
                    if price_per_night:
                        print(f"✅ {price_per_night:.2f} {CURRENCY}/nuit")
                    else:
                        print(f"⚠️ Prix non trouvé")
                    
                except Exception as e:
                    print(f"❌ Erreur: {str(e)[:50]}")
                    # Enregistrer quand même avec prix vide
                    all_records.append({
                        "room_id": room_id,
                        "date": check_in,
                        "check_out": check_out,
                        "nights": min_nights,
                        "price_per_night": None,
                        "total_price": None,
                        "original_price_display": "",
                        "discounted_price_display": "",
                        "currency": CURRENCY,
                        "title": "",
                        "room_type": "",
                        "available": True,
                    })
                
                time.sleep(DELAY_BETWEEN_DETAILS)
        
        except Exception as e:
            print(f"❌ Erreur globale pour {room_id}: {e}")
        
        # Délai entre les listings
        if idx < len(room_ids):
            time.sleep(DELAY_BETWEEN_LISTINGS)
    
    # Sauvegarder le CSV
    print("\n" + "=" * 80)
    print("📄 Sauvegarde du CSV...")
    print("=" * 80)
    
    if all_records:
        fieldnames = [
            "room_id",
            "date",
            "check_out",
            "nights",
            "price_per_night",
            "total_price",
            "original_price_display",
            "discounted_price_display",
            "currency",
            "title",
            "room_type",
            "available",
        ]
        
        with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_records)
        
        print(f"✅ {len(all_records)} lignes sauvegardées dans {OUTPUT_CSV}")
        
        # Git commit
        git_commit_and_push(f"Prices data: {len(all_records)} records from {len(room_ids)} listings")
    else:
        print("⚠️ Aucune donnée à sauvegarder")
    
    # Résumé final
    print("\n" + "=" * 80)
    print("🎉 TERMINÉ")
    print("=" * 80)
    print(f"📊 Listings traités: {len(room_ids)}")
    print(f"📊 Enregistrements: {len(all_records)}")
    print(f"📄 Fichier: {OUTPUT_CSV}")
    print("=" * 80)


if __name__ == "__main__":
    main()
