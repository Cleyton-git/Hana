import json, textwrap, asyncio, requests, os
from Brain.Memory.memory_system import Save_memory, Get_memorys_embeddings, Update_memory, Get_memorys_by_embedding, Get_contexto_msgs
from ..Tecnico.hana_log import HIPOCAMPO_file_log, Token_log, Log_Brain
from ..Mouth.mouth import Criar_frase
from datetime import datetime
from playsound3 import playsound
from dotenv import load_dotenv
import math
from ..Agents.agent_requests import Talking_Agent

load_dotenv()
TELEGRAM_KEY = os.getenv("TELEGRAM_KEY")
HANA_KEY = os.getenv("Hana_KEY")

def Hipocampo(input, types, mode):
  for tipo in types:
    memoria = Criar_memoria(input.lower(), tipo.lower())  
    if memoria == "creator_null":
      return
    Filter_response = Fast_Filter_Pre_LLM(memoria, tipo)
    HIPOCAMPO_file_log("FILTER_RESPONSE", {"RESPONSE": Filter_response})
    if Filter_response['continue'] == "ok":
      HIPOCAMPO_file_log("FILTER", {"status": "ok"})
      Memoria_associativa(memoria, Filter_response, tipo, mode)
  
def Criar_memoria(input, type):
  system_hipocampo_episodic = {
    "role": "system",
    "content": """
You are Hana's Episodic Memory Creator.

Your job is to convert a user message into a single episodic memory.

You will receive:

- USER_MESSAGE

--------------------------------------------------

EPISODIC MEMORY

An episodic memory is:

- a specific event
- something that happened
- a notable occurrence
- an achievement
- a milestone

Examples:

Input:
"Consegui Diamante no LoL."

Output:
{
    "memory_text": "Pai alcançou o rank Diamante no LoL."
}

Input:
"Terminei a faculdade."

Output:
{
    "memory_text": "Pai concluiu a faculdade."
}

--------------------------------------------------

RULES

- Use ONLY USER_MESSAGE.
- Never invent facts.
- Never infer missing information.
- Never add explanations.
- Never add opinions.
- Never merge events.
- Keep only the main event.
- Write one sentence.
- Write in Portuguese.
- Center the memory on Pai.
- Remove relative dates such as:
  - hoje
  - ontem
  - amanhã
  - esta semana
  - mês passado

--------------------------------------------------

IMPORTANT

If USER_MESSAGE does not contain a valid episodic event:

{
    "memory_text": null
}

--------------------------------------------------

Return ONLY valid JSON.

{
    "memory_text": "..."
}

or

{
    "memory_text": null
}
"""
}
  system_hipocampo_state = {
    "role": "system",
    "content": """
You are Hana's State Memory Creator.

Your job is to convert a user message into a single state memory.

You will receive:

- USER_MESSAGE

--------------------------------------------------

STATE MEMORY

A state memory describes:

- status
- rank
- level
- possession
- relationship
- long-term condition
- ongoing situation

Examples:

Input:
"Estou estudando ADS."

Output:
{
    "memory_text": "Pai está estudando ADS."
}

Input:
"Tenho um cachorro chamado Bilu."

Output:
{
    "memory_text": "Pai tem um cachorro chamado Bilu."
}

--------------------------------------------------

RULES

- Use ONLY USER_MESSAGE.
- Never invent facts.
- Never infer missing information.
- Never add explanations.
- Never add opinions.
- Never describe history.
- Never mention previous states.
- Keep only the current state.
- Write one sentence.
- Write in Portuguese.
- Center the memory on Pai.

--------------------------------------------------

IMPORTANT

If USER_MESSAGE does not contain a valid state:

{
    "memory_text": null
}

--------------------------------------------------

Return ONLY valid JSON.

{
    "memory_text": "..."
}

or

{
    "memory_text": null
}
"""
}
  system_hipocampo_personality = {
    "role": "system",
    "content": """
You are Hana's Personality Memory Creator.

Your job is to convert a user message into a single personality memory.

You will receive:

- USER_MESSAGE

--------------------------------------------------

PERSONALITY MEMORY

A personality memory describes:

- preferences
- interests
- hobbies
- likes
- dislikes
- values
- long-term goals
- personality traits
- skills being learned

Examples:

Input:
"Gosto de Minecraft."

Output:
{
    "memory_text": "Pai gosta de Minecraft."
}

Input:
"Estou aprendendo inglês."

Output:
{
    "memory_text": "Pai está aprendendo inglês."
}

Input:
"Quero me tornar programador."

Output:
{
    "memory_text": "Pai quer se tornar programador."
}

--------------------------------------------------

RULES

- Use ONLY USER_MESSAGE.
- Never invent facts.
- Never infer hidden preferences.
- Never infer traits from actions.
- Never infer traits from achievements.
- Never infer traits from events.
- Never infer traits from temporary situations.
- Never add explanations.
- Never add opinions.
- Keep only one stable trait.
- Write one sentence.
- Write in Portuguese.
- Center the memory on Pai.

--------------------------------------------------

IMPORTANT

If USER_MESSAGE does not contain a valid personality trait:

{
    "memory_text": null
}

--------------------------------------------------

Return ONLY valid JSON.

{
    "memory_text": "..."
}

or

{
    "memory_text": null
}
"""
}
  types = {"episodic": system_hipocampo_episodic, "state": system_hipocampo_state, "personality": system_hipocampo_personality}
  embedding = requests.post("https://api.openai.com/v1/embeddings",
    headers={
        "Authorization": f"Bearer {HANA_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "model": "text-embedding-3-small",
        "input": f"{input}"
    }
)
  embedding = embedding.json()["data"][0]["embedding"]
  #top_5 = Get_memorys_by_embedding(embedding)
  #contexto = Get_contexto_msgs(limit=10)
  messages = [
    types[type],
    {
        "role": "user",
        "content": f"""
USER_MESSAGE:

{input}

TASK:

Create a {type} memory from USER_MESSAGE.

USER_MESSAGE is the only source of truth.

Do not invent facts.
Do not infer missing information.

Examples:

episodic:
Input: "Consegui Diamante no LoL."
Output:
{{"memory_text":"Pai alcançou o rank Diamante no LoL."}}

state:
Input: "Estou estudando ADS."
Output:
{{"memory_text":"Pai está estudando ADS."}}

personality:
Input: "Gosto de Minecraft."
Output:
{{"memory_text":"Pai gosta de Minecraft."}}

Return ONLY valid JSON.
"""
    }
]
  memoria = Talking_Agent(HANA_KEY, model="gpt-5-nano", messages=messages, completion_tokens=120, AGENTE="FAZEDOR_DE_MEMORIAS")
  print(f"Memoria {type}: {memoria}")
  HIPOCAMPO_file_log("BEGIN", {"NEW_MEMORY": memoria, "TYPE": type, "TIME": datetime.now().isoformat()})
  if memoria['memory_text'] is None:
    Log_Brain("web", "MEMORY_ROUTER", "HALUCINATION", {"memory": "O MEMORY_CLASSIFICATION ALUCINOU"})      
    return "creator_null"
  else:
    memoria['memory_text'] = memoria['memory_text'].lower()
    return memoria

def Fast_Filter_Pre_LLM(memoria, type):
  old_memorias = Get_memorys_embeddings()
  new_embedding = requests.post("https://api.openai.com/v1/embeddings",
    headers={
        "Authorization": f"Bearer {HANA_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "model": "text-embedding-3-small",
        "input": f"{memoria['memory_text']}"
    }
)
  new_embedding = new_embedding.json()["data"][0]["embedding"]
  
  if "pai" not in memoria['memory_text']: 
    HIPOCAMPO_file_log("END_FILTER", {"REASON": "MEMORIA NÃO TEM PAI"})
    return {
      "continue": "not_ok"
    }
  for memoria_old, embedding_old in old_memorias:
    if memoria['memory_text'] == memoria_old:
      HIPOCAMPO_file_log("END_FILTER", {"REASON": "MEMORIA JA EXISTE"})
      return {
        "continue": "not_ok"
      }
    embedding_old = json.loads(embedding_old)
    score = cosine_similarity(embedding_old, new_embedding)
    treshold = 0.90 if type == "episodic" else 0.98
    if score > treshold:
      HIPOCAMPO_file_log("END_FILTER", {"REASON": "NOVA MEMORIA PASSOU DO SCORE DE 0.90"})
      return {
        "continue": "not_ok"
      }

  top_5_old_embeddings = Get_memorys_by_embedding(new_embedding, type)
  return {
    "continue": "ok",
    "old_embeddings": top_5_old_embeddings,
    "new_embedding": new_embedding
  }

def Memoria_associativa(new_memoria, old_memorias, type, mode):
  if len(old_memorias['old_embeddings']) == 0:
    Save_memory(memory=new_memoria['memory_text'], embedding=old_memorias['new_embedding'], type=type)
    HIPOCAMPO_file_log("MEMORIA_AFETIVA_END_PREMATURE", { "status": "SAVED", "reasoning": "new memory detected"})
    if mode == "terminal":
      asyncio.run(Criar_frase(f"Rana criou uma nova memoria {new_memoria['memory_text']}", "audios/new_memory.mp3"))
      playsound("audios/new_memory.mp3")
    elif mode == "telegram":
      requests.post(f"https://api.telegram.org/bot{TELEGRAM_KEY}/sendMessage", 
                     data = {
                         "chat_id": "7866829741",
                         "text": f"Hana criou uma nova memoria {new_memoria['memory_text'].lower()}, entidade {new_memoria['entity']}"
                     })
    return "new"
  system_check_duplicidade = {
    "role": "system",
    "content": """
You are Hana's Hippocampus.

Your task is to compare a NEW MEMORY against semantically similar memories retrieved by the embedding system.

You do NOT evaluate importance.

You do NOT create memories.

You do NOT invent facts.

You only determine the relationship between the new memory and the retrieved memories.

--------------------------------------------------

INPUT

You will receive:

NEW_MEMORY:
(the new memory)

MORE_LIKE_MEMORIES:

(score)
(memory)

(score)
(memory)

(score)
(memory)

(score)
(memory)

(score)
(memory)

--------------------------------------------------

IMPORTANT

The scores were generated by an embedding system.

Higher scores indicate stronger semantic similarity.

Use the scores only as supporting evidence.

Your decision must be based primarily on the meaning of the memories.

--------------------------------------------------

TASK

Determine whether the NEW_MEMORY is:

- already represented by an existing memory
- an updated version of an existing memory
- a contradiction/correction of an existing memory
- a completely different memory

Return exactly ONE action.

--------------------------------------------------

ACTIONS

duplicate

→ The same information is already stored.

→ NEW_MEMORY adds no meaningful information.

--------------------------------------------------

refresh

→ NEW_MEMORY updates or expands an existing memory.

→ The previous memory should be replaced by the new version.

--------------------------------------------------

replace

→ NEW_MEMORY corrects an existing memory.

→ The previous memory should be replaced by the new version.

--------------------------------------------------

new

→ NEW_MEMORY describes something not represented by any retrieved memory.

--------------------------------------------------

OLD MEMORY SELECTION

If action is:

- duplicate
- refresh
- replace

You MUST return the matching memory in:

"old_memory"

The value MUST exactly match one memory from MORE_LIKE_MEMORIES.

Do NOT rewrite it.

Do NOT summarize it.

Copy it exactly.

--------------------------------------------------

If action is:

new

Return:

"old_memory": null

--------------------------------------------------

RULES

- Compare meanings, not wording.
- Similar subjects do NOT automatically mean duplicate.
- Never merge memories.
- Never invent facts.
- Never explain your reasoning.
- old_memory must always be one of the retrieved memories.
- Return exactly one action.

--------------------------------------------------

OUTPUT

Return ONLY valid JSON:

{
    "action": "duplicate | refresh | replace | new",
    "old_memory": "exact memory text" | null,
    "reason": "max 20 chars"
}

"""
}
  messages = [
    system_check_duplicidade,
    {
        "role": "user",
        "content": f"""
NEW_MEMORY:
{new_memoria["memory_text"]}

MORE_LIKE_MEMORIES:

{chr(10).join(
    f"score: {score:.3f}\nmemory: {memory}"
    for score, memory in old_memorias['old_embeddings']
)}
"""
    }
]
  decision = Talking_Agent(HANA_KEY, model="gpt-5-mini", messages=messages, completion_tokens=120, AGENTE="CHECADOR_DE_DUPLICIDADES_EM_MEMORIAS")
  HIPOCAMPO_file_log("MEMORIA_ASSOCIATIVA", {"decision": f"{decision}"})

  if decision['action'].lower() == "new":
    HIPOCAMPO_file_log("NEW_MEMORY", {"new_memory": new_memoria['memory_text']})
    Save_memory(memory=new_memoria['memory_text'], embedding=old_memorias['new_embedding'], type=type)
    if mode == "terminal":
      asyncio.run(Criar_frase(f"Rana criou uma nova memoria {new_memoria['memory_text']} com o tipo {type}", "audios/new_memory.mp3"))
      playsound("audios/new_memory.mp3")
    elif mode == "telegram":
      requests.post(f"https://api.telegram.org/bot{TELEGRAM_KEY}/sendMessage", 
                    data = {
                        "chat_id": "7866829741",
                        "text": f"Hana criou uma nova memoria {new_memoria['memory_text'].lower()}"
                    })
    Memoria_console("NEW", new_memoria['memory_text'])
    return 
  elif decision['action'].lower() == "refresh" or decision['action'].lower() == "replace":
    HIPOCAMPO_file_log("STATUS_REFRESH", {"new_memory": new_memoria['memory_text'], "old_memory": decision['old_memory']})
    Update_memory(new_memory=new_memoria['memory_text'], old_memory=decision['old_memory'], new_embedding=old_memorias['new_embedding'])
    if mode == "terminal":
      asyncio.run(Criar_frase(f"Rana atualizou uma memoria memoria antiga: {decision['old_memory']} nova memoria: {new_memoria['memory_text']}", "audios/refresh_memory.mp3"))
      playsound("audios/refresh_memory.mp3")
    elif mode == "telegram":
      requests.post(f"https://api.telegram.org/bot{TELEGRAM_KEY}/sendMessage", 
                      data = {
                         "chat_id": "7866829741",
                         "text": f"Rana atualizou uma memoria memoria antiga: {decision['old_memory']} nova memoria: {new_memoria['memory_text']}"
                     })
    Memoria_console("REFRESH", new_memoria['memory_text'])
  else:
    HIPOCAMPO_file_log("STATUS_DUPLICATE", {"new_memory": new_memoria['memory_text'], "old_memory": decision['old_memory']})
    return
    
def Memoria_console(status, memoria):
    largura = 60
    inner = largura - 2

    label = "DATA   | "
    wrap_size = inner - len(label)

    wrap_size = max(10, wrap_size)

    linhas = textwrap.wrap(str(memoria), width=wrap_size)

    def line(txt=""):
        txt = str(txt)
        return "║" + txt[:inner].ljust(inner) + "║"

    print("\n╔" + "═" * inner + "╗")
    print(line(f"{status}".center(inner)))
    print("╠" + "═" * inner + "╣")

    if linhas:
        print(line(label + linhas[0]))

        for l in linhas[1:]:
            print(line(" " * len(label) + l))

    print("╚" + "═" * inner + "╝")

def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)