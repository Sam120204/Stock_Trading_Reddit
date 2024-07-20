import requests
from bs4 import BeautifulSoup
import time
import random

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
    
    # Extracting the title
    title_tag = soup.find('shreddit-title')
    title = title_tag['title'] if title_tag else 'N/A'
    
    # Extracting the score
    post_tag = soup.find('shreddit-post')
    score = post_tag['score'] if post_tag and 'score' in post_tag.attrs else 'N/A'
    
    # Extracting the number of comments
    comments = post_tag['comment-count'] if post_tag and 'comment-count' in post_tag.attrs else 'N/A'
    
    # Extracting comments URL from faceplate-partial with name="TopComments_9T32hK"
    comments_url_tag = soup.find('faceplate-partial', {'name': 'TopComments_9T32hK'})
    comments_url = comments_url_tag['src'] if comments_url_tag else 'N/A'
    
    # Handling potential HTML structure changes
    if title == 'N/A':
        title_tag = soup.find('h1')
        title = title_tag.text if title_tag else 'N/A'
    
    if score == 'N/A':
        score_tag = soup.find('div', {'data-test-id': 'score'})
        score = score_tag.text if score_tag else 'N/A'
    
    if comments == 'N/A':
        comments_tag = soup.find('span', {'class': 'comments'})
        comments = comments_tag.text if comments_tag else 'N/A'
    
    return {
        'title': title,
        'score': score,
        'comments': comments,
        'comments_url': comments_url
    }

def fetch_comments(comments_url):
    base_url = "https://www.reddit.com"
    full_url = base_url + comments_url
    headers = {
        'User-Agent': random.choice(USER_AGENTS)
    }
    for attempt in range(5):  # Retry up to 5 times
        response = requests.get(full_url, headers=headers)
        if response.status_code == 200:
            return response.text
        elif response.status_code == 429:
            print(f"Rate limited. Retrying in 10 seconds... (Attempt {attempt + 1})")
            time.sleep(10)  # Wait for 10 seconds before retrying
        else:
            print(f"Failed to fetch comments from {full_url}: {response.status_code}")
            return None
    return None

def parse_comments(html, score_threshold):
    soup = BeautifulSoup(html, 'html.parser')
    comments = []

    # Parsing all comments
    comment_tags = soup.find_all('shreddit-comment-action-row')

    for comment_tag in comment_tags:
        parent = comment_tag.find_parent('shreddit-comment')
        comment_text_tag = parent.find('div', {'slot': 'comment'})
        comment_text = clean_text(comment_text_tag.get_text() if comment_text_tag else '')
        comment_score = comment_tag['score'] if 'score' in comment_tag.attrs else 'N/A'
        
        # Filtering comments with absolute score greater than or equal to the threshold
        if comment_score != 'N/A' and abs(int(comment_score)) >= score_threshold:
            comments.append({
                'text': comment_text,
                'score': comment_score
            })

    return comments

def clean_text(text):
    # Remove redundant whitespace and other cleanup
    lines = text.strip().split('\n')
    cleaned_lines = [line.strip() for line in lines if line.strip()]
    return ' '.join(cleaned_lines)

if __name__ == "__main__":
    # Start timing
    start_time = time.time()
    
    # Read URLs from file
    with open('post_urls.txt', 'r') as f:
        urls = f.readlines()
    
    for url in urls:
        url = url.strip()
        html = fetch_reddit_post(url)
        if html:
            post_details = parse_post(html)
            
            if post_details['comments_url'] != 'N/A':
                post_score = int(post_details['score']) if post_details['score'] != 'N/A' else 0
                score_threshold = max(10, int(post_score * 0.15))  # 10% of the post score or 10, whichever is higher

                comments_html = fetch_comments(post_details['comments_url'])
                if comments_html:
                    comments_details = parse_comments(comments_html, score_threshold)
                    post_details['comments_details'] = comments_details

            print(post_details)
        else:
            print(f"Failed to fetch post details for URL: {url}")
        
        # Add delay between requests
        time.sleep(5)
    
    # End timing
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Total elapsed time: {elapsed_time:.2f} seconds")
