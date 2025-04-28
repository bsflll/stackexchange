import requests
import json
import time
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import html2text

def scrape_single_question(url,user):
    """Scrape detailed content of a single Stack Exchange question
    :param url: Full URL of the question page
    :param user: User who asked the question
    """
    print(f"Scraping question page: {url}")
    
    # Check if file already exists
    import os
    output_dir = './reverseengineering'
    os.makedirs(output_dir, exist_ok=True)
    json_filename = os.path.join(output_dir, url.split('/')[-2] + '.json')
    if os.path.exists(json_filename):
        print(f"File {json_filename} already exists, skipping")
        return
    
    
    # Send HTTP request
    session = requests.Session()
    retry_strategy = requests.adapters.HTTPAdapter(
        max_retries=3
    )
    session.mount('https://', retry_strategy)
    session.mount('http://', retry_strategy)
    
    response = session.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract question body
    question = soup.select_one('.question, .s-prose.js-post-body')
    if not question:
        print(f"Unable to find question body element: {url}")
        print(f"Response status code: {response.status_code}")
        print(f"First 100 characters of response content: {response.text[:100]}")
        print(f"Tried selectors: .question, .s-prose.js-post-body")
        return False


    # Extract detailed question information
    question_data = {
        'title': soup.select_one('h1.fs-headline1 a.question-hyperlink').text.strip() if soup.select_one('h1.fs-headline1 a.question-hyperlink') else None,
        'link': url,
        'content': str(soup.select_one('.s-prose.js-post-body')) if soup.select_one('.s-prose.js-post-body') else None,
        'votes': soup.select_one('.js-vote-count').text.strip() if soup.select_one('.js-vote-count') else None,
        'answers': len(soup.select('.answer')) if soup.select('.answer') else 0,
        'views': soup.select_one('div.flex--item.ws-nowrap.mb8[title*="Viewed"]').text.split()[1] if soup.select_one('div.flex--item.ws-nowrap.mb8[title*="Viewed"]') else None,
        'tags': [tag.text.strip() for tag in question.select('.s-tag')],
        'user': user,
        'time': question.select_one('.relativetime').text.strip() if question.select_one('.relativetime') else None,
        'comments': [
            {
                'user': c.select_one('.comment-user').text.strip() if c.select_one('.comment-user') else None,
                'text': str(c.select_one('.comment-copy')) if c.select_one('.comment-copy') else None,
                'time': c.select_one('.relativetime').text.strip() if c.select_one('.relativetime') else None
            } for c in question.select('.comment')
        ],
        'answers_data': [
            {
                'content': str(a.select_one('.js-post-body')) if a.select_one('.js-post-body') else None,
                'votes': a.select_one('.js-vote-count').text.strip(),
                'user': a.select_one('.user-details a').text.strip() if a.select_one('.user-details a') else None,
                'time': a.select_one('.relativetime').text.strip() if a.select_one('.relativetime') else None,
                'is_accepted': 'accepted-answer' in a.get('class', []),
                'comments': [
                    {
                        'user': c.select_one('.comment-user').text.strip() if c.select_one('.comment-user') else None,
                        'text': str(c.select_one('.comment-copy')) if c.select_one('.comment-copy') else None,
                        'time': c.select_one('.relativetime').text.strip() if c.select_one('.relativetime') else None
                    } for c in a.select('.comment')
                ]
            } for a in soup.select('.answer')
        ]
    }
    
    # Add request interval to avoid being banned
    time.sleep(2)
    
    # Save data
    import os
    output_dir = './reverseengineering'
    os.makedirs(output_dir, exist_ok=True)
    
    # Save as JSON format
    json_filename = os.path.join(output_dir, url.split('/')[-2] + '.json')
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(question_data, f, ensure_ascii=False, indent=4)

    print(f"Question data saved to {json_filename}")
    return True
        
        
def process_all_questions(json_file):
    """Process all question links in the JSON file
    :param json_file: Path to the JSON file containing question links
    """
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            questions = json.load(f)
        print(f"Found {len(questions)} questions, starting processing...")
        
        # Initialize error counter
        error_count = 0
        max_errors = 10
        
        # Use thread pool for parallel processing
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = []
            for i, q in enumerate(questions, 1):
                url = "https://reverseengineering.stackexchange.com" + q['link']
                futures.append(executor.submit(scrape_single_question, url, q['user']))
            
            # Use tqdm to show progress bar
            with tqdm(total=len(futures), desc="Processing Progress") as pbar:
                for future in as_completed(futures):
                    try:
                        future.result()
                        pbar.update(1)
                    except Exception as e:
                        print(f"Error processing question: {e}")
                        error_count += 1
                        pbar.update(1)
                        
                        # Check if error count reaches threshold
                        if error_count >= max_errors:
                            print(f"Error count reached {error_count}, terminating scraping")
                            executor._threads.clear()
                            for f in futures:
                                f.cancel()
                            break
            
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading JSON file: {e}")

if __name__ == "__main__":
    # Example: Process all questions from stackexchange_questions.json
    process_all_questions('stackexchange_questions.json')
    
    # Alternatively, handle a specific URL
    # url = "https://reverseengineering.stackexchange.com/questions/33410/interpreting-binary-data-with-repeating-xxxx-xx40-structure"
    # scrape_single_question(url)