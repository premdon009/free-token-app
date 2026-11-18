# Local models

Local models are the last hop in every chat lane and the whole `local` lane. They cost nothing,
work offline and keep everything on your machine. They're also much weaker and slower than the
hosted free models.

## What fits a laptop without a GPU

With about 7–8 GB of RAM and no GPU, stay at **3B parameters or less** (4-bit quantised, about
2 GB each). Expect a few tokens per second.

| Model | Size | For | Lane |
|---|---|---|---|
| `qwen2.5-coder:3b` | ~1.9 GB | Code completion, small edits | `local`, end of `free/coding` |
| `llama3.2:3b` | ~2.0 GB | General chat | `local`, end of `free/fast` / `free/private` |
| `nomic-embed-text` | ~0.3 GB | Embeddings | end of `free/embed` |
| `qwen2.5-coder:1.5b` | ~1.0 GB | Faster, weaker coder | swap in if 3B is too slow |

With 16 GB+ RAM or a GPU, 7B–14B coder models are a big step up.

## Ollama (what the router uses)

```bash
curl -fsSL https://ollama.com/install.sh | sh        # or your distro's package
ollama pull qwen2.5-coder:3b
ollama pull llama3.2:3b
ollama pull nomic-embed-text
ollama ps                                             # what's loaded right now
```

Ollama listens on `127.0.0.1:11434`, which is `OLLAMA_API_BASE` in `router/.env`. Because the
router container uses host networking, it reaches Ollama directly. On Docker Desktop use
`http://host.docker.internal:11434` (see [troubleshooting](../router/troubleshooting.md)).

To keep memory free, Ollama unloads idle models after 5 minutes (`OLLAMA_KEEP_ALIVE`).

## llama.cpp

`llama-server` serves an OpenAI-compatible API from one GGUF file:

```bash
llama-server -m qwen2.5-coder-3b-instruct-q4_k_m.gguf --host 127.0.0.1 --port 8080 -c 8192
```

Use it straight from an app (`base_url=http://127.0.0.1:8080/v1`). It isn't in the router chain;
to add it, give the `llama-cpp` row in `providers.yml` a model and `router.include: true`.

## LM Studio

A desktop app with a model browser. Its local server (Developer tab) is OpenAI-compatible on
`http://127.0.0.1:1234/v1`. Same as llama.cpp: usable directly, not in the default chain.
