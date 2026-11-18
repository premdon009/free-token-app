# Python

The examples are [PEP 723](https://peps.python.org/pep-0723/) scripts: `uv run` installs the
OpenAI SDK for them. Export the key first:

```bash
export LITELLM_MASTER_KEY=sk-...
uv run examples/python/chat.py "Explain HTTP 429 in one line"
```

## Client

```python
--8<-- "examples/python/_client.py"
```

## Chat and streaming

```python
--8<-- "examples/python/chat.py"
```

## Tool calling

Uses `free/coding`, whose models all support tools. Free models sometimes answer without calling
the tool, so the example handles that.

```python
--8<-- "examples/python/tools.py"
```

## Embeddings and RAG

Embeddings from different models can't be compared. If `free/embed` falls back mid-way, vectors
you stored earlier won't match new ones. For a real index, pin one embedding deployment (for
example `ollama/nomic-embed-text`) instead of the lane, and store which model made each vector.

```python
--8<-- "examples/python/rag.py"
```

## Caching

```python
--8<-- "examples/python/cache.py"
```
