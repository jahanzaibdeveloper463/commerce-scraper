# ==========================================
# VIP PROJECT: E-Commerce Product & Price Scraper
# Author: Jahanzaib (Indie AI Engineer & Scraper)
# ==========================================

import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_books_to_excel():
    print("🚀 [INFO] Web scraping process started...")
    
    # Target: Books to Scrape (Demo e-commerce site for testing/scraping)
    base_url = "https://books.toscrape.com/catalogue/page-{}.html"
    
    all_products = []
    
    # Hum pehle 3 pages se data scrape karenge (Aap isay increase bhi kar sakte hain)
    for page in range(1, 4):
        target_url = base_url.format(page)
        print(f"📄 Scraping Page {page}: {target_url}")
        
        response = requests.get(target_url)
        
        if response.status_code != 200:
            print(f"❌ Error: Page {page} load nahi hua. Status: {response.status_code}")
            continue
            
        soup = BeautifulSoup(response.text, "html.parser")
        products = soup.find_all("article", class_="product_pod")
        
        for product in products:
            # Product Title
            title = product.find("h3").find("a")["title"]
            
            # Product Price
            price_raw = product.find("p", class_="price_color").text
            # Price string se currency symbol (£) hatane ke liye
            price = price_raw.replace("Â£", "£").replace("£", "") 
            
            # Stock Status
            stock_status = product.find("p", class_="instock availability").text.strip()
            
            # Product Detail Link
            relative_link = product.find("h3").find("a")["href"]
            product_link = "https://books.toscrape.com/catalogue/" + relative_link.replace("../", "")
            
            # Data dictionary mein store karna
            all_products.append({
                "Product Title": title,
                "Price (GBP)": float(price),
                "Availability": stock_status,
                "Product URL": product_link
            })
            
    # Pandas DataFrame mein convert karna
    df = pd.DataFrame(all_products)
    
    # Excel file mein export karna (Bina index ke)
    excel_filename = "ecommerce_products_export.xlsx"
    df.to_excel(excel_filename, index=False)
    
    print(f"\n✅ SUCCESS! Total {len(all_products)} products successfully scrape ho gaye hain.")
    print(f"📁 File saved as: '{excel_filename}' (WPS Office ya Google Sheets mein open karein).")

if __name__ == "__main__":
    scrape_books_to_excel()
