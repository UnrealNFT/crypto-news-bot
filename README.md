# Crypto News Bot FR

Bot Telegram automatique qui recupere les flux RSS crypto, traduit avec Llama (Ollama), et poste sur votre canal.

## Fonctionnement

1. **Recupere les flux RSS** toutes les X minutes (CoinTelegraph, CoinDesk, CryptoNews)
2. **Deduplique** les articles deja postes
3. **Traduit** en francais avec Llama (local)
4. **Poste** sur Telegram avec image de l'article

## Installation

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai) installe avec modele `llama3:latest`

### 1. Clone et installation

```bash
git clone https://github.com/Bulls-Dev/crypto-news-bot.git
cd crypto-news-bot

# Creer l'environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Installer les dependances
pip install -r requirements.txt
```

### 2. Configuration

```bash
cp config.py.example config.py
nano config.py
```

Remplir les variables:
- `BOT_TOKEN` - Token Telegram (obtenir via @BotFather)
- `CHAT_ID` - ID du canal Telegram

### 3. Lancer Ollama

```bash
# Verifier qu'Ollama fonctionne
curl http://localhost:11434/api/tags

# Si pas installe:
# curl -fsSL https://ollama.com/install.sh | sh
# ollama pull llama3:latest
```

### 4. Lancer le bot

```bash
python -m bot.main
```

## Configuration

| Variable | Description | Defaut |
|----------|-------------|--------|
| `BOT_TOKEN` | Token bot Telegram | - |
| `CHAT_ID` | ID du canal Telegram | - |
| `POST_INTERVAL_MINUTES` | Intervalle entre les posts | 5 |
| `MAX_ARTICLES_PER_CYCLE` | Articles max par cycle | 5 |
| `DELAY_BETWEEN_POSTS` | Delai entre posts (secondes) | 5 |
| `GENERATE_IMAGES` | Activer generation DALL-E | False |
| `LOG_LEVEL` | Niveau de log | INFO |

## Structure du Projet

```
crypto-news-bot/
├── bot/
│   └── main.py              # Point d'entree
├── src/
│   ├── config.py            # Configuration
│   ├── rss/
│   │   ├── fetcher.py       # Recuperation RSS
│   │   ├── parser.py        # Parsing XML
│   │   └── cleaner.py       # Nettoyage HTML
│   ├── translation/
│   │   └── translator.py    # Traduction Llama
│   ├── telegram/
│   │   ├── client.py        # Client Telegram
│   │   └── poster.py        # Envoi des messages
│   ├── deduplication/
│   │   └── dedupe.py        # Detection doublons
│   └── utils/
│       ├── logger.py        # Logging
│       └── storage.py      # Persistance fichiers
├── tests/
├── config.py.example        # Template de configuration
└── requirements.txt
```

## Docker

```bash
docker build -t crypto-news-bot .
docker run -d --name crypto-bot \
  -v $(pwd)/config.py:/app/config.py \
  crypto-news-bot
```

## Tests

```bash
python -m pytest tests/
```

## Troubleshooting

### Erreur Ollama 404
Verifier qu'Ollama est running et le modele installe:
```bash
curl http://localhost:11434/api/tags
ollama list
```

### Bot already running
```bash
rm bot_running.lock
```

## License

MIT
