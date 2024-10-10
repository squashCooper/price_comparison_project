from bs4 import BeautifulSoup 

from sqlalchemy.engine import URL
from sqlalchemy import create_engine
import pandas as pd
from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import requests

#connect to database

url_object = URL.create(
    "postgresql",
    username="--------",#changed for security purposes
    password="--------",  
    host="localhost",
    database="grocery_app_db",
)

engine = create_engine(url_object)
conn = engine.connect
#print("engine connected")
#print engine created
#conn = psycopg2.connect(database='grocery_app_db',user='-------', password='-------', port=5432)
def scrape_product_names(): 
    
    scrape_page = requests.get("https://shop.newleaf.com/store/new-leaf-community-markets/storefront")
    soup = BeautifulSoup(scrape_page.text, "html.parser")
    product_names = soup.findAll('h2', attrs = {'class': 'e-9773mu'})
   
    for name in product_names:
        print(name.text)
    #define dataframe
    


scrape_product_names()

