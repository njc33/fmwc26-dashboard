import json
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

def load_credentials():
    with open("fantrax_credentials.json", "r") as f:
        return json.load(f)

def get_fantrax_token():
    creds = load_credentials()
    username = creds["username"]
    password = creds["password"]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # 1. Go to Fantrax home
        page.goto("https://www.fantrax.com/home")
        page.wait_for_load_state("networkidle")

        # 2. Click the Login button (retry until modal appears)
        for _ in range(10):
            try:
                page.get_by_role("button", name="Login").click()
                page.wait_for_selector("text=Email or User ID", timeout=3000)
                break
            except PlaywrightTimeout:
                print("Login modal not detected yet, retrying...")
                time.sleep(1)
        else:
            raise Exception("Could not open login modal")

        # 3. Fill modal login form (retry-safe)
        for _ in range(10):
            try:
                page.get_by_placeholder("Email or User ID").fill(username)
                page.get_by_placeholder("Password").fill(password)
                break
            except PlaywrightTimeout:
                print("Modal fields not ready, retrying...")
                time.sleep(1)

        # 4. Click the modal Log In button (the second one)
        for _ in range(10):
            try:
                page.get_by_role("button", name="Login").nth(1).click()
                break
            except PlaywrightTimeout:
                print("Modal login button not ready, retrying...")
                time.sleep(1)

        # 5. Wait for login to complete
        print("Waiting for login to complete...")
        time.sleep(5)

        token = None

        # 6. Attach listener AFTER login
        def handle_request(request):
            nonlocal token
            auth = request.headers.get("authorization")
            if auth and auth.startswith("Bearer "):
                token = auth

        context.on("request", handle_request)

        # 7. Trigger API calls
        print("Navigating to league page to trigger API calls...")
        page.goto("https://www.fantrax.com/fantasy/league")
        page.wait_for_load_state("networkidle")
        time.sleep(5)

        browser.close()

        if not token:
            raise Exception("Could not find Fantrax Bearer token")

        return token


if __name__ == "__main__":
    token = get_fantrax_token()
    print("TOKEN:", token)