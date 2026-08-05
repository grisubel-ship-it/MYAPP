#!/opt/plugins-venv/bin/python
import asyncio
from playwright.async_api import async_playwright
import os

URL = "https://app-release-config.preview.emergentagent.com"
OUT = "/app/release/screenshots"
os.makedirs(OUT, exist_ok=True)

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        # Contesto ad alta risoluzione: viewport 540x960 CSS + deviceScaleFactor 2 → screenshot 1080x1920 nativo
        context = await browser.new_context(
            viewport={"width": 540, "height": 960},
            device_scale_factor=2,
        )
        page = await context.new_page()
        await page.goto(URL, wait_until="networkidle", timeout=25000)
        await page.wait_for_timeout(1200)

        # 1) HOME
        await page.screenshot(path=f"{OUT}/01-home.png", type="png", full_page=False)
        print("1 ✓ home")

        # Apri Maria Rossi
        buttons = page.locator('[data-testid^="open-patient-"]')
        n = await buttons.count()
        for i in range(n):
            t = await buttons.nth(i).inner_text()
            if "Maria" in t:
                await buttons.nth(i).click(force=True)
                break
        await page.wait_for_timeout(2000)

        # 2) DETAIL — vista alto con AI card + consegne + trend
        await page.screenshot(path=f"{OUT}/02-detail.png", type="png", full_page=False)
        print("2 ✓ detail")

        # 3) HANDOVER dialog aperto
        hist = page.locator('[data-testid^="handover-history-"]').first
        await hist.click(force=True)
        await page.wait_for_timeout(1500)
        await page.screenshot(path=f"{OUT}/03-handover.png", type="png", full_page=False)
        print("3 ✓ handover")
        await page.click('[data-testid="handover-close-btn"]', force=True)
        await page.wait_for_timeout(500)

        # 4) TREND CHART centrato — scroll + cambia parametro a Glicemia
        await page.evaluate("window.scrollTo(0, 380)")
        await page.wait_for_timeout(500)
        try:
            await page.click('[data-testid="trend-select"]', force=True)
            await page.wait_for_timeout(300)
            glc = page.locator('div[role="option"]:has-text("Glicemia")').first
            if await glc.count() > 0:
                await glc.click(force=True)
        except Exception:
            pass
        await page.wait_for_timeout(1000)
        await page.screenshot(path=f"{OUT}/04-trend.png", type="png", full_page=False)
        print("4 ✓ trend")

        # 5) MENU ⋮ APERTO su voce diario
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(500)
        menu = page.locator('[data-testid^="entry-"][data-testid$="-menu-btn"]').first
        await menu.click(force=True)
        await page.wait_for_timeout(600)
        await page.screenshot(path=f"{OUT}/05-menu.png", type="png", full_page=False)
        print("5 ✓ menu")

        await browser.close()
        print("DONE")

asyncio.run(main())
