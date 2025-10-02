# commands.py
import os, requests, urllib.parse, threading, json, http.server, subprocess
from config import DISCORD_TOKEN, DISCORD_ME, DISCORD_GUILDS, CONFIG_PATH
from storage import read_tokens, write_tokens, now
from oauth import gen_code_verifier, gen_code_challenge, CodeHandler, find_free_port
from browser import open_and_capture

EXPORT_DIR = "exports"
os.makedirs(EXPORT_DIR, exist_ok=True)

# Simple interactive menu used after login
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

def cmd_export(_):
    tok = read_tokens()
    if not tok:
        raise RuntimeError("Not logged in")

    # Prompt user for channel ID
    channel_id = input("Enter the channel ID to export: ").strip()

    # Prompt user for format
    print("Select export format:")
    print("1. JSON")
    print("2. HTML")
    print("3. CSV")
    fmt_choice = input("Choose (1/2/3): ").strip()

    if fmt_choice == "1":
        fmt = "Json"
    elif fmt_choice == "2":
        fmt = "Html"
    elif fmt_choice == "3":
        fmt = "Csv"
    else:
        print("Invalid choice.")
        return

    # Prompt user about media
    download_media = input("Download all media attachments? (y/N): ").strip().lower() == "y"

    token = tok["access_token"]
    output_file = os.path.join(EXPORT_DIR, f"export_{channel_id}.{fmt.lower()}")

    cmd = [
        "./lib/exporter/DiscordChatExporter.Cli",
        "export",
        "--channel", channel_id,
        "--token", token,
        "-f", fmt,
        "-o", output_file
    ]

    if download_media:
        cmd.append("--media")

    try:
        subprocess.run(cmd, check=True)
        print(f"✅ Export complete: {output_file}")
        if download_media:
            print("✅ Media attachments downloaded as well.")
    except subprocess.CalledProcessError as e:
        print(f"Export failed: {e}")


def cmd_login():
    client_id = os.environ["CLIENT_ID"]
    redirect_uri = os.environ["REDIRECT_URI"]

    verifier = gen_code_verifier()
    challenge = gen_code_challenge(verifier)
    state = "xyz"

    port = find_free_port(53682)
    event = threading.Event()
    CodeHandler.STATE = state
    CodeHandler.DONE_EVENT = event
    CodeHandler.RESULT = {"code": None, "error": None}

    httpd = http.server.HTTPServer(("127.0.0.1", port), CodeHandler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()

    url = (
        "https://discord.com/oauth2/authorize"
        f"?client_id={client_id}"
        "&response_type=code"
        f"&redirect_uri={urllib.parse.quote(redirect_uri)}"
        "&scope=identify+guilds"
        f"&state={state}"
        f"&code_challenge={challenge}"
        "&code_challenge_method=S256"
    )

    final_url, _maybe_auth_header = open_and_capture(url, redirect_uri)

    code = urllib.parse.parse_qs(
        urllib.parse.urlparse(final_url).query
    ).get("code", [None])[0]

    event.wait(timeout=300)
    httpd.shutdown()

    if CodeHandler.RESULT.get("error"):
        raise SystemExit(f"Auth error: {CodeHandler.RESULT['error']}")
    code = CodeHandler.RESULT.get("code", code)

    if not code:
        raise SystemExit("Did not receive authorization code (timeout).")

    data = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "code": code,
        "redirect_uri": redirect_uri,
        "code_verifier": verifier,
    }
    r = requests.post(DISCORD_TOKEN, data=data, timeout=30)
    if r.status_code != 200:
        raise SystemExit(f"Token exchange failed ({r.status_code}): {r.text}")
    tok = r.json()
    obtained_at = now()

    r_me = requests.get(DISCORD_ME, headers={"Authorization": f"Bearer {tok['access_token']}"}, timeout=30)
    if r_me.status_code != 200:
        raise SystemExit(f"User lookup failed ({r_me.status_code}): {r_me.text}")
    me = r_me.json()

    bundle = {
        "access_token": tok["access_token"],
        "refresh_token": tok.get("refresh_token"),
        "token_type": tok.get("token_type", "Bearer"),
        "scope": tok.get("scope", " ".join(["identify", "guilds"])),
        "expires_in": tok.get("expires_in", 0),
        "obtained_at": obtained_at,
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scopes": ["identify", "guilds"],
        "discord_user": {
            "id": me.get("id"),
            "username": me.get("username"),
            "global_name": me.get("global_name"),
            "avatar": me.get("avatar"),
        },
    }
    write_tokens(bundle)
    print(f"Logged in as {me.get('username')} ({me.get('id')}). Tokens stored at: {CONFIG_PATH}")

    menu()


def _with_access_token(fn):
    tok = read_tokens()
    if not tok:
        raise RuntimeError("Not logged in. Run: python -m auth login")
    return fn(tok["access_token"])


def cmd_whoami(_):
    tok = read_tokens()
    if not tok:
        raise RuntimeError("Not logged in")
    r = requests.get(DISCORD_ME, headers={"Authorization": f"Bearer {tok['access_token']}"})
    print(json.dumps(r.json(), indent=2))


def cmd_guilds(_):
    tok = read_tokens()
    if not tok:
        raise RuntimeError("Not logged in")
    r = requests.get(DISCORD_GUILDS, headers={"Authorization": f"Bearer {tok['access_token']}"})
    print(json.dumps(r.json(), indent=2))


def cmd_logout(_):
    if os.path.exists(CONFIG_PATH):
        os.remove(CONFIG_PATH)
        print("Local tokens deleted.")
    else:
        print("Already logged out.")
