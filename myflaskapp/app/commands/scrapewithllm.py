import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import json

# Load .env from project root
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def get_amazon_html(product_name: str) -> str:
    search_query = product_name.replace(" ", "+")
    url = f"https://www.amazon.com/s?k={search_query}&s=price-asc-rank"
    print(f"🔍 Searching for {search_query} on Amazon at {url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    response = requests.get(url, headers=headers)
    print(f"🔍 Response status: {response.status_code}")
    return response.text

def get_product_blocks(html):
    soup = BeautifulSoup(html, "html.parser")
    blocks = soup.find_all('div', {'data-component-type': 's-search-result'})
    return [str(b) for b in blocks]

def extract_info_from_llm(html_block):
    prompt = f"""
Extract the product name, image URL, and price from this Amazon product HTML block.
If any value is missing, use "N/A" or "$0.00".

HTML:
{html_block}

Return a JSON object like this:
{{
  "name": "...",
  "price": "...",
  "image": "..."
}}
"""
# You are an expert at extracting structured data (JSON) from messy HTML content.

    print(f'here is the API datas {OPENROUTER_API_KEY}')

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "http://localhost:5000",  # Customize as needed
            "X-Title": "Amazon Scraper",
        },
        json={
            "model": "openai/gpt-4o",
            "messages": [
                {"role": "system", "content": "You are an expert in web development and a tutor for web development"},
                {"role": "user", "content": 'can you explain the difference between a div and a span in html?'}
            ],
            "temperature": 0.2,
            "max_tokens": 300,
        },
    )

    if response.status_code == 200:
        result = response.json()['choices'][0]['message']['content']
        print(f'here is the normal response from the LLM {response}')
        try:
            return json.loads({"Response": result})
        except json.JSONDecodeError:
            print("⚠️ JSON parse error. Raw response:\n", result)
            return None
    else:
        print(f"❌ LLM API failed: {response.status_code} - {response.text}")
        return None

def scrape_amazon_products_with_llm(product_name: str):
    html_content = get_amazon_html(product_name)
    
    product_blocks = get_product_blocks(html_content)
    extracted_data = []
    for idx, block in enumerate(product_blocks):
        print(f"🧠 Parsing product {idx + 1}/{len(product_blocks)}...")
        data = extract_info_from_llm(block)
        if data:
            extracted_data.append(data)

    return extracted_data
