import requests
import json

def Mouth_Hana(url, msg, model):
    r = requests.post(
      url,
        json={
          "model": model,
          "messages": msg,
          "stream": False
        }
    )

    return r.json()["message"]["content"]

def Ia_duplicy_verification(msg, model):
    r = requests.post(
      "http://127.0.0.1:11434/api/chat",
        json={
          "model": model,
          "messages": msg,
          "stream": False,
          "temperature": 0
        }
    )

    return json.loads(r.json()["message"]["content"])

