import re, threading, requests, json
from datetime import datetime
from .Mouth.mouth import Mouth_Hana
from .Memory.Hana_itself.personality import Personalidade
from .Memory.memory_system import Get_memorys, Get_contexto, Save_message, Get_memorys_context
from .Memory.hipocampo import Hipocampo
from .Tecnico.hana_log import Hana_console, Hana_log
from .Ears.ouvidos import Fala_Pai
import traceback


system_brain = {
  "role": "system",
  "content": """
Você é o CÉREBRO DECISOR da IA Hana.

Sua função é analisar a mensagem do usuário e definir o comportamento interno do sistema.

Você NÃO conversa.
Você NÃO responde ao usuário.
Você APENAS retorna um JSON de controle.

---

SUA FUNÇÃO:

1. Detectar se há informação relevante para memória
2. Definir o modo de fala da Hana
3. Definir nível de silêncio (pausa/interrupção)
4. Definir nível de engajamento social da resposta

---

MEMÓRIA (memory):

- true → fatos pessoais, preferências, hábitos, projetos, objetivos
- false → conversas casuais ou comandos momentâneos

---

SPEECH MODE (speech_mode):

- "normal" → resposta completa e natural
- "minimal" → resposta curta e direta
- "silent" → não gerar resposta verbal (apenas processa memória)

---

SILENCE LEVEL (silence_level):

Número entre 0.0 e 1.0 indicando pedido de pausa:

- 0.0 → sem pausa
- 0.3 → leve pausa
- 0.6 → pausa moderada
- 0.8 → quase silêncio
- 1.0 → silêncio total

Use quando o usuário pedir:
"pera", "me dá um minuto", "me deixa pensar", "fica quieta", ou similares.

---

ENGAGEMENT (engagement):

Número entre 0.0 e 1.0 indicando nível de presença social da resposta:

- 0.0 → neutro / robótico
- 0.3 → leve interação
- 0.6 → conversa normal
- 1.0 → altamente humano / próximo

Use baseado no contexto emocional e social da mensagem.

---

REGRAS IMPORTANTES:

- O usuário sempre pode falar com a Hana
- speech_mode nunca impede processamento de memória
- silence_level pode reduzir ou bloquear resposta verbal
- engagement ajusta apenas o estilo da resposta
- nunca invente campos fora dos definidos
- seja consistente e determinístico

---

EXEMPLOS:

Usuário: "Oi Hana"
{
  "memory": false,
  "speech_mode": "normal",
  "silence_level": 0.0,
  "engagement": 0.6
}

---

Usuário: "Hana, gosto de chocolate"
{
  "memory": true,
  "speech_mode": "normal",
  "silence_level": 0.0,
  "engagement": 0.7
}

---

Usuário: "pera um pouco preciso pensar"
{
  "memory": false,
  "speech_mode": "minimal",
  "silence_level": 0.6,
  "engagement": 0.3
}

---

Usuário: "Hana, fica quieta"
{
  "memory": false,
  "speech_mode": "silent",
  "silence_level": 1.0,
  "engagement": 0.1
}

---

SAÍDA OBRIGATÓRIA:

{
  "memory": true | false,
  "speech_mode": "normal" | "minimal" | "silent",
  "silence_level": 0.0 a 1.0,
  "engagement": 0.0 a 1.0
}

---

REGRAS FINAIS:

- Responda APENAS JSON válido
- Nenhum texto fora do JSON
- Nenhuma explicação
"""
}

def Brain_Hana():
    #Pai = Fala_Pai()
    Pai = input("USER -> ")
    Hana_console("LOG -> A Hana ouviu...")
    
    messages = [system_brain, {"role": "user", "content": Pai}]
    decision = Tomada_De_Decisao("http://127.0.0.1:11434/api/chat", messages, "qwen2.5:3b")
    
    embe_input = requests.post(
    "http://localhost:11434/api/embeddings",
    json={
        "model": "nomic-embed-text",
        "prompt": Pai
    }
    ).json()['embedding']
    Hana_personalidade = Personalidade()
    Contexto = Get_contexto()
    memorias_contextuais_Hana = Get_memorys_context(embe_input)
    Comportamento_Hana = []

    Hana_log(f"\nCOMEÇO DE NOVOS LOG -> {datetime.now()}")
    Hana_log(decision)
    
    if decision["speech_mode"] == "minimal":
        Hana_log(f"O speech_mode foi {decision["speech_mode"]} A Hana vai falar de forma curta e direta")
        Comportamento_Hana.append("\nResponda de forma curta e direta")
    elif decision["speech_mode"] == "normal":
        Hana_log(f"O speech_mode foi {decision["speech_mode"]} A Hana vai falar de natural e com personalidade")
        Comportamento_Hana.append("\nResponda naturalmente com personalidade.")
        
    if decision["engagement"] >= 0.8:
        Hana_log(f"O speech_mode foi {decision["speech_mode"]} A Hana vai falar de forma carinhosa")
        Comportamento_Hana.append("\nResponda de forma mais carinhosa e próxima do usuário.")
    elif decision["engagement"] >= 0.5:
        Comportamento_Hana.append("\nFale de forma amigável e natural.")
    elif decision["engagement"] >= 0.2:
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
            "content": memorias_contextuais_Hana
        },
        {
            "role": "system",
            "content": "\n".join(Comportamento_Hana)
        }
    ]
    Hana.extend(Contexto[-4:])
    Hana.append({"role": "user", "content": Pai})
    
    try:        
        resposta = Mouth_Hana("http://127.0.0.1:11434/api/chat", Hana, model="qwen2.5:3b")
        if resposta:
            print("🤖 HANA -> ", resposta)
            Save_message(role="user", content=Pai) # Salva a msg no BD como sendo o ''user''
            Save_message(role="assistant", content=resposta) # Salva a msg da IA agr
    except Exception as e:
        traceback.print_exc()
        print("error log -> ", e)
            
    if decision['memory']:
        chunks = re.split(r",| e |\.|\n", Pai)
        for c in chunks:
            if len(c) > 15:
                Hana_log(f"A memoria {c} vai entrar no hipocampo da Hana...")
                threading.Thread(
                    target=Hipocampo,
                    args=(c, "llama3.1:8b")
                ).start()
                # No futuro, vou adicionar o embeding nisso e comparar com os embedings do bd, se der um resultado mto baixo vale a tentativa mandar pro bd, se for mto alto descarta, se for algo em torno de 0.70/0.80 envia, pode ser refresh, porém isso é so no futuro

def Tomada_De_Decisao(url, msg, model):
    decision = requests.post(
        url,
        json={
            "model": model,
            "messages": msg,
            "stream": False
        }
    )
    print(decision)
    return
    
    return decision.json()["message"]["content"]
