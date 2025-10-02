# Discord CLI Auth

A command-line tool to authenticate with Discord via OAuth2 + PKCE, then interact with the API or export chat logs.

---

## ✨ Features

- **Automatic login flow** - Authentication happens automatically when you run the app
- Show your profile info (`Who am I?`)
- List your guilds (`List my guilds`)
- Export Discord data with [DiscordChatExporter.Cli](https://github.com/Tyrrrz/DiscordChatExporter):
  - Export specific channels by ID
  - Export all channels from a guild/server (with guild selection)
  - Export DM channels by ID
  - Filter by date ranges (--after/--before)
  - Include threads (None/Active/All)
  - Download media attachments
  - Multiple export formats: JSON, HTML (Dark/Light), CSV, Plain Text
- **Analyze exported data** - AI-powered analysis using Google Gemini:
  - **HTML Parser**: Extracts messages, timestamps, authors, attachments, and reactions from Discord HTML exports
  - **Media Analysis**: Analyzes images, videos, and audio files for metadata and content
  - **AI-Powered Analysis**: Uses Google Gemini AI for sentiment analysis, topic extraction, and relationship dynamics
  - **Participant Profiling**: Creates detailed individual profiles with personality traits, likes/dislikes, communication styles, and interests
  - **Visualizations**: Creates charts, graphs, and interactive dashboards including participant profile radar charts and interest word clouds
  - **Privacy-Focused**: Optional anonymization and sensitive content removal
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

- **For Analysis Features**: [Google Gemini API key](https://makersuite.google.com/app/apikey) (free tier available)

---

## 🚀 Setup

### 1. Clone repo

```bash
git clone https://github.com/yourname/discord-cli-auth.git
cd discord-cli-auth
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
python -m playwright install
```

### 3. Create `.env`

```env
CLIENT_ID=your_discord_app_client_id
REDIRECT_URI=http://127.0.0.1:53682/callback
ROOT=https://discord.com/api/
SCOPES=identify guilds
GEMINI_API_KEY=your_gemini_api_key_here  # Optional: for analysis features
```

### 4. Run the application

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
3. **Export** → Exports Discord data using `DiscordChatExporter.Cli`
   - Choose from 3 export modes:
     - Export a specific channel by ID
     - Export all channels from a guild (with selectable guild list)
     - Export a DM channel by ID
   - Select export format (JSON, HTML Dark, HTML Light, CSV, Plain Text)
   - Optional date range filtering
   - Optional media download
   - Optional thread inclusion (None/Active/All)
4. **Analyze** → Analyze exported data (only enabled when exports exist in `exports/` directory)
   - Select an HTML export file to analyze
   - Enter your Google Gemini API key (or set GEMINI_API_KEY environment variable)
   - Choose whether to generate visualizations
   - Features include:
     - AI-powered sentiment analysis
     - Topic extraction and categorization
     - Participant profiling with personality traits
     - Communication style analysis
     - Relationship dynamics insights
     - Media file analysis (images, videos, audio)
     - Interactive visualizations and charts
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
