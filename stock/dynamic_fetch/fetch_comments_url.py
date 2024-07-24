import requests
from bs4 import BeautifulSoup
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, JavascriptException, NoSuchElementException

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 11; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.181 Mobile Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; AS; rv:11.0) like Gecko',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (iPad; CPU OS 13_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
]

def setup_selenium():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument(f'user-agent={random.choice(USER_AGENTS)}')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def fetch_comments_with_selenium(url):
    driver = setup_selenium()
    driver.get(url)
    try:
        # Wait for the outer shadow DOM host element
        outer_shadow_host = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'shreddit-comments-sort-dropdown'))
        )
        
        # Access the outer shadow DOM
        outer_shadow_root = driver.execute_script('return arguments[0].shadowRoot', outer_shadow_host)
        
        # Wait for the inner shadow DOM host element
        inner_shadow_host = WebDriverWait(outer_shadow_root, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'shreddit-sort-dropdown'))
        )
        
        # Access the inner shadow DOM
        inner_shadow_root = driver.execute_script('return arguments[0].shadowRoot', inner_shadow_host)
        
        # Wait for and click the sort dropdown
        sort_button = WebDriverWait(inner_shadow_root, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[slot="selected-item"]'))
        )
        driver.execute_script("arguments[0].click();", sort_button)
        
        # Wait for and click the "Top" option
        top_option = WebDriverWait(inner_shadow_root, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'data[value="TOP"]'))
        )
        driver.execute_script("arguments[0].click();", top_option)

        # Wait for the comments to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'shreddit-comment'))
        )
        soup = BeautifulSoup(driver.page_source, 'html.parser')
    except TimeoutException:
        print(f"Timeout occurred while loading comments for URL: {url}")
        soup = BeautifulSoup(driver.page_source, 'html.parser')
    except JavascriptException as e:
        print(f"JavaScript exception: {e}")
        soup = BeautifulSoup(driver.page_source, 'html.parser')
    except NoSuchElementException as e:
        print(f"No such element: {e}")
        soup = BeautifulSoup(driver.page_source, 'html.parser')
    finally:
        driver.quit()
    return soup

def parse_comments(soup):
    comments = []
    for comment_tag in soup.find_all('shreddit-comment'):
        if comment_tag.get('depth') == '0':  # Only top-level comments
            comment_details = {
                'author': comment_tag.get('author'),
                'score': int(comment_tag.get('score').replace(' points', '').replace(' point', '')),
                'comment_text': comment_tag.find('div', {'slot': 'comment'}).get_text(strip=True),
                'comment_url': f"https://www.reddit.com{comment_tag.get('permalink')}"
            }
            comments.append(comment_details)
    # Sort comments by score in descending order
    comments = sorted(comments, key=lambda x: x['score'], reverse=True)
    return comments

if __name__ == "__main__":
    # Start timing
    start_time = time.time()
    
    # Read URLs from file
    with open('post_urls.txt', 'r') as f:
        urls = f.readlines()
    
    for url in urls:
        url = url.strip()
        soup = fetch_comments_with_selenium(url)
        comments = parse_comments(soup)
        
        for comment in comments[:10]:  # Limit to top 10 comments
            print(comment)
        
        # Add delay between requests
        time.sleep(5)
    
    # End timing
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Total elapsed time: {elapsed_time:.2f} seconds")
