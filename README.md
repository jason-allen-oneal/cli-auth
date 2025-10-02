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
python app.py
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

## 📊 Analysis Features

The analysis feature is powered by Google Gemini AI and provides comprehensive insights into Discord conversations.

### Prerequisites

1. Export your Discord data in **HTML format** (required for analysis)
2. Get a [Google Gemini API key](https://makersuite.google.com/app/apikey) (free tier available)
3. Set the `GEMINI_API_KEY` environment variable (optional but recommended)

### What Gets Analyzed

- **Sentiment Analysis**: Overall conversation sentiment and per-participant sentiment
- **Topic Extraction**: Main topics and themes discussed in the conversation
- **Participant Profiling**: Detailed profiles for each participant including:
  - Personality traits
  - Communication styles
  - Likes, dislikes, and interests
  - Important ideas and beliefs
  - Emotional patterns
  - Role in conversation dynamics
  - Activity and influence levels
- **Relationship Dynamics**: Communication patterns and relationship health
- **Media Analysis**: Metadata extraction from images, videos, and audio files
- **Key Insights**: AI-generated insights about the conversation

### Visualizations

When you opt to generate visualizations, the system creates:

- **Message Timeline**: Activity over time
- **Sentiment Charts**: Sentiment analysis visualizations
- **Topic Word Cloud**: Visual representation of topics
- **Participant Profiles**: Individual radar charts showing personality metrics
- **Participant Interests**: Word clouds of each person's interests and ideas
- **Media Analysis**: File type distribution charts
- **Interactive Dashboard**: Comprehensive Plotly dashboard (open `index.html` in browser)

### Output Files

- `analysis_YYYYMMDD_HHMMSS.json`: Complete analysis results in JSON format
- `visualizations_YYYYMMDD_HHMMSS/`: Directory containing all visualization files
  - `index.html`: Main page to view all visualizations
  - Various PNG files for static charts
  - `interactive_dashboard.html`: Interactive Plotly dashboard

---

## 📁 Project Structure

- `app.py` - Main entry point with auto-login flow
- `lib/` - All library modules
  - `commands.py` - All CLI command implementations
  - `util.py` - Menu and utility functions
  - `config.py` - Configuration and constants
  - `storage.py` - Token storage and management
  - `oauth.py` - OAuth2 + PKCE implementation
  - `browser.py` - Browser automation for authentication
  - `parser.py` - Discord HTML export parser
  - `analyzer.py` - Main analysis orchestrator
  - `gemini.py` - Gemini AI analyzer with conversation analysis
  - `wrapper.py` - Gemini API wrapper with retry logic
  - `media.py` - Media file analyzer (images, videos, audio)
  - `visualizer.py` - Visualization generation (charts, graphs, dashboards)
  - `exporter/` - DiscordChatExporter.Cli binary
- `exports/` - Directory for exported channel data and analysis results

---

## 📜 License

MIT
