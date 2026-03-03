#!/usr/bin/env python3
"""
Test simple pour vérifier les imports et connexion Telegram
"""
# Import from config.py
from config import *
import asyncio
import logging
from telegram import Bot
from openai import OpenAI

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialisation des clients
bot = Bot(token=BOT_TOKEN)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

async def test_connection():
    """Test de connexion Telegram"""
    try:
        me = await bot.get_me()
        logger.info(f"✅ Bot connecté: @{me.username}")
        return True
    except Exception as e:
        logger.error(f"❌ Erreur connexion: {e}")
        return False

async def test_message():
    """Test d'envoi de message"""
    try:
        message = "🚀 Test bot crypto - Connexion OK!"
        await bot.send_message(chat_id=CHANNEL_ID, text=message)
        logger.info("✅ Message envoyé avec succès")
        return True
    except Exception as e:
        logger.error(f"❌ Erreur envoi: {e}")
        return False

async def main():
    """Fonction principale de test"""
    print("🔄 Test du bot crypto...")
    
    # Test connexion
    if await test_connection():
        # Test envoi
        await test_message()
    
    print("✅ Test terminé!")

if __name__ == "__main__":
    asyncio.run(main())