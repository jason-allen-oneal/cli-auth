from playwright.sync_api import sync_playwright

def open_and_capture(url, redirect_uri):
    token_container = {"auth": None}  # mutable dict to hold captured header

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False)  # visible window so user can log in
        page = browser.new_page()

        # Hook into requests to capture the Discord "authorization" header
        def on_request(request):
            if "oauth2/authorize" in request.url and "authorization" in request.headers:
                token_container["auth"] = request.headers["authorization"]

        # Attach listener
        page.on("request", on_request)

        # Navigate to OAuth2 page
        page.goto(url)

        # Step 1: check if login redirect occurs
        try:
            page.wait_for_url("**/login*", timeout=5000)
            print("User was redirected to login...")
            # Step 2: wait until login completes and we’re back on OAuth2 authorize page
            page.wait_for_url("**/oauth2/authorize*", timeout=120000)
            print("Login complete, back on OAuth2 authorize.")
        except:
            print("Already authenticated, skipping login step.")

        # Step 3: wait until redirect back to our callback
        page.wait_for_url(f"{redirect_uri}*")
        final_url = page.url

        browser.close()
        return final_url, token_container["auth"]
