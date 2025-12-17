import pyairbnb
import json
import os
from datetime import datetime

# ==============================================================================
# CONFIG
# ==============================================================================

ROOM_ID = os.environ.get("ROOM_ID", "")
PROXY_URL = ""

# ==============================================================================
# MAIN
# ==============================================================================

print("=" * 80)
print("🧪 TEST GET_CALENDAR — pyairbnb 2.1.1")
print("=" * 80)
print(f"📅 Date du test  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"🏠 Room ID       : {ROOM_ID}")
print("=" * 80)

if not ROOM_ID:
    print("❌ ERREUR: Aucun ROOM_ID fourni!")
    print("   → Vérifie que tu as bien saisi un Room ID dans l'input du workflow")
    exit(1)


# ------------------------------------------------------------------------------
# ÉTAPE 1 : Récupérer l'API Key
# ------------------------------------------------------------------------------

print("\n" + "-" * 80)
print("📦 ÉTAPE 1 : Récupération de l'API Key")
print("-" * 80)

try:
    api_key = pyairbnb.get_api_key(PROXY_URL)
    print(f"✅ API Key récupérée : {api_key[:20]}..." if len(api_key) > 20 else f"✅ API Key : {api_key}")
except Exception as e:
    print(f"❌ ERREUR get_api_key(): {repr(e)}")
    exit(1)


# ------------------------------------------------------------------------------
# ÉTAPE 2 : Appeler get_calendar()
# ------------------------------------------------------------------------------

print("\n" + "-" * 80)
print("📦 ÉTAPE 2 : Appel de get_calendar()")
print("-" * 80)

try:
    calendar_data = pyairbnb.get_calendar(
        api_key=api_key,
        room_id=ROOM_ID,
        proxy_url=PROXY_URL,
    )
    print("✅ get_calendar() réussi!")
except Exception as e:
    print(f"❌ ERREUR get_calendar(): {repr(e)}")
    exit(1)


# ------------------------------------------------------------------------------
# ÉTAPE 3 : Analyser la structure des données
# ------------------------------------------------------------------------------

print("\n" + "-" * 80)
print("📦 ÉTAPE 3 : Structure des données reçues")
print("-" * 80)

print(f"\n🔍 Type de calendar_data : {type(calendar_data).__name__}")

if isinstance(calendar_data, list):
    print(f"🔍 Nombre d'éléments (mois) : {len(calendar_data)}")
    
    if len(calendar_data) > 0:
        first_month = calendar_data[0]
        print(f"\n🔍 Type du premier élément : {type(first_month).__name__}")
        
        if isinstance(first_month, dict):
            print(f"🔍 Clés du premier mois : {list(first_month.keys())}")

elif isinstance(calendar_data, dict):
    print(f"🔍 Clés principales : {list(calendar_data.keys())}")

else:
    print(f"🔍 Données brutes : {calendar_data}")


# ------------------------------------------------------------------------------
# ÉTAPE 4 : Afficher le PREMIER MOIS en détail
# ------------------------------------------------------------------------------

print("\n" + "-" * 80)
print("📦 ÉTAPE 4 : Premier mois — Structure complète")
print("-" * 80)

if isinstance(calendar_data, list) and len(calendar_data) > 0:
    first_month = calendar_data[0]
    
    # Afficher les métadonnées du mois (sans les jours)
    month_info = {k: v for k, v in first_month.items() if k != 'days'}
    print("\n📅 Infos du mois (hors jours) :")
    print(json.dumps(month_info, indent=2, ensure_ascii=False))
    
    # Afficher le nombre de jours
    days = first_month.get('days', [])
    print(f"\n📅 Nombre de jours dans ce mois : {len(days)}")
    
    if len(days) > 0:
        print("\n📅 Structure d'UN JOUR (premier jour) :")
        print(json.dumps(days[0], indent=2, ensure_ascii=False))
        
        print("\n📅 Clés disponibles pour chaque jour :")
        print(list(days[0].keys()))


# ------------------------------------------------------------------------------
# ÉTAPE 5 : Afficher les 5 premiers jours avec prix
# ------------------------------------------------------------------------------

print("\n" + "-" * 80)
print("📦 ÉTAPE 5 : Les 10 premiers jours (aperçu rapide)")
print("-" * 80)

if isinstance(calendar_data, list) and len(calendar_data) > 0:
    first_month = calendar_data[0]
    days = first_month.get('days', [])
    
    print("\n{:<15} {:<12} {:<20} {:<10}".format("DATE", "AVAILABLE", "PRIX", "MIN NIGHTS"))
    print("-" * 60)
    
    for day in days[:10]:
        date = day.get('calendarDate', day.get('date', 'N/A'))
        available = day.get('available', 'N/A')
        
        # Chercher le prix dans différentes structures possibles
        price_data = day.get('price', {})
        if isinstance(price_data, dict):
            price = price_data.get('localPriceFormatted', 
                    price_data.get('localPrice',
                    price_data.get('amount', 'N/A')))
        else:
            price = price_data if price_data else 'N/A'
        
        min_nights = day.get('minNights', day.get('minimumNights', 'N/A'))
        
        print(f"{date:<15} {str(available):<12} {str(price):<20} {str(min_nights):<10}")


# ------------------------------------------------------------------------------
# ÉTAPE 6 : Résumé de TOUS les mois
# ------------------------------------------------------------------------------

print("\n" + "-" * 80)
print("📦 ÉTAPE 6 : Résumé de tous les mois")
print("-" * 80)

if isinstance(calendar_data, list):
    print("\n{:<10} {:<8} {:<12} {:<15}".format("MOIS", "ANNÉE", "NB JOURS", "JOURS DISPO"))
    print("-" * 50)
    
    for month_data in calendar_data:
        if isinstance(month_data, dict):
            month = month_data.get('month', 'N/A')
            year = month_data.get('year', 'N/A')
            days = month_data.get('days', [])
            nb_days = len(days)
            available_days = sum(1 for d in days if d.get('available', False))
            
            print(f"{month:<10} {year:<8} {nb_days:<12} {available_days:<15}")


# ------------------------------------------------------------------------------
# ÉTAPE 7 : Dump JSON complet (1er mois seulement pour ne pas surcharger)
# ------------------------------------------------------------------------------

print("\n" + "-" * 80)
print("📦 ÉTAPE 7 : JSON brut du PREMIER MOIS (complet)")
print("-" * 80)

if isinstance(calendar_data, list) and len(calendar_data) > 0:
    print("\n" + json.dumps(calendar_data[0], indent=2, ensure_ascii=False))


# ------------------------------------------------------------------------------
# FIN
# ------------------------------------------------------------------------------

print("\n" + "=" * 80)
print("🎉 TEST TERMINÉ")
print("=" * 80)
print(f"Room ID testé : {ROOM_ID}")
print(f"Mois récupérés: {len(calendar_data) if isinstance(calendar_data, list) else 'N/A'}")
print("=" * 80)
