import webbrowser, requests, json

def Pesquisar_web(Pai):
    system_search = {
  "role": "system",
  "content": """
Você é um módulo de EXTRAÇÃO DE QUERY para pesquisa na web.

Sua função é simples:
- Receber uma frase do usuário
- Retornar APENAS a QUERY de pesquisa limpa

Você NÃO conversa.
Você NÃO explica.
Você NÃO adiciona palavras.
Você NÃO responde perguntas.

━━━━━━━━━━━━━━━━━━━━━━
SAÍDA OBRIGATÓRIA
━━━━━━━━━━━━━━━━━━━━━━

Retorne APENAS uma string com a query final.

Exemplo:
"como fazer api em python"

Nada mais.

━━━━━━━━━━━━━━━━━━━━━━
REGRAS DE LIMPEZA
━━━━━━━━━━━━━━━━━━━━━━

Remova:
- nomes de comando (Hana, filha, pai)
- pedidos educados (por favor, para mim)
- verbos de comando (pesquisa, pesquisar, busca, procurar, vê, olha)

━━━━━━━━━━━━━━━━━━━━━━
EXEMPLOS
━━━━━━━━━━━━━━━━━━━━━━

Input:
"Hana pesquisa como fazer API em Python pra mim"

Output:
como fazer API em Python

---

Input:
"filha, pesquisa melhores jogos de 2024"

Output:
melhores jogos de 2024

---

Input:
"procura no google como treinar IA"

Output:
como treinar IA

━━━━━━━━━━━━━━━━━━━━━━
REGRA FINAL

- Retorne SOMENTE a query
- Sem aspas
- Sem JSON
- Sem explicações
"""
}
    messages = [
        system_search,
        {
            "role": "user",
            "content": Pai
        }
    ]
    query = requests.post("http://127.0.0.1:11434/api/chat",
        json={
            "model": "qwen2.5:3b",
            "messages": messages,
            "stream": False
        }
    )
    query = json.loads(query.text)
    return query['message']['content']
    

query = Pesquisar_web(Pai="Hana, pesquisa atarashi gakkou para mim")    
print(query)
webbrowser.open(f"https://www.google.com/search?q={query}")
