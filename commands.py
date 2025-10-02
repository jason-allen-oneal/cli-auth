import os, requests, urllib.parse, threading, json, http.server
from config import DISCORD_TOKEN, DISCORD_ME, DISCORD_GUILDS, CONFIG_PATH
from storage import read_tokens, write_tokens, now
from oauth import gen_code_verifier, gen_code_challenge, CodeHandler, find_free_port
from browser import open_and_capture


def cmd_login():
    from menu import menu   # ✅ local import, avoids circular import

    client_id = os.environ["CLIENT_ID"]
    redirect_uri = os.environ["REDIRECT_URI"]

    verifier = gen_code_verifier()
    challenge = gen_code_challenge(verifier)
    state = "xyz"

    # Start callback server
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

    final_url, auth_header = open_and_capture(url, redirect_uri)
    print(auth_header)

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

    r_me = requests.get(
        DISCORD_ME, headers={"Authorization": f"Bearer {tok['access_token']}"}, timeout=30
    )
    if r_me.status_code != 200:
        raise SystemExit(f"User lookup failed ({r_me.status_code}): {r_me.text}")
    me = r_me.json()

    bundle = {
        **tok,
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
        "auth_header": auth_header
    }
    write_tokens(bundle)
    print(f"Logged in as {me.get('username')} ({me.get('id')}). Tokens stored at: {CONFIG_PATH}")

    # ✅ call menu here
    menu()


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
