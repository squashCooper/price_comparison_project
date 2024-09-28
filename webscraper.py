from bs4 import BeautifulSoup 
import requests

def scrape_product_names(): 
    
    scrape_page = requests.get("https://shop.newleaf.com/store/new-leaf-community-markets/storefront")
    soup = BeautifulSoup(scrape_page.text, "html.parser")
    product_names = soup.findAll('h2', attrs = {'class': 'e-147kl2c'})
   
    for name in product_names:
        print(name.text)

scrape_product_names()
