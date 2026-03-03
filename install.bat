@echo off
echo ===============================================
echo     🚀 CRYPTO NEWS BOT FR - INSTALLATION 🚀
echo ===============================================
echo.

echo 📦 Installation des dépendances Python...
pip install -r requirements.txt

echo.
echo ⚙️  Configuration nécessaire:
echo.
echo 1. Modifiez config.py avec votre CHAT_ID
echo    Format canal: @nomcanal
echo    Format groupe: -1001234567890
echo.
echo 2. Vos APIs sont déjà configurées dans note.txt ✅
echo.

echo 🎯 Pour lancer le bot:
echo    python crypto_news_bot.py
echo.

pause