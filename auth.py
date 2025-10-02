import argparse, sys
from commands import cmd_login, cmd_whoami, cmd_guilds, cmd_logout
from menu import menu


def main():
    parser = argparse.ArgumentParser(description="Discord CLI Auth")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("login")
    sub.add_parser("whoami")
    sub.add_parser("guilds")
    sub.add_parser("logout")
    sub.add_parser("menu")

    args = parser.parse_args()

    if args.command == "login":
        cmd_login()
    elif args.command == "whoami":
        cmd_whoami(None)
    elif args.command == "guilds":
        cmd_guilds(None)
    elif args.command == "logout":
        cmd_logout(None)
    elif args.command == "menu":
        menu()
    else:
        parser.print_help()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(130)
