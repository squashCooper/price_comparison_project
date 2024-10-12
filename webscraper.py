from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import sqlalchemy as db
from sqlalchemy.engine import URL
from sqlalchemy import create_engine, Table, Column, String, MetaData
import time

# Connect to database
url_object = URL.create(
    "postgresql",
    username="XXXXXXX",
    password="XXXXX",
    host="XXXXX",
    database="grocery_app_db",
)

engine = create_engine(url_object)

# Create meta data
metadata = MetaData()

Product = Table('product', metadata,
                db.Column('Store Name', db.String),
                db.Column('Product Name', db.String)
                )
metadata.create_all(engine)

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def scrape_product_data():
    driver = setup_driver()
    url = "https://shop.newleaf.com/store/new-leaf-community-markets/collections/rc-sales-flyer"
    
    try:
        driver.get(url)
        
        # Scroll page
        scroll_pause = 2
        screen_height = driver.execute_script("return window.screen.height;")
        print(screen_height)
        i = 1
        while True:
            driver.execute_script(f"window.scrollTo(0,{screen_height * i});")
            i += 1
            time.sleep(scroll_pause)
            scroll_height = driver.execute_script("return document.body.scrollHeight;")
            print(scroll_height)
            if screen_height * i > scroll_height:
                break
        
        soup = BeautifulSoup(driver.page_source, "html.parser")
        print("parsed")
        
        product_data = []
        store_name = "New Leaf"
        print(store_name)
        
        items = soup.find_all('h2', attrs={'class': 'e-9773mu'})
        prices = soup.find_all('span', attrs = {'class':'screen-reader-only'})
        print(items)
        for item in items:
            product_data.append((store_name, item.text))
            print(item.text)
        for price in prices:
            print(price.text)
        
        return product_data
    
    finally:
        driver.quit() 

def insert_products_to_db(product_data):
    with engine.connect() as conn:
        conn.execute(Product.insert(), [
            {"Store Name": store, "Product Name": product}
            for store, product in product_data
        ])
        conn.commit()

if __name__ == "__main__":
    product_data = scrape_product_data()
   # insert_products_to_db(product_data)
   # print(f"Inserted {len(product_data)} products into the database.")