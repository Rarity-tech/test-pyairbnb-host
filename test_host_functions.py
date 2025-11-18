import pyairbnb
from datetime import datetime, timedelta

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------

# Centre approximatif de Downtown Dubai (ton point de départ)
LAT = 25.195
LNG = 55.276

CHECKIN  = "2025-11-19"
CHECKOUT = "2026-03-16"

ZOOM_VALUE   = 10
PRICE_MIN    = 0
PRICE_MAX    = 20000
CURRENCY     = "AED"
LANGUAGE     = "en"
PROXY_URL    = ""          # laisse vide si pas de proxy
PLACE_TYPE   = ""          # "Entire home/apt" / "Private room" / "" pour tout
AMENITIES    = []          # ex: [4,7] si tu veux filtrer, sinon vide
FREE_CANCEL  = False       # True si tu veux uniquement annulation flexible

# Pour transformer ton point (LAT, LNG) en petite "boîte" autour
DELTA = 0.02  # ~ petite zone autour de Downtown


# ---------------------------------------------------------
# FONCTIONS UTILES
# ---------------------------------------------------------

def build_bbox_from_center(lat, lng, delta=0.02):
    """
    À partir d'un point (lat, lng), construit un petit rectangle
    nord-est / sud-ouest compatible avec pyairbnb.search_all().
    """
    ne_lat = lat + delta
    ne_long = lng + delta
    sw_lat = lat - delta
    sw_long = lng - delta
    return ne_lat, ne_long, sw_lat, sw_long


def extract_room_id_and_url(listing: dict):
    """
    Essaie de récupérer un room_id et/ou une URL depuis la structure du listing.
    On ne casse pas tout si une clé manque : on teste plusieurs possibilités.
    """
    if not isinstance(listing, dict):
        return None, None

    # Différentes variantes possibles selon la structure
    room_id = (
        listing.get("id")
        or listing.get("room_id")
        or listing.get("roomId")
        or listing.get("listing", {}).get("id")
        or listing.get("listing", {}).get("roomId")
    )

    room_url = (
        listing.get("url")
        or listing.get("room_url")
        or listing.get("listing", {}).get("url")
    )

    return room_id, room_url


# ---------------------------------------------------------
# TEST DOWNTOWN
# ---------------------------------------------------------

print("🚀 TEST DOWNTOWN — pyairbnb 2.1.1\n")

# 1) BBOX pour search_all
ne_lat, ne_long, sw_lat, sw_long = build_bbox_from_center(LAT, LNG, DELTA)

print("="*80)
print("📦 PARAMÈTRES DE RECHERCHE")
print("="*80)
print(f"Centre         : ({LAT}, {LNG})")
print(f"BBOX NE / SW   : NE=({ne_lat}, {ne_long})  SW=({sw_lat}, {sw_long})")
print(f"Dates          : {CHECKIN} → {CHECKOUT}")
print(f"Prix min / max : {PRICE_MIN} / {PRICE_MAX}")
print(f"Zoom value     : {ZOOM_VALUE}")
print("")

# 2) SEARCH ALL
print("\n" + "="*80)
print("📦 LISTINGS — DOWNTOWN (pyairbnb.search_all)")
print("="*80)

try:
    listings = pyairbnb.search_all(
        check_in=CHECKIN,
        check_out=CHECKOUT,
        ne_lat=ne_lat,
        ne_long=ne_long,
        sw_lat=sw_lat,
        sw_long=sw_long,
        zoom_value=ZOOM_VALUE,
        price_min=PRICE_MIN,
        price_max=PRICE_MAX,
        place_type=PLACE_TYPE,
        amenities=AMENITIES,
        free_cancellation=FREE_CANCEL,
        currency=CURRENCY,
        language=LANGUAGE,
        proxy_url=PROXY_URL,
    )

    print("✅ SUCCÈS search_all()\n")

    # Selon la lib, ça peut retourner une liste directe ou un dict {"results": [...]}
    if isinstance(listings, dict) and "results" in listings:
        results = listings["results"]
    else:
        results = listings

    print("📋 Nombre d’éléments:", len(results))

    if len(results) == 0:
        print("⚠️ Aucun listing trouvé.")
        exit(0)

    print("\n🔍 Premier élément brut (keys au 1er niveau):")
    first = results[0]
    if isinstance(first, dict):
        print("Clés disponibles:", list(first.keys()))
    print(first)

except Exception as e:
    print("❌ ERREUR LISTINGS:", repr(e))
    exit(1)


# 3) SURCOUCHE : DÉTAILS POUR LES 3 PREMIERS LISTINGS
print("\n" + "="*80)
print("📦 DÉTAILS — PREMIERS LISTINGS (pyairbnb.get_details)")
print("="*80)

try:
    sample = results[:3]  # on limite à 3 listings

    for idx, item in enumerate(sample, start=1):
        print(f"\n--- 🔎 DETAILS LISTING #{idx} ---")

        room_id, room_url = extract_room_id_and_url(item)

        if room_id is None and room_url is None:
            print("⚠️ Impossible de trouver un room_id ou une URL dans ce listing, on saute.")
            continue

        print("➡️ room_id :", room_id)
        print("➡️ room_url:", room_url)

        # On essaye d'abord avec room_id, sinon avec room_url
        if room_id is not None:
            details = pyairbnb.get_details(
                room_id=room_id,
                currency=CURRENCY,
                proxy_url=PROXY_URL,
                adults=2,
                language=LANGUAGE,
            )
        else:
            details = pyairbnb.get_details(
                room_url=room_url,
                currency=CURRENCY,
                adults=2,
                language=LANGUAGE,
            )

        # On ne flood pas tout : on montre juste quelques clés
                if isinstance(details, dict):
            print("🧩 DETAILS — clés au 1er niveau:", list(details.keys()))
        print("🧩 DETAILS COMPLETS (repr brut) :")
        print(details)

except Exception as e:
    print("❌ ERREUR DETAILS:", repr(e))

# 4) RÉSUMÉ
print("\n" + "🎉"*40)
print(f"Listings trouvés : {len(results)}")
print(f"Dates utilisées  : {CHECKIN} → {CHECKOUT}")
print(f"Prix min/max     : {PRICE_MIN} / {PRICE_MAX}")
print(f"Zoom value       : {ZOOM_VALUE}")
print("🎉"*40)
