from Brain.brain import Brain_Hana
import traceback


def main():
    print("🧠 Hana acordando...")

while True:
    try:
        Brain_Hana()
    except KeyboardInterrupt:
        print("Hana encerrada. ")
        break
    except Exception as e:
        traceback.print_exc()
        print(f"\n⚠️ Erro no cérebro da Hana: {e}")


if __name__ == "__main__":
    main()
