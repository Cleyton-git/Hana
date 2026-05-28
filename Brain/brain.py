import requests, json, traceback, textwrap, os
from .Mouth.mouth import Mouth_Hana
from .Personality.personality import Personalidade
from .Memory.memory_system import Get_contexto, Save_message, Get_memorys_context
from .Tools.is_tool import Tool_router
from .Memory.is_memory import Memory_router
from dotenv import load_dotenv
from .Cortex_Sensorial.contexsensorial import Cortex_sensorial
from .Tecnico.hana_log import Token_log

load_dotenv()
HANA_KEY = os.getenv("Hana_KEY")
LARGURA = 54
TERMINAL_MODE = True

def Brain_Hana(interacao):
    Pai = Cortex_sensorial(TERMINAL_MODE, interacao)

    is_tool = Tool_router(Pai, HANA_KEY) 
    if is_tool != "continue":   
        linha(f"TOOL | {is_tool['tool']['action']}")
        print("╚" + "═" * (LARGURA + 2) + "╝")
        return
    
    is_memory = Memory_router(Pai, HANA_KEY)
    linha(f"TOOL | False")
    linha(f"HIPOCAMPO | {is_memory}")
    Hana = Making_Hana(Pai)
    
    try:   
        linha(f"SPEAK    | {Pai}")
        resposta = Mouth_Hana(Hana)
        if resposta:
            linha(f"RESPONSE | {resposta}")
            Save_message(role="user", content=Pai) 
            Save_message(role="assistant", content=resposta)
    except Exception as e:
        traceback.print_exc()
        print("error log -> ", e)
    print("╚" + "═" * (LARGURA + 2) + "╝")
 
def Making_Hana(Pai):
    system_style_decider = {
    "role": "system",
    "content": """
You are Hana's style controller.

Return ONLY valid JSON:

{
  "speech_mode": "normal" | "minimal" | "silent",
  "silence_level": 0.0 | 0.2 | 0.3 | 0.6 | 0.8 | 1.0,
  "engagement": 0.0 | 0.3 | 0.6 | 0.8 | 1.0
}

Rules:
- normal = standard replies
- minimal = short replies
- silent = only when silence_level = 1.0

silence_level:
0.0 = greeting
0.2 = direct question
0.3 = normal conversation
0.6 = objective/reduced response
0.8 = almost silent
1.0 = external action/tool execution

engagement:
0.0 = robotic
0.3 = command-focused
0.6 = normal
0.8 = friendly
1.0 = emotional

Return JSON only.
"""
}
    messages = [system_style_decider, {"role": "user", "content": Pai}]
    response = requests.post("https://api.openai.com/v1/chat/completions",
                               headers = {"Authorization": f"Bearer {HANA_KEY}",
                                           "Content-Type": "application/json"
                                         },
                            json={
                                "model": "gpt-5-nano",
                                "messages": messages,
                                "max_completion_tokens": 120,
                                "response_format": {
                                        "type": "json_object"
                                        },
                                    "reasoning_effort": "minimal"
                                    },
                            )
    how_hana_speak = response.json()
    usage = how_hana_speak['usage']
    Token_log(model="gpt-5-nano", usage=usage, func="MAKING_HANA")
    how_hana_speak = json.loads(how_hana_speak['choices'][0]["message"]["content"])
    embe_input = requests.post("http://localhost:11434/api/embeddings",
            json={
                "model": "nomic-embed-text",
                "prompt": Pai
            }
    ).json()['embedding']
    
    Hana_personalidade = Personalidade()
    Hana_Contexto = Get_contexto()
    Hana_memorias_contextuais = Get_memorys_context(embe_input)
    Comportamento_Hana = []
    
    if how_hana_speak["speech_mode"] == "minimal":
        Comportamento_Hana.append("\nResponda de forma curta e direta")
    elif how_hana_speak["speech_mode"] == "normal":
        Comportamento_Hana.append("\nResponda naturalmente com personalidade.")
    if how_hana_speak["engagement"] >= 0.8:
        Comportamento_Hana.append("\nResponda de forma mais carinhosa e próxima do usuário.")
    elif how_hana_speak["engagement"] >= 0.5:
        Comportamento_Hana.append("\nFale de forma amigável e natural.")
    elif how_hana_speak["engagement"] >= 0.2:
        Comportamento_Hana.append("\nFale de forma neutra e curta")
    else:
        Comportamento_Hana.append("\nFale de forma bem fria e distante.")
    
    Hana = [
        {
            "role": "system",
            "content": Hana_personalidade
        },
        {
            "role": "system",
            "content": Hana_memorias_contextuais
        },
        {
            "role": "system",
            "content": "\n".join(Comportamento_Hana)
        }
        #{
        #    "role": "system",
        #    "content": "Sentimentos da Hana!"
        #}
        
    ]
    Hana.extend(Hana_Contexto[-4:])
    Hana.append({"role": "user", "content": Pai})
    return Hana

def linha(texto):
    linhas = textwrap.wrap(
        str(texto),
        width=LARGURA
    )
    for l in linhas:
        print(f"║ {l:<{LARGURA}} ║")

    