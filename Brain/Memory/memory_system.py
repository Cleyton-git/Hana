import sqlite3,  json
import numpy as np

def create_tables():
    con = sqlite3.connect("Brain/BD/hana_memorys.db")
    cursor = con.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mensagens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            content TEXT
        )
        """)

    cursor.execute("""
        CREATE TABLE memorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            memory TEXT,
            embedding float,
            type string,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
        """)
    
    cursor.execute("""CREATE TABLE father_personality (
    id INTEGER PRIMARY KEY,
    fact TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

    con.commit()

def Get_memorys_context(entity):
    con = sqlite3.connect("Brain/BD/hana_memorys.db")
    cursor = con.cursor()
    
    lista_memorias = []
    
    for c in entity:
        cursor.execute(
            "SELECT memory FROM memorias WHERE entity = ? ORDER BY id ASC",
            (c.lower(),)
        )
        rows = cursor.fetchall()
        
        for row in rows:
            lista_memorias.append(row[0])
            
    con.close()
    
    return "\n".join(lista_memorias)

def Get_memorys():
    con = sqlite3.connect("Brain/BD/hana_memorys.db")
    cursor = con.cursor()
    
    cursor.execute(
        f"SELECT * from memorias ORDER BY id ASC"
    )
    rows = cursor.fetchall()
    print(rows)
    system_content = "\n".join(
        row[1] for row in rows
    )
    system_content = "\n".join(
        f"- {row[1]}"
        for row in rows
    )   
    
    return [
        {"role": "system",
        "content": system_content}
    ]
    
def Get_contexto_msgs(limit):
    con = sqlite3.connect("Brain/BD/hana_memorys.db")
    cursor = con.cursor()
    
    cursor.execute(
        f"""
        SELECT role, content
        FROM mensagens
        ORDER BY id DESC
        LIMIT {limit}
        """
    )
    mensagens = cursor.fetchall()
    con.close()
    linhas = []

    for role, content in reversed(mensagens):

        if role == "[USER_MESSAGE]":
            linhas.append(f"Pai: {content}")

        elif role == "[ASSISTANT_MESSAGE]":
            linhas.append(f"Hana: {content}")

        else:
            linhas.append(content)

    return "\n".join(linhas)
    return "\n".join(
        content for role, content in reversed(mensagens)
    )
    
def Save_message(role, content):
    con = sqlite3.connect("Brain/BD/hana_memorys.db")
    cursor = con.cursor()
    
    cursor.execute(
        f"INSERT INTO mensagens (role, content) VALUES(?, ?)",
        (role, content)
    )
    con.commit()

def Save_memory(memory, embedding, type):
    con = sqlite3.connect("Brain/BD/hana_memorys.db")
    cursor = con.cursor()
    embedding = json.dumps(embedding)
    
    cursor.execute(
        f"INSERT INTO memorias (memory, embedding, type) VALUES(?, ?, ?)",
        (memory, embedding, type)
    )
    con.commit()
    con.close()


def Get_memorys_embeddings():
    con = sqlite3.connect("Brain/BD/hana_memorys.db")
    cursor = con.cursor()
    cursor.execute(
        f"SELECT memory, embedding from memorias ORDER BY id ASC"
    )
    rows = cursor.fetchall()
    return rows

def Get_memorys_by_embedding(novo_embedding, type=""):
    con = sqlite3.connect("Brain/BD/hana_memorys.db")
    cursor = con.cursor()
    if type == "episodic":
        cursor.execute(f"SELECT memory, embedding from memorias WHERE type = 'episodic' ORDER BY id ASC")
    elif type == "state":
        cursor.execute(f"SELECT memory, embedding from memorias WHERE type = 'state' ORDER BY id ASC")
    else:
        cursor.execute(f"SELECT memory, embedding from memorias ORDER BY id ASC")
    rows = cursor.fetchall()
    lista = []
    for memoria, embeding_atual in rows:
        embedding_atual = json.loads(embeding_atual)
        score = np.dot(novo_embedding, embedding_atual) / ( np.linalg.norm(novo_embedding) * np.linalg.norm(embedding_atual))
        lista.append((score, memoria))
    lista.sort(reverse=True)
    top_5 = lista[:5]
        
    return top_5

def Update_memory(new_memory, old_memory, new_embedding):
    con = sqlite3.connect("Brain/BD/hana_memorys.db")
    cursor = con.cursor()
    new_embedding = json.dumps(new_embedding)

    query = """
        UPDATE memorias
        SET memory = ?,
            embedding = COALESCE(?, embedding) 
        WHERE memory = ?
    """
    cursor.execute(query, (new_memory, new_embedding, old_memory))


    con.commit()
    con.close()

def Get_personality_father():
    con = sqlite3.connect("Brain/BD/hana_memorys.db")
    cursor = con.cursor()
    cursor.execute("SELECT memory FROM memorias WHERE type = 'personality'" )
    Personalidade  = cursor.fetchall()
    
    return "\n".join(fact[0] for fact in Personalidade)

def Get_embeddings_personality_father():
    con = sqlite3.connect("Brain/BD/hana_memorys.db")
    cursor = con.cursor()
    cursor.execute("SELECT fact, embedding FROM father_personality")
    embeddings = cursor.fetchall()
    
    return embeddings

def Add_personality(fact, embedding):
    con = sqlite3.connect("Brain/BD/hana_memorys.db")
    cursor = con.cursor()
    embedding = json.dumps(embedding)
    cursor.execute("INSERT INTO father_personality (fact, embedding) VALUES (?, ?)",
                   (fact, embedding))
    con.commit()
    con.close()
    return

def Update_personality(old_fact, fact, new_embedding):
    con = sqlite3.connect("Brain/BD/hana_memorys.db")
    cursor = con.cursor()
    new_embedding = json.dumps(new_embedding)
    
    cursor.execute("UPDATE father_personality SET fact = ?, embedding = ? WHERE fact = ? ", (fact, new_embedding, old_fact))
    con.commit()
    con.close()
    return


#Save_memory("O usuario gostaria que Bilu pudesse falar", 10)
#Save_memory("O usuario gostaria de conseguir beber mais agua durante o dia", 10)
#Save_memory("O usuario esta cansado por conta da faculdade", 10)
#Save_memory("O usuario esta desenvolvendo a IA Hana", 10)


#create_tables()
#Get_memorys_context(embe=10)
#memorias = Get_memorys()
#print(memorias)


#memorias = [mem[1] for mem in get_memorys_ids()]
#for c in memorias:
#    print(c)
#create_tables()
#memorias = Get_memorys()
#print(memorias)
#mensagens = Get_contexto()
#print(mensagens)

