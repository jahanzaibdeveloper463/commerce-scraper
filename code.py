"""
Project: E-Commerce Catalog Scraper & Excel Exporter
Author: Jahanzaib
Description: Production-ready web scraper that extracts product inventory 
             data across multi-page catalogs and serializes it into structured 
             Excel worksheets using pandas.
"""

import sys
import logging
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Configure standard stream logging for pipeline visibility
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"
OUTPUT_FILENAME = "ecommerce_products_export.xlsx"
MAX_PAGES = 3

def extract_catalog_data():
    """Iterates through target catalog pages, extracts DOM nodes, 
    parses attributes, and returns a flat dataset list."""
    scraped_records = []
    
    logging.info("Initializing scraping sequence...")

    for page_idx in range(1, MAX_PAGES + 1):
        target_url = BASE_URL.format(page_idx)
        logging.info(f"Fetching payload from target: {target_url}")
        
        try:
            response = requests.get(target_url, timeout=10)
            response.raise_for_status() # Raise HTTPError for bad status codes (4xx/5xx)
        except requests.exceptions.RequestException as err:
            logging.error(f"Network exception encountered on page {page_idx}: {err}")
            continue

        # Parse raw markup into traversable DOM tree
        soup = BeautifulSoup(response.text, "html.parser")
        product_pods = soup.find_all("article", class_="product_pod")
        
        if not product_pods:
            logging.warning(f"No product nodes resolved on page {page_idx}. Terminating pagination.")
            break

        for pod in product_pods:
            # Extract title attribute safely from nested anchor node
            anchor_tag = pod.find("h3").find("a")
            title = anchor_tag.get("title", "").strip()
            
            # Normalize price string to raw float value
            raw_price = pod.find("p", class_="price_color").text
            cleaned_price = float(raw_price.replace("Â£", "").replace("£", "").strip())
            
            # Extract stock state metadata
            stock_state = pod.find("p", class_="instock availability").text.strip()
            
            # Construct absolute resource URI
            relative_uri = anchor_tag.get("href", "")
            absolute_url = "https://books.toscrape.com/catalogue/" + relative_uri.replace("../", "")
            
            # Append normalized dictionary record
            scraped_records.append({
                "Product Title": title,
                "Price (GBP)": cleaned_price,
                "Availability": stock_state,
                "Product URL": absolute_url
            })

    logging.info(f"Extraction complete. Total records harvested: {len(scraped_records)}")
    return scraped_records

def export_to_spreadsheet(data_records):
    """Serializes dataset records into a formatted .xlsx spreadsheet file."""
    if not data_records:
        logging.warning("Dataset is empty. Skipping file generation.")
        return

    logging.info("Serializing dataset into DataFrame...")
    dataframe = pd.DataFrame(data_records)

    # Export buffer without internal pandas index row numbering
    dataframe.to_excel(OUTPUT_FILENAME, index=False)
    logging.info(f"Successfully flushed spreadsheet to disk: {OUTPUT_FILENAME}")

if __name__ == "__main__":
    raw_data = extract_catalog_data()
    export_to_spreadsheet(raw_data)
