import os
import json
import requests
from bs4 import BeautifulSoup

# Get the absolute path of the script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Construct the correct file paths
CONFIG_FILE_PATH = os.path.join(BASE_DIR, "websites_config.json")
PRODUCTS_FILE_PATH = os.path.join(BASE_DIR, "products_to_scrape.json")

# Load website configurations from JSON file
with open(CONFIG_FILE_PATH, "r") as config_file:
    WEBSITES_CONFIG = json.load(config_file)

# Load product URLs to scrape from JSON file
with open(PRODUCTS_FILE_PATH, "r") as product_file:
    PRODUCTS_TO_SCRAPE = json.load(product_file)

# Fake headers to bypass bot detection
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Function to extract values dynamically
def extract_value(soup, strategy, stock_mappings=None):
    """Extracts a value from the soup based on the given strategy and maps stock status correctly."""
    value = "Unknown"

    if strategy["type"] == "meta":
        tag = soup.find("meta", {"property": strategy["property"]})
        value = tag["content"].strip() if tag else "Unknown"

    elif strategy["type"] == "selector":
        tag = soup.select_one(strategy["selector"])
        value = tag.text.strip() if tag else "Unknown"

    elif strategy["type"] == "attribute":
        tag = soup.select_one(strategy["selector"])
        value = tag.get(strategy["attribute"], "Unknown").strip() if tag else "Unknown"

    elif strategy["type"] == "text":
        tag = soup.select_one(strategy["selector"])
        value = tag.text.strip() if tag else "Unknown"

    elif strategy["type"] == "class":
        tag = soup.select_one(strategy["selector"])
        if tag:
            class_list = tag.get("class", [])
            for cls in class_list:
                if cls in stock_mappings:
                    return stock_mappings[cls]
            value = "Unknown"

    # Map stock status using stock_mappings if applicable
    if stock_mappings and value in stock_mappings:
        return stock_mappings[value]
    
    return value
    
# List to store results
products_data = []

# Loop through each product URL
for product in PRODUCTS_TO_SCRAPE:
    url = product["url"]
    site = product["site"]

    # Ensure site config exists
    if site not in WEBSITES_CONFIG:
        print(f"Skipping {url}, no configuration found for site: {site}")
        continue

    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        page_soup = BeautifulSoup(response.text, "html.parser")

        # Get site-specific configurations
        site_config = WEBSITES_CONFIG[site]
        stock_mappings = site_config.get("stock_mappings", {})

        # Extract product details using defined rules
        product_name = extract_value(page_soup, site_config["product_name"])
        stock_status = extract_value(page_soup, site_config["stock_status"], stock_mappings)
        price = extract_value(page_soup, site_config["price"])

        # Remove currency symbols and commas from price
        price = price.replace("£", "").replace("$", "").replace(",", "").strip()

        # Store results in dictionary
        product_info = {
            "site": site,
            "product_name": product_name,
            "stock_status": stock_status,
            "price": price,
            "url": url
        }

        # Append to results list
        products_data.append(product_info)

    else:
        print(f"Failed to fetch {url}. HTTP Status Code: {response.status_code}")

# Print final JSON output
print(json.dumps(products_data, indent=4))