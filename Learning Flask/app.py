from flask import Flask, request, render_template, jsonify
import time  
import redis
import json
import asyncio


'''app = Flask(__name__)
redis_client = redis.from_url("redis://localhost")

# Example dataset
products = {
    "69": {
        "brand": "Apple",
        "model": "iPhone 13",
        "storage_type": "128GB",
        "color": "Starlight"
    },
    # Add more products as needed
}

def get_unique_key(brand, model, storage_type, color):
    for key, product in products.items():
        if (product["brand"] == brand and 
            product["model"] == model and 
            product["storage_type"] == storage_type and 
            product["color"] == color):
            return key
    return None

@app.route('/search', methods=['POST'])
async def search():
    data = request.json
    brand = data['brand']
    model = data['model']
    storage_type = data['storage_type']
    color = data['color']
    
    unique_key = get_unique_key(brand, model, storage_type, color)
    if not unique_key:
        return jsonify({"error": "Product not found"}), 404
    
    # Check if data exists in cache
    cached_data = await redis_client.get(unique_key)
    if cached_data:
        return jsonify({"data": cached_data.decode('utf-8')})
    
    # If not in cache, scrape the data
    query = f"{brand} {model} {storage_type} {color}"
    scraped_data = await scrape_all_platforms(query)
    
    # Store result in cache
    await redis_client.set(unique_key, str(scraped_data))
    
    return jsonify({"data": scraped_data})
@app.route('/')
async def homepage():
    return "This is the home page"
if __name__ == '__main__':
    app.run(debug=True)'''



'''app = Flask(__name__)

# Configure Redis client
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

def scrape_data(query):
    # Simulate scraping process
    time.sleep(2)  # Simulate delay
    # Simulate data returned from scraping function
    return {
        "query": query,
        "data": scrape_all_platforms(query)
    }

async def get_scraped_data(query):
    # Check cache first
    cached_data = redis_client.get(query)
    if cached_data:
        return json.loads(cached_data)

    # If not in cache, scrape data
    scraped_data = scrape_data(query)
    # Cache the scraped data
    redis_client.set(query, json.dumps(scraped_data), ex=3600)  # Cache for 1 hour
    return scraped_data

@app.route('/')
def homepage():
    return render_template("index.html")

@app.route('/search', methods=['POST'])
async def search():
    data = request.json
    query = data.get('query')

    if not query:
        return jsonify({"error": "No query provided"}), 400

    # Get scraped data, using cache if available
    scraped_data = await get_scraped_data(query)
    return jsonify(scraped_data)

if __name__ == "__main__":
    app.run(debug=True)'''

from selenium_search import scrape_all_platforms, all_results  
from flask import Flask, request, jsonify, render_template
import redis
import json
import time

app = Flask(__name__)

# Configure Redis client
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

# Sample dataset with unique keys
products_dataset = {
    69: {"brand": "Apple", "model": "iPhone 13", "storage_type": "128GB", "color": "Starlight", "image_library":["https://m.media-amazon.com/images/I/71GLMJ7TQiL._SX679_.jpg","https://m.media-amazon.com/images/I/61NTwRtdzfL._SX679_.jpg","https://m.media-amazon.com/images/I/71OxEU5mSCL._SX679_.jpg","https://m.media-amazon.com/images/I/71G44HUh7yL._SX679_.jpg","https://m.media-amazon.com/images/I/81otRqY0XXL._SX679_.jpg","https://m.media-amazon.com/images/I/61BvZ6EbUvL._SX679_.jpg"], "about-item":["15 cm (6.1-inch) Super Retina XDR display","Cinematic mode adds shallow depth of field and shifts focus automatically in your videos","Advanced dual-camera system with 12MP Wide and Ultra Wide cameras; Photographic Styles, Smart HDR 4, Night mode, 4K Dolby Vision HDR recording","12MP TrueDepth front camera with Night mode, 4K Dolby Vision HDR recording","A15 Bionic chip for lightning-fast performance"]},
    68: {"brand": "OnePlus", "model": "12R", "storage_type": " 8GB 128GB", "color": "Cool Blue", "image_library":["https://m.media-amazon.com/images/I/717JX3femML._SX679_.jpg","https://m.media-amazon.com/images/I/61nlAS5+y4L._SX679_.jpg","https://m.media-amazon.com/images/I/51hACPRIwKL._SX679_.jpg","https://m.media-amazon.com/images/I/61dXJigjlJL._SX679_.jpg","https://m.media-amazon.com/images/I/61I7YQ4fk4L._SX679_.jpg","https://m.media-amazon.com/images/I/51kR5Cux4xL._SX679_.jpg"], "about-item":["Fast & Smooth for years: Snapdragon 8 Gen 2 Mobile Platform, Up to 16GB of LPDDR5X RAM with RAM-Vita - Dual Cryo-velocity VC Cooling System, TÜV SÜD 48-Month Fluency Rating A","Pristine Display with Aqua Touch: Super-Bright 1.5K LTPO ProXDR Display with Dolby Vision, and a DisplayMate A+ rating, Intellignent Eye Care certified by TÜV Rheinland, 4500 nits Peak Brightness, Aqua Touch helps you stay swiping, even with wet hands","Computational Photography That's Incomparable: RAW HDR Algorithm, 50MP Sony IMX890 Camera and Ultra-wide Camera 112° FoV Sony IMX355, Ultra-Clear Image Quality","Longest-Lasting Battery : 5500 mAh Battery with 100W SUPERVOOC, Paired with our advanced Battery Health Engine for longevity","Smoother and more stable connectivity: WiFi 7 Ready, Enhanced Wi-Fi, Lower gaming latency, Reduced network recovery time."]},
    67: {"brand": "OnePlus", "model": "12", "storage_type": "12GB  256GB", "color": "Glacial White", "image_library":["https://m.media-amazon.com/images/I/71YzJwmRFCL._SY450_.jpg","https://m.media-amazon.com/images/I/61f3YwT0eTL._SY450_.jpg","https://m.media-amazon.com/images/I/61czuTl29lL._SY450_.jpg","https://m.media-amazon.com/images/I/51akCyzBpdL._SY450_.jpg","https://m.media-amazon.com/images/I/517LLmw9eYL._SY450_.jpg","https://m.media-amazon.com/images/I/51CJ8rqcfEL._SY450_.jpg"], "about-item":["Pro-Level Hasselblad Camera System: Primary 50MP Sony's LYT-808 with OIS - 64 MP 3X Periscope Telephoto for studio-level portraits - 48 MP Ultra-wide 114° Fov", "Elite, Long-lasting Performance - Qualcomm Snapdragon 8 Gen 3 Mobile Platform - Software-assisted platform for Optimization - Keep apps active for up to 72 hours without reloading - Up to 3 hours of heavy gaming","Pristine 2K Display with Aqua Touch: - 2K 120 Hz ProXDR Display with advanced LTPO for brighter, more vibrant visuals - Eye Care certified by TÜV Rheinland - Aqua Touch helps you stay swiping, even with wet hands","Operating System: OxygenOS based on Android 14","Ultra fast charging, unwired: - Amp up your power with the 5400 mAh battery, wired 100W SUPERVOOC - Ultra-fast 50W wireless charging - 19 hours of YouTube playback"]},
    66: {"brand": "Samsung", "model": "S24 Ultra", "storage_type": "12GB 256GB", "color": "Titanium Yellow", "image_library":["https://m.media-amazon.com/images/I/71DoeQ838GL._SX522_.jpg","https://m.media-amazon.com/images/I/71JLhofuYJL._SX522_.jpg","https://m.media-amazon.com/images/I/71ZdFihN4YL._SX522_.jpg","https://m.media-amazon.com/images/I/71E-ptCgHcL._SX522_.jpg","https://m.media-amazon.com/images/I/71xI+CuesJL._SX522_.jpg","https://m.media-amazon.com/images/I/71vdd0pLCiL._SX522_.jpg"], "about-item":["Dynamic LTPO AMOLED 2X, 120Hz, HDR10+, 2600 nits (peak) 6.8 inches Display","Featuring IP68 dust/water resistant (up to 1.5m for 30 min)","Qualcomm SM8650-AC Snapdragon 8 Gen 3 (4 nm) of poweful processor","Main Camera: 200 + 10 + 50 + 12 MP (Quad), Selfie Camera: Single 12 MP, f/2.2, 26mm (wide),", "Super Long battery backup of  5000 mAh, Charing :45W wired, PD3.0, 65 percent inn 30 min (advertised)"]},
    65: {"brand": "Samsung", "model": "S24 Ultra", "storage_type": "12GB 256GB", "color": "Titanium Gray", "image_library":["https://m.media-amazon.com/images/I/81vxWpPpgNL._SX569_.jpg","https://m.media-amazon.com/images/I/71JLhofuYJL._SX569_.jpg","https://m.media-amazon.com/images/I/71ZdFihN4YL._SX569_.jpg","https://m.media-amazon.com/images/I/71E-ptCgHcL._SX569_.jpg","https://m.media-amazon.com/images/I/71xI+CuesJL._SX569_.jpg"], "about-item":["Dynamic LTPO AMOLED 2X, 120Hz, HDR10+, 2600 nits (peak) 6.8 inches Display","Featuring IP68 dust/water resistant (up to 1.5m for 30 min)","Qualcomm SM8650-AC Snapdragon 8 Gen 3 (4 nm) of poweful processor","Main Camera: 200 + 10 + 50 + 12 MP (Quad), Selfie Camera: Single 12 MP, f/2.2, 26mm (wide),", "Super Long battery backup of  5000 mAh, Charing :45W wired, PD3.0, 65 percent inn 30 min (advertised)"]},
    64: {"brand": "OnePlus", "model": "12R", "storage_type": " 8GB 128GB", "color": "Iron Grey", "image_library":["https://m.media-amazon.com/images/I/71XNeka-BRL._SX522_.jpg","https://m.media-amazon.com/images/I/71kaI4Zo5vL._SX522_.jpg","https://m.media-amazon.com/images/I/61t6JSSRflL._SX522_.jpg","https://m.media-amazon.com/images/I/51plgD7ju7L._SX522_.jpg","https://m.media-amazon.com/images/I/71W-Q-U8etL._SX522_.jpg","https://m.media-amazon.com/images/I/61EaUXLTV6L._SX522_.jpg"], "about-item":["Fast & Smooth for years: Snapdragon 8 Gen 2 Mobile Platform, Up to 16GB of LPDDR5X RAM with RAM-Vita - Dual Cryo-velocity VC Cooling System, TÜV SÜD 48-Month Fluency Rating A","Pristine Display with Aqua Touch: Super-Bright 1.5K LTPO ProXDR Display with Dolby Vision, and a DisplayMate A+ rating, Intellignent Eye Care certified by TÜV Rheinland, 4500 nits Peak Brightness, Aqua Touch helps you stay swiping, even with wet hands","Computational Photography That's Incomparable: RAW HDR Algorithm, 50MP Sony IMX890 Camera and Ultra-wide Camera 112° FoV Sony IMX355, Ultra-Clear Image Quality","Longest-Lasting Battery : 5500 mAh Battery with 100W SUPERVOOC, Paired with our advanced Battery Health Engine for longevity","Smoother and more stable connectivity: WiFi 7 Ready, Enhanced Wi-Fi, Lower gaming latency, Reduced network recovery time."]},
    63: {"brand": "Apple", "model": "iPhone 13", "storage_type": "128GB", "color": "Midnight", "image_library":["https://m.media-amazon.com/images/I/61VuVU94RnL._SX679_.jpg","https://m.media-amazon.com/images/I/61cecOpZrxL._SX679_.jpg","https://m.media-amazon.com/images/I/71SfvBP1gBL._SX679_.jpg","https://m.media-amazon.com/images/I/71G44HUh7yL._SX679_.jpg","https://m.media-amazon.com/images/I/818a-pz0BvL._SX679_.jpg","https://m.media-amazon.com/images/I/61YfilUZTUL._SX679_.jpg"], "about-item":["15 cm (6.1-inch) Super Retina XDR display","Cinematic mode adds shallow depth of field and shifts focus automatically in your videos","Advanced dual-camera system with 12MP Wide and Ultra Wide cameras; Photographic Styles, Smart HDR 4, Night mode, 4K Dolby Vision HDR recording","12MP TrueDepth front camera with Night mode, 4K Dolby Vision HDR recording","A15 Bionic chip for lightning-fast performance"]},
    62: {"brand": "Motorola", "model": "Edge 50 Pro", "storage_type": "8GB 256GB", "color": "Luxe Lavender", "image_library":["https://www.jiomart.com/images/product/original/rvp2cb8u16/motorola-edge-50-pro-5g-with-68w-charger-8gb-ram-256gb-rom-luxe-lavender-smartphone-product-images-orvp2cb8u16-p609197281-0-202406041152.jpg?im=Resize=(420,420)","https://www.jiomart.com/images/product/original/rvp2cb8u16/motorola-edge-50-pro-5g-with-68w-charger-8gb-ram-256gb-rom-luxe-lavender-smartphone-product-images-orvp2cb8u16-p609197281-1-202406041152.jpg?im=Resize=(420,420)","https://www.jiomart.com/images/product/original/rvp2cb8u16/motorola-edge-50-pro-5g-with-68w-charger-8gb-ram-256gb-rom-luxe-lavender-smartphone-product-images-orvp2cb8u16-p609197281-2-202406041152.jpg?im=Resize=(420,420)"], "about-item":["6.7 inches P-OLED, 1B colors, 144Hz, HDR10+, 2000 nits (peak) brightness Display","Snapdragon 7 Gen 3 (4 nm) Chipset","Main Camera: 50 + 10 + 13 MP with OIS","Selfie Camera: 50 MP HDR, 4K@30fps, 1080p@30/60/120fps, 10-bit HDR10+, gyro-EIS","Stereo Speakers", "Li-Po 4500 mAh, non-removable, 125W wired, 100 percent in 18 min (advertised), 50W wireless"]},
    70: {"brand": "Apple", "model": "iPhone 13", "storage_type": "128GB", "color": "Pink", "image_library":["https://m.media-amazon.com/images/I/61l9ppRIiqL._SX679_.jpg","https://m.media-amazon.com/images/I/61iTWldZ9qL._SX679_.jpg","https://m.media-amazon.com/images/I/71uNkgYrWcL._SX679_.jpg","https://m.media-amazon.com/images/I/71G44HUh7yL._SX679_.jpg","https://m.media-amazon.com/images/I/8163F9RhOlL._SX679_.jpg","https://m.media-amazon.com/images/I/61paF2JiudL._SX679_.jpg"], "about-item":["15 cm (6.1-inch) Super Retina XDR display","Cinematic mode adds shallow depth of field and shifts focus automatically in your videos","Advanced dual-camera system with 12MP Wide and Ultra Wide cameras; Photographic Styles, Smart HDR 4, Night mode, 4K Dolby Vision HDR recording","12MP TrueDepth front camera with Night mode, 4K Dolby Vision HDR recording","A15 Bionic chip for lightning-fast performance"]},
    71: {"brand": "Apple", "model": "iPhone 13", "storage_type": "256GB", "color": "Pink", "image_library":["https://m.media-amazon.com/images/I/61l9ppRIiqL._SX679_.jpg","https://m.media-amazon.com/images/I/61iTWldZ9qL._SX679_.jpg","https://m.media-amazon.com/images/I/71uNkgYrWcL._SX679_.jpg","https://m.media-amazon.com/images/I/71G44HUh7yL._SX679_.jpg","https://m.media-amazon.com/images/I/8163F9RhOlL._SX679_.jpg","https://m.media-amazon.com/images/I/61paF2JiudL._SX679_.jpg"], "about-item":["15 cm (6.1-inch) Super Retina XDR display","Cinematic mode adds shallow depth of field and shifts focus automatically in your videos","Advanced dual-camera system with 12MP Wide and Ultra Wide cameras; Photographic Styles, Smart HDR 4, Night mode, 4K Dolby Vision HDR recording","12MP TrueDepth front camera with Night mode, 4K Dolby Vision HDR recording","A15 Bionic chip for lightning-fast performance"]},
    72: {"brand": "Nothing", "model": "CMF Phone 1", "storage_type": "6GB 128GB", "color": "Orange", "image_library":["https://media-ik.croma.com/prod/https://media.croma.com/image/upload/v1720678984/Croma%20Assets/Communication/Mobiles/Images/308337_0_mjsvxq.png?tr=w-640","https://media-ik.croma.com/prod/https://media.croma.com/image/upload/v1721631618/308337_1_v6xnri.png?tr=w-640","https://media-ik.croma.com/prod/https://media.croma.com/image/upload/v1721387850/Croma%20Assets/Communication/Mobiles/Images/308337_2_izwlgs.png?tr=w-640","https://media-ik.croma.com/prod/https://media.croma.com/image/upload/v1720593660/Croma%20Assets/Communication/Mobiles/Images/308337_9_hvoshn.png?tr=w-640","https://media-ik.croma.com/prod/https://media.croma.com/image/upload/v1720593663/Croma%20Assets/Communication/Mobiles/Images/308337_10_nmsyp2.png?tr=w-640","https://media-ik.croma.com/prod/https://media.croma.com/image/upload/v1720593667/Croma%20Assets/Communication/Mobiles/Images/308337_11_lahfxp.png?tr=w-640","https://media-ik.croma.com/prod/https://media.croma.com/image/upload/v1720593667/Croma%20Assets/Communication/Mobiles/Images/308337_12_x9srbs.png?tr=w-640","https://media-ik.croma.com/prod/https://media.croma.com/image/upload/v1720593671/Croma%20Assets/Communication/Mobiles/Images/308337_13_gxbfno.png?tr=w-640","https://media-ik.croma.com/prod/https://media.croma.com/image/upload/v1720593673/Croma%20Assets/Communication/Mobiles/Images/308337_14_yjq6fr.png?tr=w-640","https://media-ik.croma.com/prod/https://media.croma.com/image/upload/v1720593675/Croma%20Assets/Communication/Mobiles/Images/308337_15_nozjsl.png?tr=w-640","https://media-ik.croma.com/prod/https://media.croma.com/image/upload/v1721631618/308337_1_v6xnri.png?tr=w-640"], "about-item":["AMOLED, 120Hz, 500 nits (typ), 2000 nits (peak)","Mediatek Dimensity 7300 (4 nm)","Glass front, plastic back or silicone polymer back (eco leather)","5000 mAh, non-removable","Rear: 50 + 2 MP, Selfie: 16 MP","Dual SIM (Nano-SIM, dual stand-by)"]},
    73: {"brand": "Nothing", "model": "CMF Phone 1", "storage_type": "6GB 128GB", "color": "Black", "image_library":["https://media-ik.croma.com/prod/https://media.croma.com/image/upload/v1720681155/308330_0_li240c.png?tr=w-640","https://media-ik.croma.com/prod/https://media.croma.com/image/upload/v1721631612/308330_1_izy755.png?tr=w-640","https://media-ik.croma.com/prod/https://media.croma.com/image/upload/v1721387849/Croma%20Assets/Communication/Mobiles/Images/308330_2_got6up.png?tr=w-640","https://media-ik.croma.com/prod/https://media.croma.com/image/upload/v1720593611/Croma%20Assets/Communication/Mobiles/Images/308330_9_jjmsup.png?tr=w-640","https://media-ik.croma.com/prod/https://media.croma.com/image/upload/v1720593615/Croma%20Assets/Communication/Mobiles/Images/308330_11_gxv3ib.png?tr=w-640","https://media-ik.croma.com/prod/https://media.croma.com/image/upload/v1720593621/Croma%20Assets/Communication/Mobiles/Images/308330_14_muggjq.png?tr=w-640"], "about-item":["AMOLED, 120Hz, 500 nits (typ), 2000 nits (peak)","Mediatek Dimensity 7300 (4 nm)","Glass front, plastic back or silicone polymer back (eco leather)","5000 mAh, non-removable","Rear: 50 + 2 MP, Selfie: 16 MP","Dual SIM (Nano-SIM, dual stand-by)"]},
    74: {"brand": "Apple", "model": "iPhone 14", "storage_type": "128GB", "color": "Midnight", "image_library":["https://m.media-amazon.com/images/I/61cwywLZR-L._SX679_.jpg","https://m.media-amazon.com/images/I/51lRv8lbOVL._SX679_.jpg","https://m.media-amazon.com/images/I/71KdlxeM59L._SX679_.jpg","https://m.media-amazon.com/images/I/711JE+dD1KL._SX679_.jpg","https://m.media-amazon.com/images/I/81LtCGVH+dL._SX679_.jpg","https://m.media-amazon.com/images/I/61xGIi8VUAL._SX679_.jpg"], "about-item":["15.40 cm (6.1-inch) Super Retina XDR display","Advanced camera system for better photos in any light","Cinematic mode now in 4K Dolby Vision up to 30 fps","Vital safety technology — Crash Detection calls for help when you can't","All-day battery life and up to 20 hours of video playback","Industry-leading durability features with Ceramic Shield and water resistance","A15 Bionic chip with 5-core GPU for lightning-fast performance. Superfast 5G cellular","iOS 16 offers even more ways to personalise, communicate and share"]}
    

    
}

def scrape_data(query):
    # Simulate scraping process
    time.sleep(2)  # Simulate delay
    # Simulate data returned from scraping function
    return (scrape_all_platforms(query)) 
        
        
def get_unique_key(brand, model, storage_type, color, products_dataset):
    for key, details in products_dataset.items():
        normalized_details = {
            'brand': normalize(details['brand']),
            'model': normalize(details['model']),
            'storage_type': normalize(details['storage_type']),
            'color': normalize(details['color'])
        }
        if (normalized_details['brand'] == brand and
            normalized_details['model'] == model and
            normalized_details['storage_type'] == storage_type and
            normalized_details['color'] == color):
            return key
    return None
   

async def get_scraped_data(unique_key, query):
    # Check cache first
    cached_data = redis_client.get(unique_key)
    if cached_data:
        return json.loads(cached_data)

    # If not in cache, scrape data
    scraped_data = scrape_data(query)
    # Cache the scraped data
    redis_client.set(unique_key, json.dumps(scraped_data), ex=3500)  # Cache for 30 seconds
    return scraped_data

@app.route('/')
def homepage():
    return render_template("index.html")
@app.route('/loading')
def loading_screen():
    return render_template('loading-screen.html')


@app.route('/get-models', methods=['POST'])
def get_models():
    data = request.json
    brand = data.get('brand')
    print(f"Selected brand: {brand}")  # Add this line for debugging
    models = list({details['model'] for key, details in products_dataset.items() if details['brand'] == brand})
    print(f"Models for brand {brand}: {models}")  # Add this line for debugging
    return jsonify(models)



@app.route('/get-variants', methods=['POST'])
def get_variants():
    data = request.json
    brand = data.get('brand')
    model = data.get('model')
    print(f"Selected brand: {brand}, model: {model}")
    variants = [
        {"storage_type": details['storage_type'], "color": details['color']}
        for key, details in products_dataset.items()
        if details['brand'] == brand and details['model'] == model
    ]
    print(f"Variants for brand {brand}, model {model}: {variants}")
    return jsonify(variants)


def normalize(text):
    return text.lower().strip() if text else ""

@app.route('/search', methods=['POST'])
async def search():
    data = request.get_json()
    print(data)
    
    brand = normalize(data.get('brand'))
    model = normalize(data.get('model'))
    storage_type = normalize(data.get('storage_type'))
    color = normalize(data.get('color'))

    print(f"Received search data: brand={brand}, model={model}, storage_type={storage_type}, color={color}")

    if not all([brand, model, storage_type, color]):
        return jsonify({"error": "Incomplete product information"}), 400

    # Use the get_unique_key function to find the unique key
    unique_key = get_unique_key(brand, model, storage_type, color, products_dataset)

    if unique_key is None:
        print("Product not found in dataset.")
        return jsonify({"error": "Product not found"}), 404

    print(f"Found product with unique key: {unique_key}")

    # Get scraped data, using cache if available
    scraped_data = await get_scraped_data(unique_key, f"{brand} {model} {storage_type} {color}")
    if not scraped_data:
        return jsonify({"error": "Error retrieving data"}), 500
    
    # Get the product's image library and about-item from the dataset and add it to the response
    product_images = products_dataset[unique_key].get('image_library', [])
    product_specs = products_dataset[unique_key].get('about-item', [])
    scraped_data["images"] = product_images
    scraped_data["about-item"] = product_specs

    # Get all available variants (storage_type and color) for the same brand and model
    variants = [
        {"storage_type": details["storage_type"], "color": details["color"]}
        for key, details in products_dataset.items()
        if details["brand"].lower() == brand and details["model"].lower() == model
    ]
    
    scraped_data["variants"] = variants  # Add variants to the response

    print(scraped_data)
    return jsonify(scraped_data)

#nono

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

