from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import re

# Function to extract Product Name from URL
def get_product_name(url):
    return url.split('/')[-1].replace('-', ' ')

# Function to extract ASIN from URL
def get_asin(url):
    match = re.search(r'(B\w{9})', url)
    return match.group(1) if match else None

# Function to extract Product Price
def get_price(soup):
    original_price = soup.find('span', {'class': 'priceBlockStrikePriceString'})
    original_price = original_price.get_text() if original_price else None

    discounted_price = soup.find('span', {'class': 'priceBlockBuyingPriceString'})
    discounted_price = discounted_price.get_text() if discounted_price else None

    return original_price, discounted_price

# Function to extract Product Rating
def get_rating(soup):
    rating = soup.find('span', {'class': 'a-icon-alt'})
    rating = rating.get_text().split()[0] if rating else None
    return rating

# Function to scrape and extract data from Amazon product pages
def scrape_amazon_product_page(url, headers):
    # Send a GET request to the URL
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract product name and ASIN from the URL
    product_name = get_product_name(url)
    asin = get_asin(url)

    # Extract original and discounted prices
    original_price, discounted_price = get_price(soup)

    # Extract product rating
    rating = get_rating(soup)

    return {
        'Product Name': product_name,
        'ASIN': asin,
        'Original Price': original_price,
        'Discounted Price': discounted_price,
        'Product Rating': rating
    }

if __name__ == '__main__':

    print ("Inside the function")
    # Define headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US, en;q=0.5'
    }

    # The webpage URL
    url = "https://www.amazon.com/s?k=playstation+4&ref=nb_sb_noss_2"
    print("This is my url : ",url)
    
    # Send a GET request to the URL
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print("Request sent successfully")
        soup = BeautifulSoup(response.content, "html.parser")

        # Fetch links as List of Tag Objects
        links = soup.find_all("a", attrs={'class': 'a-link-normal s-no-outline'})

        # Store the links
        links_list = []

        # Loop for extracting links from Tag Objects
        for link in links:
            links_list.append(link.get('href'))

        d = {"Product Name": [], "ASIN": [], "Original Price": [], "Discounted Price": [], "Product Rating": []}

        # Loop for extracting product details from each link
        for link in links_list:
            new_url = "https://www.amazon.com" + link
            product_data = scrape_amazon_product_page(new_url, headers)
            for key in product_data:
                d[key].append(product_data[key])

        # Create DataFrame
        amazon_df = pd.DataFrame.from_dict(d)
        amazon_df['Product Name'].replace('', np.nan, inplace=True)
        amazon_df.dropna(subset=['Product Name'], inplace=True)
        amazon_df.to_csv("amazon_data.csv", header=True, index=False)
        print("DataFrame saved as 'amazon_data.csv'")
    else:
        print("Failed to fetch URL:", url)