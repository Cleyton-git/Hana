import requests, json
from ..Tecnico.hana_log import Token_log

def Talking_Agent(HANA_KEY, model, messages, completion_tokens, AGENTE):
    response = requests.post("https://api.openai.com/v1/chat/completions",
                               headers = {"Authorization": f"Bearer {HANA_KEY}",
                                           "Content-Type": "application/json"
                                         },
                            json={
                                "model": f"{model}",
                                "messages": messages,
                                "max_completion_tokens": completion_tokens,
                                "response_format": {
                                        "type": "json_object"
                                        },
                                    "reasoning_effort": "minimal"
                                    }, timeout=30
                            )
    data = response.json()
    
    usage = data['usage']
    Token_log(model=f"{model}", usage=usage, func=f"{AGENTE}")
    response = json.loads(data['choices'][0]["message"]["content"]) 
    print(f"Response {AGENTE} -> {response}")
    return response