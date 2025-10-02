# storage.py
import os, json, time, requests
from config import CONFIG_PATH, DISCORD_TOKEN

# --- Time helper ---
def now() -> int:
    return int(time.time())

# --- File helpers ---
def read_tokens():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def write_tokens(tok: dict):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    tmp = CONFIG_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(tok, f, indent=2)
    os.replace(tmp, CONFIG_PATH)
    try:
        os.chmod(CONFIG_PATH, 0o600)
    except Exception:
        pass

# --- Expiry + Refresh ---
def is_expired(tok: dict) -> bool:
    # 60s margin
    return now() >= (tok.get("obtained_at", 0) + tok.get("expires_in", 0) - 60)

def refresh(tok: dict) -> dict:
    if not tok.get("refresh_token"):
        raise RuntimeError("No refresh_token available. Run login again.")
    data = {
        "grant_type": "refresh_token",
        "refresh_token": tok["refresh_token"],
        "client_id": tok["client_id"],
    }
    r = requests.post(DISCORD_TOKEN, data=data, timeout=30)
    if r.status_code != 200:
        raise RuntimeError(f"Refresh failed ({r.status_code}): {r.text}")
    j = r.json()
    updated = {
        **tok,
        "access_token": j["access_token"],
        "refresh_token": j.get("refresh_token", tok["refresh_token"]),
        "expires_in": j["expires_in"],
        "token_type": j["token_type"],
        "scope": j.get("scope", tok.get("scope", "")),
        "obtained_at": now(),
    }
    write_tokens(updated)
    return updated

# --- Wrapper ---
def with_access_token(fn):
    tok = read_tokens()
    if not tok:
        raise RuntimeError("Not logged in. Run: python auth.py login")
    if is_expired(tok):
        tok = refresh(tok)
    return fn(tok["access_token"])
