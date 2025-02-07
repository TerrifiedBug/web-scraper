import requests
import json
from bs4 import BeautifulSoup

# Load website configurations from JSON file
with open("websites_config.json", "r") as config_file:
    WEBSITES_CONFIG = json.load(config_file)

# Load product URLs to scrape from JSON file
with open("products_to_scrape.json", "r") as product_file:
    PRODUCTS_TO_SCRAPE = json.load(product_file)

# Fake headers to bypass bot detection
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Function to extract values dynamically
def extract_value(soup, strategy, stock_mappings=None):
    """Extracts a value from the soup based on the given strategy."""
    if strategy["type"] == "meta":
        tag = soup.find("meta", {"property": strategy["property"]})
        return tag["content"].strip() if tag else "Unknown"

    elif strategy["type"] == "selector":
        tag = soup.select_one(strategy["selector"])
        return tag.text.strip() if tag else "Unknown"

    elif strategy["type"] == "attribute":
        tag = soup.select_one(strategy["selector"])
        return tag.get(strategy["attribute"], "Unknown").strip() if tag else "Unknown"

    elif strategy["type"] == "text":
        tag = soup.select_one(strategy["selector"])
        return tag.text.strip() if tag else "Unknown"

    elif strategy["type"] == "class":
        tag = soup.select_one(strategy["selector"])
        if tag:
            class_list = tag.get("class", [])
            for cls in class_list:
                if cls in stock_mappings:
                    return stock_mappings[cls]
            return "Unknown"

    return "Unknown"

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