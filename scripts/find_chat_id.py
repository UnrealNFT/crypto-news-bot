"""
🔍 Trouveur d'ID Telegram

Ce script t'aide à trouver l'ID de ton canal/groupe/chat pour configurer le bot.
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram import Bot, Update
from telegram.error import TelegramError
from src.config import BOT_TOKEN


async def find_chat_ids():
    bot = Bot(BOT_TOKEN)

    print("🔍 TROUVEUR D'ID TELEGRAM")
    print("=" * 40)

    try:
        # Info du bot
        me = await bot.get_me()
        print(f"🤖 Bot: @{me.username}")
        print()

        # Récupérer les mises à jour récentes
        print("📱 Recherche des chats récents...")
        updates = await bot.get_updates()

        chats_found = set()

        for update in updates[-20:]:  # 20 dernières interactions
            chat = None

            if update.message:
                chat = update.message.chat
            elif update.channel_post:
                chat = update.channel_post.chat
            elif update.edited_message:
                chat = update.edited_message.chat
            elif update.edited_channel_post:
                chat = update.edited_channel_post.chat

            if chat and chat.id not in chats_found:
                chats_found.add(chat.id)

                # Type de chat
                if chat.type == "private":
                    chat_type = "👤 Privé"
                elif chat.type == "group":
                    chat_type = "👥 Groupe"
                elif chat.type == "supergroup":
                    chat_type = "👥 Supergroupe"
                elif chat.type == "channel":
                    chat_type = "📺 Canal"
                else:
                    chat_type = "❓ Inconnu"

                # Nom du chat
                name = chat.title or chat.first_name or "Sans nom"
                username = f"@{chat.username}" if chat.username else "Pas de @username"

                print(f"{chat_type}: {name}")
                print(f"   ID: {chat.id}")
                print(f"   Username: {username}")
                print(f'   📋 Pour config.py: CHAT_ID = "{chat.id}"')
                print()

        if not chats_found:
            print("❌ Aucun chat trouvé dans l'historique récent.")
            print("\n💡 Solutions:")
            print("1. Envoie un message à ton bot (@Crypto_Frbot) dans le canal")
            print("2. Ou ajoute le bot comme admin du canal puis relance ce script")
            print("3. Ou utilise @userinfobot pour avoir ton ID personnel")

    except TelegramError as e:
        print(f"❌ Erreur Telegram: {e}")
    except Exception as e:
        print(f"❌ Erreur: {e}")


if __name__ == "__main__":
    asyncio.run(find_chat_ids())
