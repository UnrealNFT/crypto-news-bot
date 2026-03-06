# Bot Crypto News FR - Automatic RSS to Telegram

Bot Telegram automatique qui recupere les flux RSS des sites crypto, traduit les articles en francais avec ChatGPT, genere des images avec DALL-E, et poste automatiquement dans votre canal Telegram.

## Fonctionnement

Le bot est un **agent Python personnalise de A a Z** qui :

1. **Interroge les flux RSS** toutes les 5 minutes :
   - CoinTelegraph: `https://cointelegraph.com/rss`
   - CryptoNews: `https://cryptonews.com/news/feed/`
   - Utilise un **UserAgent** pour eviter les bans IP

2. **Verifie les doublons** : 
   - Compare les titres avec les articles deja postes
   - Detection de similarite pour eviter le spam

3. **Traduit avec ChatGPT** :
   - Traduction professionnelle en francais
   - Resume et formatage optimise

4. **Genere une image avec OpenAI DALL-E** :
   - Style anime/manga Studio Ghibli
   - Superpose votre logo sur l'image generee
   - Alternative : recupere les images originales des articles (marquees source)

5. **Poste sur Telegram** avec formatage professionnel

## Installation Rapide

### 1. Clone le projet
```bash
git clone https://github.com/Bulls-Dev/crypto-news-bot.git
cd crypto-news-bot
```

### 2. Configuration
```bash
# Copier le fichier de configuration exemple
cp config.py.example config.py

# Editer avec vos cles API
nano config.py  # ou notepad config.py sur Windows
```

**Configuration minimale requise dans `config.py` :**
```python
BOT_TOKEN = "votre_token_telegram"         # De @BotFather
OPENAI_API_KEY = "votre_cle_openai"        # De platform.openai.com
CHAT_ID = "@votre_canal"                   # Votre canal Telegram
```

### 3. Installation des dependances
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

## Configuration Avancee

### API Keys
- **Telegram Bot Token** : Obtenez-le via [@BotFather](https://t.me/BotFather)
- **OpenAI API Key** : Creez-la sur [platform.openai.com](https://platform.openai.com/api-keys)

### Trouver votre CHAT_ID
- **Canal public** : `@nomdevotrecanal`
- **Groupe prive** : Ajoutez [@userinfobot](https://t.me/userinfobot), il vous donnera l'ID
- **Via script** : `python find_chat_id.py`

### Parametres de frequence
```python
POST_INTERVAL_MINUTES = 5   # Intervalle entre chaque verification (defaut: 5min)
MAX_ARTICLES_PER_CYCLE = 5  # Nombre max d'articles par cycle
DELAY_BETWEEN_POSTS = 5     # Delai entre chaque post (secondes)
```

### Generation d'images
```python
GENERATE_IMAGES = True   # Activer DALL-E
IMAGE_STYLE = "Beautiful anime manga cartoon illustration in Studio Ghibli style"
```

## Architecture Technique

### Backend 100% Python
- **feedparser** : Lecture des flux RSS
- **requests** : Requetes HTTP avec UserAgent personnalise
- **python-telegram-bot** : API Telegram Bot
- **openai** : ChatGPT pour traduction + DALL-E pour images
- **Pillow (PIL)** : Superposition du logo sur les images

### Flux de donnees
```
RSS Feed -> Parse -> Dedupe Check -> Translate (GPT) -> Generate Image (DALL-E) 
-> Overlay Logo -> Post to Telegram -> Log Posted Article
```

### Eviter les bans IP
Le bot utilise :
- **UserAgent** personnalise pour les requetes HTTP
- **Proxies CORS** alternatifs en cas de timeout
- **Rate limiting** : delai entre les posts
- **Politeness** : pas de spam des serveurs RSS

### Stockage persistant
```
posted_articles.txt   # URLs deja postees
posted_titles.txt     # Titres pour deduplication
bot_running.lock      # Prevention des instances multiples
```

## Fonctionnalites Principales

- **Multi-sources RSS** (CoinTelegraph, CryptoNews, etc.)
- **Traduction IA** francaise professionnelle
- **Generation d'images** DALL-E + logo overlay
- **Anti-doublons** intelligent
- **UserAgent** pour eviter les bans
- **CORS Proxies** alternatifs
- **Logging** detaille
- **Lock file** anti-multi-instances
- **Planning automatique** avec schedule

## Format des Messages

```
[Titre traduit en francais]

Resume court (2-3 phrases)

Description complete traduite...

Lire l'article complet : [URL]
Date de publication  
#CryptoNews #Bitcoin #Blockchain

-----------------------
Traduit par ChatGPT | Source: [NomDuSite]
```

## Scripts Utilitaires

- `install.bat` : Installation automatique Windows
- `run.bat` : Lancement rapide
- `find_chat_id.py` : Trouver l'ID de votre canal/groupe
- `test_bot.py` : Tester la connexion Telegram

## Debugging

### Verifier les logs
Le bot affiche en temps reel :
- Articles recuperes
- Traductions reussies
- Images generees
- Posts Telegram
- Erreurs eventuelles

### Problemes courants
```bash
# Erreur "Bot already running"
rm bot_running.lock  # ou del bot_running.lock sur Windows

# Erreur RSS timeout
# -> Le bot basculera automatiquement sur les proxies CORS alternatifs

# Erreur Telegram
# -> Verifiez que le bot est admin du canal avec droits de post
```

## Deploiement

### Linux (VPS/serveur)
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
# Ctrl+A+D pour detacher

# Relancer la session
screen -r cryptobot
```

### Windows
```bash
# Installation
git clone https://github.com/Bulls-Dev/crypto-news-bot.git
cd crypto-news-bot
install.bat

# Modifier config.py avec vos cles

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

## Contribution

1. Fork le projet
2. Creez votre branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## Securite

- **NE JAMAIS** commiter `config.py` avec vos vraies cles
- Utiliser `config.py.example` comme template
- Le `.gitignore` exclut automatiquement les fichiers sensibles
- Regenererez vos tokens si accidentellement exposes

## License

MIT License - Voir [LICENSE](LICENSE) pour plus de details

## Auteur

**Testiz** - [@crypto_francophone](https://t.me/crypto_francophone)

Developpe avec passion pour la communaute crypto francaise

---

**Automatisez vos actualites crypto maintenant !**
