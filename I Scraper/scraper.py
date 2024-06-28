from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import json

# Set up Chrome options
chrome_options = Options()

# Set up Chrome driver
chrome_path = "/usr/local/bin/chromedriver"  # Replace with the path to your chromedriver executable
chrome_service = ChromeService(chrome_path)

# Start the Chrome browser
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

# Navigate to Amazon
driver.get("https://www.amazon.com/")
time.sleep(2)

results = []
base_url = "https://www.amazon.com/"

def feed_results():
    # Wait for the results to load
    time.sleep(2)

    # Scroll down to load more results (adjust the number of scrolls as needed)
    for _ in range(200):
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ARROW_DOWN)
    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)

    # Get the page source
    page_source = driver.page_source

    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')

    # Extract information from the page as needed
    # For example, let's print the titles of the search results
    # a-size-medium a-color-base a-text-normal
    # a-size-base-plus a-color-base a-text-normal
    result_elements = soup.find_all("span", class_=" a-size-base-plus a-color-base a-text-normal")
    if (len(result_elements) == 0):
        result_elements = soup.find_all("span", class_=" a-size-medium a-color-base a-text-normal")

    for result_element in result_elements:
        # Find the parent 'a' tag
        parent_a = result_element.find_parent("a", class_="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal")
        
        # Extract text and href if the 'a' tag is found
        if parent_a:
            text = result_element.text.strip()
            href = base_url + parent_a.get("href")
            results.append({"prod_name": text, "prod_link": href})

def fetch_product_name_and_link(prod_name):
    # Find the search input field and enter the query
    search_box = driver.find_element(By.ID, "twotabsearchtextbox")
    search_box.send_keys(prod_name)
    search_box.send_keys(Keys.RETURN)
    feed_results()

    # Click on pagination links for up to 5 pages
    for page_number in range(2, 8):  # Assuming you want to go up to page 5
        # Locate the pagination link and click on it
        pagination_link = driver.find_element(By.XPATH, f"//a[text()='{page_number}']")
        pagination_link.click()
        feed_results()

    # Print or use the results as needed
    # for result in results:
    #     print(f"Text: {result['prod_name']}, Href: {result['prod_link']}")
    print(len(results))

# Fire your query here and fetch results
fetch_product_name_and_link("smart camera iot")
all_products = {}
cnt = 1

for item in results:
    name = item['prod_name']
    print(name)
    prod_link = item['prod_link']
    driver.get(prod_link)

    # Scroll down to load more results (adjust the number of scrolls as needed)
    for _ in range(10):
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ARROW_DOWN)

    # Get the page source
    page_source = driver.page_source

    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')
    decription_list = []

    # Extract product decriptions
    try: 
        feature_bullets_div = soup.find("div", id="feature-bullets")
        if feature_bullets_div:
            uls = feature_bullets_div.find_all("ul")
            for ul_index, ul in enumerate(uls, 1):
                list_items = ul.find_all("li")
                for li_index, item in enumerate(list_items, 1):
                    decription_list.append(item.text.strip())
                    # print(f"UL {ul_index}, Bullet {li_index}: {item.text.strip()}")
    except Exception as e:
        print("Exception encoutered while fetching prod from: ", prod_link)
    
    # Extract image links
    img_src = ""
    try:
        img_tag_wrapper = soup.find("div", id="imgTagWrapperId")
        if img_tag_wrapper:
            img_tag = img_tag_wrapper.find("img")
            if img_tag:
                image_source = img_tag.get("src")
                img_src = image_source
    except Exception as e:
        print(f"An error occurred while extracting image source: {e}")
    
    # Format to dump into json
    json_value = {'prod_name' : name, 'prod_link' : prod_link, 'decription' : decription_list, 'image_link': img_src}
    all_products[cnt] = json_value
    cnt += 1


json_file_path = "output.json"

# Dump the dictionary into the JSON file
with open(json_file_path, "w") as json_file:
    json.dump(all_products, json_file, indent=2)

# Close the browser
driver.quit()
