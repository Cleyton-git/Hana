from ..Ears.ouvidos import Fala_Pai
import textwrap

LARGURA = 54

def Cortex_sensorial(interacao, channel, web_text):
    if channel == "API":
        Pai = web_text
        print("╔" + "═" * (LARGURA + 2) + "╗")
        linha(f"{f'HANA | INTERAÇÃO #{interacao}':^{LARGURA}}")
        print("╠" + "═" * (LARGURA + 2) + "╣")
        linha(f"PAI | {Pai}")
        return Pai
    elif channel == "ZAP":
        Pai = web_text
        return Pai
    else:
        print("╔" + "═" * (LARGURA + 2) + "╗")
        linha(f"{f'HANA | INTERAÇÃO #{interacao}':^{LARGURA}}")
        print("╠" + "═" * (LARGURA + 2) + "╣")
        Pai = Fala_Pai()
        return Pai

def linha(texto):
    linhas = textwrap.wrap(
        str(texto),
        width=LARGURA
    )
    for l in linhas:
        print(f"║ {l:<{LARGURA}} ║")
