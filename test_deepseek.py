import os
import requests
import sys

# 配置部分：请在此处填入你的 DeepSeek API Key
API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-xxx") 
BASE_URL = "https://api.deepseek.com" # 或者是其他兼容 OpenAI 的地址

def test_deepseek_connection():
    print(f"Testing connection to {BASE_URL}...")
    
    url = f"{BASE_URL}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat", # 或者是 deepseek-reasoner
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, this is a test. Please reply with 'Connection Successful'."}
        ],
        "stream": True
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, stream=True, timeout=30)
        
        if response.status_code != 200:
            print(f"Error: Status Code {response.status_code}")
            print(response.text)
            return

        print("Response received. Streaming content:")
        for line in response.iter_lines(decode_unicode=True):
            if line:
                if line.startswith("data: [DONE]"):
                    break
                if line.startswith("data: "):
                    import json
                    try:
                        data = json.loads(line[6:])
                        content = data['choices'][0]['delta'].get('content', '')
                        print(content, end="", flush=True)
                    except:
                        pass
        print("\n\nTest Finished!")
        
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    if API_KEY == "sk-xxx":
        print("Please set your DEEPSEEK_API_KEY in the script or environment variable.")
    else:
        test_deepseek_connection()
