import pyairbnb
import json
import time
from datetime import datetime

# ============================================================
# 🎯 PARAMÈTRES DE LA ZONE (DOWNTOWN DUBAI)
# ============================================================
NE_LAT = 25.2109
NE_LONG = 55.2850
SW_LAT = 25.1880
SW_LONG = 55.2560
ZOOM_VALUE = 13

PROXY_URL = ""
LANGUAGE = "en"

# ============================================================
# 📊 FONCTION D'AFFICHAGE
# ============================================================
def print_result(title, data, error=None):
    print("\n" + "=" * 80)
    print(f"📦 {title}")
    print("=" * 80)
    
    if error:
        print(f"❌ ERREUR: {error}")
        return
    
    print("✅ SUCCÈS")
    print("\n🔍 TYPE:", type(data).__name__)
    
    if isinstance(data, list):
        print(f"📋 Nombre d’éléments: {len(data)}")

        if len(data) > 0:
            print("\n🔍 Premier élément:")
            print(json.dumps(data[0], indent=2, ensure_ascii=False))
        
        print("\n📄 LISTE COMPLÈTE:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    
    elif isinstance(data, dict):
        print("\n📋 Dictionnaire:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(data)

    print("=" * 80 + "\n")

# ============================================================
# 🚀 DÉBUT TEST
# ============================================================
print("\n" + "🚀" * 40)
print(f"🧪 TEST PYAIRBNB — LISTINGS DOWNTOWN SANS DATES")
print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("🚀" * 40)

# ============================================================
# TEST 1 : API KEY
# ============================================================
print("\n" + "🔑" * 40)
print("TEST 1 : pyairbnb.get_api_key(PROXY_URL)")
print("🔑" * 40)

try:
    api_key = pyairbnb.get_api_key(PROXY_URL)
    print_result("API KEY", {"api_key": api_key, "length": len(api_key)})
except Exception as e:
    print_result("API KEY", None, error=str(e))
    exit(1)

time.sleep(2)

# ============================================================
# TEST 2 : SEARCH_ALL SANS DATES
# ============================================================
print("\n" + "🌍" * 40)
print("TEST 2 : search_all() — Downtown, sans dates")
print("🌍" * 40)

try:
    listings = pyairbnb.search_all(
        api_key=api_key,
        ne_lat=NE_LAT,
        ne_long=NE_LONG,
        sw_lat=SW_LAT,
        sw_long=SW_LONG,
        zoom_value=ZOOM_VALUE,
        proxy_url=PROXY_URL,
        language=LANGUAGE
    )

    print_result("LISTINGS — DOWNTOWN (NO DATES)", listings)

except Exception as e:
    print_result("LISTINGS — DOWNTOWN (NO DATES)", None, error=str(e))
    exit(1)

# ============================================================
# RÉSUMÉ
# ============================================================
print("\n" + "🎉" * 40)
print("📊 RÉSUMÉ")
print("🎉" * 40)

print(f"Listings trouvés : {len(listings) if listings else 0}")
print(f"Zoom utilisé : {ZOOM_VALUE}")
print(f"Zone NE → ({NE_LAT}, {NE_LONG})")
print(f"Zone SW → ({SW_LAT}, {SW_LONG})")
print("🎉" * 40)
