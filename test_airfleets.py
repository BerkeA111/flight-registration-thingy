from curl_cffi import requests
from bs4 import BeautifulSoup
import sys
import re

def test_airfleets_extraction(registration):
    # Construct the search query URL
    url = f"https://www.airfleets.net/recherche/?clef={registration}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.airfleets.net/"
    }
    
    print(f"Executing TLS-spoofed request to Airfleets for {registration}...")
    
    try:
        response = requests.get(url, headers=headers, impersonate="chrome", timeout=15)
        
        if response.status_code != 200:
            print(f"HTTP Failure: {response.status_code}")
            sys.exit(1)
            
        html_content = response.text
        
        # WAF Detection
        if "captcha" in html_content.lower() or "access denied" in html_content.lower():
            print("CRITICAL FAILURE: Airfleets WAF intercepted the request. CAPTCHA served.")
            sys.exit(1)
            
        soup = BeautifulSoup(html_content, 'html.parser')
        
        print(f"Page Title Retrieved: {soup.title.string if soup.title else 'No Title'}")
        
        msn_value = None
        
        # DOM Traversal Protocol: Hunt for the MSN cell
        for td in soup.find_all('td'):
            text = td.get_text(strip=True)
            # The site typically labels the data as "MSN"
            if text.upper() == "MSN" or "SERIAL NUMBER" in text.upper():
                next_td = td.find_next_sibling('td')
                if next_td:
                    msn_value = next_td.get_text(strip=True)
                    break
        
        if msn_value:
            print(f"SUCCESS: Extracted MSN -> {msn_value}")
        else:
            print("HTML fetched, but MSN not found in the standard DOM location.")
            print("Fallback regex search on raw HTML...")
            # Fallback: regex to find MSN followed by digits in the raw text
            match = re.search(r'MSN.*?(\d{3,6})', html_content, re.IGNORECASE)
            if match:
                print(f"Regex Extracted MSN -> {match.group(1)}")
            else:
                print("Data not found. The registration may not exist on this site, or the search returned a list instead of a direct aircraft profile.")
                
    except Exception as e:
        print(f"Network Exception: {e}")
        sys.exit(1)

if __name__ == "__main__":
    TEST_REGISTRATION = "9H-IBJ" 
    test_airfleets_extraction(TEST_REGISTRATION)
