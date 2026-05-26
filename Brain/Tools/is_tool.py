
import requests, json, threading
from ..Tecnico.hana_log import Token_log
from .tools import Tool_Hana

system_tool_router = {
"role": "system",
"content": """
Detecte a tool da mensagem.

TOOLS:
- abrir_projeto
- pesquisar_web
- pesquisar_youtube
- abrir_video
- tocar_musica

Retorne SOMENTE:

{"tool":{"action":"NOME"}}

ou

{"tool":null}

REGRAS:

- música, banda, artista, ouvir, toca, coloca
→ tocar_musica

- abrir ou assistir vídeo específico
→ abrir_video

- pesquisar/procurar vídeos no youtube
→ pesquisar_youtube

- pesquisar google/web/internet
→ pesquisar_web

- abrir projeto
→ abrir_projeto

EXEMPLOS:

"toca linkin park"
→ {"tool":{"action":"tocar_musica"}}

"abre video de minecraft"
→ {"tool":{"action":"abrir_video"}}

"pesquisa python no youtube"
→ {"tool":{"action":"pesquisar_youtube"}}

"pesquisa fastapi no google"
→ {"tool":{"action":"pesquisar_web"}}

"abre o projeto hana"
→ {"tool":{"action":"abrir_projeto"}}

"você gosta de música?"
→ {"tool":null}

Somente JSON.
"""
}

def Tool_router(Pai, HANA_KEY):
    is_tool = Fast_Filter(Pai)
    options = ["tocar_musica", "pesquisar_youtube", "pesquisar_web", "abrir_projeto"]
    if is_tool['tool']['action'] in options:
        pass # LOGAR ESSE DADO AQUI, DPS OU NEM, SLA PORRA
    else:
        messages = [system_tool_router, {"role": "user", "content": Pai}]
        response = requests.post("https://api.openai.com/v1/chat/completions",
                               headers = {"Authorization": f"Bearer {HANA_KEY}",
                                           "Content-Type": "application/json"
                                         },
                            json={
                                "model": "gpt-5-nano",
                                "messages": messages,
                                "max_completion_tokens": 40,
                                "response_format": {
                                        "type": "json_object"
                                        },
                                    "reasoning_effort": "minimal"
                                    },
                            )
        data = response.json()
        usage = data['usage']
        Token_log(model="gpt-5-nano", usage=usage, func="Mouth")
        content = data['choices'][0]["message"]["content"]
        is_tool = json.loads(content)
    if is_tool.get('tool') is not None:
        threading.Thread(target=Tool_Hana,
                         args=(Pai, is_tool['tool']['action'])).start()
        #Tool_Hana(Pai, is_tool['tool']['action'])
        return is_tool
    return "continue"

def Fast_Filter(Pai):
    is_tool = {"tool": {"action": None}}
    if len(Pai.split()) > 15:
        is_tool['tool']['action'] = None
        return is_tool
    if "?" in Pai: ## isso aqui não faz sentido, o bagulho simplesmente fala "NÃO É UM TOOL É UMA PERGUNTA E ELE AINDA ENVIA PRO LLM? KKK"
        is_tool['tool']['action'] = None
        return is_tool
    texto = Pai.lower()
    LOCAL_ACTION_MAP = {
        "tocar_musica": ["toca a música", "toca a musica"],
        "pesquisar_youtube": ["pesquisa no yt", "pesquisa no youtube"],
        "abrir_video": ["abre esse video", "abre esse vídeo", "abre um video", "abre um vídeo"],
        "pesquisar_web": ["pesquisa para mim", "pesquisa sobre", "pesquisa isso", "pesquisa ai sobre"],
        "abrir_projeto": ["abre o projeto"]
    }
    if any(gatilho in texto for gatilho in LOCAL_ACTION_MAP['tocar_musica']):
        is_tool['tool']['action'] = "tocar_musica"
        return is_tool
    elif any(gatilho in texto for gatilho in LOCAL_ACTION_MAP['pesquisar_youtube']):
        is_tool['tool']['action'] = "pesquisar_youtube"
        return is_tool
    elif any(gatilho in texto for gatilho in LOCAL_ACTION_MAP['abrir_video']):
        is_tool['tool']['action'] = "abrir_video"
        return is_tool
    elif any(gatilho in texto for gatilho in LOCAL_ACTION_MAP['pesquisar_web']):
        is_tool['tool']['action'] = "pesquisar_web"
        return is_tool
    elif any(gatilho in texto for gatilho in LOCAL_ACTION_MAP['abrir_projeto']):
        is_tool['tool']['action'] = "abrir_projeto"
        return is_tool
    return is_tool
