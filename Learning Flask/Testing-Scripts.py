'''import redis.asyncio as redis
import asyncio

#Testing if Connection for the Redis Server
async def test_redis_connection():
    redis_client = redis.from_url("redis://localhost:6379")
    try:
        await redis_client.ping()
        print("Connected to Redis")
    except Exception as e:
        print(f"Error connecting to Redis: {e}")
    finally:
        await redis_client.aclose()

def main():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    try:
        loop.run_until_complete(test_redis_connection())
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()

if __name__ == "__main__":
    main()'''


#Testing JSON Request
'''import requests

url = 'http://127.0.0.1:5000/search'
data = {
    "brand": "Apple",
    "model": "iPhone 13",
    "storage_type": "128GB",
    "color": "Starlight"
}
response = requests.post(url, json=data)
print(response.json())'''

#Testing to get the product URL
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
def search_reliancedigital(product_name):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service("C:/Users/Rajan/OneDrive/Desktop/Likenings Project/chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    url = f"https://www.reliancedigital.in/search?q={product_name}"
    driver.get(url)
    time.sleep(5)

    product_data = {}

    try:
        # Locate the first product's li element
        product_elem = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "li.grid.pl__container__sp.blk__lg__3.blk__md__4.blk__sm__6.blk__xs__6"))
        )
        
        # Locate the div and anchor tag within the li element
        div_elem = product_elem.find_element(By.CSS_SELECTOR, "div.sp.grid")
        anchor_elem = div_elem.find_element(By.CSS_SELECTOR, "a[attr-tag='anchor']")

        # Extract the product URL
        product_data['url'] = anchor_elem.get_attribute('href')

        # Extract the title
        product_data['title'] = anchor_elem.text.strip()

        # Price
        price_elem = driver.find_element(By.CSS_SELECTOR, "span.TextWeb__Text-sc-1cyx778-0.gimCrs")
        child_spans = price_elem.find_elements(By.TAG_NAME, "span")
        price_text = ''.join([span.text.strip() for span in child_spans])
        product_data['price'] = price_text

        # Discount (may not always be present)
        try:
            discount_elem = driver.find_element(By.CSS_SELECTOR, "span.TextWeb__Text-sc-1cyx778-0.jhOcrk.Block-sc-u1lygz-0.SpmXl, span.priceboxm__save.sp__price__mrp:not(:empty)")
            product_data['discount'] = discount_elem.text.strip()
        except Exception as e:
            product_data['discount'] = 'No discount available'
            logging.info(f"Discount element not found: {e}")

        # Offers (may not always be present)
        try:
            offers_elem = driver.find_element(By.CSS_SELECTOR, "div.Block-sc-u1lygz-0.bRRPwi.sp__chip, div.Block-sc-u1lygz-0.gySVZc.sp__chip")
            child_divs = offers_elem.find_elements(By.TAG_NAME, "div")
            offers_text = ' '.join([div.text.strip() for div in child_divs])
            product_data['offers'] = offers_text
        except Exception as e:
            product_data['offers'] = 'No offers available'
            logging.info(f"Offers element not found: {e}")

        return {
            'platform': 'Reliance Digital',
            'name': product_data.get('title', 'No title available'),
            'price': product_data.get('price', 'No price available'),
            'discount': product_data.get('discount', 'No discount available'),
            'offers': product_data.get('offers', 'No offers available'),
            'url': product_data.get('url', 'No URL available')
        }
    except Exception as e:
        logging.error(f"Error scraping Reliance Digital: {e}")
        return None
    finally:
        driver.quit()



def search_amazon(query):
    url = f"https://www.amazon.in/s?k={query}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
        'Accept-Language': 'en-US, en;q=0.5'
    }
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, "html.parser")
    
    # Extract product details
    product_containers = soup.find_all("div", {"data-component-type": "s-search-result"})
    for container in product_containers:
        # Check for sponsored tag more robustly
        sponsored = container.find("span", class_="a-color-secondary")
        sponsored_badge = container.find("span", class_="puis-sponsored-label-text")
        
        if (sponsored and "Sponsored" in sponsored.text.strip()) or sponsored_badge:
            continue

        name_elem = container.find("span", class_="a-size-medium a-color-base a-text-normal")
        price_elem = container.find("span", class_="a-offscreen")
        stars_elem = container.find("span", class_="a-icon-alt")
        ratings_elem = container.find("span", class_="a-size-base s-underline-text")
        link_elem = container.find("a", class_="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal")

        if name_elem and price_elem and stars_elem and ratings_elem and link_elem:
            name = name_elem.text.strip()
            price = price_elem.text.strip()
            stars = stars_elem.text.strip()
            ratings = ratings_elem.text.strip()
            link = f"https://www.amazon.in{link_elem['href']}"
            return {
                'platform': 'Amazon',
                'name': name,
                'price': price,
                'stars': stars,
                'ratings': ratings,
                'url': link
            }
    return {
        'platform': 'Amazon',
        'name': "Name not found",
        'price': "Price not found",
        'stars': "Stars not found",
        'ratings': "Ratings not found",
        'url': "URL not found"
    }


def search_croma(query):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service("C:/Users/Rajan/OneDrive/Desktop/Likenings Project/chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    url = f"https://www.croma.com/searchB?q={query}"
    driver.get(url)

    try:
        name = get_element_text(driver, By.CSS_SELECTOR, "h3.product-title.plp-prod-title a", "Name not found")
        price = get_element_text(driver, By.CSS_SELECTOR, "span.amount.plp-srp-new-amount", "Price not found")
        saveprice = get_element_text(driver, By.CSS_SELECTOR, "span.dicount-value", "SavePrice not found")
        discount = get_element_text(driver, By.CSS_SELECTOR, "span.discount.discount-mob-plp.discount-newsearch-plp", "Discount not found")
        ratings = get_element_text(driver, By.CSS_SELECTOR, "span.rating-text-icon", "Ratings not found")

        # Extract product URL
        link_elem = driver.find_element(By.CSS_SELECTOR, "h3.product-title.plp-prod-title a")
        href = link_elem.get_attribute('href')
        link = href if href.startswith("http") else f"https://www.croma.com{href}"
        
        return {
            'platform': 'Croma',
            'name': name,
            'price': price,
            'discount': discount,
            'save price': saveprice,
            'ratings': ratings,
            'url': link
        }
    except Exception as e:
        logging.error(f"Error scraping Croma: {e}")
        return None
    finally:
        driver.quit()

def get_element_text(driver, by, value, default):
    try:
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((by, value)))
        return element.text.strip()
    except:
        return default


def search_flipkart(query):
    url = f"https://www.flipkart.com/search?q={query}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
        'Accept-Language': 'en-US, en;q=0.5'
    }
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, "html.parser")
    
    print("-----Flipkart-----")

    try:
        name_elem = soup.find("div", class_="KzDlHZ")
        price_elem = soup.find("div", class_="Nx9bqj _4b5DiR")
        desc_elem = soup.find("div", class_="_6NESgJ")
        stars_elem = soup.find("div", class_="XQDdHH")
        ratings_elem = soup.find("span", class_="Wphh3N")
        
        if not all([name_elem, price_elem, desc_elem, stars_elem, ratings_elem]):
            raise ValueError("Some elements not found in the page")

        name = name_elem.text.strip()
        price = price_elem.text.strip()
        desc = desc_elem.text.strip()
        stars = stars_elem.text.strip()
        ratings = ratings_elem.text.strip()

        # Extract product URL
        link_container = soup.find("div", class_="tUxRFH")
        if not link_container:
            raise ValueError("Link container not found")
        
        link_elem = link_container.find("a", class_="CGtC98")
        if not link_elem:
            raise ValueError("Link element not found")

        href = link_elem['href']
        link = href if href.startswith("http") else f"https://www.flipkart.com{href}"

        return {
            "platform": "Flipkart",
            "name": name,
            "price": price,
            "description": desc,
            "stars": stars,
            "ratings": ratings,
            "url": link
        }
    except Exception as e:
        logging.error(f"Error scraping Flipkart: {e}")
        return {
            "platform": "Flipkart",
            "name": "Name not found",
            "price": "Price not found",
            "description": "Description not found",
            "stars": "Stars not found",
            "ratings": "Ratings not found",
            "url": "URL not found"
        }

def search_vijaysales(query):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service("C:/Users/Rajan/OneDrive/Desktop/Likenings Project/chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    url = f"https://www.vijaysales.com/search/{query}"
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h2.BcktPrdNm_")))
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        name_elem = soup.select_one("h2.BcktPrdNm_")
        name = name_elem.text.strip() if name_elem else "Name not found"
        price_elem = soup.select_one("span.Prdvsprc_")
        price = price_elem.text.strip() if price_elem else "Price not found"
        offer_elem = soup.select_one("div.BcktPrdemi.h54")
        offer = offer_elem.text.strip() if offer_elem else "Offer not found"
        discount_elem = soup.select_one("span.ofrnm_")
        discount = discount_elem.text.strip() if discount_elem else "Discount not found"
        
        # Extract product URL
        link_elem = soup.select_one("div.BcktPrd a")
        href = link_elem['href'] if link_elem and 'href' in link_elem.attrs else "URL not found"
        link = href if href.startswith("http") else f"https://www.vijaysales.com{href}"

        return {
            'platform': 'Vijay Sales',
            'name': name,
            'price': price,
            'offers': offer,
            'discount': discount,
            'url': link
        }

    except Exception as e:
        logging.error(f"Error scraping Vijay Sales: {e}")
        return {
            'platform': 'Vijay Sales',
            'name': 'Name not found',
            'price': 'Price not found',
            'offers': 'Offer not found',
            'discount': 'Discount not found',
            'url': 'URL not found'
        }
    finally:
        driver.quit()

print(search_vijaysales('iPhone 13 128GB Starlight'))