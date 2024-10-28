import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

#Scaraping from Reliance Digital
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

# Function to clean and normalize text (remove special characters, lowercase, etc.)
def normalize(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)  # Remove special characters
    return text.strip()

# Function to find the best match using TF-IDF and Cosine Similarity
def find_best_match_tfidf(product_list, search_query):
    # Normalize search query and product titles
    search_query = normalize(search_query)
    product_titles = [normalize(product['title']) for product in product_list]

    # Combine the search query with product titles for vectorization
    documents = [search_query] + product_titles

    # Initialize the TF-IDF Vectorizer
    vectorizer = TfidfVectorizer()

    # Fit and transform the documents into a TF-IDF matrix
    tfidf_matrix = vectorizer.fit_transform(documents)

    # Calculate Cosine Similarity between the search query and all product titles
    cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

    # Find the index of the highest similarity score
    best_match_index = cosine_similarities.argmax()

    # Return the product with the highest cosine similarity
    return product_list[best_match_index]

# Example usage with search query and product data
product_list = search_reliancedigital("Apple iphone 13 128GB Midnight")
best_product = find_best_match_tfidf(product_list, "Apple iphone 13 128GB Midnight")

print("Best Match:", best_product)


# Scraping from Vijay Sales
def search_vijaysales(query):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service("C:/Users/Rajan/OneDrive/Desktop/Likenings Project/chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    url = f"https://www.vijaysales.com/search/{query}"
    driver.get(url)
    time.sleep(5)  # Allow the page to load

    products = []  # To store all product data

    try:
        # Scrape the top 10-15 products
        product_elems = driver.find_elements(By.CSS_SELECTOR, "div.BcktPrd")[:15]  # Limit to top 15

        for product_elem in product_elems:
            product_data = {}
            try:
                # Product title
                name_elem = product_elem.find_element(By.CSS_SELECTOR, "h2.BcktPrdNm_")
                product_data['title'] = name_elem.text.strip()

                # Product price
                price_elem = product_elem.find_element(By.CSS_SELECTOR, "span.Prdvsprc_")
                product_data['price'] = price_elem.text.strip()

                # Product offers
                try:
                    offer_elem = product_elem.find_element(By.CSS_SELECTOR, "div.BcktPrdemi.h54")
                    product_data['offers'] = offer_elem.text.strip()
                except Exception as e:
                    product_data['offers'] = 'No offers available'

                # Product discount
                try:
                    discount_elem = product_elem.find_element(By.CSS_SELECTOR, "span.ofrnm_")
                    product_data['discount'] = discount_elem.text.strip()
                except Exception as e:
                    product_data['discount'] = 'No discount available'

                # Product URL
                link_elem = product_elem.find_element(By.CSS_SELECTOR, "a[href]")
                product_data['url'] = link_elem.get_attribute('href')

                products.append(product_data)  # Add product data to the list
            except Exception as e:
                logging.error(f"Error scraping a product: {e}")
                continue
        print(products)
        # If no products are found, return None
        if not products:
            return None

        # Return all scraped products
        return products

    except Exception as e:
        logging.error(f"Error scraping Vijay Sales: {e}")
        return None
    finally:
        driver.quit()

# Example usage with search query and product data
product_list = search_vijaysales("oneplus 12r 8gb 128gb iron grey")
if product_list:
    best_product = find_best_match_tfidf(product_list, "oneplus 12r 8gb 128gb iron grey")
    print("Best Match:", best_product)
else:
    print("No products found from Vijay Sales.")



#Scaping from Croma
# Scraping from Croma
def search_croma(product_name):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service("C:/Users/Rajan/OneDrive/Desktop/Likenings Project/chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    url = f"https://www.croma.com/searchB?q={product_name}"
    driver.get(url)
    time.sleep(5)  # Let the page load

    products = []  # To store all product data

    try:
        # Scrape the top 10-15 products
        product_elems = driver.find_elements(By.CSS_SELECTOR, "div.plp-product-grid div.plp-card")[:15]

        for product_elem in product_elems:
            product_data = {}
            try:
                # Extract product title
                title_elem = product_elem.find_element(By.CSS_SELECTOR, "h3.product-title.plp-prod-title a")
                product_data['title'] = title_elem.text.strip()

                # Extract product URL
                product_data['url'] = title_elem.get_attribute('href')

                # Extract product price
                price_elem = product_elem.find_element(By.CSS_SELECTOR, "span.amount.plp-srp-new-amount")
                product_data['price'] = price_elem.text.strip()

                # Discount and offers (if available)
                try:
                    discount_elem = product_elem.find_element(By.CSS_SELECTOR, "span.dicount-value")
                    product_data['discount'] = discount_elem.text.strip()
                except Exception as e:
                    product_data['discount'] = 'No discount available'

                try:
                    saveprice_elem = product_elem.find_element(By.CSS_SELECTOR, "span.discount.discount-mob-plp.discount-newsearch-plp")
                    product_data['save_price'] = saveprice_elem.text.strip()
                except Exception as e:
                    product_data['save_price'] = 'No save price available'

                # Ratings (if available)
                try:
                    ratings_elem = product_elem.find_element(By.CSS_SELECTOR, "span.rating-text-icon")
                    product_data['ratings'] = ratings_elem.text.strip()
                except Exception as e:
                    product_data['ratings'] = 'No ratings available'

                products.append(product_data)  # Add to the list of products
            except Exception as e:
                logging.error(f"Error scraping a product: {e}")
                continue
        print(products)
        # If no products found, return None
        if not products:
            return None

        # Return the scraped product data
        return products

    except Exception as e:
        logging.error(f"Error scraping Croma: {e}")
        return None
    finally:
        driver.quit()

# Example usage with search query and product data
product_list = search_croma("Apple iphone 13 128GB Midnight")
if product_list:
    best_product = find_best_match_tfidf(product_list, "Apple iphone 13 128GB Midnight")
    print("Best Match:", best_product)