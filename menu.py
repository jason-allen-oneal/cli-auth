# menu.py
from commands import cmd_whoami, cmd_guilds, cmd_logout
from exporter import cmd_export


def menu():
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
                cmd_export(None)  # 👈 cleanly calls exporter
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
