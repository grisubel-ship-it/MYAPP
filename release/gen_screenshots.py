"""Generate Play Store screenshots at 1080x1920 (9:16, PNG)."""
import asyncio
import os
from playwright.async_api import async_playwright

URL = "https://app-release-config.preview.emergentagent.com"
OUT = "/app/release/screenshots"
P3 = os.environ.get("P3_ID", "")

async def shoot(page, url, path, wait=1500, before=None):
    await page.goto(url, wait_until="networkidle", timeout=30000)
    await page.wait_for_timeout(wait)
    if before:
        await before(page)
    await page.screenshot(path=path, full_page=False, type="png")
    print(f"OK: {path}")

async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(args=["--no-sandbox"])
        ctx = await browser.new_context(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
        page = await ctx.new_page()

        # 1. Home dashboard
        await shoot(page, f"{URL}/", f"{OUT}/01-home.png")

        # 2. Patient detail top (name + Consegna IA + chart + form)
        await shoot(page, f"{URL}/paziente/{P3}", f"{OUT}/02-detail.png")

        # 3. Diary + chart scrolled (shows entries + trend clearly)
        async def scroll_a(page):
            await page.evaluate("window.scrollTo(0, 500)")
            await page.wait_for_timeout(600)
        await shoot(page, f"{URL}/paziente/{P3}", f"{OUT}/03-diary.png", before=scroll_a)

        # 4. Settings / GDPR page
        await shoot(page, f"{URL}/impostazioni", f"{OUT}/04-settings.png")

        await browser.close()

asyncio.run(main())
