# hf2ollama

[![CI](https://github.com/wachawo/hf2ollama/actions/workflows/ci.yml/badge.svg)](https://github.com/wachawo/hf2ollama/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/hf2ollama.svg)](https://pypi.org/project/hf2ollama/)
[![Downloads](https://img.shields.io/pypi/dm/hf2ollama.svg)](https://pypi.org/project/hf2ollama/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/wachawo/hf2ollama/blob/main/LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/hf2ollama.svg)](https://pypi.org/project/hf2ollama/)

[English](https://github.com/wachawo/hf2ollama/blob/main/README.md) | [中文](https://github.com/wachawo/hf2ollama/blob/main/docs/README_ZH.md) | [हिन्दी](https://github.com/wachawo/hf2ollama/blob/main/docs/README_HI.md) | **[Español](https://github.com/wachawo/hf2ollama/blob/main/docs/README_ES.md)** | [Français](https://github.com/wachawo/hf2ollama/blob/main/docs/README_FR.md) | [العربية](https://github.com/wachawo/hf2ollama/blob/main/docs/README_AR.md) | [বাংলা](https://github.com/wachawo/hf2ollama/blob/main/docs/README_BN.md) | [Русский](https://github.com/wachawo/hf2ollama/blob/main/docs/README_RU.md) | [Português](https://github.com/wachawo/hf2ollama/blob/main/docs/README_PT.md) | [اردو](https://github.com/wachawo/hf2ollama/blob/main/docs/README_UR.md)

Ejecuta cualquier modelo de texto de HuggingFace dentro de Ollama con un solo comando.

Apunta `hf2ollama` a un repositorio de HuggingFace: descarga el modelo, lo
convierte al formato GGUF que necesita Ollama, e imprime los dos comandos
`ollama` que tienes que ejecutar para registrarlo y empezar a chatear. Sin
llamar a `convert_hf_to_gguf.py` a mano, sin escribir el `Modelfile`.

Requiere Python 3.11 o superior y una instalación funcional de
[Ollama](https://ollama.com).

---

## Instalación

```bash
pip install hf2ollama
```

---

## Uso

Pon tu token de HuggingFace en un `.env` al lado de donde vayas a ejecutar
el comando, y apunta la herramienta a un repositorio:

```bash
echo "HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxx" > .env
hf2ollama SicariusSicariiStuff/Assistant_Pepe_70B
```

Cuando termina, la herramienta imprime dos comandos. Ejecútalos y ya estás chateando:

```
ollama create assistant-pepe-70b -f <path>/Modelfile
ollama run assistant-pepe-70b
```

(Consigue un token de HuggingFace en <https://huggingface.co/settings/tokens>
con permiso `Read`. Solo es obligatorio para modelos privados o con licencia,
pero tenerlo configurado nunca está de más.)

### Opciones

```bash
# Ver qué cuantizaciones GGUF trae un repo *-GGUF (sin descargar nada):
hf2ollama some-user/some-model-GGUF --list

# Descargar solo una cuantización; los demás .gguf se omiten:
hf2ollama some-user/some-model-GGUF --quant Q5_K_M

# Nombre personalizado del modelo en Ollama:
hf2ollama some-user/some-model --ollama-name my-model
```

---

## Instalación desde git

Para tener los cambios aún no publicados:

```bash
pip install git+https://github.com/wachawo/hf2ollama.git
# o, por SSH:
pip install git+ssh://git@github.com/wachawo/hf2ollama.git
```

## Instalación desde el código fuente

Para desarrollar localmente:

```bash
git clone git@github.com:wachawo/hf2ollama.git
cd hf2ollama
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env   # luego pon tu HF_TOKEN en .env
hf2ollama --help
```

---

## Configuración

`.env` en el directorio desde el que vas a ejecutar `hf2ollama`:

```ini
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
# Opcional. f16 (por defecto) | f32 | bf16 | q8_0 | auto
OUTTYPE=f16
```

### Rutas

Todo se escribe bajo el directorio actual. Para compartir entre proyectos
puedes sobrescribir con variables de entorno:

| Variable                     | Por defecto                  | Propósito                              |
|------------------------------|------------------------------|----------------------------------------|
| `HF2OLLAMA_WORKSPACE`        | `$PWD`                       | Directorio base de todo lo demás.      |
| `HF2OLLAMA_HF_DIR`           | `<workspace>/hf`             | Dónde van los snapshots HF y los GGUF. |
| `HF2OLLAMA_CACHE_DIR`        | `<workspace>/.hf_cache`      | Caché de `huggingface_hub`.            |
| `HF2OLLAMA_LLAMA_CPP_DIR`    | `<workspace>/llama.cpp`      | Dónde clonar `llama.cpp`.              |

---

## Qué acaba en disco

```
<workspace>/
├── .env                # HF_TOKEN, OUTTYPE
├── hf/                 # aquí caen los snapshots de HF
│   └── <org>/<name>/   # ficheros fuente + GGUF resultante + Modelfile, todo junto
│       ├── config.json
│       ├── model.safetensors
│       ├── ...
│       ├── <name>.f16.gguf
│       └── Modelfile
└── .hf_cache/          # caché local de huggingface_hub

<workspace>/llama.cpp/   # clonado en la primera ejecución de conversión
```

La primera ejecución de conversión clona
[`llama.cpp`](https://github.com/ggerganov/llama.cpp) dentro del workspace,
para que las siguientes sean rápidas. Solo los repositorios que ya traen
archivos GGUF preconstruidos saltan este paso. Para compartir un mismo clon
entre varios workspaces, define `HF2OLLAMA_LLAMA_CPP_DIR`
(por ejemplo `../llama.cpp`).

## Salida de ejemplo

```
======================================================================
GGUF:      <workspace>/hf/SicariusSicariiStuff/Assistant_Pepe_70B/Assistant_Pepe_70B.f16.gguf
Modelfile: <workspace>/hf/SicariusSicariiStuff/Assistant_Pepe_70B/Modelfile

Done. To import the model into Ollama, run these 2 commands:
  ollama create assistant-pepe-70b -f <workspace>/hf/SicariusSicariiStuff/Assistant_Pepe_70B/Modelfile
  ollama run assistant-pepe-70b
======================================================================
```

`ollama create` copia las capas a `~/.ollama/models/blobs/` y crea su propio
manifiesto. **No** copies ficheros manualmente dentro de `~/.ollama/models/`:
Ollama indexa los blobs por sha256, y una copia manual romperá el índice.

---

## Problemas frecuentes

### `RepositoryNotFoundError`

El repositorio no existe en HuggingFace. Algunos modelos se publican en otro
sitio — por ejemplo `xai/grok-*` vive detrás de la API de xAI y este flujo
no puede descargarlo.

### `GatedRepoError`

El modelo requiere aceptar una licencia. Abre la página del modelo en HF,
pulsa "Agree and access", y asegúrate de que el token en `.env` tiene acceso
a ese repositorio.

### `No .safetensors files found`

El repo solo trae los pesos en formato heredado `pytorch_model.bin`. Por
defecto se excluye `.bin` para evitar duplicar safetensors. Quita `*.bin` y
`*.pth` de `IGNORE_PATTERNS` en `hf2ollama.py` y vuelve a ejecutar.

### Sin espacio en disco o VRAM

`f16` para un modelo de 70B ocupa unos 140 GB en disco y otros tantos de VRAM
al cargarlo. Dos salidas:

- Convertir a `f16` primero y luego cuantizar a `Q4_K_M` (ver abajo): `Q4_K_M`
  reduce el fichero ~4×, con pérdida de calidad mínima.
- Buscar un GGUF ya hecho por la comunidad (`<org>/<name>-GGUF`); con `--list`
  ves las cuantizaciones disponibles y con `--quant Q4_K_M` descargas solo la
  que necesitas.

---

## Cuantización manual (opcional)

Si ya tienes `f16` y quieres un `Q4_K_M` más pequeño:

```bash
cd llama.cpp   # o el directorio apuntado por HF2OLLAMA_LLAMA_CPP_DIR
cmake -B build && cmake --build build --target llama-quantize -j
./build/bin/llama-quantize \
    <workspace>/hf/<org>/<name>/<name>.f16.gguf \
    <workspace>/hf/<org>/<name>/<name>.Q4_K_M.gguf \
    Q4_K_M
```

Luego crea un nuevo `Modelfile` apuntando al `Q4_K_M.gguf` y ejecuta
`ollama create` con un nombre nuevo.
