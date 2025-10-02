# Discord CLI Auth

A command-line tool to authenticate with Discord via OAuth2 + PKCE, then interact with the API or export chat logs.

---

## ✨ Features

- Login with your Discord account (OAuth2 Authorization Code + PKCE flow).
- Show your profile info (`whoami`).
- List your guilds (`guilds`).
- Export a channel with [DiscordChatExporter.Cli](https://github.com/Tyrrrz/DiscordChatExporter).
- Logout & clear tokens.

---

## ⚙️ Requirements

- Python **3.9+**
- [Playwright](https://playwright.dev/python/) for browser automation:

```bash
pip install playwright
python -m playwright install
```

- [DiscordChatExporter.Cli](https://github.com/Tyrrrz/DiscordChatExporter) binary in `./lib/exporter/`
- A Discord application with **OAuth2 Redirect URI** set to:

http://127.0.0.1:53682/callback
```

---

## 🚀 Setup

### 1. Clone repo

```bash
git clone https://github.com/yourname/discord-cli-auth.git
cd discord-cli-auth
```

### 2. Create `.env`

```env
CLIENT_ID=your_discord_app_client_id
REDIRECT_URI=http://127.0.0.1:53682/callback
ROOT=https://discord.com/api/
SCOPES=identify guilds
```

### 3. Run login

```bash
python auth.py login
```

After login, your tokens will be stored securely under:

- Linux: `~/.config/cli-auth/config.json`
- macOS: `~/Library/Application Support/cli-auth/config.json`
- Windows: `%APPDATA%\cli-auth\config.json`

---

## 📦 Usage

Once logged in, use the interactive menu:

- `Who am I?` → Prints your Discord profile.
- `List my guilds` → Lists all guilds you belong to.
- `Export` → Runs `DiscordChatExporter.Cli` for the channel you specify.
- `Logout` → Deletes saved tokens.

---

## 📜 License

MIT
