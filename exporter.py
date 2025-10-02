# exporter.py
import os, subprocess
from storage import read_tokens
from config import EXPORT_DIR

os.makedirs(EXPORT_DIR, exist_ok=True)


def cmd_export(_):
    tok = read_tokens()
    if not tok:
        raise RuntimeError("Not logged in")

    # Prompt user for channel ID
    channel_id = input("Enter the channel ID to export: ").strip()

    # Prompt user for format
    print("Select export format:")
    print("1. JSON")
    print("2. HTML (Dark)")
    print("3. HTML (Light)")
    print("4. CSV")
    fmt_choice = input("Choose (1/2/3/4): ").strip()

    if fmt_choice == "1":
        fmt = "Json"
        ext = "json"
    elif fmt_choice == "2":
        fmt = "HtmlDark"
        ext = "htmldark"
    elif fmt_choice == "3":
        fmt = "HtmlLight"
        ext = "htmllight"
    elif fmt_choice == "4":
        fmt = "Csv"
        ext = "csv"
    else:
        print("Invalid choice.")
        return

    # Prompt user about media
    download_media = input("Download all media attachments? (y/N): ").strip().lower() == "y"

    # Use auth_header if available, else fallback to access_token
    auth_token = tok.get("auth_header")  # <- use raw user token
    if not auth_token:
        raise RuntimeError("No auth_token found. Try logging in again.")

    output_file = os.path.join(EXPORT_DIR, f"export_{channel_id}.{ext}")

    cmd = [
        "./lib/exporter/DiscordChatExporter.Cli",
        "export",
        "--channel", channel_id,
        "--token", auth_token,
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
        print(f"❌ Export failed: {e}")
