import sys
from lib.commands import perform_authentication, cmd_whoami, cmd_guilds, cmd_logout, cmd_export, cmd_analyze
from lib.storage import read_tokens
from lib.util import menu


def main():
    """
    Main entry point - automatically handles authentication and shows menu.
    If not logged in, performs authentication first.
    """
    # Check if user is already logged in
    tok = read_tokens()
    
    if not tok:
        print("You are not logged in. Authenticating...")
        perform_authentication()
    else:
        print(f"Welcome back, {tok.get('discord_user', {}).get('username', 'User')}!")
    
    # Show interactive menu
    menu(cmd_whoami, cmd_guilds, cmd_export, cmd_analyze, cmd_logout)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(130)
