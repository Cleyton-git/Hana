import requests, json, threading, asyncio
from .Personality.personality import Personalidade
from .Memory.memory_system import Get_contexto_msgs, Get_memorys_context, Get_personality_father, Add_personality, Update_personality, Get_embeddings_personality_father, Get_memorys_by_embedding
from .Tools.is_tool import Tool_router
from .Tecnico.hana_log import Token_log, Log_Brain, end_interaction_log
from .Memory.hipocampo import Hipocampo
import numpy as np
from .Agents.agent_requests import Talking_Agent
from playsound3 import playsound
from .Mouth.mouth import Criar_frase


def Brain_Hana(interacao, web_text, HANA_KEY, mode):
    Pai = web_text
    Log_Brain(interacao, "BEGIN_NEW_INPUT", "INPUT", {"input": Pai})
    
    #is_tool = Tool_Brain(mode, Pai, HANA_KEY, interacao)
    #Log_Brain(interacao, "TOOL_ROUTER", "IS_TOOL?", {"tool": is_tool})
    #if is_tool == "yes":
    #    end_interaction_log("Logs/hana_brain.jsonl")
    #    return {
    #            "prompt": 'dont have',
    #            "memory": 'dont have',
    #            "tool": 'yes',
    #            "entity": "not"
    #        }

    embedding = requests.post("https://api.openai.com/v1/embeddings",
    headers={
        "Authorization": f"Bearer {HANA_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "model": "text-embedding-3-small",
        "input": f"{Pai}"
    }
    )
    embedding = embedding.json()["data"][0]["embedding"]
    Hana = Making_Hana(Pai, interacao, embedding)
    
    threading.Thread(target=Memory_Brain,
                    args=(Pai, HANA_KEY, mode)).start()

    return {
        "prompt": Hana,
        "tool": "em manutenção kk",
    }

def Tool_Brain(mode, Pai, HANA_KEY, interacao):
    if mode != "telegram":
        is_tool = Tool_router(Pai, HANA_KEY, interacao)
        if is_tool != "not":   
            return "yes"
    return "not"

def Father_Brain(Pai, HANA_KEY):
    personalidade_pai = Get_personality_father() 
    contexto = Get_contexto_msgs(limit=10)
    messages = [
    system_personality_extractor,
    {
        "role": "user",
        "content": f"""
Recent conversation:

{contexto}

Current message:

Pai: {Pai}

Task:

Extract ONE explicit long-term trait about Pai.

Use the conversation only to resolve references in the current message.

Examples:
- "it"
- "that"
- "my favorite one"
- "yes, I like it"

Do NOT extract traits from the conversation itself.

Return null if the current message does not explicitly reveal a stable trait.
"""
    }
]
    response_extractor = Talking_Agent(HANA_KEY, model="gpt-5-mini", messages=messages, completion_tokens=120, AGENTE="PERSONALITY_EXTRACTOR")
    
    if response_extractor['fact'] == None:
        Log_Brain("web", "PERSONALITY", "IS_PERSONALITY?", {"SEM FATO NOVO": response_extractor['fact']})
        return
    else:
        embedding = requests.post("https://api.openai.com/v1/embeddings",
        headers={
            "Authorization": f"Bearer {HANA_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "text-embedding-3-small",
            "input": f"{response_extractor['fact']}"
        }
    )
        embedding = embedding.json()["data"][0]["embedding"]
        decision = Filter_pre_LLM(response_extractor['fact'], personalidade_pai, embedding)
        Log_Brain("web", "PERSONALITY", "IS_PERSONALITY?", {"NOVO FATO": response_extractor['fact']})
        if decision == "already_exists":
            Log_Brain("web", "PERSONALITY", "FILTER", {"JA EXISTIA": response_extractor['fact']})
            return
        else:
            system_personality_manager = {
    "role": "system",
    "content": """
You are Hana's Identity Manager.

Input:
- New Fact
- Top similar existing facts

The existing facts were selected using semantic similarity search.

Each fact may include a similarity score.

Higher scores usually indicate a closer semantic match, but the score is only a hint.

Always compare meanings yourself.

Decision rules:

- Same meaning -> IGNORE
- Paraphrase -> IGNORE
- More specific or less specific version of the same fact -> IGNORE
- Contradiction -> UPDATE
- Genuinely new information -> ADD

Use the most relevant matching fact when deciding UPDATE or IGNORE.

Never create facts.
Never rewrite facts.
Never use the similarity score as the only reason for a decision.

Return only JSON.

ADD
{
  "action": "ADD"
}

UPDATE
{
  "action": "UPDATE",
  "old_fact": "...",
  "fact": "..."
}

IGNORE
{
  "action": "IGNORE"
}
"""
}
            messages = [
    system_personality_manager,
    {
        "role": "user",
        "content": f"""
Top 5 most semantically similar facts to the new fact:

{chr(10).join(
    f"- [{score:.3f}] {fact}"
    for score, fact in decision["top_5"]
)}

New fact:

{response_extractor['fact']}
"""
    }
]
            print(messages)
            response_manager = Talking_Agent(HANA_KEY, model="gpt-5-nano", messages=messages, completion_tokens=120, AGENTE="PERSONALITY_MANAGER")
            Log_Brain("web", "PERSONALITY", "MANAGER", {"decision": response_manager['action']})
            
            if response_manager['action'] == "ADD":
                asyncio.run(Criar_frase(f"Rana detectou um novo traço de personalidade {response_extractor['fact']}", "audios/new_fact.mp3"))
                playsound("audios/new_fact.mp3")
                Add_personality(response_extractor['fact'], embedding)
                return
            elif response_manager['action'] == "UPDATE":
                asyncio.run(Criar_frase(f"Rana detectou uma atualização na personalidade do Pai. Novo fato {response_extractor['fact']}. Antigo fato: {response_manager['old_fact']} ", "audios/refresh_fact.mp3"))
                playsound("audios/refresh_fact.mp3")
                Update_personality(response_manager['old_fact'], response_extractor['fact'], embedding)
                return
            elif response_manager['action'] == "IGNORE":
                return 
            else:
                return 

def Filter_pre_LLM(fato_novo, personalidade_pai, novo_embedding):
    lista_fatos = []
    embeddings_atuais = Get_embeddings_personality_father()
    if fato_novo in personalidade_pai:
        return "already_exists"
    for (fact, embedding_atual) in embeddings_atuais:
        embedding_atual = json.loads(embedding_atual)
        score = np.dot(novo_embedding, embedding_atual) / ( np.linalg.norm(novo_embedding) * np.linalg.norm(embedding_atual))
        lista_fatos.append((score, fact))
        if score >= 0.92:
            return "already_exists"
    lista_fatos.sort(reverse=True)
    top_5 = lista_fatos[:5]
    return {"decision": "llm_decision", "top_5": top_5}
            
def Entity_Brain(Pai, HANA_KEY):
    system_entity_extractor = {
"role": "system",
"content": """
You are Hana's ENTITY EXTRACTOR.

Identify ALL meaningful entities in the user message.

Entities can be:
- people
- characters
- animals
- places
- brands
- games
- books
- movies
- music artists
- series
- technologies
- concepts

Rules:
- Ignore stopwords and filler words
- Ignore grammatical fragments
- Remove duplicates
- Keep the order of importance

If an entity is uncertain, omit it.

Do not generate placeholders such as:
- unknown
- hmm
- hmm?
- maybe
- something

When multiple known entities appear consecutively,
return them separately.

Output:

{
  "entities": ["entity1", "entity2"]
}

Return ONLY valid JSON.
"""
}
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
    return entity

def Memory_Brain(Pai, HANA_KEY, mode):
    system_memory_router = {
    "role": "system",
    "content": """
You are Hana's Memory Router.

Your only job is to decide whether the message contains any memory worth processing.

You are NOT a classifier.

You do NOT identify memory types.

--------------------------------------------------

Return ONLY valid JSON:

{
    "store_memory": true | false
}

--------------------------------------------------

STORE MEMORY

Return:

{
    "store_memory": true
}

if the message contains ANY of the following:

- a personal preference
- a personal interest
- a hobby
- a dislike
- a long-term goal
- a personality trait
- a skill being learned

OR

- a personal state
- a possession
- a relationship
- a role
- an ongoing situation

OR

- a specific event
- an achievement
- a milestone
- something that happened

--------------------------------------------------

EXAMPLES

Input:
"I like Minecraft."

Output:
{
    "store_memory": true
}

Input:
"I am learning English."

Output:
{
    "store_memory": true
}

Input:
"I have a dog named Bilu."

Output:
{
    "store_memory": true
}

Input:
"I reached Diamond in LoL."

Output:
{
    "store_memory": true
}

Input:
"I adopted a dog."

Output:
{
    "store_memory": true
}

Input:
"I want to become a programmer."

Output:
{
    "store_memory": true
}

--------------------------------------------------

DO NOT STORE

Return:

{
    "store_memory": false
}

for:

- greetings
- questions
- casual conversation
- temporary conditions
- reactions
- low-information messages

--------------------------------------------------

EXAMPLES

Input:
"Good morning."

Output:
{
    "store_memory": false
}

Input:
"I am tired."

Output:
{
    "store_memory": false
}

Input:
"I ate lunch."

Output:
{
    "store_memory": false
}

Input:
"What is a pointer in C?"

Output:
{
    "store_memory": false
}

Input:
"Cool."

Output:
{
    "store_memory": false
}

Input:
"Haha."

Output:
{
    "store_memory": false
}

--------------------------------------------------

RULES

- Do not classify memory types.
- Do not create facts.
- Do not rewrite the input.
- Do not infer missing information.
- Be permissive.
- If there is reasonable memory value, return true.

Return ONLY valid JSON.
"""
}
    messages = [system_memory_router, {"role": "user", "content": Pai}]
    memory_judge = Talking_Agent(HANA_KEY, model="gpt-5-nano", messages=messages, completion_tokens=120, AGENTE="MEMORY_JUDGE")
    Log_Brain("web", "MEMORY_ROUTER", "IS_MEMORY?", {"memory": "yes"})
    if memory_judge['store_memory'] == True:
        system_memory_classifier = {
    "role": "system",
    "content": """
You are Hana's Memory Classifier.

The message was already considered potentially memorable.

Your only job is to detect which memory types are present.

Return ONLY valid JSON.

--------------------------------------------------

VALID OUTPUTS

{
    "type": []
}

{
    "type": ["episodic"]
}

{
    "type": ["state"]
}

{
    "type": ["personality"]
}

{
    "type": ["episodic","state"]
}

{
    "type": ["episodic","personality"]
}

{
    "type": ["state","personality"]
}

{
    "type": ["episodic","state","personality"]
}

--------------------------------------------------

MEMORY TYPES

EPISODIC

A specific event, action, achievement,
milestone, or occurrence that happened
at a particular moment.

Examples:

- Pai killed the Wither
- Pai got hired
- Pai adopted a dog
- Pai graduated
- Pai reached Diamond in LoL
- Pai finished the community center
- Pai bought a new computer

--------------------------------------------------

STATE

A current condition, status, role,
relationship, possession, progression,
or ongoing situation.

Examples:

- Pai is studying ADS
- Pai owns a dog named Bilu
- Pai is employed
- Pai is married
- Pai is learning C
- Pai is Diamond in LoL
- Pai is in the third semester

--------------------------------------------------

PERSONALITY

A stable preference, interest, hobby,
value, long-term goal, like, dislike,
or personality trait.

Examples:

- Pai likes Minecraft
- Pai likes Coraline
- Pai enjoys chess
- Pai prefers PCs
- Pai is competitive
- Pai wants to become a programmer
- Pai is learning English

--------------------------------------------------

FAILSAFE RULE

If the message does not clearly contain
any episodic, state, or personality memory:

{
    "type": []
}

Do NOT force a classification.

When uncertain, return:

{
    "type": []
}

--------------------------------------------------

EXAMPLES

Input:
"Bom dia Haninha"

Output:
{
    "type": []
}

Input:
"kkkk"

Output:
{
    "type": []
}

Input:
"Que legal"

Output:
{
    "type": []
}

Input:
"O que é um ponteiro em C?"

Output:
{
    "type": []
}

Input:
"Eu gosto de Minecraft"

Output:
{
    "type": ["personality"]
}

Input:
"Consegui Diamante no LoL"

Output:
{
    "type": ["episodic","state"]
}

Input:
"Adotei um cachorro chamado Bilu"

Output:
{
    "type": ["episodic","state"]
}

Input:
"Estou aprendendo inglês"

Output:
{
    "type": ["state","personality"]
}

--------------------------------------------------

RULES

- A message may contain multiple memory types
- Detect all memory types present
- Do not create facts
- Do not rewrite the input
- Do not infer missing information
- Do not merge memories
- Do not deduplicate memories
- Do not force a memory type
- If no valid memory exists, return:
  {"type":[]}

--------------------------------------------------

Return ONLY valid JSON.
"""
}
        messages = [system_memory_classifier, {"role": "user", "content": f"""PAI MESSAGE: 
                                           - {Pai}"""}]
        memory_classification = Talking_Agent(HANA_KEY, model="gpt-5-mini", messages=messages, completion_tokens=120, AGENTE="MEMORY_CLASSIFICATOR")
        if memory_classification['type']:
            Hipocampo(Pai, memory_classification['type'], mode)
        else:
            Log_Brain("web", "MEMORY_ROUTER", "HALUCINATION", {"memory": "O MEMORY_JUDGE ALUCINOU"})      
    else:
        Log_Brain("web", "MEMORY_ROUTER", "IS_MEMORY?", {"memory": "not"})
        return
    
def Making_Hana(Pai, interacao, embedding):
    Hana_personalidade = Personalidade()
    Hana_Contexto = Get_contexto_msgs(limit=20)
    Hana_memorias_contextuais = Get_memorys_by_embedding(embedding)
    Hana_memorias_contextuais = "\n".join(
        f"- {memoria}"
        for _, memoria in Hana_memorias_contextuais
    )
    Pai_personalidade = Get_personality_father()
    
    Log_Brain(interacao, "Memorias contextuais", "Memorias contextuais enviadas", {"Memorias": [Hana_memorias_contextuais]})
    Log_Brain(interacao, "Contexto", "Contexto enviado", {"Contexto": Hana_Contexto})
    Log_Brain(interacao, "Personalidade_pai", "PERSONALIDADE enviada", {"Personalidade": [Pai_personalidade]})
    
    Hana = [
    {
        "role": "system",
        "content": f"""
### PERSONALIDADE DA HANA
{Hana_personalidade}
"""
    },
    {
        "role": "system",
        "content": f"""
### PERSONALIDADE DO PAI
{Pai_personalidade}
"""
    },
    {
        "role": "system",
        "content": f"""
### MEMÓRIAS
{Hana_memorias_contextuais}
"""
    },
    {
        "role": "system",
        "content": f"""
### CONTEXTO_ATUAL - ULTIMAS 20 MENSAGENS
{Hana_Contexto}
"""
    }
]
    Hana.append({"role": "user", "content": Pai})
    return Hana

