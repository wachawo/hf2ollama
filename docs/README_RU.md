# hf2ollama

[![CI](https://github.com/wachawo/hf2ollama/actions/workflows/ci.yml/badge.svg)](https://github.com/wachawo/hf2ollama/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/hf2ollama.svg)](https://pypi.org/project/hf2ollama/)
[![Downloads](https://img.shields.io/pypi/dm/hf2ollama.svg)](https://pypi.org/project/hf2ollama/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/wachawo/hf2ollama/blob/main/LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/hf2ollama.svg)](https://pypi.org/project/hf2ollama/)

[English](https://github.com/wachawo/hf2ollama/blob/main/README.md) | [中文](https://github.com/wachawo/hf2ollama/blob/main/docs/README_ZH.md) | [हिन्दी](https://github.com/wachawo/hf2ollama/blob/main/docs/README_HI.md) | [Español](https://github.com/wachawo/hf2ollama/blob/main/docs/README_ES.md) | [Français](https://github.com/wachawo/hf2ollama/blob/main/docs/README_FR.md) | [العربية](https://github.com/wachawo/hf2ollama/blob/main/docs/README_AR.md) | [বাংলা](https://github.com/wachawo/hf2ollama/blob/main/docs/README_BN.md) | **[Русский](https://github.com/wachawo/hf2ollama/blob/main/docs/README_RU.md)** | [Português](https://github.com/wachawo/hf2ollama/blob/main/docs/README_PT.md) | [اردو](https://github.com/wachawo/hf2ollama/blob/main/docs/README_UR.md)

Запусти любую текстовую модель с HuggingFace в Ollama одной командой.

Покажи `hf2ollama` ссылку на HuggingFace-репозиторий — он скачает модель,
сконвертирует её в GGUF (формат, который понимает Ollama) и напечатает
две команды `ollama`, которые ты выполнишь, чтобы зарегистрировать
модель и начать с ней общаться. Никакого ручного `convert_hf_to_gguf.py`,
никакого собственноручного `Modelfile`.

Нужен Python 3.11+ и установленный [Ollama](https://ollama.com).

---

## Установка

```bash
pip install hf2ollama
```

---

## Использование

Положи HuggingFace-токен в `.env` рядом с тем местом, откуда будешь
запускать команду, и укажи инструменту репозиторий:

```bash
echo "HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxx" > .env
hf2ollama SicariusSicariiStuff/Assistant_Pepe_70B
```

В конце тулза напечатает две команды. Выполни их — и можешь общаться:

```
ollama create assistant-pepe-70b -f <path>/Modelfile
ollama run assistant-pepe-70b
```

(Токен бери на <https://huggingface.co/settings/tokens> со scope `Read`.
Обязательно нужен только для приватных и gated-моделей, но и в остальных
случаях не помешает.)

### Опциональные флаги

```bash
# Посмотреть, какие GGUF-кванты лежат в *-GGUF репо (без скачивания):
hf2ollama some-user/some-model-GGUF --list

# Скачать только один квант — остальные .gguf пропускаются:
hf2ollama some-user/some-model-GGUF --quant Q5_K_M

# Своё имя для модели в Ollama:
hf2ollama some-user/some-model --ollama-name my-model
```

---

## Установка с git

Для самых свежих, ещё не выложенных в PyPI изменений:

```bash
pip install git+https://github.com/wachawo/hf2ollama.git
# или по SSH:
pip install git+ssh://git@github.com/wachawo/hf2ollama.git
```

## Установка из исходников

Для локальной разработки:

```bash
git clone git@github.com:wachawo/hf2ollama.git
cd hf2ollama
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env   # потом впиши свой HF_TOKEN в .env
hf2ollama --help
```

---

## Конфигурация

`.env` в каталоге, из которого запускаешь `hf2ollama`:

```ini
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
# Опционально. f16 (по умолчанию) | f32 | bf16 | q8_0 | auto
OUTTYPE=f16
```

### Переопределение путей

Всё пишется в текущий рабочий каталог. Чтобы разделить ресурсы между
несколькими проектами, переопредели через env-переменные:

| Переменная                   | По умолчанию                 | Назначение                              |
|------------------------------|------------------------------|-----------------------------------------|
| `HF2OLLAMA_WORKSPACE`        | `$PWD`                       | Корневой каталог для всего ниже.        |
| `HF2OLLAMA_HF_DIR`           | `<workspace>/hf`             | Куда кладутся HF-снапшоты и GGUF.       |
| `HF2OLLAMA_CACHE_DIR`        | `<workspace>/.hf_cache`      | Кэш `huggingface_hub`.                  |
| `HF2OLLAMA_LLAMA_CPP_DIR`    | `<workspace>/../llama.cpp`   | Куда клонируется `llama.cpp`.           |

---

## Что окажется на диске

```
<workspace>/
├── .env                # HF_TOKEN, OUTTYPE
├── hf/                 # сюда падают HF-снапшоты
│   └── <org>/<name>/   # исходники + готовый GGUF + Modelfile в одной папке
│       ├── config.json
│       ├── model.safetensors
│       ├── ...
│       ├── <name>.f16.gguf
│       └── Modelfile
└── .hf_cache/          # локальный кэш huggingface_hub

<workspace>/../llama.cpp/   # клонируется один раз, переиспользуется между workspace
```

При первом запуске тулза также клонирует
[`llama.cpp`](https://github.com/ggerganov/llama.cpp) на уровень выше
workspace — последующие запуски быстрее. Шаг пропускается только для репо,
которые уже содержат готовые GGUF.

## Пример вывода

```
======================================================================
GGUF:      <workspace>/hf/SicariusSicariiStuff/Assistant_Pepe_70B/Assistant_Pepe_70B.f16.gguf
Modelfile: <workspace>/hf/SicariusSicariiStuff/Assistant_Pepe_70B/Modelfile

Done. To import the model into Ollama, run these 2 commands:
  ollama create assistant-pepe-70b -f <workspace>/hf/SicariusSicariiStuff/Assistant_Pepe_70B/Modelfile
  ollama run assistant-pepe-70b
======================================================================
```

`ollama create` сам копирует слои в `~/.ollama/models/blobs/` и создаёт
манифест. **Не нужно** руками класть файлы в `~/.ollama/models/` — Ollama
хранит blob-ы по sha256, ручное копирование сломает индекс.

---

## Типичные проблемы

### `RepositoryNotFoundError`

Репозитория нет на HuggingFace. Некоторые модели публикуются не на HF —
например, `xai/grok-*` живут за xAI API, и этот пайплайн их получить
не сможет.

### `GatedRepoError`

Нужно сначала согласиться с лицензией. Открой страницу модели на HF,
нажми «Agree and access», убедись, что токен в `.env` имеет к ней доступ.

### `No .safetensors files found`

Репозиторий публикует веса только в старом формате `pytorch_model.bin`.
По умолчанию `.bin` исключён, чтобы не качать дубликат к safetensors.
Удали `*.bin` и `*.pth` из `IGNORE_PATTERNS` в `hf2ollama.py` и запусти
заново.

### Не хватает места на диске или VRAM

`f16` для 70B-модели — это ~140 GB на диске и столько же в VRAM при
загрузке. Два варианта:

- Сначала сконвертировать в `f16`, потом сквантовать в `Q4_K_M` (см. ниже)
  — `Q4_K_M` уменьшает файл примерно в 4 раза с минимальной потерей качества.
- Взять готовый сообществом GGUF (`<org>/<name>-GGUF`) — `--list` покажет
  доступные кванты, `--quant Q4_K_M` скачает только нужный.

---

## Ручная квантизация (опционально)

Если уже есть `f16` и хочется компактный `Q4_K_M`:

```bash
cd ../llama.cpp
cmake -B build && cmake --build build --target llama-quantize -j
./build/bin/llama-quantize \
    <workspace>/hf/<org>/<name>/<name>.f16.gguf \
    <workspace>/hf/<org>/<name>/<name>.Q4_K_M.gguf \
    Q4_K_M
```

Потом сделай новый `Modelfile` с указанием на `Q4_K_M.gguf` и запусти
`ollama create` с новым именем.
