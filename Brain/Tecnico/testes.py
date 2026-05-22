import requests

API_KEY = "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"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

data = {
    "model": "gpt-5-mini",
    "messages": [
        {
            "role": "system",
            "content": "Você é Hana."
        },
        {
            "role": "user",
            "content": "Oi Hana"
        }
    ],
    "max_completion_tokens": 100
}

response = requests.post(
    "https://api.openai.com/v1/chat/completions",
    headers=headers,
    json=data
)

print(response.json())