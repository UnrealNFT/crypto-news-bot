import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import BOT_TOKEN, CHAT_ID
from src.rss import fetch_news
from src.translation import translate_with_llama
from src.telegram import TelegramClient


async def quick_test():
    print("Test de connectivite...")

    print("\n1. Test Telegram Bot...")
    client = TelegramClient(BOT_TOKEN)
    try:
        me = await client.get_me()
        print(f"   Bot connected: @{me.username}")
        telegram_ok = True
    except Exception as e:
        print(f"   Error: {e}")
        telegram_ok = False

    print("\n2. Test RSS Sources...")
    articles = fetch_news()
    print(f"   {len(articles)} articles retrieved")

    print("\n3. Test Translation...")
    translation = None
    if articles:
        translation = translate_with_llama(articles[0])
        print(f"   Translation: {translation.get('titre_fr', 'N/A')[:50]}...")

    print(f"\nResults:")
    print(f"   Telegram: {'OK' if telegram_ok else 'ERROR'}")
    print(f"   RSS: {'OK' if articles else 'ERROR'}")
    print(
        f"   Translation: {'OK' if translation and 'titre_fr' in translation else 'ERROR'}"
    )


if __name__ == "__main__":
    asyncio.run(quick_test())
