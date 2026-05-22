import sqlite3
import numpy as np
import json

def cosine(a, b):
    a = np.array(a)
    b = np.array(b)

    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def create_tables():
    con = sqlite3.connect("Brain/Memory/Hana_itself/hana_memorys.db")
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
            importance INTEGER,
            embedding float,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
        """)

    con.commit()

def Get_memorys_context(embe):
    con = sqlite3.connect("Brain/Memory/Hana_itself/hana_memorys.db")
    cursor = con.cursor()
    
    #cursor.execute(
    #    f"SELECT * from memorias WHERE category IN ('comportamento', 'identidade') ORDER BY id ASC"
    #)
    cursor.execute(
        f"SELECT * from memorias ORDER BY id ASC"
    )
    rows = cursor.fetchall()
    
    memorias_relevantes = []
    
    for c in rows:
        embe_old = json.loads(c[3])
        score = cosine(embe, embe_old)
        memorias_relevantes.append({
            "memory": c[1],
            "score": score
        })
    con.close()
    
    memorias_relevantes.sort(
        key=lambda x: x["score"],
        reverse=True
    )
    top_memorias = memorias_relevantes[:5]

    memorias_contexto = "\n".join(
        f"- {m['memory']}"
        for m in top_memorias
    )
    return memorias_contexto


def Get_memorys():
    con = sqlite3.connect("Brain/Memory/Hana_itself/hana_memorys.db")
    cursor = con.cursor()
    
    #cursor.execute(
    #    f"SELECT * from memorias WHERE category IN ('comportamento', 'identidade') ORDER BY id ASC"
    #)
    cursor.execute(
        f"SELECT * from memorias ORDER BY id ASC"
    )
    rows = cursor.fetchall()
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

def Get_contexto(limit=1000):
    con = sqlite3.connect("Brain/Memory/Hana_itself/hana_memorys.db")
    cursor = con.cursor()
    
    cursor.execute(
        f"SELECT role, content FROM mensagens ORDER BY id ASC LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()
    
    return [
        {"role": role, "content": content}
        for role, content in rows
    ]

def Save_message(role, content):
    con = sqlite3.connect("Brain/Memory/Hana_itself/hana_memorys.db")
    cursor = con.cursor()
    
    cursor.execute(
        f"INSERT INTO mensagens (role, content) VALUES(?, ?)",
        (role, content)
    )
    con.commit()

def Save_memory(memory, importance, embedding):
    import json
    embedding_json = json.dumps(embedding)
    con = sqlite3.connect("Brain/Memory/Hana_itself/hana_memorys.db")
    cursor = con.cursor()
    
    cursor.execute(
        f"INSERT INTO memorias (memory, importance, embedding) VALUES(?, ?, ?)",
        (memory, importance, embedding_json)
    )
    con.commit()
    con.close()

def Get_memorys_category():
    con = sqlite3.connect("database/hana.db")
    cursor = con.cursor()
    cursor.execute(
        f"SELECT category from memorias ORDER BY id ASC"
    )
    rows = cursor.fetchall()
    return rows[-5:]

def Get_memorys_ids():
    con = sqlite3.connect("Brain/Memory/Hana_itself/hana_memorys.db")
    cursor = con.cursor()
    cursor.execute(
        f"SELECT id, memory, embedding from memorias ORDER BY id ASC"
    )
    rows = cursor.fetchall()
    return rows

def Update_memory(mem_id, new_memory, importance=None, embedding=None):
    import json
    embedding_json = json.dumps(embedding)
    con = sqlite3.connect("Brain/Memory/Hana_itself/hana_memorys.db")
    cursor = con.cursor()

    query = """
        UPDATE memorias
        SET memory = ?,
            importance = COALESCE(?, importance),
            embedding = COALESCE(?, embedding)
        WHERE id = ?
    """

    cursor.execute(query, (new_memory, importance, embedding_json, mem_id))


    con.commit()
    con.close()
    

#create_tables()
#Get_memorys_context(embe=10)

#memorias = [mem[1] for mem in get_memorys_ids()]
#for c in memorias:
#    print(c)
#create_tables()
#memorias = Get_memorys()
#print(memorias)
#mensagens = Get_contexto()
#print(mensagens)

