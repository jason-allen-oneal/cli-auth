# auth.py
import argparse, sys
from commands import cmd_login, cmd_whoami, cmd_guilds, cmd_logout

def main():
    p = argparse.ArgumentParser(description="Discord OAuth2 CLI (Authorization Code + PKCE)")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("login").set_defaults(func=cmd_login)
    sub.add_parser("whoami").set_defaults(func=cmd_whoami)
    sub.add_parser("guilds").set_defaults(func=cmd_guilds)
    sub.add_parser("logout").set_defaults(func=cmd_logout)

    args = p.parse_args()
    try:
        # commands expect no args, so call directly
        args.func(None) if args.cmd != "login" else args.func()
    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(130)
    except Exception as e:
        print("Error:", e, file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
