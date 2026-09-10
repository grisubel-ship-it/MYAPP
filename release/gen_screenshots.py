"""Generate Play Store safe screenshots with clear DEMO watermark.
1080x1920 PNG, no real health data."""
import asyncio
import os
from playwright.async_api import async_playwright

URL = "https://app-release-config.preview.emergentagent.com"
OUT = "/app/release/screenshots"
P3 = os.environ.get("P3_ID", "")

# CSS injected into every page to add a bright "ESEMPIO" watermark
DEMO_BADGE_CSS = """
  body::before {
    content: 'ESEMPIO · DATI FITTIZI';
    position: fixed;
    top: 92px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 9999;
    background: #fef3c7;
    color: #92400e;
    padding: 6px 16px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.5px;
    border: 2px solid #f59e0b;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    font-family: system-ui, sans-serif;
    pointer-events: none;
  }
"""

async def shoot(page, url, path, wait=1500, before=None):
    await page.goto(url, wait_until="networkidle", timeout=30000)
    await page.wait_for_timeout(wait)
    if before:
        await before(page)
    # Inject demo badge just before screenshot
    await page.add_style_tag(content=DEMO_BADGE_CSS)
    await page.wait_for_timeout(300)
    await page.screenshot(path=path, full_page=False, type="png")
    print(f"OK: {path}")

async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(args=["--no-sandbox"])
        ctx = await browser.new_context(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
        page = await ctx.new_page()

        # 1. Home dashboard
        await shoot(page, f"{URL}/", f"{OUT}/01-home.png")

        # 2. Patient detail top
        await shoot(page, f"{URL}/paziente/{P3}", f"{OUT}/02-detail.png")

        # 3. New patient form — shows the data-entry flow
        async def fill_form(page):
            try:
                await page.locator('[data-testid="patient-name-input"]').fill("Nome dell'assistito")
                await page.wait_for_timeout(200)
            except Exception as e:
                print("form fill skipped:", e)
        await shoot(page, f"{URL}/nuovo", f"{OUT}/03-new-patient.png", before=fill_form)

        # 4. Settings / GDPR page
        await shoot(page, f"{URL}/impostazioni", f"{OUT}/04-settings.png")

        await browser.close()

asyncio.run(main())
