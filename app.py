import asyncio
import sys
import streamlit as st
import pandas as pd
from scraper import scrape_seek_jobs

# Fix for Windows asyncio subprocess issue
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

st.title("Australian Job Scraper - Seek Only")
st.write("Scrape jobs from Seek in Australia")

# Sidebar inputs
query = st.text_input("Job title or keyword", value="Data Analyst")
location = st.text_input("Location", value="Melbourne")
pages = st.number_input("Pages to scrape (Seek)", min_value=1, max_value=5, value=2)
headless = st.checkbox("Run browser in headless mode", value=True)

if st.button("Scrape Jobs"):
    with st.spinner("Scraping jobs... this may take a while"):
        # Run the async scraper safely
        df = asyncio.run(scrape_seek_jobs(query, location, pages=pages, headless=headless))
    
    if df.empty:
        st.warning("No jobs found.")
    else:
        st.success(f"Found {len(df)} jobs!")
        st.dataframe(df)
        st.download_button(
            "Download as CSV",
            data=df.to_csv(index=False),
            file_name=f"{query}_{location}_jobs.csv",
            mime="text/csv"
        )
