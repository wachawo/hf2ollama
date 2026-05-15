# hf2ollama

[![CI](https://github.com/wachawo/hf2ollama/actions/workflows/ci.yml/badge.svg)](https://github.com/wachawo/hf2ollama/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/hf2ollama.svg)](https://pypi.org/project/hf2ollama/)
[![Downloads](https://img.shields.io/pypi/dm/hf2ollama.svg)](https://pypi.org/project/hf2ollama/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/wachawo/hf2ollama/blob/main/LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/hf2ollama.svg)](https://pypi.org/project/hf2ollama/)

[English](https://github.com/wachawo/hf2ollama/blob/main/README.md) | [中文](https://github.com/wachawo/hf2ollama/blob/main/docs/README_ZH.md) | [हिन्दी](https://github.com/wachawo/hf2ollama/blob/main/docs/README_HI.md) | [Español](https://github.com/wachawo/hf2ollama/blob/main/docs/README_ES.md) | [Français](https://github.com/wachawo/hf2ollama/blob/main/docs/README_FR.md) | [العربية](https://github.com/wachawo/hf2ollama/blob/main/docs/README_AR.md) | [বাংলা](https://github.com/wachawo/hf2ollama/blob/main/docs/README_BN.md) | [Русский](https://github.com/wachawo/hf2ollama/blob/main/docs/README_RU.md) | **[Português](https://github.com/wachawo/hf2ollama/blob/main/docs/README_PT.md)** | [اردو](https://github.com/wachawo/hf2ollama/blob/main/docs/README_UR.md)

Execute qualquer modelo de texto do HuggingFace dentro do Ollama com um único comando.

Aponte o `hf2ollama` para um repositório no HuggingFace — ele baixa o modelo,
converte para o formato GGUF que o Ollama precisa, e imprime os dois comandos
`ollama` que você executa para registrar e conversar com o modelo. Sem chamar
`convert_hf_to_gguf.py` à mão, sem escrever um `Modelfile`.

Requer Python 3.11+ e uma instalação funcional do [Ollama](https://ollama.com).

---

## Instalação

```bash
pip install hf2ollama
```

---

## Uso

Coloque seu token do HuggingFace num `.env` ao lado do diretório de onde vai
executar o comando, depois aponte a ferramenta para um repositório:

```bash
echo "HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxx" > .env
hf2ollama SicariusSicariiStuff/Assistant_Pepe_70B
```

Ao terminar, a ferramenta imprime dois comandos. Execute-os e você já está conversando:

```
ollama create assistant-pepe-70b -f <path>/Modelfile
ollama run assistant-pepe-70b
```

(Pegue um token em <https://huggingface.co/settings/tokens> com escopo `Read`.
É obrigatório apenas para modelos privados e gated, mas tê-lo configurado
nunca é demais.)

### Opções

```bash
# Ver quais quantizações GGUF um repo *-GGUF traz (sem baixar):
hf2ollama some-user/some-model-GGUF --list

# Baixar só uma quantização — as outras .gguf são puladas:
hf2ollama some-user/some-model-GGUF --quant Q5_K_M

# Nome customizado para o modelo no Ollama:
hf2ollama some-user/some-model --ollama-name my-model
```

---

## Instalação via git

Para mudanças ainda não publicadas:

```bash
pip install git+https://github.com/wachawo/hf2ollama.git
# ou por SSH:
pip install git+ssh://git@github.com/wachawo/hf2ollama.git
```

## Instalação a partir do código

Para desenvolvimento local:

```bash
git clone git@github.com:wachawo/hf2ollama.git
cd hf2ollama
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env   # depois coloque seu HF_TOKEN no .env
hf2ollama --help
```

---

## Configuração

`.env` no diretório de onde você executa o `hf2ollama`:

```ini
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
# Opcional. f16 (padrão) | f32 | bf16 | q8_0 | auto
OUTTYPE=f16
```

### Sobrescrever caminhos

Tudo é escrito por padrão dentro do diretório atual. Para compartilhar entre
workspaces, sobrescreva via variáveis de ambiente:

| Variável                     | Padrão                       | Função                                 |
|------------------------------|------------------------------|----------------------------------------|
| `HF2OLLAMA_WORKSPACE`        | `$PWD`                       | Diretório base de tudo abaixo.         |
| `HF2OLLAMA_HF_DIR`           | `<workspace>/hf`             | Onde vão os snapshots HF e os GGUF.    |
| `HF2OLLAMA_CACHE_DIR`        | `<workspace>/.hf_cache`      | Cache do `huggingface_hub`.            |
| `HF2OLLAMA_LLAMA_CPP_DIR`    | `<workspace>/llama.cpp`      | Onde clonar o `llama.cpp`.             |

---

## O que acaba no disco

```
<workspace>/
├── .env                # HF_TOKEN, OUTTYPE
├── hf/                 # snapshots HF caem aqui
│   └── <org>/<name>/   # arquivos-fonte + GGUF gerado + Modelfile, tudo junto
│       ├── config.json
│       ├── model.safetensors
│       ├── ...
│       ├── <name>.f16.gguf
│       └── Modelfile
└── .hf_cache/          # cache local do huggingface_hub

<workspace>/llama.cpp/   # clonado na primeira execução de conversão
```

A primeira execução de conversão clona o
[`llama.cpp`](https://github.com/ggerganov/llama.cpp) dentro do workspace,
para que as próximas execuções sejam rápidas. Apenas repositórios que já
entregam arquivos GGUF pré-construídos pulam essa etapa. Para compartilhar
um mesmo clone entre vários workspaces, defina `HF2OLLAMA_LLAMA_CPP_DIR`
(por exemplo `../llama.cpp`).

## Exemplo de saída

```
======================================================================
GGUF:      <workspace>/hf/SicariusSicariiStuff/Assistant_Pepe_70B/Assistant_Pepe_70B.f16.gguf
Modelfile: <workspace>/hf/SicariusSicariiStuff/Assistant_Pepe_70B/Modelfile

Done. To import the model into Ollama, run these 2 commands:
  ollama create assistant-pepe-70b -f <workspace>/hf/SicariusSicariiStuff/Assistant_Pepe_70B/Modelfile
  ollama run assistant-pepe-70b
======================================================================
```

`ollama create` copia as camadas para `~/.ollama/models/blobs/` e cria o
próprio manifest. **Não** copie arquivos manualmente para `~/.ollama/models/`
— o Ollama indexa blobs por sha256, e uma cópia manual quebra o índice.

---

## Problemas comuns

### `RepositoryNotFoundError`

O repositório não existe no HuggingFace. Alguns modelos são publicados em
outro lugar — por exemplo, `xai/grok-*` fica atrás da API da xAI e este
fluxo não consegue buscá-lo.

### `GatedRepoError`

O modelo exige aceitar uma licença. Abra a página do modelo no HF, clique em
"Agree and access" e confirme que o token em `.env` tem acesso ao repositório.

### `No .safetensors files found`

O repo só publica pesos no formato antigo `pytorch_model.bin`. Por padrão
`.bin` é excluído para evitar duplicar safetensors. Remova `*.bin` e `*.pth`
de `IGNORE_PATTERNS` em `hf2ollama.py` e rode de novo.

### Sem espaço em disco ou VRAM

`f16` para um modelo 70B ocupa cerca de 140 GB em disco e o mesmo em VRAM ao
carregar. Dois caminhos:

- Converter para `f16` primeiro e depois quantizar para `Q4_K_M` (ver abaixo)
  — `Q4_K_M` reduz o arquivo cerca de 4×, com perda mínima de qualidade.
- Procurar um GGUF já feito pela comunidade (`<org>/<name>-GGUF`) — `--list`
  mostra as quantizações disponíveis e `--quant Q4_K_M` baixa só a desejada.

---

## Quantização manual (opcional)

Se já tem `f16` e quer um `Q4_K_M` menor:

```bash
cd llama.cpp   # ou o diretório apontado por HF2OLLAMA_LLAMA_CPP_DIR
cmake -B build && cmake --build build --target llama-quantize -j
./build/bin/llama-quantize \
    <workspace>/hf/<org>/<name>/<name>.f16.gguf \
    <workspace>/hf/<org>/<name>/<name>.Q4_K_M.gguf \
    Q4_K_M
```

Depois crie um novo `Modelfile` apontando para o `Q4_K_M.gguf` e execute
`ollama create` com um nome diferente.
