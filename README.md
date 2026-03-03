# 🚀 Bot Crypto News FR - Automatic RSS to Telegram

Bot Telegram automatique qui récupère les flux RSS des sites crypto, traduit les articles en français avec ChatGPT, génère des images avec DALL-E, et poste automatiquement dans votre canal Telegram.

## 🎯 Fonctionnement

Le bot est un **agent Python personnalisé de A à Z** qui :

1. 📡 **Interroge les flux RSS** toutes les 5 minutes :
   - CoinTelegraph: `https://cointelegraph.com/rss`
   - CryptoNews: `https://cryptonews.com/news/feed/`
   - Utilise un **UserAgent** pour éviter les bans IP

2. 🔍 **Vérifie les doublons** : 
   - Compare les titres avec les articles déjà postés
   - Détection de similarité pour éviter le spam

3. 🤖 **Traduit avec ChatGPT** :
   - Traduction professionnelle en français
   - Résumé et formatage optimisé

4. 🎨 **Génère une image avec OpenAI DALL-E** :
   - Style anime/manga Studio Ghibli
   - Superpose votre logo sur l'image générée
   - Alternative : récupère les images originales des articles (marquées source)

5. 📤 **Poste sur Telegram** avec formatage professionnel

## ⚡ Installation Rapide

### 1. Clone le projet
```bash
git clone https://github.com/Bulls-Dev/crypto-news-bot.git
cd crypto-news-bot
```

### 2. Configuration
```bash
# Copier le fichier de configuration exemple
cp config.py.example config.py

# Éditer avec vos clés API
nano config.py  # ou notepad config.py sur Windows
```

**Configuration minimale requise dans `config.py` :**
```python
BOT_TOKEN = "votre_token_telegram"         # De @BotFather
OPENAI_API_KEY = "votre_cle_openai"        # De platform.openai.com
CHAT_ID = "@votre_canal"                   # Votre canal Telegram
```

### 3. Installation des dépendances
```bash
# Windows
install.bat

# Linux/Mac
pip install -r requirements.txt
```

### 4. Lancement
```bash
# Windows
run.bat

# Linux/Mac
python crypto_news_bot.py
```

## 🔧 Configuration Avancée

### API Keys
- **Telegram Bot Token** : Obtenez-le via [@BotFather](https://t.me/BotFather)
- **OpenAI API Key** : Créez-la sur [platform.openai.com](https://platform.openai.com/api-keys)

### Trouver votre CHAT_ID
- **Canal public** : `@nomdevotrecanal`
- **Groupe privé** : Ajoutez [@userinfobot](https://t.me/userinfobot), il vous donnera l'ID
- **Via script** : `python find_chat_id.py`

### Paramètres de fréquence
```python
POST_INTERVAL_MINUTES = 5   # Intervalle entre chaque vérification (défaut: 5min)
MAX_ARTICLES_PER_CYCLE = 5  # Nombre max d'articles par cycle
DELAY_BETWEEN_POSTS = 5     # Délai entre chaque post (secondes)
```

### Génération d'images
```python
GENERATE_IMAGES = True   # Activer DALL-E
IMAGE_STYLE = "Beautiful anime manga cartoon illustration in Studio Ghibli style"
```

## 📋 Architecture Technique

### Backend 100% Python
- **feedparser** : Lecture des flux RSS
- **requests** : Requêtes HTTP avec UserAgent personnalisé
- **python-telegram-bot** : API Telegram Bot
- **openai** : ChatGPT pour traduction + DALL-E pour images
- **Pillow (PIL)** : Superposition du logo sur les images

### Flux de données
```
RSS Feed → Parse → Dedupe Check → Translate (GPT) → Generate Image (DALL-E) 
→ Overlay Logo → Post to Telegram → Log Posted Article
```

### Éviter les bans IP
Le bot utilise :
- **UserAgent** personnalisé pour les requêtes HTTP
- **Proxies CORS** alternatifs en cas de timeout
- **Rate limiting** : délai entre les posts
- **Politeness** : pas de spam des serveurs RSS

### Stockage persistant
```
posted_articles.txt   # URLs déjà postées
posted_titles.txt     # Titres pour déduplication
bot_running.lock      # Prévention des instances multiples
```

## 🤖 Fonctionnalités Principales

✅ **Multi-sources RSS** (CoinTelegraph, CryptoNews, etc.)  
✅ **Traduction IA** française professionnelle  
✅ **Génération d'images** DALL-E + logo overlay  
✅ **Anti-doublons** intelligent  
✅ **UserAgent** pour éviter les bans  
✅ **CORS Proxies** alternatifs  
✅ **Logging** détaillé  
✅ **Lock file** anti-multi-instances  
✅ **Planning automatique** avec schedule  

## 📱 Format des Messages

```
🚀 [Titre traduit en français]

📝 Résumé court (2-3 phrases)

💎 Description complète traduite...

🔗 Lire l'article complet : [URL]
📅 Date de publication  
🏷️ #CryptoNews #Bitcoin #Blockchain

────────────────────
🤖 Traduit par ChatGPT | 📡 Source: [NomDuSite]
```

## 🛠️ Scripts Utilitaires

- `install.bat` : Installation automatique Windows
- `run.bat` : Lancement rapide
- `find_chat_id.py` : Trouver l'ID de votre canal/groupe
- `test_bot.py` : Tester la connexion Telegram

## 🐛 Debugging

### Vérifier les logs
Le bot affiche en temps réel :
- ✅ Articles récupérés
- 🤖 Traductions réussies
- 🎨 Images générées
- 📱 Posts Telegram
- ⚠️ Erreurs éventuelles

### Problèmes courants
```bash
# Erreur "Bot already running"
rm bot_running.lock  # ou del bot_running.lock sur Windows

# Erreur RSS timeout
# → Le bot basculera automatiquement sur les proxies CORS alternatifs

# Erreur Telegram
# → Vérifiez que le bot est admin du canal avec droits de post
```

## 🚀 Déploiement

### Linux (VPS/Serveur)
```bash
# Installation
git clone https://github.com/Bulls-Dev/crypto-news-bot.git
cd crypto-news-bot
cp config.py.example config.py
nano config.py
pip install -r requirements.txt

# Lancement avec screen (persistant)
screen -S cryptobot
python crypto_news_bot.py
# Ctrl+A+D pour détacher

# Relancer la session
screen -r cryptobot
```

### Windows
```bash
# Installation
git clone https://github.com/Bulls-Dev/crypto-news-bot.git
cd crypto-news-bot
install.bat

# Modifier config.py avec vos clés

# Lancement
run.bat
```

### Docker (optionnel)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "crypto_news_bot.py"]
```

## 🤝 Contribution

1. Fork le projet
2. Créez votre branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## ⚠️ Sécurité

- **NE JAMAIS** commiter `config.py` avec vos vraies clés
- Utiliser `config.py.example` comme template
- Le `.gitignore` exclut automatiquement les fichiers sensibles
- Régénérez vos tokens si accidentellement exposés

## 📜 License

MIT License - Voir [LICENSE](LICENSE) pour plus de détails

## 👤 Auteur

**Testiz** - [@crypto_francophone](https://t.me/crypto_francophone)

Développé avec ❤️ pour la communauté crypto française

---

🎯 **Automatisez vos actualités crypto maintenant !** 🚀