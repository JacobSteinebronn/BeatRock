import vercel_ai
client = vercel_ai.Client()

print(json.dumps(client.model_ids, indent=2))
for chunk in client.generate("openai:gpt-3.5-turbo", "Summarize the GNU GPL v3"):
    print(chunk, end="", flush=True)