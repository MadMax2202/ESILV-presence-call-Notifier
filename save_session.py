from playwright.sync_api import sync_playwright

START_URL = "https://my.devinci.fr/student/presences/"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    ctx = browser.new_context()
    page = ctx.new_page()
    page.goto(START_URL)

    print("Log in manually in the opened browser. Then press Enter here.")
    input()

    ctx.storage_state(path="session.json")
    browser.close()
    print("Saved session.json")
