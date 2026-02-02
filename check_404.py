
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

BASE_URL = "https://yohi.github.io/docs-manager/"

def get_links(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        links = set()
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            full_url = urljoin(url, href)
            # Only check internal links or related
            if full_url.startswith(BASE_URL):
                links.add(full_url)
        return links
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return set()

def check_link(url):
    try:
        response = requests.head(url, allow_redirects=True)
        if response.status_code == 404:
            # Try GET if HEAD fails (some servers don't like HEAD)
             response = requests.get(url, allow_redirects=True)
        
        return response.status_code
    except Exception as e:
        return f"Error: {e}"

def main():
    print(f"Scanning {BASE_URL} for links...")
    links = get_links(BASE_URL)
    print(f"Found {len(links)} links.")
    
    broken_links = []
    
    print("\nChecking links...")
    for link in links:
        status = check_link(link)
        if status == 404:
            print(f"[404] {link}")
            broken_links.append(link)
        # else:
        #     print(f"[{status}] {link}")

    print("\nExtraction Complete.")
    if broken_links:
        print(f"Found {len(broken_links)} 404 pages:")
        for link in broken_links:
            print(link)
    else:
        print("No 404 pages found linked from the homepage.")

if __name__ == "__main__":
    main()
