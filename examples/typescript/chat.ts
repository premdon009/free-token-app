// Plain and streamed chat through the router.
//   cd examples/typescript && npm install && npm run chat -- "Explain HTTP 429 in one line"
import OpenAI from "openai";

const apiKey = process.env.LITELLM_MASTER_KEY;
if (!apiKey) throw new Error("export LITELLM_MASTER_KEY first (the value from router/.env)");

const client = new OpenAI({
  baseURL: process.env.ROUTER_URL ?? "http://127.0.0.1:4000/v1",
  apiKey,
  maxRetries: 2,
  timeout: 120_000,
});

const prompt = process.argv.slice(2).join(" ") || "Say hi in five words.";

const r = await client.chat.completions.create({
  model: "free/fast",
  messages: [{ role: "user", content: prompt }],
});
console.log(`[${r.model}] ${r.choices[0]?.message.content}\n`);

const stream = await client.chat.completions.create({
  model: "free/fast",
  messages: [{ role: "user", content: prompt }],
  stream: true,
});
process.stdout.write("streamed: ");
for await (const chunk of stream) {
  process.stdout.write(chunk.choices[0]?.delta?.content ?? "");
}
process.stdout.write("\n");
