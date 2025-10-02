import os
from platformdirs import user_config_dir
from dotenv import load_dotenv
load_dotenv()

APP_NAME = "cli-auth"
CONFIG_DIR = user_config_dir(APP_NAME)
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")
EXPORT_DIR = "exports"

ROOT = os.environ.get("ROOT", "https://discord.com/api/")

DISCORD_AUTHZ = f"{ROOT}oauth2/authorize"
DISCORD_TOKEN = f"{ROOT}oauth2/token"
DISCORD_ME    = f"{ROOT}users/@me"
DISCORD_GUILDS= f"{ROOT}users/@me/guilds"