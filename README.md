This is a dynamic Stock Scraper to scrape Title, Stock Status and Price. Product URLs can be defined in products_to_scrape.json and the site must have a relevent websites_config.json config where you define the BeautifulSoup HTML tags for product_name, stock_status and price. Output is in json format.

ToDo:

- Current json output for stock levels are not consistent. Map via websites_config.json where if out of stock its always outputted as "Out of Stock" instead of availability_status_preorder for example 