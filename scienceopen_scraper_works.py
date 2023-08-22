from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Configure Chrome WebDriver with options
chrome_options = Options()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
driver_path = "/usr/local/bin/chromedriver"

# Create a ChromeDriver service with the executable path
chrome_service = Service(driver_path)

# Create the WebDriver instance using the service and options
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

# Navigate to the ScienceOpen advanced search URL
driver.get("https://www.scienceopen.com/search#('v'~4_'id'~''_'queryType'~1_'context'~null_'kind'~77_'order'~0_'orderLowestFirst'~false_'query'~''_'filters'~!('kind'~115_'notPreprint'~true_'preprint'~true)_('kind'~38_'not'~false_'offset'~1_'timeUnit'~7)_('kind'~39_'not'~false_'disciplines'~!('kind'~23_'id'~'79f00115-6f95-11e2-bcfd-0800200c9a66')*)*_'hideOthers'~false)")

# Wait for the "accept all cookies" button to appear and click it
try:
    accept_cookies_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@class='so-b3 so--long so--tall so--selected' and contains(text(), 'Accept all cookies')]")))
    accept_cookies_button.click()
except Exception as e:
    print("Error clicking the 'Accept all cookies' button:", e)

# Introduce a delay to allow the cookies to be accepted
time.sleep(5)  # waits for 5 seconds

# Set to keep track of processed paper URLs for the current session
processed_paper_urls = set()

def scrape_paper_info(paper_link):
    try:
        # Get the paper page URL
        paper_page_url = paper_link.get_attribute("href")
        
        # Check if the paper has already been processed in this session
        if paper_page_url in processed_paper_urls:
            print("Paper already processed in this session:", paper_page_url)
            return

        # Add the paper URL to the processed set for this session
        processed_paper_urls.add(paper_page_url)

        # Open the paper page in a new tab using JavaScript
        driver.execute_script("window.open(arguments[0], '_blank');", paper_page_url)
        
        # Switch to the new tab
        driver.switch_to.window(driver.window_handles[-1])
        
        # Wait for the paper page to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//span[@itemprop='author']")))
        
        # Extract paper information
        try:
            author_names = [author.text for author in driver.find_elements(By.XPATH, "//span[@itemprop='author']")]
            paper_name = driver.find_element(By.XPATH, "//h1[@class='so-article-header-title']").text
            publication_date = driver.find_element(By.XPATH, "//span[@itemprop='datePublished']").text
            journal = driver.find_element(By.XPATH, "//a[@itemprop='journal-url']").text
            publisher = driver.find_element(By.XPATH, "//a[@itemprop='publisher-url']").text

            print("Authors:", author_names)
            print("Paper Name:", paper_name)
            print("Publication Date:", publication_date)
            print("Journal:", journal)
            print("Publisher:", publisher)

        except Exception as e:
            print("Error extracting paper information:", e)
        
        # Close the tab after scraping
        driver.close()
        
        # Switch back to the original tab
        driver.switch_to.window(driver.window_handles[0])
    
    except Exception as e:
        print("Error processing paper:", e)

def click_load_more_results():
    # Find and click the "Load More Results" button
    try:
        load_more_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'so--green-2') and contains(text(), 'Load more results')]")))
        load_more_button.click()
    except Exception as e:
        print("Error clicking the 'Load More Results' button:", e)

def load_and_scrape_papers():
    # Find all paper links
    paper_links = driver.find_elements_by_xpath("//a[contains(@href, '/document?vid=')]")

    # Extract and print paper information
    for paper_link in paper_links:
        scrape_paper_info(paper_link)

    # Clear the processed URLs for this session
    processed_paper_urls.clear()

# Scrape initial batch of papers
load_and_scrape_papers()

last_processed_index = 10  # Index of the last paper scraped in the initial batch

while True:
    # Click the "Load More Results" button
    click_load_more_results()
    
    # Wait for the newly loaded papers to appear
    time.sleep(20)  # waits for 20 seconds
    
    # Scrape the newly loaded papers
    paper_links = driver.find_elements_by_xpath("//a[contains(@href, '/document?vid=')]")
    for paper_link in paper_links[last_processed_index:]:
        scrape_paper_info(paper_link)