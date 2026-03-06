from telegram import Bot


class TelegramClient:
    """Telegram bot client wrapper."""

    def __init__(self, token: str):
        self.bot = Bot(token=token)

    async def get_me(self):
        """Get bot info."""
        return await self.bot.get_me()

    async def send_message(self, chat_id: str, text: str, **kwargs):
        """Send text message."""
        return await self.bot.send_message(chat_id=chat_id, text=text, **kwargs)

    async def send_photo(self, chat_id: str, photo: str, caption: str = None, **kwargs):
        """Send photo with optional caption."""
        return await self.bot.send_photo(
            chat_id=chat_id, photo=photo, caption=caption, **kwargs
        )
