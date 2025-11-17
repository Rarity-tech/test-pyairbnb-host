import pyairbnb
import json
import time
from datetime import datetime

# ============================================
# 🎯 CONFIGURATION - MODIFIEZ JUSTE ICI
# ============================================
TEST_HOST_ID = "1470649053408437506"  # ← METTEZ VOTRE HOST_ID ICI
PROXY_URL = ""
LANGUAGE = "en"

# ============================================
# 📊 FONCTION POUR AFFICHER LES RÉSULTATS
# ============================================
def print_result(title, data, error=None):
    """Affiche les résultats de manière lisible"""
    print("\n" + "=" * 80)
    print(f"📦 {title}")
    print("=" * 80)
    
    if error:
        print(f"❌ ERREUR: {error}")
    else:
        print("✅ SUCCÈS")
        print("\n🔍 TYPE DE DONNÉES:", type(data).__name__)
        
        if data is None:
            print("⚠️ Résultat: None (vide)")
        elif isinstance(data, dict):
            print(f"📋 Dictionnaire avec {len(data)} clés")
            print("\n🗝️ CLÉS DISPONIBLES:")
            for key in data.keys():
                print(f"   • {key}")
            print("\n📄 CONTENU COMPLET (JSON):")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        elif isinstance(data, list):
            print(f"📋 Liste avec {len(data)} éléments")
            if len(data) > 0:
                print(f"\n🔍 Premier élément (type: {type(data[0]).__name__}):")
                print(json.dumps(data[0], indent=2, ensure_ascii=False))
                if len(data) > 1:
                    print(f"\n... et {len(data) - 1} autres éléments")
            print("\n📄 LISTE COMPLÈTE:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"📄 VALEUR: {data}")
    
    print("=" * 80 + "\n")


# ============================================
# 🧪 TESTS DES FONCTIONS HOST
# ============================================

print("\n" + "🚀" * 40)
print(f"🧪 TEST PYAIRBNB HOST FUNCTIONS")
print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("🚀" * 40)
print(f"\n🎯 Host ID à tester: {TEST_HOST_ID}")
print(f"🌍 Langue: {LANGUAGE}")
print(f"🔗 Proxy: {'Oui' if PROXY_URL else 'Non'}\n")

# ============================================
# TEST 1: Récupérer l'API Key
# ============================================
print("\n" + "🔑" * 40)
print("TEST 1: pyairbnb.get_api_key()")
print("🔑" * 40)

try:
    api_key = pyairbnb.get_api_key(PROXY_URL)
    print_result("API KEY", {"api_key": api_key, "length": len(api_key) if api_key else 0})
except Exception as e:
    print_result("API KEY", None, error=str(e))
    api_key = None

time.sleep(2)

# ============================================
# TEST 2: get_host_details (avec API key)
# ============================================
print("\n" + "👤" * 40)
print("TEST 2: pyairbnb.get_host_details()")
print("👤" * 40)

if api_key:
    try:
        print(f"📞 Appel: pyairbnb.get_host_details(api_key, None, '{TEST_HOST_ID}', '{LANGUAGE}', '{PROXY_URL}')")
        
        host_details = pyairbnb.get_host_details(
            api_key,
            None,  # cookies
            TEST_HOST_ID,
            LANGUAGE,
            PROXY_URL
        )
        
        print_result("HOST DETAILS", host_details)
        
        # Extraire les infos importantes si disponibles
        if host_details and isinstance(host_details, dict):
            print("\n🎯 INFORMATIONS EXTRAITES:")
            print(f"   • Nom: {host_details.get('first_name', 'N/A')}")
            print(f"   • Rating: {host_details.get('overall_rating', 'N/A')}")
            print(f"   • Reviews: {host_details.get('review_count', 'N/A')}")
            print(f"   • Member since: {host_details.get('member_since', 'N/A')}")
            print(f"   • Identité vérifiée: {host_details.get('is_identity_verified', 'N/A')}")
            
    except Exception as e:
        print_result("HOST DETAILS", None, error=str(e))
        host_details = None
else:
    print("⚠️ SKIP - Pas d'API key disponible")
    host_details = None

time.sleep(2)

# ============================================
# TEST 3: get_listings_from_user
# ============================================
print("\n" + "🏠" * 40)
print("TEST 3: pyairbnb.get_listings_from_user()")
print("🏠" * 40)

if api_key:
    try:
        print(f"📞 Appel: pyairbnb.get_listings_from_user('{TEST_HOST_ID}', api_key, '{PROXY_URL}')")
        
        host_listings = pyairbnb.get_listings_from_user(
            TEST_HOST_ID,
            api_key,
            PROXY_URL
        )
        
        print_result("HOST LISTINGS", host_listings)
        
        # Compter les listings
        if host_listings:
            if isinstance(host_listings, list):
                print(f"\n🎯 TOTAL LISTINGS: {len(host_listings)}")
                if len(host_listings) > 0:
                    print("\n🏠 Exemple - Premier listing:")
                    first = host_listings[0]
                    if isinstance(first, dict):
                        print(f"   • ID: {first.get('id', 'N/A')}")
                        print(f"   • Nom: {first.get('name', 'N/A')}")
                        print(f"   • Type: {first.get('room_type', 'N/A')}")
            
    except Exception as e:
        print_result("HOST LISTINGS", None, error=str(e))
        host_listings = None
else:
    print("⚠️ SKIP - Pas d'API key disponible")
    host_listings = None

time.sleep(2)

# ============================================
# TEST 4: Tester avec un host_id différent
# ============================================
print("\n" + "🔄" * 40)
print("TEST 4: Test avec host_id alternatif (pour comparaison)")
print("🔄" * 40)

ALTERNATIVE_HOST_ID = "6967528"  # Un autre host pour comparer

if api_key:
    try:
        print(f"📞 Appel: pyairbnb.get_host_details() avec host_id={ALTERNATIVE_HOST_ID}")
        
        alt_host = pyairbnb.get_host_details(
            api_key,
            None,
            ALTERNATIVE_HOST_ID,
            LANGUAGE,
            PROXY_URL
        )
        
        print_result("HOST ALTERNATIF - DETAILS", alt_host)
        
    except Exception as e:
        print_result("HOST ALTERNATIF - DETAILS", None, error=str(e))
else:
    print("⚠️ SKIP - Pas d'API key disponible")

# ============================================
# RÉSUMÉ FINAL
# ============================================
print("\n" + "🎉" * 40)
print("📊 RÉSUMÉ DES TESTS")
print("🎉" * 40)
print(f"✅ API Key: {'Récupérée' if api_key else '❌ Échec'}")
print(f"✅ Host Details: {'Récupéré' if host_details else '❌ Échec'}")
print(f"✅ Host Listings: {'Récupéré' if 'host_listings' in locals() and host_listings else '❌ Échec'}")
print("\n💡 Consultez les logs ci-dessus pour voir les données brutes complètes")
print("🎉" * 40 + "\n")
