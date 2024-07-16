import requests
from bs4 import BeautifulSoup
import time

def fetch_reddit_post(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to fetch data: {response.status_code}")
        return None

def parse_post(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    # Extracting the title
    title_tag = soup.find('shreddit-title')
    title = title_tag['title'] if title_tag else 'N/A'
    
    # Extracting the score and number of comments
    post_tag = soup.find('shreddit-post')
    score = post_tag['score'] if post_tag and 'score' in post_tag.attrs else 'N/A'
    comments = post_tag['comment-count'] if post_tag and 'comment-count' in post_tag.attrs else 'N/A'
    
    # Extracting comments URL
    comments_url_tag = soup.find('faceplate-partial', {'name': 'comments_forest'})
    comments_url = comments_url_tag['src'] if comments_url_tag else 'N/A'
    
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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(full_url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to fetch comments: {response.status_code}")
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
    
    url = 'https://www.reddit.com/r/wallstreetbets/comments/1e3w4bn/another_15k_day/'  # replace with your specific URL
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
    
    # End timing
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Total elapsed time: {elapsed_time:.2f} seconds")
