import requests, json, textwrap
from Brain.Memory.memory_system import Save_memory, Get_memorys_ids, Update_memory, Get_memorys_by_type
import numpy as np
from ..Tecnico.hana_log import HIPOCAMPO_file_log, end_interaction_log
from ..Mouth.mouth import Ia_duplicy_verification
from datetime import datetime

def Hipocampo(memoria):
    HIPOCAMPO_file_log("BEGIN", {"NEW_MEMORY": memoria, "TIME": datetime.now().isoformat()})
    cortex_orbito_frontal_resp = Cortex_Orbitofrontal(memoria)
    HIPOCAMPO_file_log("CORTEX_ORBITO_FRONTAL", {"valid": cortex_orbito_frontal_resp})
    if cortex_orbito_frontal_resp == "ok":
      reconsolidacao_resp = Reconsolidacao(memoria)
      if reconsolidacao_resp == "new":
        Memoria_console("NEW", memoria['memory_text'])
        return
      elif reconsolidacao_resp == "refresh":
        Memoria_console("REFRESH", memoria['memory_text'])
      elif reconsolidacao_resp == "ignore":
        Memoria_console("IGNORE", memoria['memory_text'])
    else:
      pass
    end_interaction_log("Logs/Hipocampo.log")
  
  
def Cortex_Orbitofrontal(memoria):
  if not isinstance(memoria.get("importance"), int): # ve se a memoria vem com importance
    HIPOCAMPO_file_log("END_CORTEX_ORBITO_FRONTAL", {"REASON": "ERRO NO IMPORTANCE"})
    return "NOT"
  if "O usuário" not in memoria['memory_text']: # Ve se a memoria tem "O usuario"
    HIPOCAMPO_file_log("END_CORTEX_ORBITO_FRONTAL", {"REASON": "MEMORIA NÃO TEM O USUARIO"})
    return "NOT"
  return "ok"

def Reconsolidacao(memoria):
  HIPOCAMPO_file_log("RECONSOLIDATION", { "status": "running"})
  memorias = [mem[1] for mem in Get_memorys_ids()]
  for c in memorias: # Ve se tem uma memoria IDENTICA no BD
    if memoria['memory_text'] == c:
      HIPOCAMPO_file_log("RECONSOLIDATION_END_PREMATURE", {"status": "UNSAVED", "reasoning": "memoria identica"})
      return "ignore"
  old_memorias = Get_memorys_by_type(memoria['memory_type'])
  response = Memoria_associativa(memoria, old_memorias)
  if response == "new":
    return "new"
  elif response == "refresh":
    return "refresh"
  elif response == "ignore":
    return "ignore"
  return "ignore"

def Memoria_associativa(new_memoria, old_memorias):
  candidatos = []
  emb1_new = requests.post(
      "http://localhost:11434/api/embeddings",
      json={
          "model": "nomic-embed-text",
          "prompt": new_memoria['memory_text']
    }
  ).json()['embedding']
  if len(old_memorias) == 0:
    Save_memory(memory=new_memoria['memory_text'], importance=new_memoria['importance'], memory_type=new_memoria['memory_type'], embedding=emb1_new)
    HIPOCAMPO_file_log("RECONSOLIDATION_END_PREMATURE", { "status": "SAVED", "reasoning": "new memory detected"})
    return "new"
  for mem_id, mem_old, mem_embe, mem_type in old_memorias: 
    mem_embe = json.loads(mem_embe)
    score = cosine(emb1_new, mem_embe)
    if score > 0.70:
      candidatos.append({"id": mem_id,"memory": mem_old,"score": score})
    #if score > 0.99:
    #  HIPOCAMPO_file_log("MEMORIA_ASSOCIATIVA_END_PREMATURE", { "status": "EMBEDING IDENTICO"})
    #  return "ignore"
      
  candidatos.sort(key=lambda x: x["score"], reverse=True)
  if len(candidatos) == 0:
    HIPOCAMPO_file_log("MEMORIA_ASSOCIATIVA_END_PREMATURE", {"status": "0 CANDIDATOS"})
    Save_memory(memory=new_memoria['memory_text'], importance=new_memoria['importance'], memory_type=new_memoria['memory_type'], embedding=emb1_new)
    return "new"
  top = candidatos[:3]
  HIPOCAMPO_file_log("MEMORIA_ASSOCIATIVA_CANDIDATOS", {"NEW_MEMORY": f"{new_memoria['memory_text']}", "Candidatos": f"{candidatos}"})
  
  
  decisions = []
  for candidate in top:
    system_check_duplicidade = {
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
    msg = [
      system_check_duplicidade,
      {
          "role": "user",
          "content": json.dumps({
              "memory_a": candidate['memory'],
              "memory_b": new_memoria['memory_text']
          })
        }
    ]
    decision = Ia_duplicy_verification(msg=msg, model="llama3.1:8b")
    decisions.append({
      "candidate": candidate,
      "decision": decision
    })
  
  for item in decisions:
    candidate = item['candidate']
    action = item["decision"]["action"]
    
    if action == "refresh":
      HIPOCAMPO_file_log("STATUS_REFRESH", {"new_memory": new_memoria['memory_text'], "Old_memory": candidate})
      Update_memory(candidate['id'], new_memoria['memory_text'], new_memoria['importance'], memory_type=new_memoria['memory_type'], embedding=emb1_new)
      return "refresh"
  
  for item in decisions:
    candidate = item['candidate']
    action = item["decision"]["action"]
    
    if action == "replace":
      HIPOCAMPO_file_log("STATUS_REPLACE", {"new_memory": new_memoria['memory_text'], "Old_memory": candidate})
      Update_memory(candidate['id'], new_memoria['memory_text'], new_memoria['importance'], memory_type=new_memoria['memory_type'], embedding=emb1_new)
      return "refresh"
  
  for item in decisions:
    action = item["decision"]["action"]
    if action == "new":
      HIPOCAMPO_file_log("STATUS_NEW", {"new_memory": new_memoria['memory_text']})
      Save_memory(memory=new_memoria['memory_text'], importance=new_memoria['importance'], memory_type=new_memoria['memory_type'], embedding=emb1_new)
      return "new"
  
  for item in decisions:
    action = item["decision"]["action"]
    if action == "duplicate":
      HIPOCAMPO_file_log("STATUS_DUPLICATE", {"new_memory": new_memoria['memory_text']})
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
