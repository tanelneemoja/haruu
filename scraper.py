import requests
from bs4 import BeautifulSoup
import csv
import re

def scrape_products(urls):
    products = []
    
    # Estonian to English keyword mapping for product categories
    category_map = {
        'kimono': 'Apparel & Accessories > Clothing > Kimonos',
        'mantel': 'Apparel & Accessories > Clothing > Coats',
        'bomberjakk': 'Apparel & Accessories > Clothing > Coats',
        'hommikumantel': 'Apparel & Accessories > Clothing > Bathrobes',
        'rätik': 'Home & Garden > Linens & Bedding > Towels',
        'kõrvarõngad': 'Apparel & Accessories > Accessories',
        'kinkekaart': 'Media > Gifts & Cards > Gift Cards',
        'patsikumm': 'Apparel & Accessories > Accessories',
        'öömask': 'Apparel & Accessories > Accessories',
        'retuusid': 'Apparel & Accessories > Clothing > Tights',
        'pullover': 'Apparel & Accessories > Clothing > Sweaters',
        'torusall': 'Apparel & Accessories > Accessories',
        'kosmeetikakott': 'Apparel & Accessories > Accessories',
        'müts': 'Apparel & Accessories > Accessories',
        'sall': 'Apparel & Accessories > Accessories',
        'bag': 'Apparel & Accessories > Accessories',
        'kaisukas': 'Apparel & Accessories > Accessories',
        'kleit': 'Apparel & Accessories > Clothing > Dresses',
        'seelik': 'Apparel & Accessories > Clothing > Skirts',
        'pusa': 'Apparel & Accessories > Clothing > Shirts & Tops',
        'kampsun': 'Apparel & Accessories > Clothing > Sweaters',
        'püksid': 'Apparel & Accessories > Clothing > Pants',
        'jakid': 'Apparel & Accessories > Clothing > Outerwear',
        'särk': 'Apparel & Accessories > Clothing > Shirts & Tops',
        'pluus': 'Apparel & Accessories > Clothing > Shirts & Tops',
        'aksessuaar': 'Apparel & Accessories > Accessories',
        'ehe': 'Apparel & Accessories > Jewelry',
    }

    for url in urls:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all product list items
        product_items = soup.find_all('li', class_=re.compile(r'product'))

        for item in product_items:
            product_data = {}
            
            # Extract ID from data-product_id attribute
            try:
                product_id_tag = item.find('a', {'data-product_id': True})
                if product_id_tag:
                    product_data['id'] = product_id_tag['data-product_id']
                else:
                    continue
            except (AttributeError, KeyError):
                continue
            
            # Extract link
            try:
                product_link_tag = item.find('a', class_='woocommerce-loop-product__link')
                if product_link_tag:
                    product_data['link'] = product_link_tag['href']
                else:
                    product_data['link'] = item.find('a')['href']
            except (AttributeError, KeyError):
                product_data['link'] = ''

            # Extract title and use it for description
            try:
                title = item.find('h2', class_='woocommerce-loop-product__title').text.strip()
                product_data['title'] = title
                product_data['description'] = title
            except AttributeError:
                product_data['title'] = ''
                product_data['description'] = ''

            # Extract image link (main product image)
            try:
                product_data['image_link'] = item.find('img', class_='attachment-woocommerce_thumbnail')['data-src']
            except (AttributeError, KeyError):
                product_data['image_link'] = ''

            # Extract price and format it
            try:
                price_text = item.find('span', class_='price').bdi.text.strip()
                price_number = re.sub(r'[€,]', '', price_text).strip()
                formatted_price = f"{float(price_number):.2f} EUR"
                product_data['price'] = formatted_price
            except (AttributeError, ValueError):
                product_data['price'] = ''
            
            # Set default values
            product_data['availability'] = 'in stock'
            product_data['condition'] = 'new'
            product_data['brand'] = 'haruu'

            # Determine product categories based on title keywords
            title_lower = product_data['title'].lower()
            product_data['fb_product_category'] = ''
            product_data['google_product_category'] = ''
            for keyword, category in category_map.items():
                if keyword in title_lower:
                    product_data['fb_product_category'] = category
                    product_data['google_product_category'] = category
                    break
            
            products.append(product_data)
            
    return products

def save_to_csv(products):
    # Consolidate all headers from both images for maximum compatibility
    headers = [
        'id', 'title', 'description', 'availability', 'condition', 'price', 
        'link', 'image_link', 'brand', 'product_type', 'age_group', 'color', 
        'gender', 'item_group_id', 'pattern', 'size', 'shipping', 
        'shipping_weight', 'custom_label_0', 'custom_label_1', 
        'custom_label_2', 'custom_label_3', 'custom_label_4', 
        'google_product_category', 'fb_product_category', 'product_tags[0]', 
        'additional_image_link'
    ]
    
    with open('products.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        
        for product in products:
            # Create a row with all headers, filling in only the relevant data
            row = {header: '' for header in headers}
            
            # Populate the row with scraped data
            row['id'] = product.get('id', '')
            row['title'] = product.get('title', '')
            row['description'] = product.get('description', '')
            row['availability'] = product.get('availability', '')
            row['condition'] = product.get('condition', '')
            row['price'] = product.get('price', '')
            row['link'] = product.get('link', '')
            row['image_link'] = product.get('image_link', '')
            row['brand'] = product.get('brand', '')
            row['fb_product_category'] = product.get('fb_product_category', '')
            row['google_product_category'] = product.get('google_product_category', '')
            
            writer.writerow(row)

if __name__ == "__main__":
    urls_to_scrape = [
        'https://haruu.ee/tootekategooria/koik-tooted/',
        'https://haruu.ee/tootekategooria/koik-tooted/page/2/'
    ]
    
    scraped_products = scrape_products(urls_to_scrape)
    save_to_csv(scraped_products)
    print("products.csv has been created successfully.")
