# TypeScript

```bash
cd examples/typescript
npm install
export LITELLM_MASTER_KEY=sk-...
npm run chat -- "Explain HTTP 429 in one line"
```

```typescript
--8<-- "examples/typescript/chat.ts"
```

Tools and embeddings work the same way as in the [Python examples](python.md): the same
`tools` array, `client.embeddings.create({ model: "free/embed", input })`.
