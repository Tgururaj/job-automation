import asyncio
import sys
import pandas as pd
import random
from playwright.async_api import async_playwright

# Fix for Windows asyncio subprocess issue
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

async def scrape_seek_jobs(query, location, pages=1, headless=True):
    jobs = []
    query = query.replace(" ", "-")
    location = location.replace(" ", "-")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=headless,
            args=[
                "--disable-blink-features=AutomationControlled",  # hide automation
                "--no-sandbox",
                "--disable-setuid-sandbox"
            ]
        )

        # Create browser context with viewport and user agent
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/115.0.0.0 Safari/537.36"
        )

        page = await context.new_page()

        for page_num in range(pages):
            url = f"https://www.seek.com.au/{query}-jobs/in-{location}?page={page_num+1}"
            await page.goto(url, timeout=60000)
            await asyncio.sleep(random.uniform(2, 5))  # human-like delay

            cards = await page.query_selector_all("article")
            if not cards:
                print(f"No Seek job cards found on page {page_num+1}")
                continue

            for card in cards:
                title_tag = await card.query_selector("h1, h2, h3, h4, h5, h6")
                company_tag = await card.query_selector(".job-company")
                link_tag = await card.query_selector("a")

                jobs.append({
                    "Title": await title_tag.inner_text() if title_tag else "N/A",
                    "Company": await company_tag.inner_text() if company_tag else "N/A",
                    "Link": await link_tag.get_attribute("href") if link_tag else "N/A",
                    "Source": "Seek"
                })

        await browser.close()
    return pd.DataFrame(jobs)
