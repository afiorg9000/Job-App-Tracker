import requests
from bs4 import BeautifulSoup
from notion_client import Client
import os
from datetime import datetime
from urllib.parse import urlparse
from dotenv import load_dotenv
import openai

load_dotenv()

notion = Client(auth=os.environ["NOTION_API_KEY"])
DATABASE_ID = os.environ["NOTION_DATABASE_ID"]
openai.api_key = os.environ["OPENAI_API_KEY"]

def analyze_with_gpt(text):
    prompt = f"""
    Extract the following information from this job posting:
    - Company name
    - Job location
    - Tech stack (programming languages, frameworks, tools, and technologies mentioned)
    
    Format the response as JSON with these keys:
    - company
    - location
    - tech_stack (as a single string, with technologies separated by commas)
    
    Job posting text:
    {text}
    """
    
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that extracts job posting information. Focus on identifying technical requirements and tools. Always return tech_stack as a comma-separated string."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1
    )
    
    try:
        result = eval(response.choices[0].message.content)
        if isinstance(result['tech_stack'], list):
            result['tech_stack'] = ', '.join(result['tech_stack'])
        return result
    except:
        return {
            "company": "Not found",
            "location": "Not found",
            "tech_stack": "Not found"
        }

def extract_job_info(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        text_content = soup.get_text(separator=' ', strip=True)
        gpt_analysis = analyze_with_gpt(text_content)
        
        title_elem = (soup.find('h1') or 
                     soup.find('title') or 
                     soup.find(class_=lambda x: x and ('job-title' in x.lower() or 'jobtitle' in x.lower())))
        title = title_elem.get_text().strip()[:100] if title_elem else "Not found"
        
        job_data = {
            'title': title,
            'company': gpt_analysis['company'][:100],
            'location': gpt_analysis['location'][:100],
            'tech_stack': str(gpt_analysis['tech_stack'])[:2000]
        }
        
        print("Extracted data:", job_data)
        return job_data
        
    except requests.exceptions.RequestException as e:
        print(f"RequestException: {str(e)}")
        return None
    except Exception as e:
        print(f"Error processing job: {str(e)}")
        return None

def add_to_notion(job_data, url):
    new_page = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Title": {"title": [{"text": {"content": job_data['title'][:100]}}]},
            "Company": {"rich_text": [{"text": {"content": job_data['company'][:100]}}]},
            "Location": {"rich_text": [{"text": {"content": job_data['location'][:100]}}]},
            "Tech Stack": {"rich_text": [{"text": {"content": job_data['tech_stack'][:1900]}}]},
            "Status": {"select": {"name": "To Apply"}},
            "URL": {"url": url},
            "Date Added": {"date": {"start": datetime.now().date().isoformat()}},
            "Source": {"select": {"name": urlparse(url).netloc}}
        }
    }
    
    notion.pages.create(**new_page)

def process_job_url(url):
    try:
        job_data = extract_job_info(url)
        if job_data:
            add_to_notion(job_data, url)
            return True, "Job successfully added to Notion"
        else:
            return False, "Failed to extract job information"
    except Exception as e:
        return False, f"Error processing job: {str(e)}"

def read_urls_from_file(filename):
    try:
        with open(filename, 'r') as file:
            urls = [line.strip() for line in file if line.strip()]
            print(f"Reading from {os.path.abspath(filename)}")
            if not urls:
                print("Warning: File is empty or contains no valid URLs")
            return urls
    except FileNotFoundError:
        print(f"Error: Could not find {os.path.abspath(filename)}")
        raise
    except Exception as e:
        print(f"Error reading file: {str(e)}")
        raise

def process_multiple_urls(urls):
    results = []
    for url in urls:
        print(f"\nProcessing: {url}")
        success, message = process_job_url(url)
        results.append({
            'url': url,
            'success': success,
            'message': message
        })
    
    print("\n=== Processing Summary ===")
    successful = sum(1 for r in results if r['success'])
    print(f"Successfully processed: {successful}/{len(results)}")
    
    failures = [r for r in results if not r['success']]
    if failures:
        print("\nFailed URLs:")
        for failure in failures:
            print(f"- {failure['url']}: {failure['message']}")

if __name__ == "__main__":
    print("Choose an option:")
    print("1. Process single URL")
    print("2. Process all URLs from jobs.txt")
    
    choice = input("Enter your choice (1 or 2): ")
    
    if choice == "1":
        url = input("Enter job posting URL: ")
        success, message = process_job_url(url)
        print(message)
    elif choice == "2":
        try:
            print("Looking for jobs.txt in:", os.getcwd())
            urls = read_urls_from_file('jobs.txt')
            print(f"Found {len(urls)} URLs to process")
            if urls:
                process_multiple_urls(urls)
            else:
                print("No URLs found to process. Please check your jobs.txt file.")
        except FileNotFoundError:
            print("Error: jobs.txt file not found. Please create a jobs.txt file in the same directory as this script.")
        except Exception as e:
            print(f"Error processing file: {str(e)}")
    else:
        print("Invalid choice. Please enter 1 or 2.")