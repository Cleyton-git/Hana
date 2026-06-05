import requests, os, edge_tts, json, asyncio
from playsound3 import playsound
from dotenv import load_dotenv
from ..Tecnico.hana_log import Token_log

load_dotenv()
HANA_KEY = os.getenv("Hana_KEY")

async def Criar_frase(texto, path_save):
  communicate = edge_tts.Communicate(
        texto,
        voice="pt-BR-FranciscaNeural",
        pitch="+5Hz",
        rate="+8%"
    )

  await communicate.save(path_save)
  
async def Mouth_Hana(msg, terminal):
  response = requests.post("https://api.openai.com/v1/chat/completions",
                        headers = {"Authorization": f"Bearer {HANA_KEY}",
                                    "Content-Type": "application/json"
                                  },
                        json={
                          "model": "gpt-5-nano",
                          "messages": msg,
                          "max_completion_tokens": 2000,
                          },
                      )

  data = response.json()
  usage = data['usage']
  Token_log(model="gpt-5-nano", usage=usage, func="Mouth")
  content = json.loads(data['choices'][0]["message"]["content"])
  response = content['response']
  reasoning = content['reasoning']
  
  if terminal == "on":
    await Criar_frase(response, "audios/Hana_voz.mp3")
    playsound("audios/Hana_voz.mp3")
    
  return {"resposta": response, 
          "razao": reasoning}


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

