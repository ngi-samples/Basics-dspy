import requests
import json

API_KEY = "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"
url = "https://api.openai.com/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

data = {
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Hello, how are you?"}]
}

response = requests.post(url, headers=headers, data=json.dumps(data))

# Extract headers
rate_limit_info = {
    "Requests Limit": response.headers.get("X-Ratelimit-Limit-Requests"),
    "Requests Remaining": response.headers.get("X-Ratelimit-Remaining-Requests"),
    "Requests Reset Time": response.headers.get("X-Ratelimit-Reset-Requests"),
    "Tokens Limit": response.headers.get("X-Ratelimit-Limit-Tokens"),
    "Tokens Remaining": response.headers.get("X-Ratelimit-Remaining-Tokens"),
    "Tokens Reset Time": response.headers.get("X-Ratelimit-Reset-Tokens"),
}

print(rate_limit_info)
