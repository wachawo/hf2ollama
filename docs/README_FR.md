# hf2ollama

[![CI](https://github.com/wachawo/hf2ollama/actions/workflows/ci.yml/badge.svg)](https://github.com/wachawo/hf2ollama/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/hf2ollama.svg)](https://pypi.org/project/hf2ollama/)
[![Downloads](https://img.shields.io/pypi/dm/hf2ollama.svg)](https://pypi.org/project/hf2ollama/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/wachawo/hf2ollama/blob/main/LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/hf2ollama.svg)](https://pypi.org/project/hf2ollama/)

[English](https://github.com/wachawo/hf2ollama/blob/main/README.md) | [中文](https://github.com/wachawo/hf2ollama/blob/main/docs/README_ZH.md) | [हिन्दी](https://github.com/wachawo/hf2ollama/blob/main/docs/README_HI.md) | [Español](https://github.com/wachawo/hf2ollama/blob/main/docs/README_ES.md) | **[Français](https://github.com/wachawo/hf2ollama/blob/main/docs/README_FR.md)** | [العربية](https://github.com/wachawo/hf2ollama/blob/main/docs/README_AR.md) | [বাংলা](https://github.com/wachawo/hf2ollama/blob/main/docs/README_BN.md) | [Русский](https://github.com/wachawo/hf2ollama/blob/main/docs/README_RU.md) | [Português](https://github.com/wachawo/hf2ollama/blob/main/docs/README_PT.md) | [اردو](https://github.com/wachawo/hf2ollama/blob/main/docs/README_UR.md)

Faire tourner n'importe quel modèle texte de HuggingFace dans Ollama, en une seule commande.

Pointez `hf2ollama` sur un dépôt HuggingFace : il télécharge le modèle, le
convertit au format GGUF attendu par Ollama, et affiche les deux commandes
`ollama` à exécuter pour l'enregistrer et discuter avec. Pas besoin
d'invoquer `convert_hf_to_gguf.py` à la main, pas besoin d'écrire un
`Modelfile`.

Nécessite Python 3.11 ou plus, et une installation fonctionnelle d'[Ollama](https://ollama.com).

---

## Installation

```bash
pip install hf2ollama
```

---

## Utilisation

Placez votre token HuggingFace dans un fichier `.env` à côté de l'endroit où
vous lancerez la commande, puis pointez l'outil sur un dépôt :

```bash
echo "HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxx" > .env
hf2ollama SicariusSicariiStuff/Assistant_Pepe_70B
```

Quand c'est fini, l'outil affiche deux commandes. Lancez-les, et vous discutez :

```
ollama create assistant-pepe-70b -f <path>/Modelfile
ollama run assistant-pepe-70b
```

(Récupérez un token HuggingFace sur <https://huggingface.co/settings/tokens>
avec la portée `Read`. Il n'est obligatoire que pour les modèles privés ou
sous licence, mais l'avoir configuré ne fait jamais de mal.)

### Options

```bash
# Voir quelles quantifications GGUF se trouvent dans un dépôt *-GGUF (sans téléchargement) :
hf2ollama some-user/some-model-GGUF --list

# Télécharger une seule quantification — les autres .gguf sont ignorés :
hf2ollama some-user/some-model-GGUF --quant Q5_K_M

# Nom personnalisé du modèle dans Ollama :
hf2ollama some-user/some-model --ollama-name my-model
```

---

## Installation depuis git

Pour les changements non encore publiés :

```bash
pip install git+https://github.com/wachawo/hf2ollama.git
# ou, en SSH :
pip install git+ssh://git@github.com/wachawo/hf2ollama.git
```

## Installation depuis le code source

Pour développer localement :

```bash
git clone git@github.com:wachawo/hf2ollama.git
cd hf2ollama
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env   # puis renseignez votre HF_TOKEN dans .env
hf2ollama --help
```

---

## Configuration

`.env` dans le répertoire d'où vous lancez `hf2ollama` :

```ini
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
# Optionnel. f16 (défaut) | f32 | bf16 | q8_0 | auto
OUTTYPE=f16
```

### Chemins

Tout est écrit sous le répertoire courant. Pour partager certains dossiers
entre projets, utilisez ces variables d'environnement :

| Variable                     | Défaut                       | Rôle                                   |
|------------------------------|------------------------------|----------------------------------------|
| `HF2OLLAMA_WORKSPACE`        | `$PWD`                       | Racine de tout ce qui suit.            |
| `HF2OLLAMA_HF_DIR`           | `<workspace>/hf`             | Où vont les snapshots HF et les GGUF.  |
| `HF2OLLAMA_CACHE_DIR`        | `<workspace>/.hf_cache`      | Cache de `huggingface_hub`.            |
| `HF2OLLAMA_LLAMA_CPP_DIR`    | `<workspace>/../llama.cpp`   | Où cloner `llama.cpp`.                 |

---

## Ce qui se retrouve sur le disque

```
<workspace>/
├── .env                # HF_TOKEN, OUTTYPE
├── hf/                 # les snapshots HF arrivent ici
│   └── <org>/<name>/   # fichiers source + GGUF résultant + Modelfile, tout au même endroit
│       ├── config.json
│       ├── model.safetensors
│       ├── ...
│       ├── <name>.f16.gguf
│       └── Modelfile
└── .hf_cache/          # cache local huggingface_hub

<workspace>/../llama.cpp/   # cloné une fois, réutilisé entre workspaces
```

Le premier lancement clone aussi
[`llama.cpp`](https://github.com/ggerganov/llama.cpp) un niveau au-dessus du
workspace, pour que les exécutions suivantes soient rapides. Seuls les dépôts
qui livrent déjà du GGUF sautent cette étape.

## Exemple de sortie

```
======================================================================
GGUF:      <workspace>/hf/SicariusSicariiStuff/Assistant_Pepe_70B/Assistant_Pepe_70B.f16.gguf
Modelfile: <workspace>/hf/SicariusSicariiStuff/Assistant_Pepe_70B/Modelfile

Done. To import the model into Ollama, run these 2 commands:
  ollama create assistant-pepe-70b -f <workspace>/hf/SicariusSicariiStuff/Assistant_Pepe_70B/Modelfile
  ollama run assistant-pepe-70b
======================================================================
```

`ollama create` copie les couches dans `~/.ollama/models/blobs/` et crée son
propre manifest. **Ne copiez pas** manuellement de fichiers dans
`~/.ollama/models/` — Ollama indexe les blobs par sha256, une copie manuelle
casserait l'index.

---

## Problèmes courants

### `RepositoryNotFoundError`

Le dépôt n'existe pas sur HuggingFace. Certains modèles sont publiés ailleurs
— par exemple `xai/grok-*` n'est accessible que via l'API xAI, et ce flux ne
peut pas le récupérer.

### `GatedRepoError`

Le modèle nécessite d'accepter une licence. Allez sur la page HF du modèle,
cliquez « Agree and access », et vérifiez que le token dans `.env` a accès
à ce dépôt.

### `No .safetensors files found`

Le dépôt ne fournit que des poids au vieux format `pytorch_model.bin`. Par
défaut, `.bin` est exclu pour ne pas dupliquer les safetensors. Retirez
`*.bin` et `*.pth` de `IGNORE_PATTERNS` dans `hf2ollama.py` et relancez.

### Pas assez de disque / VRAM

`f16` pour un modèle 70B, c'est environ 140 GB sur disque et autant en VRAM
au chargement. Deux options :

- Convertir en `f16` puis quantifier en `Q4_K_M` (voir plus bas) — `Q4_K_M`
  réduit le fichier d'environ 4× avec une perte de qualité minime.
- Chercher un GGUF déjà préparé par la communauté (`<org>/<name>-GGUF`) ;
  `--list` montre les quantifications dispo et `--quant Q4_K_M` ne télécharge
  que celle voulue.

---

## Quantification manuelle (optionnel)

Si vous avez déjà du `f16` et voulez un `Q4_K_M` plus léger :

```bash
cd ../llama.cpp
cmake -B build && cmake --build build --target llama-quantize -j
./build/bin/llama-quantize \
    <workspace>/hf/<org>/<name>/<name>.f16.gguf \
    <workspace>/hf/<org>/<name>/<name>.Q4_K_M.gguf \
    Q4_K_M
```

Créez ensuite un nouveau `Modelfile` pointant sur le `Q4_K_M.gguf` et lancez
`ollama create` avec un nom différent.
