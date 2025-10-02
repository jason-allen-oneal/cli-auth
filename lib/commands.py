# commands.py - All CLI commands in one place
import os, requests, urllib.parse, threading, json, http.server, subprocess
from lib.config import DISCORD_TOKEN, DISCORD_ME, DISCORD_GUILDS, DISCORD_CHANNELS, DISCORD_DM_CHANNELS, CONFIG_PATH, EXPORT_DIR
from lib.storage import read_tokens, write_tokens, now
from lib.oauth import gen_code_verifier, gen_code_challenge, CodeHandler, find_free_port
from lib.browser import open_and_capture

os.makedirs(EXPORT_DIR, exist_ok=True)


def fetch_guilds(access_token):
    """Fetch list of guilds the user belongs to"""
    r = requests.get(DISCORD_GUILDS, headers={"Authorization": f"Bearer {access_token}"}, timeout=30)
    if r.status_code != 200:
        raise RuntimeError(f"Failed to fetch guilds: {r.status_code} - {r.text}")
    return r.json()


def fetch_guild_channels(guild_id, access_token):
    """Fetch channels for a specific guild"""
    url = DISCORD_CHANNELS.format(guild_id=guild_id)
    r = requests.get(url, headers={"Authorization": f"Bearer {access_token}"}, timeout=30)
    if r.status_code != 200:
        raise RuntimeError(f"Failed to fetch channels: {r.status_code} - {r.text}")
    return r.json()


def fetch_dm_channels(access_token):
    """Fetch DM channels"""
    r = requests.get(DISCORD_DM_CHANNELS, headers={"Authorization": f"Bearer {access_token}"}, timeout=30)
    if r.status_code != 200:
        raise RuntimeError(f"Failed to fetch DM channels: {r.status_code} - {r.text}")
    return r.json()


def perform_authentication():
    """
    Perform Discord OAuth2 authentication with PKCE flow.
    Renamed from cmd_login to reflect its automatic nature.
    """
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


def cmd_whoami(_):
    """Display current user information"""
    tok = read_tokens()
    if not tok:
        raise RuntimeError("Not logged in")
    r = requests.get(DISCORD_ME, headers={"Authorization": f"Bearer {tok['access_token']}"})
    print(json.dumps(r.json(), indent=2))


def cmd_guilds(_):
    """List all guilds the user belongs to"""
    tok = read_tokens()
    if not tok:
        raise RuntimeError("Not logged in")
    r = requests.get(DISCORD_GUILDS, headers={"Authorization": f"Bearer {tok['access_token']}"})
    print(json.dumps(r.json(), indent=2))


def cmd_logout(_):
    """Log out and delete stored tokens"""
    if os.path.exists(CONFIG_PATH):
        os.remove(CONFIG_PATH)
        print("Local tokens deleted.")
    else:
        print("Already logged out.")


def cmd_export(_):
    """Export Discord channel data using DiscordChatExporter.Cli"""
    tok = read_tokens()
    if not tok:
        raise RuntimeError("Not logged in")

    # Use auth_header if available
    auth_token = tok.get("auth_header")
    if not auth_token:
        raise RuntimeError("No auth_token found. Try logging in again.")

    access_token = tok.get("access_token")

    # Select export mode
    print("\n=== Export Mode ===")
    print("1. Export a specific channel (by ID)")
    print("2. Export all channels from a guild/server")
    print("3. Export a DM channel (by ID)")
    mode = input("Choose export mode (1/2/3): ").strip()

    channel_ids = []
    guild_export = False
    guild_id = None

    if mode == "1":
        # Single channel by ID
        channel_id = input("Enter the channel ID to export: ").strip()
        if not channel_id:
            print("❌ Channel ID is required.")
            return
        channel_ids = [channel_id]
    
    elif mode == "2":
        # Export from guild
        print("\nFetching your guilds...")
        try:
            guilds = fetch_guilds(access_token)
            if not guilds:
                print("❌ No guilds found.")
                return
            
            print("\n=== Your Guilds ===")
            for idx, guild in enumerate(guilds, 1):
                print(f"{idx}. {guild['name']} (ID: {guild['id']})")
            
            guild_choice = input(f"\nSelect a guild (1-{len(guilds)}): ").strip()
            try:
                guild_idx = int(guild_choice) - 1
                if guild_idx < 0 or guild_idx >= len(guilds):
                    print("❌ Invalid selection.")
                    return
                selected_guild = guilds[guild_idx]
                guild_id = selected_guild['id']
                print(f"\n✅ Selected: {selected_guild['name']}")
                guild_export = True
            except ValueError:
                print("❌ Invalid input.")
                return
        except Exception as e:
            print(f"❌ Error fetching guilds: {e}")
            return
    
    elif mode == "3":
        # DM channel by ID
        dm_id = input("Enter the DM channel ID to export: ").strip()
        if not dm_id:
            print("❌ DM channel ID is required.")
            return
        channel_ids = [dm_id]
    
    else:
        print("❌ Invalid choice.")
        return

    # Prompt user for format
    print("\n=== Export Format ===")
    print("1. JSON")
    print("2. HTML (Dark)")
    print("3. HTML (Light)")
    print("4. CSV")
    print("5. Plain Text")
    fmt_choice = input("Choose format (1/2/3/4/5): ").strip()

    if fmt_choice == "1":
        fmt = "Json"
        ext = "json"
    elif fmt_choice == "2":
        fmt = "HtmlDark"
        ext = "html"
    elif fmt_choice == "3":
        fmt = "HtmlLight"
        ext = "html"
    elif fmt_choice == "4":
        fmt = "Csv"
        ext = "csv"
    elif fmt_choice == "5":
        fmt = "PlainText"
        ext = "txt"
    else:
        print("❌ Invalid choice.")
        return

    # Date range options
    print("\n=== Date Range (Optional) ===")
    use_date_range = input("Filter by date range? (y/N): ").strip().lower() == "y"
    after_date = None
    before_date = None
    
    if use_date_range:
        after_date = input("Start date (YYYY-MM-DD or message ID, leave empty to skip): ").strip()
        before_date = input("End date (YYYY-MM-DD or message ID, leave empty to skip): ").strip()
        if not after_date:
            after_date = None
        if not before_date:
            before_date = None

    # Media download option
    download_media = input("\nDownload all media attachments? (y/N): ").strip().lower() == "y"

    # Thread inclusion option
    print("\n=== Thread Inclusion ===")
    print("1. None")
    print("2. Active threads only")
    print("3. All threads")
    thread_choice = input("Include threads? (1/2/3, default=1): ").strip() or "1"
    
    if thread_choice == "2":
        include_threads = "Active"
    elif thread_choice == "3":
        include_threads = "All"
    else:
        include_threads = "None"

    # Build command
    if guild_export:
        # Use exportguild command
        output_dir = os.path.join(EXPORT_DIR, f"guild_{guild_id}/")
        os.makedirs(output_dir, exist_ok=True)
        
        cmd = [
            "./lib/exporter/DiscordChatExporter.Cli",
            "exportguild",
            "--guild", guild_id,
            "--token", auth_token,
            "-f", fmt,
            "-o", output_dir,
            "--include-threads", include_threads
        ]
    else:
        # Use export command for single channel
        channel_id = channel_ids[0]
        output_file = os.path.join(EXPORT_DIR, f"export_{channel_id}.{ext}")
        
        cmd = [
            "./lib/exporter/DiscordChatExporter.Cli",
            "export",
            "--channel", channel_id,
            "--token", auth_token,
            "-f", fmt,
            "-o", output_file,
            "--include-threads", include_threads
        ]

    # Add optional parameters
    if after_date:
        cmd.extend(["--after", after_date])
    if before_date:
        cmd.extend(["--before", before_date])
    if download_media:
        cmd.append("--media")

    # Execute export
    try:
        print("\n🚀 Starting export...")
        subprocess.run(cmd, check=True)
        print(f"\n✅ Export complete!")
        if guild_export:
            print(f"📁 Output directory: {output_dir}")
        else:
            print(f"📁 Output file: {output_file}")
        if download_media:
            print("✅ Media attachments downloaded as well.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Export failed: {e}")


def cmd_analyze(_):
    """Analyze exported data"""
    # Placeholder for future implementation
    print("Analyze functionality coming soon...")
    pass
