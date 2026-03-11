#!/bin/bash
# Script d'installation bot crypto pour Hetzner
echo "🚀 Installation du bot crypto..."

# Création du dossier
mkdir -p /opt/crypto-bot
cd /opt/crypto-bot

# Installation Python et deps
apt update
apt install -y python3 python3-pip python3-venv

# Création environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installation packages
pip install python-telegram-bot openai feedparser requests Pillow schedule

echo "✅ Installation terminée !"
echo "📁 Dossier: /opt/crypto-bot"
echo "🔄 Maintenant copier les fichiers Python..."