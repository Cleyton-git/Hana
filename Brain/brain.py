import requests, json, threading
from .Personality.personality import Personalidade
from .Memory.memory_system import Get_contexto, Get_memorys_context
from .Tools.is_tool import Tool_router
from dotenv import load_dotenv
from .Tecnico.hana_log import Token_log, Log_Brain, end_interaction_log
from .Memory.hipocampo import Hipocampo

load_dotenv()

def Brain_Hana(interacao, web_text, HANA_KEY, mode):
    Pai = web_text
    
    Log_Brain(interacao, "BEGIN_NEW_INPUT", "INPUT", {"input": Pai})
    is_tool = Tool_Brain(mode, Pai, HANA_KEY, interacao)
    Log_Brain(interacao, "TOOL_ROUTER", "IS_TOOL?", {"tool": is_tool})
    if is_tool == "yes":
        end_interaction_log("Logs/hana_brain.jsonl")
        return {
                "prompt": 'dont have',
                "memory": 'dont have',
                "tool": 'yes'
            }

    entity = Entity_Brain(Pai, HANA_KEY)
    Log_Brain(interacao, "ENTITY", "ENTITY_DETECTOR", {"entity": entity['entities']})
    
    is_memory = Memory_Brain(Pai, HANA_KEY, mode)
    Log_Brain(interacao, "MEMORY_ROUTER", "IS_MEMORY?", {"memory": is_memory})

    Hana = Making_Hana(Pai, interacao, entity, HANA_KEY)
    
    return {
        "prompt": Hana,
        "memory": is_memory,
        "tool": is_tool
    }

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

def Tool_Brain(mode, Pai, HANA_KEY, interacao):
    if mode != "telegram":
        is_tool = Tool_router(Pai, HANA_KEY, interacao)
        if is_tool != "not":   
            return "yes"
    return "not"

def Memory_Brain(Pai, HANA_KEY, mode):
    system_memory_detector = {
    "role": "system",
    "content": """
You are Hana's Memory Detector.

Your only task is to decide whether a user message contains information worth storing as long-term memory.

A message IS a memory if it reveals:

- a personal fact
- a preference
- a habit
- a goal
- a relationship
- an important life event
- a stable long-term project
- a long-term interest

Examples of memories:

"I have a dog named Bilu."
"I love Minecraft."
"I'm studying C programming."
"I'm building an AI called Hana."
"I want to become a software engineer."

Examples that are NOT memories:

"Hi Hana."
"How are you?"
"Thanks."
"Can you help me?"
"What is a pointer in C?"
"Good night."
"Tell me a joke."

Messages that only continue a conversation are NOT memories.

If the message explicitly asks to save or remember something:

- save this
- remember this
- guarda isso
- lembra disso
- salva essa memória

Return memory=true.

OUTPUT

Return ONLY:

Return ONLY a valid JSON object.

{"memory": true}

or

{"memory": false}
"""
}
    messages = [system_memory_detector, {"role": "user", "content": Pai}]
    memory_judge = requests.post("https://api.openai.com/v1/chat/completions",
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
    memory_judge = memory_judge.json()
    usage = memory_judge['usage']
    Token_log(model="gpt-5-nano", usage=usage, func="MEMORY_DETECTOR")
    memory_judge = json.loads(memory_judge['choices'][0]["message"]["content"])
    
    if memory_judge['memory'] == True:
        system_making_context = {
    "role": "system",
    "content": """
You are Hana's Context Summarizer.

Your task is to compress conversation history into the smallest possible amount of useful context for another AI system.

Rules:
- Do not answer the user.
- Do not generate memories.
- Do not invent information.
- Do not describe the conversation.
- Do not describe participants or their behavior.
- Ignore greetings, filler, confirmations, and small talk.
- Focus only on topics, goals, projects, decisions, problems, progress, and relevant entities.
- Preserve information that may be important for future reasoning.

Output:
Return only a plain-text summary.

Requirements:
- Maximum 80 words.
- No markdown.
- No bullet points.
- No explanations.
- No labels.
- No meta commentary.
- Write as condensed context, not as a conversation summary.
- Do not mention users, assistants, or participants.
- Describe the project, problem, or topic directly.

Good:
"Hana API integration involving payload validation, endpoint testing, channel-based routing, and message organization. Architecture includes general, logs, and commands channels with routing rules for directing messages to the appropriate module."

Bad:
"The user and Hana discussed API integration. Hana confirmed availability and suggested..."
"""
}
        Contexto = Get_contexto()
        context_text = "\n".join(
          str(msg.get("content", ""))
          for msg in Contexto[-16:]
        )
        messages = [system_making_context, {"role": "user", "content": context_text}]
        contexto = requests.post("https://api.openai.com/v1/chat/completions",
                                headers = {"Authorization": f"Bearer {HANA_KEY}",
                                            "Content-Type": "application/json"
                                            },
                            json={
                                "model": "gpt-5-nano",
                                "messages": messages,
                                "max_completion_tokens": 200,
                                "reasoning_effort": "minimal"},
                            )
        contexto_json = contexto.json()
        usage = contexto_json['usage']
        Token_log(model="gpt-5-nano", usage=usage, func="CONTEXTO_MEMORY")
        contexto_response = contexto_json['choices'][0]["message"]["content"]
        
        system_hipocampo = {
    "role": "system",
    "content": """
You are Hana's Hippocampus.

You receive:

1. The current user message.
2. A conversation context.

The context may contain:

[USER_MESSAGE]
[ASSISTANT_MESSAGE]
[TOOL_EVENT]

Analyze the entire context and create ONE useful long-term memory.

IMPORTANT

The current message is not necessarily the memory.

Messages such as:

- save this memory
- remember this
- guarda isso
- salva essa memória

are only memory triggers.

When a trigger appears, determine what should be remembered from the conversation context.

CONTEXT RULES

[USER_MESSAGE]
Contains what the user said.

[ASSISTANT_MESSAGE]
Contains Hana's responses.

[TOOL_EVENT]
Contains actions executed by Hana or the system.

Prioritize information found in USER_MESSAGE.

Use ASSISTANT_MESSAGE and TOOL_EVENT only as supporting context.

Do NOT create memories from TOOL_EVENT unless the event reveals a stable and important fact about the user.

MEMORY CREATION

Think about the entire conversation.

Ask:

"What information from this conversation would still be useful weeks or months later?"

Prefer:

- personal facts
- preferences
- interests
- habits
- goals
- relationships
- ongoing projects
- achievements
- important events
- stable information

Ignore:

- memory requests
- greetings
- commands
- temporary tasks
- filler conversation
- tool execution logs

MEMORY TEXT

- Extract only the core fact.
- Write in clean Portuguese.
- Do not mention the conversation.
- Do not mention memory requests.
- Do not quote the user.
- Always start with:

"O usuário"

ENTITY

- Return one main entity.
- Prefer specific names.
- Keep it short.
- Never use "Usuário" as the entity unless absolutely necessary.

IMPORTANCE

10 = identity, family, core relationships
7-9 = major life events
4-6 = projects, goals, interests, preferences
1-3 = minor details

OUTPUT

{
  "memory_text": "O usuário ...",
  "entity": "Hana",
  "importance": 6
}

Return ONLY valid JSON.
"""
}
        messages = [system_hipocampo, {"role": "user", "content": f"""
                                       CURRENT MESSAGE:
                                       {Pai}
                                       
                                       Context:
                                       {contexto_response}""",}]
        memory = requests.post("https://api.openai.com/v1/chat/completions",
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
        memory = memory.json()
        usage = memory['usage']
        Token_log(model="gpt-5-nano", usage=usage, func="HIPOCAMPO")
        memory = memory['choices'][0]["message"]["content"]
        memory = json.loads(memory)
        threading.Thread(
            target=Hipocampo,
            args=(memory, mode)
        ).start()
        return "yes"
    else:
        return "not"

def Making_Hana(Pai, interacao, entity, HANA_KEY):
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
    Hana_memorias_contextuais = Get_memorys_context(entity['entities'])
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

