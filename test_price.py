import pyairbnb
import json
import os
from datetime import datetime, timedelta

# ==============================================================================
# CONFIG depuis les variables d'environnement
# ==============================================================================

ROOM_ID = os.environ.get("ROOM_ID", "")
CHECK_IN = os.environ.get("CHECK_IN", "")
CHECK_OUT = os.environ.get("CHECK_OUT", "")
CURRENCY = os.environ.get("CURRENCY", "AED")
PROXY_URL = ""
LANGUAGE = "en"

# ==============================================================================
# MAIN
# ==============================================================================

print("=" * 80)
print("🧪 TEST GET_DETAILS (PRIX) — pyairbnb 2.1.1")
print("=" * 80)
print(f"📅 Date du test  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"🏠 Room ID       : {ROOM_ID}")
print(f"💰 Devise        : {CURRENCY}")
print("=" * 80)

if not ROOM_ID:
    print("❌ ERREUR: Aucun ROOM_ID fourni!")
    exit(1)


# ------------------------------------------------------------------------------
# Définir les plages de dates à tester
# ------------------------------------------------------------------------------

date_ranges = []

if CHECK_IN and CHECK_OUT:
    # Dates fournies par l'utilisateur
    date_ranges.append({
        "name": "Dates personnalisées",
        "check_in": CHECK_IN,
        "check_out": CHECK_OUT,
    })
else:
    # Dates automatiques pour tester plusieurs scénarios
    today = datetime.now()
    
    # Test 1: Demain → Après-demain (1 nuit)
    d1_in = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    d1_out = (today + timedelta(days=2)).strftime("%Y-%m-%d")
    date_ranges.append({"name": "Demain (1 nuit)", "check_in": d1_in, "check_out": d1_out})
    
    # Test 2: Dans 7 jours → +2 nuits
    d2_in = (today + timedelta(days=7)).strftime("%Y-%m-%d")
    d2_out = (today + timedelta(days=9)).strftime("%Y-%m-%d")
    date_ranges.append({"name": "Dans 7 jours (2 nuits)", "check_in": d2_in, "check_out": d2_out})
    
    # Test 3: Dans 30 jours → +3 nuits
    d3_in = (today + timedelta(days=30)).strftime("%Y-%m-%d")
    d3_out = (today + timedelta(days=33)).strftime("%Y-%m-%d")
    date_ranges.append({"name": "Dans 30 jours (3 nuits)", "check_in": d3_in, "check_out": d3_out})
    
    # Test 4: Dans 90 jours → +5 nuits
    d4_in = (today + timedelta(days=90)).strftime("%Y-%m-%d")
    d4_out = (today + timedelta(days=95)).strftime("%Y-%m-%d")
    date_ranges.append({"name": "Dans 90 jours (5 nuits)", "check_in": d4_in, "check_out": d4_out})
    
    # Test 5: Sans dates (pour comparer)
    date_ranges.append({"name": "SANS DATES", "check_in": None, "check_out": None})


print(f"\n📋 {len(date_ranges)} tests de dates prévus:")
for i, dr in enumerate(date_ranges, 1):
    print(f"   {i}. {dr['name']}: {dr['check_in']} → {dr['check_out']}")


# ------------------------------------------------------------------------------
# Fonction pour extraire et afficher les infos de prix
# ------------------------------------------------------------------------------

def extract_price_info(details):
    """Extrait toutes les infos liées au prix depuis get_details()"""
    
    price_info = {
        "found_keys": [],
        "prices": {},
    }
    
    if not isinstance(details, dict):
        return price_info
    
    # Chercher toutes les clés contenant "price" ou "cost" ou "fee"
    def search_price_keys(obj, prefix=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                full_key = f"{prefix}.{key}" if prefix else key
                key_lower = key.lower()
                
                if any(word in key_lower for word in ["price", "cost", "fee", "rate", "total", "amount"]):
                    price_info["found_keys"].append(full_key)
                    price_info["prices"][full_key] = value
                
                search_price_keys(value, full_key)
        elif isinstance(obj, list):
            for i, item in enumerate(obj[:5]):  # Limiter aux 5 premiers
                search_price_keys(item, f"{prefix}[{i}]")
    
    search_price_keys(details)
    return price_info


# ------------------------------------------------------------------------------
# Exécuter les tests
# ------------------------------------------------------------------------------

for idx, date_range in enumerate(date_ranges, 1):
    print("\n" + "=" * 80)
    print(f"📦 TEST {idx}/{len(date_ranges)}: {date_range['name']}")
    print("=" * 80)
    print(f"   Check-in  : {date_range['check_in']}")
    print(f"   Check-out : {date_range['check_out']}")
    print("-" * 80)
    
    try:
        # Appeler get_details avec ou sans dates
        if date_range['check_in'] and date_range['check_out']:
            details = pyairbnb.get_details(
                room_id=int(ROOM_ID),
                check_in=date_range['check_in'],
                check_out=date_range['check_out'],
                currency=CURRENCY,
                proxy_url=PROXY_URL,
                adults=2,
                language=LANGUAGE,
            )
        else:
            details = pyairbnb.get_details(
                room_id=int(ROOM_ID),
                currency=CURRENCY,
                proxy_url=PROXY_URL,
                adults=2,
                language=LANGUAGE,
            )
        
        print("✅ get_details() réussi!")
        
        # ----------------------------------------------------------------------
        # Afficher les clés de premier niveau
        # ----------------------------------------------------------------------
        print("\n🔍 Clés de premier niveau:")
        if isinstance(details, dict):
            keys = list(details.keys())
            print(f"   {keys}")
        
        # ----------------------------------------------------------------------
        # Chercher et afficher tout ce qui concerne les PRIX
        # ----------------------------------------------------------------------
        print("\n💰 RECHERCHE DES PRIX DANS LA RÉPONSE:")
        print("-" * 40)
        
        price_info = extract_price_info(details)
        
        if price_info["found_keys"]:
            print(f"\n✅ {len(price_info['found_keys'])} champs liés aux prix trouvés:")
            for key in price_info["found_keys"][:20]:  # Max 20
                value = price_info["prices"].get(key, "N/A")
                # Tronquer si trop long
                value_str = str(value)
                if len(value_str) > 100:
                    value_str = value_str[:100] + "..."
                print(f"   • {key}: {value_str}")
        else:
            print("   ⚠️ Aucun champ de prix trouvé!")
        
        # ----------------------------------------------------------------------
        # Afficher des champs spécifiques s'ils existent
        # ----------------------------------------------------------------------
        print("\n📊 CHAMPS SPÉCIFIQUES:")
        print("-" * 40)
        
        specific_fields = [
            "price",
            "price_string",
            "priceString", 
            "total_price",
            "totalPrice",
            "nightly_price",
            "nightlyPrice",
            "base_price",
            "basePrice",
            "cleaning_fee",
            "cleaningFee",
            "service_fee",
            "serviceFee",
            "rate",
            "rate_per_night",
        ]
        
        for field in specific_fields:
            if field in details:
                print(f"   ✅ {field}: {details[field]}")
        
        # Vérifier aussi dans des sous-objets courants
        sub_objects = ["pricing", "price_details", "priceDetails", "rates", "fees"]
        for sub in sub_objects:
            if sub in details and details[sub]:
                print(f"\n   📦 Sous-objet '{sub}':")
                print(f"   {json.dumps(details[sub], indent=2, ensure_ascii=False)[:500]}")
        
        # ----------------------------------------------------------------------
        # Afficher le JSON brut complet (limité)
        # ----------------------------------------------------------------------
        print("\n📄 JSON BRUT COMPLET (premiers 3000 caractères):")
        print("-" * 40)
        json_str = json.dumps(details, indent=2, ensure_ascii=False)
        print(json_str[:3000])
        if len(json_str) > 3000:
            print(f"\n... [TRONQUÉ - {len(json_str)} caractères au total]")
        
    except Exception as e:
        print(f"❌ ERREUR: {repr(e)}")
        import traceback
        traceback.print_exc()


# ------------------------------------------------------------------------------
# RÉSUMÉ FINAL
# ------------------------------------------------------------------------------

print("\n" + "=" * 80)
print("🎉 TESTS TERMINÉS")
print("=" * 80)
print(f"Room ID testé : {ROOM_ID}")
print(f"Devise        : {CURRENCY}")
print(f"Tests exécutés: {len(date_ranges)}")
print("=" * 80)
