from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import sqlalchemy as db
from sqlalchemy.engine import URL
from sqlalchemy import create_engine, Table, Column, String, MetaData
import time

# connect to database
url_object = URL.create(
    "postgresql",
    username="x",
    password="x",
    host="x",
    database="grocery_app_db",
)

engine = create_engine(url_object)

# create meta data
metadata = MetaData()

#create table
Product = Table('product', metadata,
                db.Column('Store Name', db.String),
                db.Column('Product Name', db.String),
                db.Column('Price', db.String ),
                db.Column('Category', db.String)
                )
metadata.create_all(engine)

#creating store configs for easy linking 

store_configs = {
    
    "new_leaf": {
    "base_url": "https://shop.newleaf.com/store/new-leaf-community-markets/collections/",
    "name": "New Leaf Community Markets",
    "selectors": {
    "products": {'name': 'h2', 'class_': 'e-147kl2c'},
    "prices": {'name': 'div', 'class_': 'e-an4oxa'}
        },
        "categories": {
            "sales": "rc-sales-flyer",
            "produce": "n-produce-42",
            "meat_seafood": "n-meat-seafood-62",
            "coffee_juice_bar": "n-coffee-juice-bar-88",
            "vitamins_supplements": "n-vitamins-supplements-80",  
            "sushi_poke": "n-sushi-poke-7",
            "deli": "n-deli-73",
            "dairy_eggs": "n-dairy-eggs-90",
            "alcohol": "n-beer-wine-spirits-92", 
            "bakery" : "n-bakery-18", 
            "body_care": "n-body-care-65", 
            "beverages": "n-beverages-70", 
            "canned_goods": "n-canned-goods-66", 
            "dry_goods": "n-dry-goods-pasta-46", 
            "frozen": "n-frozen-52", 
            "snacks": "n-snacks-60",
            "baby": "n-baby-toddler-90",
            "pets": "n-pets-85",
            "household": "n-household-85", 
            "housewares" : "n-housewares-0", 
            "breakfast" : "n-breakfast-56", 
            "bulk" : "n-bulk-29", 
            "pantry" : "n-pantry-95", 
            "international" : "n-international-44"

        }
    },
}



websites = []
for store, config in store_configs.items():
    for category, path in config["categories"].items():
        websites.append({
        "url":config["base_url"] + path, 
        "name": config["name"],
        "products": config["selectors"]["products"],
        "prices": config["selectors"]["prices"],
        "category": category
        })
  
      #safeway, deal with "load more button "
    #  {
     #     "url" : "https://www.safeway.com/order/fall/events-holidays/all-produce.html",
      #    "name" : "Safeway",
       #   "products":{'name': 'a', 'class_': 'product-title__name'},
        #  "prices" : {'name': 'div', 'class_': 'product-title__qty'}
  
         # },

    # new leaf 

      #trader joes, deal with spaces in class names
     # {
      #    "url" : "https://www.traderjoes.com/home/products/category/sliced-bread-14",
      #   "name": "Trader Joes",
      #    "products" : {'name' : 'a', 'class_': 'Link_link__1AZfr.ProductCard_card__title__301JH.ProductCard_card__title__large__3bAY6'},
     #     "prices" : {'name' : 'span', 'class_': 'ProductPrice_productPrice__price__3-50j'}
     # },
  
  
      #grocery outlet, go in store and check if instacart prices are accurate
      # since website does not offer a list of prices
  
      #target
    #  {
     #     "url" : "https://www.target.com/c/grocery-deals/-/N-k4uyq?type=products",
     #     "name" : "Target",
     #     "products" : {'name': '', 'class_' : ''},
     #     "prices" : {'name': '', 'class_' : ''}
  
    #  }
      #whole foods, problems with displaying prices
    #  {
     #     "url" : "https://www.wholefoodsmarket.com/products/produce",
      #    "name" : "Whole Foods",
       #   "products" : {'name': 'h2', 'class_' : 'w-cms--font-body__sans-bold'},
        #  "prices" : {'name': 'span', 'class_' : 'text-left.bds--heading-5'}
  
#      }
      #nob hills, spaces in class
     # {
  
     #     "url" : "https://www.raleys.com/category/PMC16/produce",
      #    "name" : "Nob Hills",
       #   "products" : {'name': '', 'class_' : ''},
        #  "prices" : {'name': '', 'class_' : ''}
  
     # }
 # ]
  


def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")  # Larger window size
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def scroll_page(driver, website):
     
        scroll_pause = 2
        screen_height = driver.execute_script("return window.screen.height;")
        i = 1
        while True:
            driver.execute_script(f"window.scrollTo(0,{screen_height * i});")
            i += 1
            time.sleep(scroll_pause)
            scroll_height = driver.execute_script("return document.body.scrollHeight;")
            if screen_height * i > scroll_height:
                break

def scrape_website(driver, website):
    try:
        print(f"Scraping {website['name']} - {website['category']}")
        driver.get(website['url'])
        scroll_page(driver, website)
        
        soup = BeautifulSoup(driver.page_source, "html.parser")
        print(f"Parsed {website['name']} - {website['category']}")
        
        product_data = []
        items = soup.find_all(website['products']['name'], class_=website['products']['class_'])
        prices = soup.find_all(website['prices']['name'], class_=website['prices']['class_'])
        
        for item, price in zip(items, prices):
            # Include category in the data
            product_data.append((
                website['name'],
                item.text.strip(),
                price.text.strip(),
                website['category']
            ))
            
        print(f"Found {len(product_data)} products in {website['category']}")
        return product_data
        
    except Exception as e:
        print(f"Error scraping {website['name']} - {website['category']}: {str(e)}")
        return []

def scrape_all():
    driver = setup_driver()
    all_data = []

    try:
        for website in websites:
            print(f"Scraping {website['name']}")
            web_data = scrape_website(driver, website)
            if web_data:
                all_data.extend(web_data)
                print(f"Successfully scraped {len(web_data)} products from {website['name']}")
            else:
                print(f"No data scraped from {website['name']}")
    finally:
        driver.quit()
    
    return all_data

if __name__ == "__main__":
    product_data = scrape_all()
   # insert_products_to_db(product_data)
   # print(f"Inserted {len(product_data)} products into the database.")