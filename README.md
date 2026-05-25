# 🧠 Hana AI

Hana é um sistema de IA modular baseado em LLMs locais, projetado como uma arquitetura de agentes cognitivos com memória persistente, ferramentas externas e comportamento dinâmico.

O objetivo do projeto é simular um sistema cognitivo inspirado em cérebro humano, separando funções como memória, raciocínio, percepção e execução de ações.

---

# ⚙️ Arquitetura Geral
hana/
├── brain.py # Orquestrador (decisão e roteamento)
├── mouth.py # Agente de resposta (personalidade da Hana)
├── memory.py # Sistema de memória persistente
├── tools/ # Ferramentas externas

# 🧠 Brain (Orquestrador)
O cérebro da Hana.

Responsável por:
- Interpretar input do usuário
- Decidir ações (tool / memória / resposta)
- Roteamento entre agentes
- Retornar JSON estruturado com decisões

Exemplo de saída:

{
  "action": "save_memory",
  "tool": null,
}

# 🧾 Hipocampo (Memória)
Sistema responsável por extrair memórias persistentes.

Funções:

Extrair fatos explícitos do usuário
Converter em formato estruturado
Evitar inferências e alucinações
Filtrar conteúdo irrelevante

Memórias são salvas como:

{
  "memory": "texto normalizado da memória",
  "embedding": [0.12, 0.98, ...],
  "importance": 7
}

🔍 Pipeline de Memória
Antes de enviar para o Hipocampo:

separação de frases
remoção de conectivos (e, vírgula, etc)
filtragem por tamanho (> 15 chars)
normalização textual

🧠 Sistema de Contexto (Memory Retrieval)
A Hana mantém duas camadas de memória:

Memória de personalidade (system prompt fixo)
Memória dinâmica (contexto do usuário)

Como eu dou contexto para o modelo:

embeddings da entrada
comparação com banco de dados
threshold (~0.75)
seleção de memórias relevantes (top 5)

🧠 Sistema de Importance
Cada memória recebe um score:

9–10 → identidade / relações centrais
7–8 → objetivos importantes
4–6 → hobbies e preferências
1–3 → detalhes leves

# 🧩 Tool System
O Brain pode acionar ferramentas externas.

Ferramentas já feitas:
🗂️ Abrir projetos pessoais
🌐 Pesquisado na web
🎥 Pesquisado no YouTube

# 🗣️ Mouth (Personalidade)
Responsável por:
gerar resposta final da Hana
aplicar estilo de fala
usar contexto + memória + tools

🎙️ Voice System
transcrição de voz em tempo real
envio direto ao Brain
resposta instantânea da Hana

# 👁️ Vision System
Entrada visual (imagem/vídeo)
interpretação multimodal

# 🎯 Objetivo do projeto
Criar uma IA modular com:

memória persistente real
execução de ferramentas externas
separação de agentes cognitivos
comportamento adaptativo
arquitetura escalável estilo "cérebro artificial"

# ⚠️ Status
🚧 Em desenvolvimento ativo e experimental

O sistema já possui:

cérebro funcional
memória funcional
fala/personalidade/comportamento funcional
tools funcionais
arquitetura modular base

# 🧠 Nota final

Hana não é um chatbot.
É um sistema de agentes cognitivos modulares altamente escalavel com memória persistente e execução de ferramentas

