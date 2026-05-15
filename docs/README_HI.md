# hf2ollama

[![CI](https://github.com/wachawo/hf2ollama/actions/workflows/ci.yml/badge.svg)](https://github.com/wachawo/hf2ollama/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/hf2ollama.svg)](https://pypi.org/project/hf2ollama/)
[![Downloads](https://img.shields.io/pypi/dm/hf2ollama.svg)](https://pypi.org/project/hf2ollama/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/wachawo/hf2ollama/blob/main/LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/hf2ollama.svg)](https://pypi.org/project/hf2ollama/)

[English](https://github.com/wachawo/hf2ollama/blob/main/README.md) | [中文](https://github.com/wachawo/hf2ollama/blob/main/docs/README_ZH.md) | **[हिन्दी](https://github.com/wachawo/hf2ollama/blob/main/docs/README_HI.md)** | [Español](https://github.com/wachawo/hf2ollama/blob/main/docs/README_ES.md) | [Français](https://github.com/wachawo/hf2ollama/blob/main/docs/README_FR.md) | [العربية](https://github.com/wachawo/hf2ollama/blob/main/docs/README_AR.md) | [বাংলা](https://github.com/wachawo/hf2ollama/blob/main/docs/README_BN.md) | [Русский](https://github.com/wachawo/hf2ollama/blob/main/docs/README_RU.md) | [Português](https://github.com/wachawo/hf2ollama/blob/main/docs/README_PT.md) | [اردو](https://github.com/wachawo/hf2ollama/blob/main/docs/README_UR.md)

एक ही कमांड से Ollama के अंदर किसी भी HuggingFace टेक्स्ट मॉडल को चलाएँ।

`hf2ollama` को किसी HuggingFace रिपॉज़िटरी पर इंगित करें — यह मॉडल डाउनलोड करता है,
उसे Ollama के लिए ज़रूरी GGUF फ़ॉर्मैट में बदलता है, और दो `ollama` कमांड प्रिंट करता है
जिन्हें चलाने पर मॉडल रजिस्टर हो जाता है और आप उससे बातचीत शुरू कर सकते हैं।
न तो खुद `convert_hf_to_gguf.py` चलाना है, न ही `Modelfile` हाथ से लिखना है।

Python 3.11+ और एक चलता हुआ [Ollama](https://ollama.com) इंस्टॉल चाहिए।

---

## इंस्टॉल

```bash
pip install hf2ollama
```

---

## उपयोग

जिस डायरेक्टरी से कमांड चलाएँगे, उसमें `.env` में अपना HuggingFace टोकन डालें
और टूल को रिपो की ओर इंगित करें:

```bash
echo "HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxx" > .env
hf2ollama SicariusSicariiStuff/Assistant_Pepe_70B
```

ख़त्म होने पर टूल दो कमांड प्रिंट करता है — उन्हें चलाइए और बातचीत शुरू:

```
ollama create assistant-pepe-70b -f <path>/Modelfile
ollama run assistant-pepe-70b
```

(टोकन <https://huggingface.co/settings/tokens> पर `Read` स्कोप के साथ बनाएँ।
केवल निजी और gated मॉडलों के लिए ज़रूरी है, पर सेट रहना नुक़सानदेह नहीं।)

### वैकल्पिक फ़्लैग

```bash
# *-GGUF रिपो में कौन-से क्वांट उपलब्ध हैं देखें (बिना डाउनलोड किए):
hf2ollama some-user/some-model-GGUF --list

# सिर्फ़ एक क्वांट डाउनलोड करें — बाक़ी .gguf छोड़ दिए जाते हैं:
hf2ollama some-user/some-model-GGUF --quant Q5_K_M

# Ollama में कस्टम नाम:
hf2ollama some-user/some-model --ollama-name my-model
```

---

## git से इंस्टॉल

जो अभी रिलीज़ नहीं हुआ है उसके लिए:

```bash
pip install git+https://github.com/wachawo/hf2ollama.git
# या SSH से:
pip install git+ssh://git@github.com/wachawo/hf2ollama.git
```

## सोर्स से इंस्टॉल

लोकल डेवलपमेंट के लिए:

```bash
git clone git@github.com:wachawo/hf2ollama.git
cd hf2ollama
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env   # फिर अपना HF_TOKEN .env में डालें
hf2ollama --help
```

---

## कॉन्फ़िगरेशन

जिस डायरेक्टरी से `hf2ollama` चलाते हैं उसी में `.env`:

```ini
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
# वैकल्पिक. f16 (डिफ़ॉल्ट) | f32 | bf16 | q8_0 | auto
OUTTYPE=f16
```

### पाथ ओवरराइड

सब कुछ डिफ़ॉल्ट से करंट डायरेक्टरी में लिखा जाता है। कई वर्कस्पेस के बीच
शेयर करना हो तो env-वेरिएबल से ओवरराइड करें:

| वेरिएबल                       | डिफ़ॉल्ट                      | उद्देश्य                                |
|------------------------------|------------------------------|----------------------------------------|
| `HF2OLLAMA_WORKSPACE`        | `$PWD`                       | नीचे की सब चीज़ों का बेस।                |
| `HF2OLLAMA_HF_DIR`           | `<workspace>/hf`             | HF स्नैपशॉट और GGUF कहाँ जाएँगे।         |
| `HF2OLLAMA_CACHE_DIR`        | `<workspace>/.hf_cache`      | `huggingface_hub` कैश।                  |
| `HF2OLLAMA_LLAMA_CPP_DIR`    | `<workspace>/llama.cpp`      | `llama.cpp` कहाँ क्लोन हो।               |

---

## डिस्क पर क्या होगा

```
<workspace>/
├── .env                # HF_TOKEN, OUTTYPE
├── hf/                 # HF स्नैपशॉट यहाँ आते हैं
│   └── <org>/<name>/   # सोर्स + तैयार GGUF + Modelfile, एक ही फ़ोल्डर में
│       ├── config.json
│       ├── model.safetensors
│       ├── ...
│       ├── <name>.f16.gguf
│       └── Modelfile
└── .hf_cache/          # लोकल huggingface_hub कैश

<workspace>/llama.cpp/   # कन्वर्ज़न के पहले रन पर क्लोन होता है
```

पहला कन्वर्ज़न रन [`llama.cpp`](https://github.com/ggerganov/llama.cpp) को
आपके वर्कस्पेस के अंदर क्लोन कर देता है, ताकि अगले रन तेज़ हों। सिर्फ़
वही रिपो यह क़दम छोड़ते हैं जो पहले से प्रीबिल्ट GGUF फ़ाइलें रखते हैं।
एक ही क्लोन को कई वर्कस्पेसों के बीच साझा करने के लिए
`HF2OLLAMA_LLAMA_CPP_DIR` सेट करें (उदाहरण के लिए `../llama.cpp`)।

## आउटपुट का उदाहरण

```
======================================================================
GGUF:      <workspace>/hf/SicariusSicariiStuff/Assistant_Pepe_70B/Assistant_Pepe_70B.f16.gguf
Modelfile: <workspace>/hf/SicariusSicariiStuff/Assistant_Pepe_70B/Modelfile

Done. To import the model into Ollama, run these 2 commands:
  ollama create assistant-pepe-70b -f <workspace>/hf/SicariusSicariiStuff/Assistant_Pepe_70B/Modelfile
  ollama run assistant-pepe-70b
======================================================================
```

`ollama create` ख़ुद ही लेयर्स को `~/.ollama/models/blobs/` में कॉपी करता है
और मैनिफ़ेस्ट बनाता है। फ़ाइलें **हाथ से** `~/.ollama/models/` में मत डालिए —
Ollama blob-s को sha256 से इंडेक्स करता है, हाथ की कॉपी इंडेक्स तोड़ देगी।

---

## आम समस्याएँ

### `RepositoryNotFoundError`

HuggingFace पर वह रिपो मौजूद नहीं है। कुछ मॉडल कहीं और publish होते हैं —
जैसे `xai/grok-*` xAI API के पीछे है, यह पाइपलाइन वहाँ से नहीं ला सकती।

### `GatedRepoError`

मॉडल लाइसेंस स्वीकार करवाता है। HF पर मॉडल पेज पर जाइए, "Agree and access"
दबाइए, और सुनिश्चित करिए कि `.env` का टोकन उस रिपो तक पहुँच रखता है।

### `No .safetensors files found`

रिपो ने पुराने `pytorch_model.bin` फ़ॉर्मैट में ही वज़न दिए हैं। डिफ़ॉल्ट में
`.bin` बाहर रखा जाता है ताकि safetensors की डुप्लिकेसी न हो। `hf2ollama.py`
के `IGNORE_PATTERNS` से `*.bin` और `*.pth` हटाइए और फिर से चलाइए।

### डिस्क या VRAM कम है

70B मॉडल का `f16` डिस्क पर लगभग 140 GB और लोड करते वक़्त उतनी ही VRAM लेता है।
दो रास्ते:

- पहले `f16` बनाइए, फिर `Q4_K_M` में क्वांटाइज़ करिए (नीचे देखिए) — `Q4_K_M`
  फ़ाइल लगभग 4× छोटी कर देता है, क्वालिटी का बहुत कम नुक़सान।
- वही मॉडल कम्युनिटी-बने GGUF (`<org>/<name>-GGUF`) में ढूँढिए — `--list` से
  उपलब्ध क्वांट देखेंगे और `--quant Q4_K_M` से सिर्फ़ ज़रूरी डाउनलोड होगा।

---

## मैन्युअल क्वांटाइज़ेशन (वैकल्पिक)

अगर `f16` तैयार है और छोटा `Q4_K_M` चाहिए:

```bash
cd llama.cpp   # या HF2OLLAMA_LLAMA_CPP_DIR की ओर इंगित निर्देशिका
cmake -B build && cmake --build build --target llama-quantize -j
./build/bin/llama-quantize \
    <workspace>/hf/<org>/<name>/<name>.f16.gguf \
    <workspace>/hf/<org>/<name>/<name>.Q4_K_M.gguf \
    Q4_K_M
```

फिर एक नया `Modelfile` बनाइए जो `Q4_K_M.gguf` की ओर इशारा करे, और नए नाम से
`ollama create` चलाइए।
