from openai import OpenAI

client = OpenAI(
  api_key='k-proj-xxx'
)

completion = client.chat.completions.create(
  model="gpt-4o-mini",
  store=True,
  messages=[
    {"role": "user", "content": "what is LPL financial service"}
  ]
)

print(completion.choices[0].message);
