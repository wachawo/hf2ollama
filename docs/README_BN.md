# hf2ollama

[![CI](https://github.com/wachawo/hf2ollama/actions/workflows/ci.yml/badge.svg)](https://github.com/wachawo/hf2ollama/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/hf2ollama.svg)](https://pypi.org/project/hf2ollama/)
[![Downloads](https://img.shields.io/pypi/dm/hf2ollama.svg)](https://pypi.org/project/hf2ollama/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/wachawo/hf2ollama/blob/main/LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/hf2ollama.svg)](https://pypi.org/project/hf2ollama/)

[English](https://github.com/wachawo/hf2ollama/blob/main/README.md) | [中文](https://github.com/wachawo/hf2ollama/blob/main/docs/README_ZH.md) | [हिन्दी](https://github.com/wachawo/hf2ollama/blob/main/docs/README_HI.md) | [Español](https://github.com/wachawo/hf2ollama/blob/main/docs/README_ES.md) | [Français](https://github.com/wachawo/hf2ollama/blob/main/docs/README_FR.md) | [العربية](https://github.com/wachawo/hf2ollama/blob/main/docs/README_AR.md) | **[বাংলা](https://github.com/wachawo/hf2ollama/blob/main/docs/README_BN.md)** | [Русский](https://github.com/wachawo/hf2ollama/blob/main/docs/README_RU.md) | [Português](https://github.com/wachawo/hf2ollama/blob/main/docs/README_PT.md) | [اردو](https://github.com/wachawo/hf2ollama/blob/main/docs/README_UR.md)

একটি কমান্ডেই Ollama-র ভেতরে HuggingFace-এর যেকোনো টেক্সট মডেল চালান।

`hf2ollama`-কে একটি HuggingFace রিপোজিটরির দিকে নির্দেশ করুন — এটি মডেল ডাউনলোড করে,
Ollama-র প্রয়োজনীয় GGUF ফরম্যাটে রূপান্তর করে, এবং দুটি `ollama` কমান্ড প্রিন্ট করে
যেগুলি চালালে মডেল রেজিস্টার হয় এবং আপনি কথা বলা শুরু করতে পারেন।
নিজে হাতে `convert_hf_to_gguf.py` চালাতে হয় না, নিজে `Modelfile` লিখতেও হয় না।

Python 3.11+ এবং একটি কর্মরত [Ollama](https://ollama.com) ইনস্টল দরকার।

---

## ইনস্টল

```bash
pip install hf2ollama
```

---

## ব্যবহার

যে ডিরেক্টরি থেকে কমান্ড চালাবেন, সেখানে `.env`-এ আপনার HuggingFace টোকেন রাখুন,
তারপর টুলটিকে একটি রিপোতে নির্দেশ করুন:

```bash
echo "HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxx" > .env
hf2ollama SicariusSicariiStuff/Assistant_Pepe_70B
```

শেষ হলে টুলটি দুটি কমান্ড প্রিন্ট করবে। সেগুলি চালান, তারপর কথা বলতে পারেন:

```
ollama create assistant-pepe-70b -f <path>/Modelfile
ollama run assistant-pepe-70b
```

(<https://huggingface.co/settings/tokens>-এ `Read` স্কোপ দিয়ে একটি টোকেন নিন।
শুধু প্রাইভেট ও gated মডেলের জন্য বাধ্যতামূলক, তবে সেট রাখলে ক্ষতি নেই।)

### অপশনাল ফ্ল্যাগ

```bash
# *-GGUF রিপোতে কোন কোয়ান্ট পাওয়া যায় দেখুন (ডাউনলোড ছাড়াই):
hf2ollama some-user/some-model-GGUF --list

# কেবলমাত্র একটি কোয়ান্ট নামান — বাকি .gguf এড়িয়ে যাবে:
hf2ollama some-user/some-model-GGUF --quant Q5_K_M

# Ollama মডেলের জন্য কাস্টম নাম:
hf2ollama some-user/some-model --ollama-name my-model
```

---

## git থেকে ইনস্টল

এখনও প্রকাশিত হয়নি এমন পরিবর্তনের জন্য:

```bash
pip install git+https://github.com/wachawo/hf2ollama.git
# অথবা SSH দিয়ে:
pip install git+ssh://git@github.com/wachawo/hf2ollama.git
```

## সোর্স থেকে ইনস্টল

লোকাল ডেভেলপমেন্টের জন্য:

```bash
git clone git@github.com:wachawo/hf2ollama.git
cd hf2ollama
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env   # তারপর HF_TOKEN .env-এ বসান
hf2ollama --help
```

---

## কনফিগারেশন

যে ডিরেক্টরি থেকে `hf2ollama` চালাবেন, সেখানে `.env`:

```ini
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
# অপশনাল. f16 (ডিফল্ট) | f32 | bf16 | q8_0 | auto
OUTTYPE=f16
```

### পাথ ওভাররাইড

ডিফল্টে সব কিছু বর্তমান ওয়ার্কিং ডিরেক্টরিতে লেখা হয়। একাধিক ওয়ার্কস্পেসের
মধ্যে শেয়ার করতে চাইলে env-ভেরিয়েবল দিয়ে ওভাররাইড করুন:

| ভেরিয়েবল                       | ডিফল্ট                        | উদ্দেশ্য                                |
|------------------------------|------------------------------|----------------------------------------|
| `HF2OLLAMA_WORKSPACE`        | `$PWD`                       | নিচের সবকিছুর বেস ডিরেক্টরি।            |
| `HF2OLLAMA_HF_DIR`           | `<workspace>/hf`             | HF স্ন্যাপশট ও GGUF কোথায় যাবে।          |
| `HF2OLLAMA_CACHE_DIR`        | `<workspace>/.hf_cache`      | `huggingface_hub` ক্যাশ।                |
| `HF2OLLAMA_LLAMA_CPP_DIR`    | `<workspace>/llama.cpp`      | `llama.cpp` কোথায় ক্লোন হবে।             |

---

## ডিস্কে যা থাকবে

```
<workspace>/
├── .env                # HF_TOKEN, OUTTYPE
├── hf/                 # HF স্ন্যাপশট এখানে আসে
│   └── <org>/<name>/   # সোর্স + তৈরি GGUF + Modelfile, একই ফোল্ডারে
│       ├── config.json
│       ├── model.safetensors
│       ├── ...
│       ├── <name>.f16.gguf
│       └── Modelfile
└── .hf_cache/          # লোকাল huggingface_hub ক্যাশ

<workspace>/llama.cpp/   # কনভার্সনের প্রথম রানে ক্লোন হয়
```

প্রথম কনভার্সন রান [`llama.cpp`](https://github.com/ggerganov/llama.cpp)-কে
ওয়ার্কস্পেসের ভিতরে ক্লোন করে, যাতে পরের রানগুলি দ্রুত হয়। কেবলমাত্র
যেসব রিপোতে আগেই প্রিবিল্ট GGUF ফাইল আছে, সেগুলি এই ধাপ এড়িয়ে যায়।
একাধিক ওয়ার্কস্পেসের মধ্যে একই ক্লোন শেয়ার করতে চাইলে
`HF2OLLAMA_LLAMA_CPP_DIR` সেট করুন (যেমন `../llama.cpp`)।

## আউটপুটের উদাহরণ

```
======================================================================
GGUF:      <workspace>/hf/SicariusSicariiStuff/Assistant_Pepe_70B/Assistant_Pepe_70B.f16.gguf
Modelfile: <workspace>/hf/SicariusSicariiStuff/Assistant_Pepe_70B/Modelfile

Done. To import the model into Ollama, run these 2 commands:
  ollama create assistant-pepe-70b -f <workspace>/hf/SicariusSicariiStuff/Assistant_Pepe_70B/Modelfile
  ollama run assistant-pepe-70b
======================================================================
```

`ollama create` নিজেই লেয়ারগুলি `~/.ollama/models/blobs/`-এ কপি করে
এবং manifest বানায়। **হাতে** `~/.ollama/models/`-এ ফাইল কপি করবেন না —
Ollama blob-এর ইনডেক্স sha256 দিয়ে রাখে, হাতে কপি করলে সেটা ভেঙে যাবে।

---

## সাধারণ সমস্যা

### `RepositoryNotFoundError`

HuggingFace-এ সেই রিপো নেই। কিছু মডেল অন্য জায়গায় প্রকাশিত হয় — যেমন
`xai/grok-*` xAI API-র পেছনে থাকে, এই পাইপলাইন তা আনতে পারে না।

### `GatedRepoError`

মডেলটি লাইসেন্স মেনে নিতে বলে। HF-এ মডেলের পৃষ্ঠায় গিয়ে "Agree and access"
চাপুন, এবং নিশ্চিত করুন `.env`-এর টোকেনটির সেই রিপোতে অ্যাক্সেস আছে।

### `No .safetensors files found`

রিপোটি ওজনগুলি কেবল পুরানো `pytorch_model.bin` ফরম্যাটে দেয়। ডিফল্টে `.bin`
বাদ দেওয়া হয় যাতে safetensors-এর ডুপ্লিকেট না হয়। `hf2ollama.py`-র
`IGNORE_PATTERNS` থেকে `*.bin` ও `*.pth` মুছুন, তারপর আবার চালান।

### ডিস্ক বা VRAM কম

70B মডেলের `f16` মোটামুটি 140 GB ডিস্ক ও লোডিংয়ের সময় ততটাই VRAM নেয়।
দুটি উপায়:

- আগে `f16`-এ কনভার্ট করুন, পরে `Q4_K_M`-এ কোয়ান্টাইজ করুন (নিচে দেখুন) —
  `Q4_K_M` ফাইলকে প্রায় 4× ছোট করে দেয়, কোয়ালিটি খুব সামান্যই কমে।
- কমিউনিটি-নির্মিত GGUF খুঁজুন (`<org>/<name>-GGUF`) — `--list`-এ উপলব্ধ
  কোয়ান্ট দেখা যাবে এবং `--quant Q4_K_M` শুধু দরকারিটি ডাউনলোড করবে।

---

## ম্যানুয়াল কোয়ান্টাইজেশন (অপশনাল)

যদি `f16` তৈরি হয়ে গিয়ে থাকে এবং ছোট `Q4_K_M` চান:

```bash
cd llama.cpp   # বা HF2OLLAMA_LLAMA_CPP_DIR-নির্দেশিত ডিরেক্টরি
cmake -B build && cmake --build build --target llama-quantize -j
./build/bin/llama-quantize \
    <workspace>/hf/<org>/<name>/<name>.f16.gguf \
    <workspace>/hf/<org>/<name>/<name>.Q4_K_M.gguf \
    Q4_K_M
```

তারপর একটি নতুন `Modelfile` বানান যা `Q4_K_M.gguf`-কে নির্দেশ করে,
এবং নতুন নাম দিয়ে `ollama create` চালান।
