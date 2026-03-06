#!/usr/bin/env python3
"""
Simple test to verify Telegram connection
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import logging
from src.config import BOT_TOKEN, CHANNEL_ID
from src.telegram import TelegramClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_connection():
    try:
        client = TelegramClient(BOT_TOKEN)
        me = await client.get_me()
        logger.info(f"Bot connected: @{me.username}")
        return True
    except Exception as e:
        logger.error(f"Connection error: {e}")
        return False


async def test_message():
    try:
        client = TelegramClient(BOT_TOKEN)
        message = "Test bot crypto - Connection OK!"
        await client.send_message(chat_id=CHANNEL_ID, text=message)
        logger.info("Message sent successfully")
        return True
    except Exception as e:
        logger.error(f"Send error: {e}")
        return False


async def main():
    print("Testing crypto bot...")

    if await test_connection():
        await test_message()

    print("Test complete!")


if __name__ == "__main__":
    asyncio.run(main())
