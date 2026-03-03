import asyncio
from crypto_news_bot import get_crypto_news, translate_with_chatgpt, test_bot

async def quick_test():
    """Test rapide des fonctionnalités principales"""
    print("🧪 Test de connectivité...")
    
    # Test 1: Telegram Bot
    print("\n1️⃣ Test Telegram Bot...")
    telegram_ok = await test_bot()
    
    # Test 2: Sources crypto multi
    print("\n2️⃣ Test sources crypto múltiples...")
    articles = get_crypto_news()
    print(f"   ✅ {len(articles)} articles récupérés")
    
    # Test 3: Traduction ChatGPT (avec le premier article)
    if articles:
        print("\n3️⃣ Test traduction ChatGPT...")
        translation = translate_with_chatgpt(articles[0])
        print(f"   ✅ Traduction réussie: {translation['titre_fr'][:50]}...")
    
    print(f"\n🎯 Résultats:")
    print(f"   Telegram: {'✅ OK' if telegram_ok else '❌ Erreur'}")
    print(f"   RSS: {'✅ OK' if articles else '❌ Erreur'}")
    print(f"   ChatGPT: {'✅ OK' if articles and 'titre_fr' in translation else '❌ Erreur'}")
    
    if telegram_ok and articles and 'titre_fr' in translation:
        print("\n🚀 Tout fonctionne ! Vous pouvez lancer le bot principal.")
    else:
        print("\n⚠️  Vérifiez votre configuration dans config.py")

if __name__ == "__main__":
    asyncio.run(quick_test())