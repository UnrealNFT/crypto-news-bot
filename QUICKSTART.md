# 🚀 Guide de Déploiement Rapide

> ⚠️ **DOCUMENTATION OBSOLÈTE** : Ce guide fait référence à l'ancienne version utilisant OpenAI.  
> Pour la version actuelle avec **Ollama + Llama**, consultez [README.md](README.md) et [OLLAMA_SETUP.md](OLLAMA_SETUP.md)

Ce guide vous permet de déployer le bot crypto en **moins de 5 minutes**.

## ⚡ Prérequis

- Python 3.8+
- Un compte Telegram avec un bot créé
- Une clé API OpenAI
- Un canal/groupe Telegram

## 📦 Installation Express

### Option 1 : Windows
```powershell
# 1. Cloner le repo
git clone https://github.com/Bulls-Dev/crypto-news-bot.git
cd crypto-news-bot

# 2. Installer
.\install.bat

# 3. Configurer
copy config.py.example config.py
notepad config.py

# 4. Lancer
.\run.bat
```

### Option 2 : Linux/Mac
```bash
# 1. Cloner le repo
git clone https://github.com/Bulls-Dev/crypto-news-bot.git
cd crypto-news-bot

# 2. Installer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Configurer
cp config.py.example config.py
nano config.py

# 4. Lancer
python crypto_news_bot.py
```

## 🔑 Configuration Minimale

Éditez `config.py` avec **seulement 3 valeurs** :

```python
# 1. Token du bot Telegram (de @BotFather)
BOT_TOKEN = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"

# 2. Clé API OpenAI (de platform.openai.com)
OPENAI_API_KEY = "sk-proj-abcdef1234567890..."

# 3. ID de votre canal/groupe
CHAT_ID = "@votre_canal"
```

**Trouver votre CHAT_ID** :
- Canal public : `@nom_du_canal`
- Groupe/canal privé : Utilisez `python find_chat_id.py`

## ✅ Vérification

Le bot devrait afficher :
```
✅ Bot Crypto News FR démarré !
📡 Canal cible: @votre_canal
⏰ Fréquence: Toutes les 5 minutes
🔄 Premier cycle dans 1 minute...
```

## 🎯 Premier Test

```bash
# Tester la connexion Telegram
python test_bot.py
```

Si tout fonctionne, vous recevrez un message test sur votre canal.

## 🐛 Dépannage Express

### Erreur "Unauthorized"
→ Votre `BOT_TOKEN` est incorrect. Vérifiez sur @BotFather

### Erreur "Chat not found"
→ Le bot n'est pas admin du canal. Ajoutez-le avec droits de post.

### Erreur "OpenAI API"
→ Votre clé API est incorrecte ou n'a plus de crédit.

### Pas d'articles postés
→ Normal ! Le bot vérifie toutes les 5 minutes. Attendez un cycle.

## 🔧 Personnalisation Rapide

### Changer la fréquence
```python
# Dans config.py
POST_INTERVAL_MINUTES = 15  # Toutes les 15 min au lieu de 5
```

### Désactiver les images DALL-E
```python
GENERATE_IMAGES = False  # Économise les coûts OpenAI
```

### Ajouter des sources
```python
# Dans crypto_news_bot.py, section NEWS_SOURCES
{
    "name": "Decrypt",
    "rss": "https://decrypt.co/feed",
    "use_proxy": False
}
```

## 📊 Monitoring

### Logs en temps réel
```bash
# Suivre les logs
tail -f bot.log

# Windows
Get-Content bot.log -Wait
```

### Statistiques
Le bot affiche automatiquement :
- ✅ Articles récupérés
- 🤖 Articles traduits
- 📱 Articles postés
- ❌ Erreurs

## 🚀 Déploiement Production

### VPS Linux (Recommandé)
```bash
# Installation sur serveur
git clone https://github.com/Bulls-Dev/crypto-news-bot.git
cd crypto-news-bot
cp config.py.example config.py
nano config.py
pip install -r requirements.txt

# Lancer avec screen (persiste après déconnexion)
screen -S cryptobot
python crypto_news_bot.py
# Ctrl+A puis D pour détacher

# Revenir à la session
screen -r cryptobot
```

### Service Systemd (Auto-start)
```bash
# Créer le service
sudo nano /etc/systemd/system/cryptobot.service
```

```ini
[Unit]
Description=Crypto News Bot
After=network.target

[Service]
Type=simple
User=votre_user
WorkingDirectory=/home/votre_user/crypto-news-bot
ExecStart=/usr/bin/python3 crypto_news_bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Activer & démarrer
sudo systemctl enable cryptobot
sudo systemctl start cryptobot
sudo systemctl status cryptobot
```

### Docker (Optionnel)
```bash
# Build
docker build -t crypto-news-bot .

# Run
docker run -d \
  --name cryptobot \
  --restart unless-stopped \
  -v $(pwd)/config.py:/app/config.py:ro \
  crypto-news-bot
```

## 💰 Estimation des Coûts

### OpenAI API (Approximatif)
- **GPT-3.5-turbo** : ~$0.002 par traduction
- **DALL-E 3** : ~$0.04 par image
- **Exemple** : 100 articles/jour = ~$6/jour avec images, ~$0.20/jour sans

### Optimisations
```python
# Dans config.py
OPENAI_MODEL = "gpt-3.5-turbo"  # Au lieu de gpt-4
GENERATE_IMAGES = False          # Désactiver DALL-E
MAX_ARTICLES_PER_CYCLE = 3       # Réduire le nombre d'articles
```

## 🔐 Sécurité

### ⚠️ IMPORTANT
- **JAMAIS** commiter `config.py` sur GitHub
- Gardez vos clés API secrètes
- Utilisez `.gitignore` (déjà configuré)
- Régénérez vos tokens si exposés

### Vérifier avant de commit
```bash
# Vérifier les fichiers qui seront committes
git status

# config.py ne doit PAS apparaître !
# S'il apparaît :
git reset config.py
```

## 📱 Support

- **Issues** : [GitHub Issues](https://github.com/Bulls-Dev/crypto-news-bot/issues)
- **Telegram** : [@crypto_francophone](https://t.me/crypto_francophone)
- **Email** : Pour les questions privées

## 📚 Documentation Complète

- [README.md](README.md) - Vue d'ensemble
- [TECHNICAL.md](TECHNICAL.md) - Documentation technique détaillée
- [CONTRIBUTING.md](CONTRIBUTING.md) - Guide de contribution

## ✨ Template de Premier Message

Une fois le bot lancé, postez ceci sur votre canal :

```
🤖 Bot Crypto News FR activé !

Ce canal poste automatiquement les dernières actus crypto :
🔹 CoinTelegraph
🔹 CryptoNews
🔹 Et plus à venir !

🤖 Traduction IA professionnelle
🎨 Images générées par DALL-E
🚀 Mise à jour toutes les 5 minutes

Bon trading ! 💎
```

---

🎯 **Votre bot devrait être opérationnel !** 🚀

Des problèmes ? Créez une [issue](https://github.com/Bulls-Dev/crypto-news-bot/issues).
