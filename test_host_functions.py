import pyairbnb
import json
import time
from datetime import datetime

# ============================================
# 🎯 HOSTS À TESTER (avec profils publics)
# ============================================
TEST_HOSTS = [
    {
        "id": "174672201",
        "description": "Host public connu (exemple de la doc)"
    },
    {
        "id": "656454528", 
        "description": "Host public (exemple de la doc)"
    },
    {
        "id": "1470649053408437506",
        "description": "Votre host original (peut être privé)"
    }
]

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
            # Vérifier si c'est une erreur de permission
            if "errors" in data:
                print("⚠️ CONTIENT DES ERREURS API:")
                for err in data.get("errors", []):
                    print(f"   • {err.get('message', 'Unknown error')}")
                    extensions = err.get('extensions', {})
                    if 'errorType' in extensions:
                        print(f"   • Type: {extensions['errorType']}")
            
            print(f"\n📋 Dictionnaire avec {len(data)} clés")
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


def extract_host_info(host_details):
    """Extrait les infos importantes d'un host_details"""
    if not host_details or not isinstance(host_details, dict):
        return None
    
    # Vérifier les erreurs
    if "errors" in host_details:
        return {"error": "PERMISSION_DENIED ou autre erreur API"}
    
    data = host_details.get("data", {})
    
    # Essayer plusieurs chemins possibles
    info = {
        "first_name": None,
        "overall_rating": None,
        "review_count": None,
        "member_since": None,
        "is_identity_verified": None,
        "languages": []
    }
    
    # Chemin 1: data.node
    node = data.get("node", {})
    if node:
        host_rating_stats = node.get("hostRatingStats", {})
        info["overall_rating"] = host_rating_stats.get("ratingAverage")
        
        prompts = node.get("prompts", {})
        display_prompts = prompts.get("displayProfilePrompts", [])
        
        for prompt in display_prompts:
            if prompt.get("fieldId") == "LANGUAGES":
                info["languages"].append(prompt.get("subtitle"))
            if prompt.get("fieldId") == "IDENTITY_VERIFIED":
                info["is_identity_verified"] = True
    
    # Chemin 2: data.presentation.userProfileContainer.userProfile
    presentation = data.get("presentation", {})
    container = presentation.get("userProfileContainer", {})
    profile = container.get("userProfile")
    
    if profile:
        info["first_name"] = profile.get("firstName")
        info["member_since"] = profile.get("memberSince")
        info["review_count"] = profile.get("reviewsCount")
    
    return info


# ============================================
# 🧪 DÉBUT DES TESTS
# ============================================

print("\n" + "🚀" * 40)
print(f"🧪 TEST PYAIRBNB HOST FUNCTIONS")
print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("🚀" * 40)
print(f"\n🎯 Nombre de hosts à tester: {len(TEST_HOSTS)}")
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

if not api_key:
    print("❌ IMPOSSIBLE DE CONTINUER SANS API KEY")
    exit(1)

time.sleep(2)

# ============================================
# TEST 2: Tester chaque host
# ============================================
print("\n" + "👥" * 40)
print("TEST 2: Tester tous les hosts")
print("👥" * 40 + "\n")

results_summary = []

for idx, host in enumerate(TEST_HOSTS, start=1):
    host_id = host["id"]
    description = host["description"]
    
    print(f"\n{'='*80}")
    print(f"HOST #{idx}: {host_id}")
    print(f"Description: {description}")
    print(f"{'='*80}\n")
    
    result = {
        "host_id": host_id,
        "description": description,
        "host_details_success": False,
        "listings_success": False,
        "has_permission_error": False,
        "extracted_info": None,
        "listings_count": 0
    }
    
    # Test get_host_details
    print(f"📞 Test: pyairbnb.get_host_details()")
    try:
        host_details = pyairbnb.get_host_details(
            api_key,
            None,
            host_id,
            LANGUAGE,
            PROXY_URL
        )
        
        print_result(f"HOST DETAILS - {host_id}", host_details)
        
        # Vérifier si erreur de permission
        if isinstance(host_details, dict) and "errors" in host_details:
            result["has_permission_error"] = True
            result["host_details_success"] = False
        else:
            result["host_details_success"] = True
            result["extracted_info"] = extract_host_info(host_details)
            
            if result["extracted_info"]:
                print("\n🎯 INFORMATIONS EXTRAITES:")
                for key, value in result["extracted_info"].items():
                    print(f"   • {key}: {value}")
        
    except Exception as e:
        print_result(f"HOST DETAILS - {host_id}", None, error=str(e))
        result["host_details_success"] = False
    
    time.sleep(2)
    
    # Test get_listings_from_user
    print(f"📞 Test: pyairbnb.get_listings_from_user()")
    try:
        listings = pyairbnb.get_listings_from_user(
            host_id,
            api_key,
            PROXY_URL
        )
        
        print_result(f"HOST LISTINGS - {host_id}", listings)
        
        if listings and isinstance(listings, list):
            result["listings_success"] = True
            result["listings_count"] = len(listings)
        
    except Exception as e:
        print_result(f"HOST LISTINGS - {host_id}", None, error=str(e))
        result["listings_success"] = False
    
    results_summary.append(result)
    time.sleep(2)

# ============================================
# RÉSUMÉ FINAL
# ============================================
print("\n" + "🎉" * 40)
print("📊 RÉSUMÉ COMPLET DES TESTS")
print("🎉" * 40 + "\n")

print(f"✅ API Key: Récupérée\n")

for idx, result in enumerate(results_summary, start=1):
    print(f"HOST #{idx}: {result['host_id']}")
    print(f"   Description: {result['description']}")
    print(f"   Host Details: {'✅' if result['host_details_success'] else '❌'}")
    print(f"   Listings: {'✅' if result['listings_success'] else '❌'} ({result['listings_count']} listings)")
    print(f"   Permission Error: {'⚠️ OUI' if result['has_permission_error'] else '✅ NON'}")
    if result['extracted_info']:
        print(f"   Infos extraites: ✅ {result['extracted_info']}")
    print()

print("🎉" * 40)
print("\n💡 CONCLUSIONS:")
print("   • Si tous les hosts ont des erreurs de permission: pyairbnb ne peut pas accéder aux profils")
print("   • Si certains fonctionnent: on peut adapter le code pour gérer les succès et échecs")
print("   • Les hosts avec profils publics devraient retourner des données complètes")
print("\n🎉" * 40 + "\n")
