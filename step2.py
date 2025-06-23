import openai

openai.api_key = 'sk-proj-xxxxx'

def chat_with_gpt_4o(prompt_text):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",  # Model name (replace with correct identifier if different)
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt_text}
        ],
        temperature=0.7,
        max_tokens=150
    )
    return response['choices'][0]['message']['content']

# Sample usage
if __name__ == "__main__":
    user_input = "Class 1 math question paper  Model"
    output = chat_with_gpt_4o(user_input)
    print("GPT-4o Mini response:\n", output)
