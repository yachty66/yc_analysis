#### imports
import requests
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import re
from supabase import create_client, Client

# Load environment variables from .env file
load_dotenv()


def main():
    url = "https://ra.co/events/us/sanfrancisco"
    proxy_username = os.getenv('proxy_username')
    proxy_password = os.getenv('proxy_password')
    proxy_url = os.getenv('proxy_url')
    html_content_start_page=fetch_start_page(url, proxy_username, proxy_password, proxy_url)
    print("html content start page", html_content_start_page)
    events=parse_events(html_content_start_page)
    print("events", events)
    event_details=fetch_event_details(events, proxy_username, proxy_password, proxy_url)
    print("event details", event_details)
    push_to_database(event_details)

#### get first page
def fetch_start_page(url, proxy_username, proxy_password, proxy_url, retries=3):
    proxies = {
        'http': f'http://{proxy_username}:{proxy_password}@{proxy_url}',
        'https': f'http://{proxy_username}:{proxy_password}@{proxy_url}'
    }
    attempt = 0
    while attempt < retries:
        response = requests.get(url, proxies=proxies, verify=False)
        if response.status_code == 200:
            return response.text
        attempt += 1
        print(f"Attempt {attempt}: Failed to retrieve the page, retrying...")
    return "Failed to retrieve the page after {retries} attempts"


#### get first section 
def parse_events(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    first_section = soup.find('div', class_='Box-sc-abq4qd-0 esoJCv')
    event_links = first_section.find_all('a', href=re.compile(r'https://ra.co/events/\d+'))
    unique_links = set()
    for link in event_links:
        if 'href' in link.attrs:
            unique_links.add(link['href'])
    return list(unique_links)


#### get all event details 
def fetch_with_web_unlocker(url, proxy_username, proxy_password, proxy_url, retries=3):
        proxies = {
            'http': f'http://{proxy_username}:{proxy_password}@{proxy_url}',
            'https': f'http://{proxy_username}:{proxy_password}@{proxy_url}'
        }
        attempt = 0
        while attempt < retries:
            response = requests.get(url, proxies=proxies, verify=False)
            if response.status_code == 200:
                return response.text
            attempt += 1
        return None  # Return None if all retries fail

def fetch_event_details(events, proxy_username, proxy_password, proxy_url):
    proxy_username = os.getenv('proxy_username')
    proxy_password = os.getenv('proxy_password')
    proxy_url = os.getenv('proxy_url')
    # Loop through each URL, fetch the content, and parse for name and address
    event_details = []
    for url in events:
        html_content = fetch_with_web_unlocker(url, proxy_username, proxy_password, proxy_url)
        if html_content:
            soup = BeautifulSoup(html_content, 'html.parser')
            name = soup.find('h1', class_='Heading__StyledBox-rnlmr6-0').text.strip()
            # Find the address within the specific span element
            address_container = soup.find('li', class_='Column-sc-4kt5ql-0')
            if address_container:
                address_span = address_container.find('span', class_='Text-sc-wks9sf-0', string=lambda text: "St" in text or "Ave" in text or "Blvd" in text or "Rd" in text)
                address = address_span.text.strip() if address_span else "Address not found"
            else:
                address = "Address container not found"
            event_details.append({'url': url, 'name': name, 'address': address})
            print("event details for ", name, "with address ", address, "and url ", url)
        else:
            print(f"Failed to fetch content for {url}.", html_content)
    return event_details


#### push to database 
def push_to_database(event_details):
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    supabase: Client = create_client(url, key)
    data = {
        'events': event_details  
    }
    response = supabase.table('resident_advisor').insert(data).execute()
    return response

main()