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
    username="xxxx",
    password="xxxx",
    host="xxx",
    database="grocery_app_db",
)

engine = create_engine(url_object)

# create meta data
metadata = MetaData()

#create table
Product = Table('product', metadata,
                db.Column('Store Name', db.String),
                db.Column('Product Name', db.String),
                db.Column('Price', db.String )
                )
metadata.create_all(engine)

#making a list of websites to scrape

websites = [
    {   "url" : "https://shop.newleaf.com/store/new-leaf-community-markets/collections/rc-sales-flyer",
        "name" : "New Leaf Community Markets",
        "products": {'name': 'h2', 'class_': 'e-9773mu'},
        "prices": {'name': 'div', 'class_': 'e-an4oxa'}
    }
]

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

#seperating functions to intake multiple websites
def scroll_page(driver):
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

def scrape_website(driver, website):

    #setup driver and get url
    driver = setup_driver()
    driver.get(website['url'])
    #scroll the page to get infro
    scroll_page(driver)
    #parse and find data
    soup = BeautifulSoup(driver.page_source, "html.parser")
    print("parsed")
    product_data = []
    items = soup.find_all(website['products']['name'], attrs={'class': website['products']['class_']})
    prices = soup.find_all(website['prices']['name'], attrs={'class': website['prices']['class_']})
    for item, price in zip(items, prices):
        product_data.append((website['name'], item.text.strip(), price.text.strip()))
    
    return product_data
    
   
def scrape_all():
    #get data for all sites by looping through website list 
    driver = setup_driver()
    all_data = []

    try:
        for website in websites:
            print(f"scraping {website['name']}")
            web_data = scrape_website(driver, website)
            all_data.extend(web_data)
            print(f"finished scraping {website['name']}. {len(web_data)} products found.")
    finally:
        driver.quit()


def insert_products_to_db(product_data):
    with engine.connect() as conn:
        conn.execute(Product.insert(), [
            {"Store Name": store, "Product Name": product, "Price": price}
            for store, product, price in product_data
        ])
        conn.commit()

if __name__ == "__main__":
    product_data = scrape_all()
   # insert_products_to_db(product_data)
   # print(f"Inserted {len(product_data)} products into the database.")