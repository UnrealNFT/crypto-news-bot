#!/usr/bin/env python3
"""Script de diagnostic Ollama pour identifier le problème de traduction"""

import requests
import json
import time

def test_ollama_connection():
    """Teste la connexion à l'API Ollama"""
    print("🔍 Test 1: Connexion API Ollama...")
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"✅ API Ollama accessible")
            print(f"📋 Modèles disponibles: {len(models)}")
            for model in models:
                print(f"   - {model['name']} ({model.get('size', 'Unknown')} bytes)")
            return [m['name'] for m in models]
        else:
            print(f"❌ API répond mais erreur: {response.status_code}")
            return []
    except requests.exceptions.ConnectionError:
        print("❌ ERREUR: Ollama n'est pas accessible sur localhost:11434")
        print("   Solution: systemctl start ollama")
        return []
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return []

def test_model_inference(model_name="llama3.2"):
    """Teste l'inférence avec un modèle spécifique"""
    print(f"\n🔍 Test 2: Inférence avec modèle '{model_name}'...")
    
    start_time = time.time()
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                "model": model_name,
                "prompt": "Translate to French: Bitcoin price rises today",
                "stream": False,
                "options": {"temperature": 0.7}
            },
            timeout=120
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result.get('response', '')
            print(f"✅ Inférence réussie en {elapsed:.1f}s")
            print(f"📝 Réponse: {generated_text[:200]}")
            return True
        elif response.status_code == 404:
            print(f"❌ Modèle '{model_name}' introuvable!")
            print("   Solution: ollama pull llama3.2")
            print("   OU changer le modèle dans crypto_news_bot.py")
            return False
        else:
            print(f"❌ Erreur API: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        print(f"❌ TIMEOUT après {elapsed:.1f}s")
        print("   Le serveur est probablement trop lent ou le modèle trop gros")
        print("   Solution: Utiliser un modèle plus petit ou augmenter la RAM")
        return False
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ Erreur après {elapsed:.1f}s: {e}")
        return False

def test_json_parsing():
    """Teste le parsing JSON avec un prompt réaliste"""
    print(f"\n🔍 Test 3: Parsing JSON avec prompt réaliste...")
    
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                "model": "llama3.2",
                "prompt": """Traduis cet article crypto en français.

Titre: Bitcoin hits new all-time high
Description: Bitcoin reaches $100,000 for the first time in history

Réponds au format JSON:
{
    "titre_fr": "titre traduit",
    "description_fr": "description traduite",
    "resume": "résumé en 2-3 phrases"
}""",
                "stream": False,
                "options": {"temperature": 0.7}
            },
            timeout=120
        )
        
        if response.status_code == 200:
            content = response.json().get('response', '')
            print(f"✅ Réponse brute reçue ({len(content)} chars)")
            
            # Nettoie la réponse
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:-3]
            elif content.startswith('```'):
                content = content[3:-3]
            
            try:
                result = json.loads(content)
                if all(k in result for k in ['titre_fr', 'description_fr', 'resume']):
                    print(f"✅ JSON valide avec tous les champs requis")
                    print(f"   titre_fr: {result['titre_fr']}")
                    print(f"   description_fr: {result['description_fr'][:80]}...")
                    return True
                else:
                    print(f"⚠️ JSON valide mais champs manquants: {list(result.keys())}")
                    return False
            except json.JSONDecodeError as e:
                print(f"❌ Erreur parsing JSON: {e}")
                print(f"   Contenu: {content[:200]}")
                return False
        else:
            print(f"❌ Erreur API: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    print("=" * 60)
    print("🔧 DIAGNOSTIC OLLAMA POUR CRYPTO-BOT")
    print("=" * 60)
    
    # Test 1: Connexion et liste des modèles
    available_models = test_ollama_connection()
    
    if not available_models:
        print("\n❌ Ollama n'est pas accessible. Arrêt du diagnostic.")
        return
    
    # Test 2: Inférence avec le modèle configuré
    if "llama3.2" in available_models or "llama3.2:latest" in available_models:
        success = test_model_inference("llama3.2")
    elif available_models:
        print(f"\n⚠️ 'llama3.2' absent, test avec '{available_models[0]}'")
        success = test_model_inference(available_models[0].split(':')[0])
    
    # Test 3: Parsing JSON complet
    if success:
        test_json_parsing()
    
    print("\n" + "=" * 60)
    print("🏁 DIAGNOSTIC TERMINÉ")
    print("=" * 60)

if __name__ == "__main__":
    main()
