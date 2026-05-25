import requests
from collections import Counter
from Brain.Memory.memory_system import Save_memory, Get_memorys_category, Get_memorys_ids, Update_memory
import numpy as np
import json, textwrap
from ..Mouth.mouth import Mouth_Hana, Ia_duplicy_verification
import textwrap
from ..Tecnico.hana_log import HIPOCAMPO_file_log
from datetime import datetime


def Hipocampo(msg, model):
    HIPOCAMPO_file_log("INPUT", {"input": msg})
    system_hipocampo = {
"role": "system",
"content": """
Você é o HIPOCAMPO.

Você transforma texto em memória factual limpa.

==================================================
REGRA PRINCIPAL
==================================================

Você NÃO copia a frase do usuário.

Você EXTRAI apenas o fato central.

==================================================
PROCESSO OBRIGATÓRIO
==================================================

1. Ignorar completamente comandos:
   "salva isso", "lembra disso", "guarda isso", "filha", "pai"

2. Identificar o fato real da frase

3. Reescrever o fato de forma neutra e corrigida

4. Prefixar sempre com:
   "O usuário"

==================================================
REGRA CRÍTICA

- NÃO repetir palavras do usuário literalmente se estiverem mal estruturadas
- NÃO manter erros de português que atrapalhem sentido
- NÃO incluir comandos ou vocativos (pai, filha, etc)
- NÃO incluir a frase original

==================================================
EXEMPLO CORRETO

Input:
"Hana, o Pelé morreu no dia 29/12/2022, salva isso filha"

Output:
{
  "memory": "O usuário informou que Pelé morreu no dia 29/12/2022",
  "importance": 7
}

==================================================
IMPORTANCE

9-10 → identidade / relações centrais
7-8 → eventos importantes
4-6 → preferências / hobbies
1-3 → detalhes leves

Se dúvida → 5

==================================================
FORMATO FINAL

{
  "memory": "string",
  "importance": number
}

==================================================
REGRA FINAL

- somente JSON
- sem explicações
- sem recusa
"""
}
    r = requests.post(
      "http://127.0.0.1:11434/api/chat",
      json={
        "model": model,
        "messages": [system_hipocampo, {"role": "user", "content": msg}],
        "temperature": 0,
        "stream": False,
        "response_format": {
         "type": "json_object"
        }
      }
    )

    data = r.json()
    content = data["message"]["content"]
    cleaned = (content.replace("```json", "").replace("```", "").strip())
    try:
      HIPOCAMPO_file_log("BEGIN", {"TIME": datetime.now()})
      start = cleaned.index("{")
      end = cleaned.rindex("}") + 1
      memory_data = json.loads(cleaned[start:end])
      HIPOCAMPO_file_log("OUTPUT_LLM", {"memory": memory_data["memory"],
                                 "importance": memory_data["importance"]})
      if memory_data["memory"]:
        cortex_orbito_frontal_resp = Cortex_Orbitofrontal(memory_data)
        HIPOCAMPO_file_log("CORTEX_ORBITO_FRONTAL", {"memory": memory_data["memory"],
                              "valid": cortex_orbito_frontal_resp})
        if cortex_orbito_frontal_resp:
          reconsolidacao_resp = Reconsolidacao(memory_data)
          HIPOCAMPO_file_log("RECONSOLIDATION", {"action": reconsolidacao_resp,
                                            "status": "running"})
          if reconsolidacao_resp == "new":
            Memoria_console("NEW", memory_data['memory'])
            return
          elif reconsolidacao_resp == "refresh":
            Memoria_console("REFRESH", memory_data['memory'])
          elif reconsolidacao_resp == "ignore":
            Memoria_console("IGNORE", memory_data['memory'])
      else:
        pass
    except Exception as e:
      HIPOCAMPO_file_log("END_PREMATURE", {"REASON": cleaned})
      return
  
def Cortex_Orbitofrontal(memoria):
  if not isinstance(memoria.get("importance"), int):
    return False
  if "O usuário" not in memoria['memory']:
    return False
  return True

def Reconsolidacao(memoria):
  memorias = [mem[1] for mem in Get_memorys_ids()]
  for c in memorias:
    if memoria['memory'] == c:
      return "ignore"
  ids_memorias = Get_memorys_ids()
  response = Memoria_associativa(memoria, ids_memorias)
  if response == "new":
    return "new"
  elif response == "refresh":
    return "refresh"
  elif response == "ignore":
    return "ignore"
  return "ignore"

def Memoria_associativa(new_memoria, old_memorias):
  candidatos = []
  system = {
  "role": "system",
  "content": """
Você é o HIPOCAMPO de um sistema de memória de uma IA.

Sua função é comparar duas memórias e decidir a relação semântica entre elas.

Você NÃO deve julgar relevância geral.
Você NÃO deve filosofar.
Você NÃO deve recusar casos ambíguos.
Você deve apenas classificar a relação entre memory_a e memory_b.

---

MEMÓRIAS:

- memory_a = memória existente no banco
- memory_b = nova memória a ser avaliada

---

TAREFA:

Classifique a relação entre as duas memórias usando APENAS UMA ação final.

---

SAÍDA OBRIGATÓRIA (JSON):

{
  "action": "duplicate | refresh | new | replace",
  "merged_memory": "string"
}

---

DEFINIÇÕES DAS AÇÕES:

1. duplicate
→ Mesma informação, sem valor adicional
→ memory_b não adiciona nada novo

2. refresh
→ Mesma ideia central, mas memory_b adiciona informação útil
→ Deve gerar merged_memory atualizado

3. new
→ Fatos diferentes ou não relacionados semanticamente
→ Não existe relação direta entre memory_a e memory_b

4. replace
→ memory_b contradiz memory_a ou substitui completamente a informação anterior
(ex: opinião mudou, gosto mudou, estado mudou)

---

REGRAS IMPORTANTES:

- Nunca retorne mais de uma action
- Nunca invente fatos
- merged_memory só deve existir quando fizer sentido (refresh ou replace)
- Seja consistente e determinístico
- Se houver dúvida entre duplicate e refresh, prefira refresh
- Se houver contradição clara, use replace
- Se não houver relação clara, use new

---

EXEMPLOS:

A: "O usuário gosta de beber água"
B: "O usuário bebe bastante água ao longo do dia"

→ {
  "action": "refresh",
  "merged_memory": "O usuário gosta de beber água e costuma beber bastante água ao longo do dia"
}

---

A: "O usuário gosta de beber água"
B: "O usuário não gosta de beber água"

→ {
  "action": "replace",
  "merged_memory": "O usuário não gosta de beber água"
}

---

A: "O usuário tem um cachorro chamado Bilu"
B: "O usuário gosta de jogar videogame"

→ {
  "action": "new",
  "merged_memory": ""
}

---

A: "O usuário gosta de água"
B: "O usuário gosta de água"

→ {
  "action": "duplicate",
  "merged_memory": ""
}

---

Responda APENAS com JSON válido.
"""
}
  emb1_new = requests.post(
      "http://localhost:11434/api/embeddings",
      json={
          "model": "nomic-embed-text",
          "prompt": new_memoria['memory']
    }
  ).json()['embedding']
  for mem_id, mem_old, mem_embe in old_memorias:
    mem_embe = json.loads(mem_embe)
    score = cosine(emb1_new, mem_embe)
    if score > 0.70:
      candidatos.append({"id": mem_id,"memory": mem_old,"score": score})
      
  candidatos.sort(key=lambda x: x["score"], reverse=True)
  if len(candidatos) == 0:
    Save_memory(memory=new_memoria['memory'], importance=new_memoria['importance'], embedding=emb1_new)
    return "new"
  top = candidatos[:3]
  
  decisions = []
  for candidate in top:
    msg = [
      system,
      {
          "role": "user",
          "content": json.dumps({
              "memory_a": candidate['memory'],
              "memory_b": new_memoria['memory']
          })
        }
    ]
    decision = Ia_duplicy_verification(msg=msg, model="llama3.1:8b")
    decisions.append({
      "candidate": candidate,
      "decision": decision
    })
    HIPOCAMPO_file_log("ASSOCIATIVE", {"candidates": len(candidatos), "decision": decisions})
    
  
  for item in decisions:
    candidate = item['candidate']
    action = item["decision"]["action"]
    
    if action == "refresh":
      Update_memory(candidate['id'], new_memoria['memory'], new_memoria['importance'], embedding=emb1_new)
      return "refresh"
  
  for item in decisions:
    candidate = item['candidate']
    action = item["decision"]["action"]
    
    if action == "replace":
      Update_memory(candidate['id'], new_memoria['memory'], new_memoria['importance'], embedding=emb1_new)
      return "refresh"
  
  for item in decisions:
    candidate = item['candidate']
    action = item["decision"]["action"]
    if action == "new":
      Save_memory(memory=new_memoria['memory'], importance=new_memoria['importance'], embedding=emb1_new)
      return "new"
  
  for item in decisions:
    candidate = item['candidate']
    action = item["decision"]["action"]
    if action == "duplicate":
      return "ignore"
    
def cosine(a, b):
    a = np.array(a)
    b = np.array(b)

    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

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
