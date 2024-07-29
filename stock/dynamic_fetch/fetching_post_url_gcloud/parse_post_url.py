import requests
from bs4 import BeautifulSoup
import random
import time

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

def fetch_reddit_post(url):
    headers = {
        'User-Agent': random.choice(USER_AGENTS)
    }
    for attempt in range(5):  # Retry up to 5 times
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        elif response.status_code == 429:
            print(f"Rate limited. Retrying in 10 seconds... (Attempt {attempt + 1})")
            time.sleep(10)  # Wait for 10 seconds before retrying
        else:
            print(f"Failed to fetch data from {url}: {response.status_code}")
            return None
    return None

def parse_post(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    # Extracting the score
    post_tag = soup.find('shreddit-post')
    score = post_tag['score'] if post_tag and 'score' in post_tag.attrs else 'N/A'
    
    # Extracting the number of comments
    comments = post_tag['comment-count'] if post_tag and 'comment-count' in post_tag.attrs else 'N/A'
    
    return {
        'score': score,
        'comments': comments
    }

def main(url):
    html = fetch_reddit_post(url)
    if html:
        post_details = parse_post(html)
        print(post_details)
    else:
        print(f"Failed to fetch post details for URL: {url}")

if __name__ == "__main__":
    # Example URL for testing
    url = 'https://www.reddit.com/r/wallstreetbets/comments/1eege3z/let_the_debate_begin/'
    main(url)
