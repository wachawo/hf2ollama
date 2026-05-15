# hf2ollama

[![CI](https://github.com/wachawo/hf2ollama/actions/workflows/ci.yml/badge.svg)](https://github.com/wachawo/hf2ollama/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/hf2ollama.svg)](https://pypi.org/project/hf2ollama/)
[![Downloads](https://img.shields.io/pypi/dm/hf2ollama.svg)](https://pypi.org/project/hf2ollama/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/wachawo/hf2ollama/blob/main/LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/hf2ollama.svg)](https://pypi.org/project/hf2ollama/)

[English](https://github.com/wachawo/hf2ollama/blob/main/README.md) | [中文](https://github.com/wachawo/hf2ollama/blob/main/docs/README_ZH.md) | [हिन्दी](https://github.com/wachawo/hf2ollama/blob/main/docs/README_HI.md) | [Español](https://github.com/wachawo/hf2ollama/blob/main/docs/README_ES.md) | [Français](https://github.com/wachawo/hf2ollama/blob/main/docs/README_FR.md) | **[العربية](https://github.com/wachawo/hf2ollama/blob/main/docs/README_AR.md)** | [বাংলা](https://github.com/wachawo/hf2ollama/blob/main/docs/README_BN.md) | [Русский](https://github.com/wachawo/hf2ollama/blob/main/docs/README_RU.md) | [Português](https://github.com/wachawo/hf2ollama/blob/main/docs/README_PT.md) | [اردو](https://github.com/wachawo/hf2ollama/blob/main/docs/README_UR.md)

<div dir="rtl" align="right">

شغّل أيّ نموذج نصّيّ من HuggingFace داخل Ollama بأمر واحد.

وجّه `hf2ollama` إلى مستودع HuggingFace — يقوم بتنزيل النموذج، وتحويله إلى
صيغة GGUF التي يحتاجها Ollama، ثم يطبع أمري `ollama` اللذين تنفّذهما
لتسجيل النموذج وبدء المحادثة. لا حاجة لاستدعاء `convert_hf_to_gguf.py`
يدويًا، ولا لكتابة `Modelfile` بنفسك.

يتطلّب Python 3.11+ وتثبيتًا فعّالًا لـ [Ollama](https://ollama.com).

</div>

---

## التثبيت

```bash
pip install hf2ollama
```

---

## الاستخدام

<div dir="rtl" align="right">

ضع رمز HuggingFace الخاصّ بك في ملفّ `.env` بجانب المكان الذي ستشغّل منه الأمر،
ثمّ وجّه الأداة إلى مستودع:

</div>

```bash
echo "HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxx" > .env
hf2ollama SicariusSicariiStuff/Assistant_Pepe_70B
```

<div dir="rtl" align="right">

عند الانتهاء، تطبع الأداة أمرين. شغّلهما لتبدأ المحادثة:

</div>

```
ollama create assistant-pepe-70b -f <path>/Modelfile
ollama run assistant-pepe-70b
```

<div dir="rtl" align="right">

(احصل على رمز HuggingFace من <https://huggingface.co/settings/tokens> بصلاحية
`Read`. هو ضروريّ فقط للنماذج الخاصّة وذات الترخيص، لكنّ إعداده دائمًا لا يضرّ.)

</div>

### <div dir="rtl" align="right">الخيارات</div>

```bash
# عرض الكوانتات المتوفّرة في مستودع *-GGUF (دون تنزيل):
hf2ollama some-user/some-model-GGUF --list

# تنزيل كوانت واحد فقط — تتجاوز بقيّة ملفّات .gguf:
hf2ollama some-user/some-model-GGUF --quant Q5_K_M

# اسم مخصّص للنموذج في Ollama:
hf2ollama some-user/some-model --ollama-name my-model
```

---

## التثبيت من git

<div dir="rtl" align="right">

للحصول على أحدث التعديلات غير المنشورة بعد:

</div>

```bash
pip install git+https://github.com/wachawo/hf2ollama.git
# أو عبر SSH:
pip install git+ssh://git@github.com/wachawo/hf2ollama.git
```

## التثبيت من المصدر

<div dir="rtl" align="right">

للتطوير محلّيًّا:

</div>

```bash
git clone git@github.com:wachawo/hf2ollama.git
cd hf2ollama
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env   # ثمّ ضع HF_TOKEN داخل .env
hf2ollama --help
```

---

## الإعدادات

<div dir="rtl" align="right">

ملفّ `.env` في المجلّد الذي تشغّل منه `hf2ollama`:

</div>

```ini
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
# اختياريّ. f16 (الافتراضيّ) | f32 | bf16 | q8_0 | auto
OUTTYPE=f16
```

### <div dir="rtl" align="right">تجاوز المسارات</div>

<div dir="rtl" align="right">

كلّ شيء يُكتب افتراضيًّا داخل المجلّد الحاليّ. للمشاركة بين عدّة بيئات عمل،
تجاوز عبر متغيّرات البيئة:

</div>

| Variable                     | Default                      | Purpose                                |
|------------------------------|------------------------------|----------------------------------------|
| `HF2OLLAMA_WORKSPACE`        | `$PWD`                       | الجذر لكلّ ما يأتي تحته.                  |
| `HF2OLLAMA_HF_DIR`           | `<workspace>/hf`             | مكان وضع لقطات HF وملفّات GGUF.            |
| `HF2OLLAMA_CACHE_DIR`        | `<workspace>/.hf_cache`      | تخزين `huggingface_hub` المؤقّت.          |
| `HF2OLLAMA_LLAMA_CPP_DIR`    | `<workspace>/llama.cpp`      | مكان استنساخ `llama.cpp`.                 |

---

## ما الذي يصل إلى القرص

```
<workspace>/
├── .env                # HF_TOKEN, OUTTYPE
├── hf/                 # لقطات HF تصل إلى هنا
│   └── <org>/<name>/   # المصدر + GGUF الناتج + Modelfile في مجلّد واحد
│       ├── config.json
│       ├── model.safetensors
│       ├── ...
│       ├── <name>.f16.gguf
│       └── Modelfile
└── .hf_cache/          # تخزين huggingface_hub المحلّيّ

<workspace>/llama.cpp/   # يُستنسخ في أوّل تشغيل تحويل
```

<div dir="rtl" align="right">

أوّل تشغيل تحويل يستنسخ
[`llama.cpp`](https://github.com/ggerganov/llama.cpp) داخل بيئة العمل،
لتكون التشغيلات اللاحقة أسرع. فقط المستودعات التي تشحن ملفّات GGUF مبنيّة
مسبقًا تتخطّى هذه الخطوة. لمشاركة الاستنساخ ذاته بين عدّة بيئات عمل، عيّن
`HF2OLLAMA_LLAMA_CPP_DIR` (على سبيل المثال `../llama.cpp`).

</div>

## مثال على المخرجات

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

`ollama create` ينسخ الطبقات بنفسه إلى `~/.ollama/models/blobs/` ويُنشئ
manifest خاصًّا به. **لا تنسخ** الملفّات يدويًّا إلى `~/.ollama/models/` —
Ollama يفهرس الـ blobs بـ sha256، والنسخ اليدويّ يكسر الفهرس.

</div>

---

## مشاكل شائعة

### `RepositoryNotFoundError`

<div dir="rtl" align="right">

المستودع غير موجود على HuggingFace. بعض النماذج تُنشر في أماكن أخرى — مثلًا
`xai/grok-*` يعمل خلف واجهة xAI، وهذا التدفّق لا يستطيع جلبه.

</div>

### `GatedRepoError`

<div dir="rtl" align="right">

النموذج يتطلّب قبول ترخيص. افتح صفحة النموذج على HF، اضغط "Agree and access"،
وتأكّد أنّ الرمز في `.env` يملك صلاحية الوصول لذلك المستودع.

</div>

### `No .safetensors files found`

<div dir="rtl" align="right">

المستودع يقدّم الأوزان فقط بالصيغة القديمة `pytorch_model.bin`. افتراضيًّا
يُستبعد `.bin` لتجنّب تكرار safetensors. احذف `*.bin` و`*.pth` من
`IGNORE_PATTERNS` في `hf2ollama.py` ثمّ شغّل مجدّدًا.

</div>

### <div dir="rtl" align="right">المساحة أو VRAM غير كافية</div>

<div dir="rtl" align="right">

`f16` لنموذج 70B يحتاج تقريبًا 140 GB على القرص ومثله من VRAM عند التحميل.
طريقتان:

- حوّل إلى `f16` ثمّ كوانتيز إلى `Q4_K_M` (انظر أدناه) — يقلّص `Q4_K_M`
  الحجم بنحو 4×, بفقد جودة طفيف جدًّا.
- ابحث عن GGUF جاهز من المجتمع (`<org>/<name>-GGUF`) — `--list` يُظهر
  الكوانتات المتاحة و`--quant Q4_K_M` ينزّل الكوانت المطلوب فقط.

</div>

---

## الكوانتيزة اليدويّة (اختياريّ)

<div dir="rtl" align="right">

إن أنشأت `f16` وتريد `Q4_K_M` أصغر:

</div>

```bash
cd llama.cpp   # أو الدليل الذي يشير إليه HF2OLLAMA_LLAMA_CPP_DIR
cmake -B build && cmake --build build --target llama-quantize -j
./build/bin/llama-quantize \
    <workspace>/hf/<org>/<name>/<name>.f16.gguf \
    <workspace>/hf/<org>/<name>/<name>.Q4_K_M.gguf \
    Q4_K_M
```

<div dir="rtl" align="right">

ثمّ أنشئ `Modelfile` جديدًا يشير إلى `Q4_K_M.gguf` وشغّل `ollama create`
باسم جديد.

</div>
