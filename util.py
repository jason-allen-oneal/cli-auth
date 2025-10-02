# utils.py
import json

def menu(cmd_whoami, cmd_guilds, cmd_export, cmd_logout):
    while True:
        print("\n=== Discord CLI Menu ===")
        print("1. Who am I?")
        print("2. List my guilds")
        print("3. Export")
        print("4. Logout")
        print("5. Exit")

        choice = input("Select an option: ").strip()

        try:
            if choice == "1":
                cmd_whoami(None)
            elif choice == "2":
                cmd_guilds(None)
            elif choice == "3":
                cmd_export(None)
            elif choice == "4":
                cmd_logout(None)
                break
            elif choice == "5":
                print("Goodbye!")
                break
            else:
                print("Invalid choice, try again.")
        except Exception as e:
            print(f"Error: {e}")


def pretty_print(data):
    print(json.dumps(data, indent=2))


def prompt_yes_no(question: str) -> bool:
    return input(f"{question} (y/N): ").strip().lower() == "y"
