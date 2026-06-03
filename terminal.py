import requests, textwrap

LARGURA = 54

def linha(texto):
    linhas = textwrap.wrap(
        str(texto),
        width=LARGURA
    )
    for l in linhas:
        print(f"║ {l:<{LARGURA}} ║")

def send_message(Pai):
    r = requests.post("http://127.0.0.1:8000/chat",
                 json={
                     "message": Pai
                 }) 
    return r.json()

while True:
    Pai = input("-> ")
    response = send_message(Pai)
    print("╔" + "═" * (LARGURA + 2) + "╗")
    linha(f"{f'HANA | INTERAÇÃO API_WEB':^{LARGURA}}")
    print("╠" + "═" * (LARGURA + 2) + "╣")
    linha(f"PAI | {Pai}")
    
    if response['tool'] == 'yes':
        linha(f"TOOL | {response['tool']}")
        print("╚" + "═" * (LARGURA + 2) + "╝")
        continue
    
    linha(f"TOOL | {response['tool']}")
    linha(f"MEMORY | {response['memory']}")
    linha(f"RESPONSE | {response['response']}")
    print("╚" + "═" * (LARGURA + 2) + "╝")
    
    
    
