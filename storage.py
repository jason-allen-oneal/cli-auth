import os, json, time
from config import CONFIG_DIR, CONFIG_PATH

def ensure_config_dir():
    os.makedirs(CONFIG_DIR, exist_ok=True)

def now():
    return int(time.time())

def read_tokens():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def write_tokens(tok: dict):
    ensure_config_dir()
    tmp = CONFIG_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(tok, f, indent=2)
    os.replace(tmp, CONFIG_PATH)
    try:
        os.chmod(CONFIG_PATH, 0o600)
    except Exception:
        pass
