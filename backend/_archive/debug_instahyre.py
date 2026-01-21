import asyncio
from playwright.async_api import async_playwright

async def debug_instahyre():
    url = "https://www.instahyre.com/python-jobs/"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(5)
            
            cards = await page.query_selector_all("div[class*='opportunity']")
            print(f"Found {len(cards)} opportunity cards\n")
            
            for i, card in enumerate(cards[:3], 1):
                print(f"--- Card {i} ---")
                text = await card.inner_text()
                print(f"Text:\n{text}\n")
                
                # Check for links
                links = await card.query_selector_all("a")
                print(f"Links in card: {len(links)}")
                for link in links[:2]:
                    href = await link.get_attribute("href")
                    link_text = await link.inner_text()
                    print(f"  - {href} ({link_text[:50]})")
                
                print()
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_instahyre())
