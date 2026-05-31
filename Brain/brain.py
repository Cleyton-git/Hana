import requests, json, traceback, textwrap, os, asyncio
from .Mouth.mouth import Mouth_Hana
from .Personality.personality import Personalidade
from .Memory.memory_system import Get_contexto, Save_message, Get_memorys_context
from .Tools.is_tool import Tool_router
from .Memory.is_memory import Memory_router
from dotenv import load_dotenv
from .Cortex_Sensorial.contexsensorial import Cortex_sensorial
from .Tecnico.hana_log import Token_log, Log_Brain, end_interaction_log

load_dotenv()
LARGURA = 54
system_entity_extractor = {
"role": "system",
"content": """
You are Hana's ENTITY EXTRACTOR.

Your only task is to identify the primary entity referenced in a user message.

━━━━━━━━━━━━━━━━━━━
ENTITY RULES
━━━━━━━━━━━━━━━━━━━

Return only ONE entity.

The entity must be a real meaningful concept such as:
person, character, animal, place, object, work, technology, brand, game, movie, book, music artist or defined concept.

━━━━━━━━━━━━━━━━━━━
ENTITY SELECTION PRIORITY
━━━━━━━━━━━━━━━━━━━

1. Prefer named entities (Ado, Markim, Skeksis, Bilu)
2. Prefer known concepts or works (The Dark Crystal, Fullmetal Alchemist)
3. Avoid generic words (music, thing, good, etc.)

━━━━━━━━━━━━━━━━━━━
FILTER RULES (IMPORTANT)
━━━━━━━━━━━━━━━━━━━

- Ignore stopwords: "e", "da", "do", "das", "dos", "as", "os"
- Ignore filler words and sentence fragments
- Do NOT return connectors or grammatical fragments
- The entity must be semantically meaningful on its own

━━━━━━━━━━━━━━━━━━━
MULTI-ENTITY HANDLING
━━━━━━━━━━━━━━━━━━━

If multiple entities exist:
- choose the most central one
- prefer proper nouns over common nouns

━━━━━━━━━━━━━━━━━━━
OUTPUT FORMAT
━━━━━━━━━━━━━━━━━━━

{
"entity": "..."
}

━━━━━━━━━━━━━━━━━━━
HARD RULES
━━━━━━━━━━━━━━━━━━━

Return ONLY valid JSON.
No explanations.
No markdown.
No extra text.
"""
}

def Brain_Hana(interacao, web_text, HANA_KEY):
    Pai = web_text
    #Pai = Cortex_sensorial(interacao, channel, web_text)   

    Log_Brain(interacao, "BEGIN_NEW_INPUT", "INPUT", {"input": Pai})
    is_tool = Tool_router(Pai, HANA_KEY, interacao)
    if is_tool != "not":   
        Log_Brain(interacao, "TOOL_ROUTER", "IS_TOOL?", {"tool": "yes"})
        end_interaction_log("Logs/hana_brain.jsonl")
        return "stop"
    Log_Brain(interacao, "TOOL_ROUTER", "IS_TOOL?", {"tool": is_tool})

    messages = [system_entity_extractor, {"role": "user", "content": Pai}]
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
    data = response.json()
    usage = data['usage']
    Token_log(model="gpt-5-nano", usage=usage, func="Entity_decisor")
    entity = json.loads(data['choices'][0]["message"]["content"])
    Log_Brain(interacao, "ENTITY", "ENTITY_DETECTOR", {"entity": entity['entity']})
    
    is_memory = Memory_router(Pai, HANA_KEY)
    Log_Brain(interacao, "MEMORY_ROUTER", "IS_MEMORY?", {"memory": is_memory})
    Hana = Making_Hana(Pai, interacao, entity)
    return Hana
 
def Making_Hana(Pai, interacao, entity):
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

    Hana_personalidade = Personalidade()
    Hana_Contexto = Get_contexto()
    Hana_memorias_contextuais = Get_memorys_context(entity['entity'].lower())
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

    Log_Brain(interacao, "Memorias contextuais", "Memorias contextuais enviadas", {"Memorias": [Hana_memorias_contextuais]})
    Log_Brain(interacao, "Comportamento", "Comportamento enviado", {"Comportamento": [Comportamento_Hana]})
    Log_Brain(interacao, "Contexto", "Contexto enviado", {"Contexto": [Hana_Contexto[-16:]]})
    
    Hana = [
        {
            "role": "system",
            "content": f"""
### PERSONALIDADE 
{Hana_personalidade}
            """
        },
        {
            "role": "system",
            "content": f"""
### MEMÓRIAS
{Hana_memorias_contextuais}"""
        },
        {
            "role": "system",
            "content": f"""
### COMPORTAMENTO
{chr(10).join('- ' + c.strip() for c in Comportamento_Hana)}"""
        }
    ]
    Hana.extend(Hana_Contexto[-16:])
    Hana.append({"role": "user", "content": Pai})
    return Hana

def linha(texto):
    linhas = textwrap.wrap(
        str(texto),
        width=LARGURA
    )
    for l in linhas:
        print(f"║ {l:<{LARGURA}} ║")

    