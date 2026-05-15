# hf2ollama

[![CI](https://github.com/wachawo/hf2ollama/actions/workflows/ci.yml/badge.svg)](https://github.com/wachawo/hf2ollama/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/hf2ollama.svg)](https://pypi.org/project/hf2ollama/)
[![Downloads](https://img.shields.io/pypi/dm/hf2ollama.svg)](https://pypi.org/project/hf2ollama/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/wachawo/hf2ollama/blob/main/LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/hf2ollama.svg)](https://pypi.org/project/hf2ollama/)

[English](https://github.com/wachawo/hf2ollama/blob/main/README.md) | **[中文](https://github.com/wachawo/hf2ollama/blob/main/docs/README_ZH.md)** | [हिन्दी](https://github.com/wachawo/hf2ollama/blob/main/docs/README_HI.md) | [Español](https://github.com/wachawo/hf2ollama/blob/main/docs/README_ES.md) | [Français](https://github.com/wachawo/hf2ollama/blob/main/docs/README_FR.md) | [العربية](https://github.com/wachawo/hf2ollama/blob/main/docs/README_AR.md) | [বাংলা](https://github.com/wachawo/hf2ollama/blob/main/docs/README_BN.md) | [Русский](https://github.com/wachawo/hf2ollama/blob/main/docs/README_RU.md) | [Português](https://github.com/wachawo/hf2ollama/blob/main/docs/README_PT.md) | [اردو](https://github.com/wachawo/hf2ollama/blob/main/docs/README_UR.md)

用一条命令在 Ollama 中运行任意 HuggingFace 文本模型。

把 `hf2ollama` 指向一个 HuggingFace 仓库 —— 它会下载模型,
将其转换为 Ollama 所需的 GGUF 格式,然后输出两条 `ollama` 命令,
你只需要运行它们就能开始对话。无需手动调用 `convert_hf_to_gguf.py`,
也不用自己写 `Modelfile`。

需要 Python 3.11 及以上版本,以及已经安装好的 [Ollama](https://ollama.com)。

---

## 安装

```bash
pip install hf2ollama
```

---

## 使用方法

在运行命令的目录里,把 HuggingFace 令牌写到 `.env` 文件,
然后把工具指向一个仓库:

```bash
echo "HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxx" > .env
hf2ollama SicariusSicariiStuff/Assistant_Pepe_70B
```

完成后,工具会输出两条命令,执行它们就能开始对话:

```
ollama create assistant-pepe-70b -f <path>/Modelfile
ollama run assistant-pepe-70b
```

(在 <https://huggingface.co/settings/tokens> 申请 `Read` 权限的令牌。
只有私有和受限模型才必须用它,但设置好也无妨。)

### 可选参数

```bash
# 查看 *-GGUF 仓库里有哪些量化版本(不下载):
hf2ollama some-user/some-model-GGUF --list

# 只下载指定的一个量化 —— 其他 .gguf 文件会被跳过:
hf2ollama some-user/some-model-GGUF --quant Q5_K_M

# 自定义 Ollama 模型名:
hf2ollama some-user/some-model --ollama-name my-model
```

---

## 从 git 安装

如果想用最新的未发布版本:

```bash
pip install git+https://github.com/wachawo/hf2ollama.git
# 或使用 SSH:
pip install git+ssh://git@github.com/wachawo/hf2ollama.git
```

## 从源码安装

本地开发时:

```bash
git clone git@github.com:wachawo/hf2ollama.git
cd hf2ollama
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env   # 然后把 HF_TOKEN 填到 .env
hf2ollama --help
```

---

## 配置

在运行 `hf2ollama` 的目录里放一个 `.env`:

```ini
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
# 可选。f16(默认)| f32 | bf16 | q8_0 | auto
OUTTYPE=f16
```

### 路径覆盖

所有内容默认写到当前工作目录。如果想让多个工作区共享某些目录,
用下面的环境变量覆盖:

| 变量                          | 默认值                       | 用途                                |
|------------------------------|------------------------------|-------------------------------------|
| `HF2OLLAMA_WORKSPACE`        | `$PWD`                       | 下面所有内容的根目录。              |
| `HF2OLLAMA_HF_DIR`           | `<workspace>/hf`             | HF 快照和 GGUF 文件的位置。         |
| `HF2OLLAMA_CACHE_DIR`        | `<workspace>/.hf_cache`      | `huggingface_hub` 缓存。            |
| `HF2OLLAMA_LLAMA_CPP_DIR`    | `<workspace>/../llama.cpp`   | `llama.cpp` 克隆目录。              |

---

## 磁盘上的最终结构

```
<workspace>/
├── .env                # HF_TOKEN, OUTTYPE
├── hf/                 # HF 快照下载到这里
│   └── <org>/<name>/   # 源文件 + 转换后的 GGUF + Modelfile,都在一个目录里
│       ├── config.json
│       ├── model.safetensors
│       ├── ...
│       ├── <name>.f16.gguf
│       └── Modelfile
└── .hf_cache/          # 本地 huggingface_hub 缓存

<workspace>/../llama.cpp/   # 克隆一次,多个工作区可以复用
```

首次运行会把 [`llama.cpp`](https://github.com/ggerganov/llama.cpp)
克隆到工作区的上一级,这样后续运行更快。只有自带 GGUF 文件的仓库
会跳过这一步。

## 输出示例

```
======================================================================
GGUF:      <workspace>/hf/SicariusSicariiStuff/Assistant_Pepe_70B/Assistant_Pepe_70B.f16.gguf
Modelfile: <workspace>/hf/SicariusSicariiStuff/Assistant_Pepe_70B/Modelfile

Done. To import the model into Ollama, run these 2 commands:
  ollama create assistant-pepe-70b -f <workspace>/hf/SicariusSicariiStuff/Assistant_Pepe_70B/Modelfile
  ollama run assistant-pepe-70b
======================================================================
```

`ollama create` 会自己把分层数据复制到 `~/.ollama/models/blobs/` 并创建 manifest。
**不要**手动把文件复制到 `~/.ollama/models/` —— Ollama 用 sha256 索引 blob,
手动复制会破坏索引。

---

## 常见问题

### `RepositoryNotFoundError`

HuggingFace 上不存在该仓库。有些模型不在 HF 上发布 —— 例如 `xai/grok-*`
只通过 xAI API 提供,本流程无法获取。

### `GatedRepoError`

模型需要先接受授权协议。打开 HF 上的模型页面,点击 "Agree and access",
并确保 `.env` 里的令牌有权限访问该仓库。

### `No .safetensors files found`

仓库只用旧的 `pytorch_model.bin` 格式发布权重。默认情况下 `.bin` 被排除,
以免重复下载 safetensors。把 `hf2ollama.py` 里 `IGNORE_PATTERNS` 中的
`*.bin` 和 `*.pth` 删掉,然后重新运行。

### 磁盘或 VRAM 不够

70B 模型的 `f16` 大约占 140 GB 磁盘和同样多的 VRAM。两种应对方法:

- 先转换成 `f16`,再量化成 `Q4_K_M`(见下文)—— `Q4_K_M` 把文件缩小约 4 倍,
  质量损失很小。
- 找社区已经构建好的 GGUF(`<org>/<name>-GGUF`),用 `--list` 看可用的量化版本,
  再用 `--quant Q4_K_M` 只下载需要的那一个。

---

## 手动量化(可选)

如果已经转换为 `f16`,想得到更小的 `Q4_K_M`:

```bash
cd ../llama.cpp
cmake -B build && cmake --build build --target llama-quantize -j
./build/bin/llama-quantize \
    <workspace>/hf/<org>/<name>/<name>.f16.gguf \
    <workspace>/hf/<org>/<name>/<name>.Q4_K_M.gguf \
    Q4_K_M
```

然后写一个指向 `Q4_K_M.gguf` 的新 `Modelfile`,
用新名字运行 `ollama create`。
