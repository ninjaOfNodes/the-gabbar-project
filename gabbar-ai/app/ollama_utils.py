import requests
import json

def is_code_request(message):
    code_keywords = [
        'generate code', 'write a function', 'python', 'javascript', 'java', 'c++', 'c#', 'code:', 'def ', 'function '
    ]
    msg = message.lower()
    return any(kw in msg for kw in code_keywords)

def chat_with_model(history, model, stream=False):
    try:
        url = 'http://localhost:11434/api/chat'
        payload = {
            'model': model,
            'messages': history
        }
        if stream:
            payload['stream'] = True
            with requests.post(url, json=payload, timeout=120, stream=True) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if line:
                        yield line.decode('utf-8')
        else:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            data = response.json()
            return json.dumps(data)
    except Exception as e:
        error_json = json.dumps({'error': f'Error communicating with Ollama API: {e}'})
        if stream:
            yield error_json
        else:
            return error_json
