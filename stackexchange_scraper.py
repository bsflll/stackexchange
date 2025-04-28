import requests
import json
import time
from bs4 import BeautifulSoup

def scrape_stackexchange(start_page=1, end_page=197):
    """Scrape question pages from Reverse Engineering Stack Exchange
    :param start_page: starting page number
    :param end_page: ending page number
    """
    base_url = "https://reverseengineering.stackexchange.com/questions?tab=newest&page="
    
    # Initialize result list
    all_questions = []
    existing_count = 0
    
    for page in range(start_page, end_page + 1):
            
        url = base_url + str(page)
        print(f"Scraping page {page}...")
        
        try:
            # Send HTTP request
            response = requests.get(url)
            response.raise_for_status()
            
            # Parse HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract question list
            questions = soup.select('.s-post-summary')
            
            # Collect questions from current page
            for q in questions:
                # Extract question ID
                question_id = q.select_one('.s-post-summary--content-title a')['href'].split('/')[2]
                
                # Check if file already exists
                import os
                json_filename = os.path.join('reverseengineering', f"{question_id}.json")
                if os.path.exists(json_filename):
                    print(f"Question {question_id} already exists, skipping...")
                    existing_count += 1
                    if existing_count >= 100:
                        print("Reached 100 existing questions, terminating scraping")
                        return
                    continue
                
                all_questions.append({
                    'title': q.select_one('.s-post-summary--content-title a').text.strip(),
                    'link': q.select_one('.s-post-summary--content-title a')['href'],
                    'description': q.select_one('.s-post-summary--content-excerpt').text.strip(),
                    'votes': q.select_one('.s-post-summary--stats-item-number').text.strip(),
                    'answers': q.select('.s-post-summary--stats-item-number')[1].text.strip(),
                    'views': q.select('.s-post-summary--stats-item-number')[2].text.strip(),
                    'tags': [tag.text.strip() for tag in q.select('.s-tag')],
                    'user': q.select_one('.s-user-card--link a').text.strip() if q.select_one('.s-user-card--link a') else None,
                    'time': q.select_one('.relativetime').text.strip() if q.select_one('.relativetime') else None
                })
            
            # Add request interval to avoid being banned
            time.sleep(2)
            
            # Save data immediately after scraping each page
            with open('stackexchange_questions.json', 'w', encoding='utf-8') as f:
                json.dump(all_questions, f, ensure_ascii=False, indent=4)
                
            print(f"Page {page} data saved")
            
            # Check termination condition
            if existing_count >= 100:
                print("Reached 100 existing questions, terminating scraping")
                return
                
        except requests.exceptions.RequestException as e:
            print(f"Error scraping page {page}: {e}")
            continue

if __name__ == "__main__":
    scrape_stackexchange()