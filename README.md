# Discord CLI Auth

A command-line tool to authenticate with Discord via OAuth2 + PKCE, then interact with the API or export chat logs.

---

## ✨ Features

- **Automatic login flow** - Authentication happens automatically when you run the app
- Show your profile info (`Who am I?`)
- List your guilds (`List my guilds`)
- Export a channel with [DiscordChatExporter.Cli](https://github.com/Tyrrrz/DiscordChatExporter)
- Analyze exported data (disabled until exports are available)
- Logout & clear tokens

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

### 3. Run the application

```bash
python auth.py
```

The application will:
1. Check if you're logged in
2. If not, automatically start the OAuth2 authentication flow
3. Once authenticated, display an interactive menu

After login, your tokens will be stored securely under:

- Linux: `~/.config/cli-auth/config.json`
- macOS: `~/Library/Application Support/cli-auth/config.json`
- Windows: `%APPDATA%\cli-auth\config.json`

---

## 📦 Usage

The app provides an interactive menu with the following options:

1. **Who am I?** → Displays your Discord profile information
2. **List my guilds** → Shows all guilds (servers) you belong to
3. **Export** → Exports a Discord channel using `DiscordChatExporter.Cli`
4. **Analyze** → Analyze exported data (only enabled when exports exist in `exports/` directory)
5. **Logout** → Deletes saved tokens and logs you out
6. **Exit** → Closes the application

---

## 📁 Project Structure

- `auth.py` - Main entry point with auto-login flow
- `lib/` - All library modules
  - `commands.py` - All CLI command implementations
  - `util.py` - Menu and utility functions
  - `config.py` - Configuration and constants
  - `storage.py` - Token storage and management
  - `oauth.py` - OAuth2 + PKCE implementation
  - `browser.py` - Browser automation for authentication
  - `exporter/` - DiscordChatExporter.Cli binary
- `exports/` - Directory for exported channel data

---

## 📜 License

MIT
