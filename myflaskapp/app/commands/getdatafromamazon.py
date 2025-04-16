import aiohttp
import asyncio
from bs4 import BeautifulSoup 
import json
import urllib3
from requests.exceptions import RequestException
import time

def get_product_data_sync(search_product_name):
    """Synchronous wrapper for GetProductData"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(GetProductData(search_product_name))
        return result
    finally:
        loop.close()

async def GetProductData(search_product_name):
    """Get product info from amazon and return it"""
    try:
        # Disable SSL verification warnings
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        search_product_name = search_product_name.replace(" ", "+")
        url = f"https://www.amazon.com/s?k={search_product_name}&s=price-asc-rank"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US, en;q=0.5',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, ssl=False) as response:
                if response.status != 200:
                    return {"error": f"Failed to fetch data. Status code: {response.status}"}
                
                html = await response.text()
                
                # Add a small delay to ensure page content is loaded
                await asyncio.sleep(2)
                
                soup = BeautifulSoup(html, features="lxml")

                # Get all matching products
                products = soup.find_all('div', {'data-component-type': 's-search-result'})
                product_data = []

                for product in products:
                    # Try multiple selectors for product name
                    product_name = None
                    
                    product_name = product.find('a',{'class':'a-link-normal s-line-clamp-2 s-link-style a-text-normal'})
                    if product_name:
                        product_name = product_name.text.strip()
                    else:
                        product_name = "N/A"
                    
                    price = product.find('span', {'class': 'a-price'})
                    # Skip this product if price doesn't exist
                    if not price or not price.find('span', {'class': 'a-offscreen'}):
                        continue
                    price_text = price.find('span', {'class': 'a-offscreen'}).text
                    
                    # Get product image
                    img = product.find('img', {'class': 's-image'})
                    image_url = img.get('src') if img else "N/A"
                    
                    # Append product if it has a valid price
                    product_data.append({
                        'name': product_name,
                        'price': price_text,
                        'image': image_url
                    })

                if not product_data:
                    return {"error": "No products found with valid data"}

                return product_data

    except asyncio.TimeoutError:
        return {"error": "Request timed out while fetching data from Amazon"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}

