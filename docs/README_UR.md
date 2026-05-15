# hf2ollama

[![CI](https://github.com/wachawo/hf2ollama/actions/workflows/ci.yml/badge.svg)](https://github.com/wachawo/hf2ollama/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/hf2ollama.svg)](https://pypi.org/project/hf2ollama/)
[![Downloads](https://img.shields.io/pypi/dm/hf2ollama.svg)](https://pypi.org/project/hf2ollama/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/wachawo/hf2ollama/blob/main/LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/hf2ollama.svg)](https://pypi.org/project/hf2ollama/)

[English](https://github.com/wachawo/hf2ollama/blob/main/README.md) | [中文](https://github.com/wachawo/hf2ollama/blob/main/docs/README_ZH.md) | [हिन्दी](https://github.com/wachawo/hf2ollama/blob/main/docs/README_HI.md) | [Español](https://github.com/wachawo/hf2ollama/blob/main/docs/README_ES.md) | [Français](https://github.com/wachawo/hf2ollama/blob/main/docs/README_FR.md) | [العربية](https://github.com/wachawo/hf2ollama/blob/main/docs/README_AR.md) | [বাংলা](https://github.com/wachawo/hf2ollama/blob/main/docs/README_BN.md) | [Русский](https://github.com/wachawo/hf2ollama/blob/main/docs/README_RU.md) | [Português](https://github.com/wachawo/hf2ollama/blob/main/docs/README_PT.md) | **[اردو](https://github.com/wachawo/hf2ollama/blob/main/docs/README_UR.md)**

<div dir="rtl" align="right">

ایک ہی کمانڈ سے Ollama کے اندر HuggingFace کا کوئی بھی ٹیکسٹ ماڈل چلائیں۔

`hf2ollama` کو ایک HuggingFace ریپوزیٹری کی طرف اشارہ کریں — یہ ماڈل ڈاؤن لوڈ
کرتا ہے، اسے Ollama کے لیے درکار GGUF فارمیٹ میں بدل دیتا ہے، اور دو
`ollama` کمانڈز پرنٹ کرتا ہے جنہیں چلانے سے ماڈل رجسٹر ہو جاتا ہے اور آپ
گفتگو شروع کر سکتے ہیں۔ نہ خود `convert_hf_to_gguf.py` چلانا ہے، نہ ہاتھ
سے `Modelfile` لکھنا ہے۔

Python 3.11+ اور ایک کام کرنے والا [Ollama](https://ollama.com) انسٹال درکار ہے۔

</div>

---

## انسٹال

```bash
pip install hf2ollama
```

---

## استعمال

<div dir="rtl" align="right">

جس ڈائریکٹری سے کمانڈ چلائیں گے، وہاں `.env` میں اپنا HuggingFace ٹوکن رکھیں،
پھر ٹول کو ایک ریپو کی طرف اشارہ کریں:

</div>

```bash
echo "HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxx" > .env
hf2ollama SicariusSicariiStuff/Assistant_Pepe_70B
```

<div dir="rtl" align="right">

ختم ہونے پر ٹول دو کمانڈز پرنٹ کرتا ہے۔ انہیں چلائیں اور آپ گفتگو میں ہیں:

</div>

```
ollama create assistant-pepe-70b -f <path>/Modelfile
ollama run assistant-pepe-70b
```

<div dir="rtl" align="right">

(<https://huggingface.co/settings/tokens> پر `Read` سکوپ کے ساتھ ٹوکن بنائیں۔
صرف نجی اور gated ماڈلز کے لیے لازمی ہے، مگر سیٹ رکھنے میں کوئی نقصان نہیں۔)

</div>

### <div dir="rtl" align="right">اختیاری فلیگز</div>

```bash
# *-GGUF ریپو میں دستیاب کوانٹس دیکھیں (بغیر ڈاؤن لوڈ کیے):
hf2ollama some-user/some-model-GGUF --list

# صرف ایک کوانٹ ڈاؤن لوڈ کریں — باقی .gguf چھوڑ دیے جاتے ہیں:
hf2ollama some-user/some-model-GGUF --quant Q5_K_M

# Ollama میں اپنی پسند کا نام:
hf2ollama some-user/some-model --ollama-name my-model
```

---

## git سے انسٹال

<div dir="rtl" align="right">

ابھی غیر مطبوعہ تبدیلیوں کے لیے:

</div>

```bash
pip install git+https://github.com/wachawo/hf2ollama.git
# یا SSH کے ذریعے:
pip install git+ssh://git@github.com/wachawo/hf2ollama.git
```

## سورس سے انسٹال

<div dir="rtl" align="right">

لوکل ڈیولپمنٹ کے لیے:

</div>

```bash
git clone git@github.com:wachawo/hf2ollama.git
cd hf2ollama
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env   # پھر HF_TOKEN کو .env میں ڈالیں
hf2ollama --help
```

---

## کنفیگریشن

<div dir="rtl" align="right">

جس ڈائریکٹری سے `hf2ollama` چلاتے ہیں، اسی میں `.env`:

</div>

```ini
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
# اختیاری۔ f16 (ڈیفالٹ) | f32 | bf16 | q8_0 | auto
OUTTYPE=f16
```

### <div dir="rtl" align="right">پاتھ اوور رائیڈ</div>

<div dir="rtl" align="right">

ڈیفالٹ پر سب کچھ موجودہ ڈائریکٹری میں لکھا جاتا ہے۔ کئی ورک سپیس کے درمیان
شیئر کرنا ہو تو env-ویری ایبل سے اوور رائیڈ کریں:

</div>

| Variable                     | Default                      | Purpose                                |
|------------------------------|------------------------------|----------------------------------------|
| `HF2OLLAMA_WORKSPACE`        | `$PWD`                       | نیچے کی ہر چیز کا بنیادی ڈائریکٹری۔     |
| `HF2OLLAMA_HF_DIR`           | `<workspace>/hf`             | HF سنیپ شاٹس اور GGUF کہاں جائیں گے۔    |
| `HF2OLLAMA_CACHE_DIR`        | `<workspace>/.hf_cache`      | `huggingface_hub` کیش۔                  |
| `HF2OLLAMA_LLAMA_CPP_DIR`    | `<workspace>/llama.cpp`      | `llama.cpp` کہاں کلون ہو۔                |

---

## ڈسک پر کیا رہے گا

```
<workspace>/
├── .env                # HF_TOKEN, OUTTYPE
├── hf/                 # HF سنیپ شاٹس یہاں آتے ہیں
│   └── <org>/<name>/   # سورس + تیار GGUF + Modelfile، سب ایک فولڈر میں
│       ├── config.json
│       ├── model.safetensors
│       ├── ...
│       ├── <name>.f16.gguf
│       └── Modelfile
└── .hf_cache/          # لوکل huggingface_hub کیش

<workspace>/llama.cpp/   # پہلی کنورژن رن پر کلون
```

<div dir="rtl" align="right">

پہلی کنورژن رن
[`llama.cpp`](https://github.com/ggerganov/llama.cpp) کو آپ کے ورک سپیس کے
اندر کلون کر دیتی ہے، تاکہ اگلے رنز تیز ہوں۔ صرف وہی ریپو یہ قدم چھوڑتے ہیں
جو پہلے سے پری بلٹ GGUF فائلیں رکھتے ہیں۔ ایک ہی کلون کو کئی ورک سپیسز میں
شیئر کرنے کے لیے `HF2OLLAMA_LLAMA_CPP_DIR` سیٹ کریں (مثلاً `../llama.cpp`)۔

</div>

## آؤٹ پٹ کی مثال

```
======================================================================
GGUF:      <workspace>/hf/SicariusSicariiStuff/Assistant_Pepe_70B/Assistant_Pepe_70B.f16.gguf
Modelfile: <workspace>/hf/SicariusSicariiStuff/Assistant_Pepe_70B/Modelfile

Done. To import the model into Ollama, run these 2 commands:
  ollama create assistant-pepe-70b -f <workspace>/hf/SicariusSicariiStuff/Assistant_Pepe_70B/Modelfile
  ollama run assistant-pepe-70b
======================================================================
```

<div dir="rtl" align="right">

`ollama create` خود ہی لیئرز کو `~/.ollama/models/blobs/` میں کاپی کرتا ہے
اور manifest بناتا ہے۔ فائلیں **ہاتھ سے** `~/.ollama/models/` میں مت ڈالیں —
Ollama بلابز کو sha256 سے انڈیکس کرتا ہے، ہاتھ کی کاپی انڈیکس توڑ دے گی۔

</div>

---

## عام مسائل

### `RepositoryNotFoundError`

<div dir="rtl" align="right">

ریپو HuggingFace پر موجود نہیں ہے۔ کچھ ماڈل کہیں اور شائع ہوتے ہیں — مثلاً
`xai/grok-*` xAI API کے پیچھے ہے، یہ پائپ لائن وہاں سے نہیں لا سکتی۔

</div>

### `GatedRepoError`

<div dir="rtl" align="right">

ماڈل لائسنس قبول کرنے کا تقاضا کرتا ہے۔ HF پر ماڈل کے صفحے پر جائیں،
"Agree and access" دبائیں، اور یقین کر لیں کہ `.env` کا ٹوکن اس ریپو تک
رسائی رکھتا ہے۔

</div>

### `No .safetensors files found`

<div dir="rtl" align="right">

ریپو نے وزن صرف پرانے `pytorch_model.bin` فارمیٹ میں دیے ہیں۔ ڈیفالٹ پر
`.bin` کو خارج رکھا جاتا ہے تاکہ safetensors کی ڈپلیکیٹ نہ ہو۔
`hf2ollama.py` کے `IGNORE_PATTERNS` سے `*.bin` اور `*.pth` ہٹائیں اور
دوبارہ چلائیں۔

</div>

### <div dir="rtl" align="right">ڈسک یا VRAM کم ہے</div>

<div dir="rtl" align="right">

70B ماڈل کا `f16` ڈسک پر تقریباً 140 GB اور لوڈ کرتے وقت اتنا ہی VRAM لیتا ہے۔
دو راستے:

- پہلے `f16` بنائیں، پھر `Q4_K_M` میں کوانٹائز کریں (نیچے دیکھیں) — `Q4_K_M`
  فائل کو تقریباً 4× چھوٹا کر دیتا ہے، کوالٹی کا بہت معمولی نقصان۔
- وہی ماڈل کمیونٹی کے بنے ہوئے GGUF (`<org>/<name>-GGUF`) میں ڈھونڈیں —
  `--list` دستیاب کوانٹس دکھائے گا اور `--quant Q4_K_M` صرف ضروری ڈاؤن لوڈ کرے گا۔

</div>

---

## دستی کوانٹائزیشن (اختیاری)

<div dir="rtl" align="right">

اگر `f16` تیار ہے اور چھوٹا `Q4_K_M` چاہیے:

</div>

```bash
cd llama.cpp   # یا HF2OLLAMA_LLAMA_CPP_DIR میں طے شدہ ڈائریکٹری
cmake -B build && cmake --build build --target llama-quantize -j
./build/bin/llama-quantize \
    <workspace>/hf/<org>/<name>/<name>.f16.gguf \
    <workspace>/hf/<org>/<name>/<name>.Q4_K_M.gguf \
    Q4_K_M
```

<div dir="rtl" align="right">

پھر ایک نیا `Modelfile` بنائیں جو `Q4_K_M.gguf` کی طرف اشارہ کرے اور نئے نام
سے `ollama create` چلائیں۔

</div>
