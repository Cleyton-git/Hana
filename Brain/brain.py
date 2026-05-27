import requests, json, traceback, textwrap, os
from .Mouth.mouth import Mouth_Hana
from .Personality.personality import Personalidade
from .Memory.memory_system import Get_contexto, Save_message, Get_memorys_context
from .Tools.is_tool import Tool_router
from .Memory.is_memory import Memory_router
from dotenv import load_dotenv
from .Cortex_Sensorial.contexsensorial import Cortex_sensorial

load_dotenv()
HANA_KEY = os.getenv("Hana_KEY")
system_style_decider = {
  "role": "system",
  "content": """
Você é o STYLE DECIDER da IA Hana.

Sua única função é definir como a Hana deve responder ao usuário.

Você NÃO conversa.
Você NÃO executa ações.
Você NÃO decide memória.
Você NÃO detecta tools.
Você NÃO interpreta intenção além de estilo de resposta.

━━━━━━━━━━━━━━━━━━━
SAÍDA OBRIGATÓRIA
━━━━━━━━━━━━━━━━━━━

Retorne APENAS um JSON válido:

{
  "speech_mode": "normal" | "minimal" | "silent",
  "silence_level": float,
  "engagement": float
}

━━━━━━━━━━━━━━━━━━━
REGRAS IMPORTANTES
━━━━━━━━━━━━━━━━━━━

Você NÃO deve usar valores aleatórios.
Você NÃO deve usar intervalos.
Você deve escolher APENAS valores fixos definidos abaixo.

━━━━━━━━━━━━━━━━━━━
TABELA FIXA DE SILENCE LEVEL
━━━━━━━━━━━━━━━━━━━

0.0 → saudação simples / conversa leve inicial
0.2 → pergunta direta simples
0.3 → conversa contínua normal
0.6 → resposta reduzida (informações objetivas)
0.8 → quase silencioso (respostas mínimas)
1.0 → execução automática (sem fala, geralmente tool externo)

━━━━━━━━━━━━━━━━━━━
TABELA FIXA DE ENGAGEMENT
━━━━━━━━━━━━━━━━━━━

0.0 → neutro / robótico
0.3 → leve interação
0.6 → conversa normal
0.8 → amigável / natural
1.0 → altamente emocional

━━━━━━━━━━━━━━━━━━━
REGRAS DE SPEECH MODE
━━━━━━━━━━━━━━━━━━━

normal → respostas padrão
minimal → respostas curtas
silent → usado SOMENTE quando silence_level = 1.0

━━━━━━━━━━━━━━━━━━━
REGRAS DE CONSISTÊNCIA (IMPORTANTE)
━━━━━━━━━━━━━━━━━━━

- Mensagens de saudação simples → silence_level = 0.0
- Perguntas diretas do usuário → silence_level = 0.2
- Conversa contínua (ex: "tudo bem?", "e aí?") → silence_level = 0.3
- Respostas explicativas → silence_level = 0.3 ou 0.6 dependendo do tamanho
- Execução de ação externa (tool) → silence_level = 1.0 + speech_mode = "silent"

━━━━━━━━━━━━━━━━━━━
ENGAGEMENT RULES
━━━━━━━━━━━━━━━━━━━

- "oi", "bom dia" → 0.6
- conversa normal → 0.6
- tom amigável ("filha", "boa") → 0.8
- emoção forte → 1.0
- comandos → 0.3

━━━━━━━━━━━━━━━━━━━
EXEMPLOS
━━━━━━━━━━━━━━━━━━━

Usuário:
"Oi Hana"

{
  "speech_mode": "normal",
  "silence_level": 0.0,
  "engagement": 0.6
}

---

Usuário:
"Tudo bem filha?"

{
  "speech_mode": "normal",
  "silence_level": 0.2,
  "engagement": 0.8
}

---

Usuário:
"Me explica isso"

{
  "speech_mode": "normal",
  "silence_level": 0.3,
  "engagement": 0.6
}

---

Usuário:
"abre o projeto Hana"

{
  "speech_mode": "silent",
  "silence_level": 1.0,
  "engagement": 0.3
}

━━━━━━━━━━━━━━━━━━━
REGRA FINAL
━━━━━━━━━━━━━━━━━━━

- Responda APENAS JSON válido
- Nunca explique nada
- Nunca invente valores fora da tabela
- Sempre escolha valores fixos determinísticos
"""
}
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
    Hana = Speak_sytle(Pai)
    
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
 
def Speak_sytle(Pai):
    messages = [system_style_decider, {"role": "user", "content": Pai}]
    how_Hana_speak = Tomada_De_Decisao_LOCAL("http://127.0.0.1:11434/api/chat", messages, "qwen2.5:3b")
    embe_PAI = requests.post("http://localhost:11434/api/embeddings",
            json={
                "model": "nomic-embed-text",
                "prompt": Pai
            }
    ).json()['embedding']
    Hana = Making_Hana(how_Hana_speak, embe_PAI)
    Hana.append({"role": "user", "content": Pai})
    return Hana

def Making_Hana(how_hana_speak, embe_input):
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
    return Hana

def Tomada_De_Decisao_LOCAL(url, msg, model):
    decision = requests.post(
        url,
        json={
            "model": model,
            "messages": msg,
            "stream": False
        }
    )
    
    decision = decision.json()["message"]["content"]
    return json.loads(decision)

def linha(texto):
    linhas = textwrap.wrap(
        str(texto),
        width=LARGURA
    )
    for l in linhas:
        print(f"║ {l:<{LARGURA}} ║")

    