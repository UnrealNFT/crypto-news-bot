# 🎨 Génération d'Images FLUX.1

## Nouvelle Fonctionnalité

Le bot peut maintenant **générer des images** pour chaque article avec le modèle **FLUX.1-schnell** de Black Forest Labs.

### Caractéristiques

- **Modèle** : FLUX.1-schnell (ultra-rapide, 4 steps)
- **Mode** : CPU (pas besoin de GPU)
- **Style** : Anime/Manga Studio Ghibli
- **Logo** : Superposition automatique du logo sur les images
- **Gratuit** : Modèle local, pas d'API payante

## Configuration

Dans `config.py` :

```python
# Active la génération d'images avec FLUX.1
GENERATE_IMAGES = True

# Active la superposition du logo
ADD_LOGO = True

# Position du logo : "top-left", "top-right", "bottom-left", "bottom-right"
LOGO_POSITION = "top-left"

# Taille du logo en pixels
LOGO_SIZE = 200
```

## Installation

### 1. Dépendances

```bash
pip install -r requirements.txt
```

Nouvelles dépendances :
- `torch>=2.0.0` - PyTorch pour l'IA
- `diffusers>=0.25.0` - Bibliothèque de diffusion
- `transformers>=4.36.0` - Transformateurs
- `accelerate>=0.24.0` - Optimisation
- `sentencepiece>=0.1.99` - Tokenisation

### 2. Téléchargement du modèle

Au premier lancement, FLUX.1-schnell sera téléchargé automatiquement (~23GB).

```bash
# Le modèle sera stocké dans ~/.cache/huggingface/
```

## Performances

| Mode | Temps | VRAM | Qualité |
|------|-------|------|---------|
| **CPU** | ~8-12 min | 0 GB | ⭐⭐⭐⭐⭐ |
| GPU (si disponible) | ~30 s | 12+ GB | ⭐⭐⭐⭐⭐ |

**Mode CPU recommandé** : Lent mais gratuit et accessible partout.

## Workflow

1. 📡 **Récupération RSS** - Articles crypto
2. 🔍 **Déduplication** - Anti-doublons
3. 🤖 **Traduction Llama** - FR avec Ollama
4. 🎨 **Génération FLUX.1** - Image style anime (~10 min)
5. 🖼️ **Logo overlay** - Superposition du logo
6. 📤 **Post Telegram** - Avec image générée

## Architecture

```
src/images/
├── __init__.py
├── generator.py      # Génération FLUX.1
└── logo_overlay.py   # Superposition logo
```

## Prompt

Le prompt est construit automatiquement à partir de l'article :

```
Beautiful anime manga illustration in Studio Ghibli style representing: {titre}.

Context: {description}

Style: Bright colorful manga art with vibrant colors, clean cartoon aesthetic, 
cherry blossoms, warm color palette with soft pinks and golden yellows. 
Cheerful anime environment with soft lighting. NO logos, NO text, NO symbols.
```

## Désactivation

Pour utiliser uniquement les images RSS (rapide) :

```python
GENERATE_IMAGES = False
```

## Logo

Le logo doit être placé dans `assets/Logofr.PNG` :
- Format : PNG avec transparence
- Taille recommandée : 512x512 ou plus
- Position par défaut : Haut gauche (15px de marge)

## Troubleshooting

### Erreur mémoire CPU
```python
# Réduire la résolution dans generator.py
width=512, height=512  # Au lieu de 768x768
```

### Téléchargement lent
Le modèle FLUX.1 fait ~23GB. Première installation longue (30-60 min selon connexion).

### GPU non détecté
Normal, le bot utilise le CPU par défaut. Pour activer GPU (si disponible) :
```python
# Dans generator.py, ligne 63
device="cuda"  # Au lieu de "cpu"
```

## Comparaison avec DALL-E

| | DALL-E 3 | FLUX.1-schnell |
|---|----------|----------------|
| **Coût** | $0.04/image | Gratuit |
| **Vitesse (CPU)** | N/A | ~10 min |
| **Vitesse (GPU)** | ~10 s | ~30 s |
| **Qualité** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Local** | ❌ API | ✅ Oui |

## Résumé

✅ **Gratuit** - Modèle local  
✅ **Qualité maximale** - FLUX.1 = niveau DALL-E 3  
✅ **Logo automatique** - Branding sur chaque image  
⏱️ **Lent sur CPU** - 8-12 min par image  
💾 **Storage** - 23GB pour le modèle
