import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Levenshtein import distance as levenshtein_distance  # Make sure to install python-Levenshtein
import re
def search_reliancedigital(product_name):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service("C:/Users/Rajan/OneDrive/Desktop/Likenings Project/chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    url = f"https://www.reliancedigital.in/search?q={product_name}"
    driver.get(url)
    time.sleep(5)  # Let the page load

    products = []  # To store all product data

    try:
        # Scrape the top 10-15 products
        product_elems = driver.find_elements(By.CSS_SELECTOR, "li.grid.pl__container__sp.blk__lg__3.blk__md__4.blk__sm__6.blk__xs__6")[:15]

        for product_elem in product_elems:
            product_data = {}
            try:
                # Locate the div and anchor tag within the li element
                div_elem = product_elem.find_element(By.CSS_SELECTOR, "div.sp.grid")
                anchor_elem = div_elem.find_element(By.CSS_SELECTOR, "a[attr-tag='anchor']")
                title_elem = product_elem.find_element(By.CSS_SELECTOR, "p.sp__name")

                # Extract the product URL
                product_data['url'] = anchor_elem.get_attribute('href')

                # Extract the title
                product_data['title'] = title_elem.text.strip()

                # Price
                price_elem = product_elem.find_element(By.CSS_SELECTOR, "span.TextWeb__Text-sc-1cyx778-0.gimCrs")
                child_spans = price_elem.find_elements(By.TAG_NAME, "span")
                price_text = ''.join([span.text.strip() for span in child_spans])
                product_data['price'] = price_text

                # Discount (may not always be present)
                try:
                    discount_elem = product_elem.find_element(By.CSS_SELECTOR, "span.TextWeb__Text-sc-1cyx778-0.jhOcrk.Block-sc-u1lygz-0.SpmXl, span.priceboxm__save.sp__price__mrp:not(:empty)")
                    product_data['discount'] = discount_elem.text.strip()
                except Exception as e:
                    product_data['discount'] = 'No discount available'
                    logging.info(f"Discount element not found: {e}")

                # Offers (may not always be present)
                try:
                    offers_elem = product_elem.find_element(By.CSS_SELECTOR, "div.Block-sc-u1lygz-0.bRRPwi.sp__chip, div.Block-sc-u1lygz-0.gySVZc.sp__chip")
                    child_divs = offers_elem.find_elements(By.TAG_NAME, "div")
                    offers_text = ' '.join([div.text.strip() for div in child_divs])
                    product_data['offers'] = offers_text
                except Exception as e:
                    product_data['offers'] = 'No offers available'
                    logging.info(f"Offers element not found: {e}")

                products.append(product_data)  # Add to the list of products
            except Exception as e:
                logging.error(f"Error scraping a product: {e}")
                continue

        # If no products found, return None
        if not products:
            return None
        print(products)
        

        # Return the best match
        return products
            
        

    except Exception as e:
        logging.error(f"Error scraping Reliance Digital: {e}")
        return None
    finally:
        driver.quit()

# Function to clean and normalize text (remove stopwords and special characters)
def normalize(text):
    # Convert text to lowercase
    text = text.lower()
    # Remove special characters and extra spaces
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip()

# Modified function with normalization and improved matching
def find_best_match(product_list, search_query):
    search_query = normalize(search_query)
    best_match = None
    highest_score = float('inf')  # Initialize with a high value

    for product in product_list:
        product_title = normalize(product['title'])
        # Calculate the Levenshtein distance
        distance = levenshtein_distance(search_query, product_title)

        # Find the product with the smallest distance (best match)
        if distance < highest_score:
            highest_score = distance
            best_match = product

    return best_match

print(find_best_match(search_reliancedigital("Apple iphone 13 128GB Midnight"),"Apple iphone 13 128GB Midnight"))