import sqlite3
import numpy as np
import json

def cosine(a, b):
    a = np.array(a)
    b = np.array(b)

    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

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
            importance INTEGER,
            memory_type TEXT,
            embedding float,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
        """)

    con.commit()

def Get_memorys_context(entity):
    con = sqlite3.connect("Brain/BD/hana_memorys.db")
    cursor = con.cursor()
    
    #cursor.execute(
    #    f"SELECT * from memorias WHERE category IN ('comportamento', 'identidade') ORDER BY id ASC"
    #)
    cursor.execute(
        "SELECT memory FROM memorias WHERE entity = ? ORDER BY id ASC",
        (entity,)
    )
    rows = cursor.fetchall()
    con.close()
    
    return "\n".join(row[0] for row in rows)


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

def Get_contexto(limit=1000):
    con = sqlite3.connect("Brain/BD/hana_memorys.db")
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
    con = sqlite3.connect("Brain/BD/hana_memorys.db")
    cursor = con.cursor()
    
    cursor.execute(
        f"INSERT INTO mensagens (role, content) VALUES(?, ?)",
        (role, content)
    )
    con.commit()

def Save_memory(memory, importance, entity):
    con = sqlite3.connect("Brain/BD/hana_memorys.db")
    cursor = con.cursor()
    
    cursor.execute(
        f"INSERT INTO memorias (memory, importance, entity) VALUES(?, ?, ?)",
        (memory, importance, entity)
    )
    con.commit()
    con.close()

def Get_memorys_category():
    con = sqlite3.connect("Brain/BD/hana_memorys.db")
    cursor = con.cursor()
    cursor.execute(
        f"SELECT category from memorias ORDER BY id ASC"
    )
    rows = cursor.fetchall()
    return rows[-5:]

def Get_memorys_ids():
    con = sqlite3.connect("Brain/BD/hana_memorys.db")
    cursor = con.cursor()
    cursor.execute(
        f"SELECT id, memory from memorias ORDER BY id ASC"
    )
    rows = cursor.fetchall()
    return rows

def Get_memorys_by_entity(entity):
    print(entity)
    con = sqlite3.connect("Brain/BD/hana_memorys.db")
    cursor = con.cursor()
    cursor.execute(
        f"SELECT id, memory, entity, importance from memorias WHERE entity = '{entity}' ORDER BY id ASC"
    )
    rows = cursor.fetchall()
    return rows

def Update_memory(mem_id, new_memory, entity, importance):
    con = sqlite3.connect("Brain/BD/hana_memorys.db")
    cursor = con.cursor()

    query = """
        UPDATE memorias
        SET memory = ?,
            importance = COALESCE(?, importance),
            entity = COALESCE(?, entity)
        WHERE id = ?
    """

    cursor.execute(query, (new_memory, importance, entity, mem_id))


    con.commit()
    con.close()
    

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

