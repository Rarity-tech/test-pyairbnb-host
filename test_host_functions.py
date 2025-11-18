from pyairbnb import Api
from datetime import datetime, timedelta

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
API_KEY = "d306zoyjsyarp7ifhu67rjxn52tv0t20"

# Downtown Dubai
LAT = 25.195
LNG = 55.276

CHECKIN  = "2025-01-15"
CHECKOUT = "2025-01-16"

ZOOM = 13
PRICE_MIN = 0
PRICE_MAX = 20000

# ---------------------------------------------------------
# INIT API
# ---------------------------------------------------------
api = Api(api_key=API_KEY)

print("🚀 TEST DOWNTOWN — pyairbnb 2.1.1\n")

# ---------------------------------------------------------
# TEST API KEY
# ---------------------------------------------------------
try:
    print("="*80)
    print("📦 API KEY")
    print("="*80)

    result = api.get_key()
    print("✅ SUCCÈS\n")
    print(result)

except Exception as e:
    print("❌ ERREUR KEY:", e)
    exit()

# ---------------------------------------------------------
# LISTINGS
# ---------------------------------------------------------
print("\n" + "="*80)
print("📦 LISTINGS — DOWNTOWN")
print("="*80)

try:
    listings = api.search_all(
        lat=LAT,
        lng=LNG,
        checkin=CHECKIN,
        checkout=CHECKOUT,
        min_price=PRICE_MIN,
        max_price=PRICE_MAX,
        zoom=ZOOM
    )

    print("✅ SUCCÈS\n")
    print("📋 Nombre d’éléments:", len(listings))

    if len(listings) == 0:
        print("⚠️ Aucun listing trouvé.")
        exit()

    print("\n🔍 Premier élément brut:")
    print(listings[0])

except Exception as e:
    print("❌ ERREUR LISTINGS:", e)
    exit()

# ---------------------------------------------------------
# DETAILS POUR LES PREMIERS LISTINGS
# ---------------------------------------------------------
print("\n" + "="*80)
print("📦 DÉTAILS — PREMIERS LISTINGS")
print("="*80)

try:
    # On limite volontairement à 3 listings pour éviter les logs massifs
    sample = listings[:3]

    for idx, item in enumerate(sample):
        print(f"\n--- 🔎 DETAILS LISTING #{idx+1} ---")

        listing_id = item.get("id")

        if not listing_id:
            print("⚠️ Listing sans ID, ignoré.")
            continue

        print("➡️ ID:", listing_id)

        try:
            details = api.get_listing_details(listing_id)

            print("🧩 DETAILS COMPLETS:")
            print(details)

        except Exception as err_details:
            print(f"❌ ÉCHEC RÉCUP DETAILS POUR {listing_id}: {err_details}")

except Exception as e:
    print("❌ ERREUR DETAILS:", e)

# ---------------------------------------------------------
# FIN
# ---------------------------------------------------------
print("\n" + "🎉"*40)
print(f"Listings trouvés : {len(listings)}")
print(f"Dates            : {CHECKIN} → {CHECKOUT}")
print(f"Prix min/max     : {PRICE_MIN} / {PRICE_MAX}")
print(f"Zoom             : {ZOOM}")
print("🎉"*40)
