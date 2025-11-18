import pyairbnb
import json
import time
from datetime import datetime

# =================================================================
# ZONE DOWNTOWN DUBAI — bounding box stable
# =================================================================
NE_LAT = 25.2109
NE_LONG = 55.2850
SW_LAT = 25.1880
SW_LONG = 55.2560
ZOOM_VALUE = 13

PROXY_URL = ""
LANGUAGE = "en"

# =================================================================
# Dates OBLIGATOIRES (mais on les rend très larges pour maximiser)
# =================================================================
CHECK_IN = "2025-01-15"
CHECK_OUT = "2025-01-16"

PRICE_MIN = 0
PRICE_MAX = 20000   # très large = remonte presque tout

# =================================================================
def print_result(title, data, error=None):
    print("\n" + "="*80)
    print(f"📦 {title}")
    print("="*80)
    if error:
        print(f"❌ ERREUR: {error}")
        return
    print("✅ SUCCÈS\n")
    if isinstance(data, list):
        print(f"📋 Nombre d’éléments: {len(data)}")
        if len(data) > 0:
            print("\n🔍 Premier élément:")
            print(json.dumps(data[0], indent=2, ensure_ascii=False))
    else:
        print(json.dumps(data, indent=2, ensure_ascii=False))

# =================================================================
print("🚀 TEST DOWNTOWN — pyairbnb 2.1.1")

# =================================================================
# TEST API KEY
# =================================================================
try:
    api_key = pyairbnb.get_api_key(PROXY_URL)
    print_result("API KEY", {"value": api_key})
except Exception as e:
    print_result("API KEY", None, error=str(e))
    api_key = None

time.sleep(1)

# =================================================================
# TEST SEARCH_ALL — Downtown, dates fictives
# =================================================================
try:
    listings = pyairbnb.search_all(
        ne_lat=NE_LAT,
        ne_long=NE_LONG,
        sw_lat=SW_LAT,
        sw_long=SW_LONG,
        zoom_value=ZOOM_VALUE,
        check_in=CHECK_IN,
        check_out=CHECK_OUT,
        price_min=PRICE_MIN,
        price_max=PRICE_MAX,
        language=LANGUAGE,
        proxy_url=PROXY_URL,
    )
    print_result("LISTINGS — DOWNTOWN", listings)
except Exception as e:
    print_result("LISTINGS — DOWNTOWN", None, error=str(e))
    listings = []

# =================================================================
# RÉSUMÉ
# =================================================================
print("\n" + "🎉"*40)
print(f"Listings trouvés : {len(listings)}")
print(f"Dates utilisées : {CHECK_IN} → {CHECK_OUT}")
print(f"Prix min/max     : {PRICE_MIN} / {PRICE_MAX}")
print(f"Zoom             : {ZOOM_VALUE}")
print("🎉"*40)
