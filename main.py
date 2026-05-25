from Brain.brain import Brain_Hana
import traceback

interacao = 1

def main():
    print("🧠 Hana acordando...")

while True:
    try:
        Brain_Hana(interacao)
    except KeyboardInterrupt:
        print("Hana encerrada. ")
        break
    except Exception as e:
        traceback.print_exc()
        print(f"\n⚠️ Erro no cérebro da Hana: {e}")
    interacao += 1


if __name__ == "__main__":
    main()
