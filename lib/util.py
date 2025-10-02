# util.py
import os
import json
from lib.config import EXPORT_DIR


def menu(cmd_whoami, cmd_guilds, cmd_export, cmd_analyze, cmd_logout):
    """Interactive menu for Discord CLI"""
    while True:
        print("\n=== Discord CLI Menu ===")
        print("1. Who am I?")
        print("2. List my guilds")
        print("3. Export")
        
        # Check if analyze should be enabled
        analyze_enabled = os.path.exists(EXPORT_DIR) and len(os.listdir(EXPORT_DIR)) > 0
        if analyze_enabled:
            print("4. Analyze")
            print("5. Logout")
            print("6. Exit")
        else:
            print("4. Analyze (disabled - no exports found)")
            print("5. Logout")
            print("6. Exit")

        choice = input("Select an option: ").strip()

        try:
            if choice == "1":
                cmd_whoami(None)
            elif choice == "2":
                cmd_guilds(None)
            elif choice == "3":
                cmd_export(None)
            elif choice == "4":
                if analyze_enabled:
                    cmd_analyze(None)
                else:
                    print("Analyze is disabled. Export data first.")
            elif choice == "5":
                cmd_logout(None)
                break
            elif choice == "6":
                print("Goodbye!")
                break
            else:
                print("Invalid choice, try again.")
        except Exception as e:
            print(f"Error: {e}")


def pretty_print(data):
    """Pretty print JSON data"""
    print(json.dumps(data, indent=2))


def prompt_yes_no(question: str) -> bool:
    """Prompt user for yes/no question"""
    return input(f"{question} (y/N): ").strip().lower() == "y"
