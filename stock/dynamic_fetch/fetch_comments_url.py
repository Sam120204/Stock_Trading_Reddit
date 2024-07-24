import time
import random
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, JavascriptException, NoSuchElementException
from concurrent.futures import ThreadPoolExecutor, as_completed

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
    print(f"Starting to fetch comments for URL: {url}")
    start_time = time.time()
    
    driver = setup_selenium()
    driver.get(url)
    comments = []
    try:
        # Wait for the comments to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'shreddit-comment'))
        )
        
        # Extract comments directly using Selenium
        comment_elements = driver.find_elements(By.CSS_SELECTOR, 'shreddit-comment')
        for element in comment_elements:
            try:
                author = element.get_attribute('author')
                score = int(element.get_attribute('score').replace(' points', '').replace(' point', ''))
                comment_text = element.find_element(By.CSS_SELECTOR, 'div[slot="comment"]').text
                comment_url = f"https://www.reddit.com{element.get_attribute('permalink')}"
                comments.append({
                    'author': author,
                    'score': score,
                    'comment_text': comment_text,
                    'comment_url': comment_url
                })
            except Exception as e:
                print(f"Error extracting comment details: {e}")
                continue
    except TimeoutException:
        print(f"Timeout occurred while loading comments for URL: {url}")
    except JavascriptException as e:
        print(f"JavaScript exception: {e}")
    except NoSuchElementException as e:
        print(f"No such element: {e}")
    finally:
        driver.quit()

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed time for fetching comments from {url}: {elapsed_time:.2f} seconds")
    
    # Sort comments by score in descending order and return top 10
    comments = sorted(comments, key=lambda x: x['score'], reverse=True)
    return {
        'url': url,
        'fetched_at': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time)),
        'elapsed_time': elapsed_time,
        'comments': comments[:10]
    }

def fetch_all_comments(urls):
    # Clear the JSON file before appending new data
    with open('comments.json', 'w') as f:
        f.write('')

    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(fetch_comments_with_selenium, url): url for url in urls}
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                result = future.result()
                # Append the result to the JSON file
                with open('comments.json', 'a') as f:
                    json.dump(result, f, indent=4)
                    f.write('\n')
            except Exception as e:
                print(f"Error fetching comments for {url}: {e}")

if __name__ == "__main__":
    # Start timing
    overall_start_time = time.time()
    
    # Read URLs from file
    with open('post_urls.txt', 'r') as f:
        urls = [url.strip() for url in f.readlines()]
    
    # Fetch comments for all URLs
    fetch_all_comments(urls)
    
    # End overall timing
    overall_end_time = time.time()
    overall_elapsed_time = overall_end_time - overall_start_time
    print(f"Total elapsed time: {overall_elapsed_time:.2f} seconds")
