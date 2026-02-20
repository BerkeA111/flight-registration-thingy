import undetected_chromedriver as uc
import pandas as pd
import time
import sys
import os
import re

def execute_stealth_extraction(input_csv, output_csv):
    print("Initializing patched Brave binary...")
    mac_brave_path = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
    
    if not os.path.exists(mac_brave_path):
        print(f"CRITICAL ERROR: Brave Browser not found at {mac_brave_path}.")
        sys.exit(1)
    
    options = uc.ChromeOptions()
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--no-sandbox')
    
    try:
        driver = uc.Chrome(options=options, browser_executable_path=mac_brave_path)
    except Exception as e:
        print(f"Failed to initialize Brave Driver: {e}")
        sys.exit(1)
    
    print("Navigating to Airfleets.net...")
    driver.get("https://www.airfleets.net/home/")
    
    print("\n[!] MANUAL INTERVENTION REQUIRED [!]")
    print("1. Solve the Cloudflare CAPTCHA in the browser.")
    print("2. Turn OFF Brave Shields for this site.")
    input("3. Press ENTER in this terminal ONLY when you have completed these steps...")
    
    try:
        df = pd.read_csv(input_csv, header=None, names=['registration'])
        registrations = df['registration'].dropna().astype(str).str.strip().str.upper().tolist()
    except Exception as e:
        print(f"Data ingestion failed: {e}")
        driver.quit()
        sys.exit(1)

    results = []
    total = len(registrations)
    print(f"\nInitiating Direct Regex extraction for {total} targets...")
    
    for i, reg in enumerate(registrations, 1):
        # THE FIX: Using ?key= instead of ?clef=
        url = f"https://www.airfleets.net/recherche/?key={reg}"
        driver.get(url)
        
        # WAF check
        if "Just a moment" in driver.title or "Cloudflare" in driver.title:
            print(f"\n[!] WAF RE-ENGAGED ON {reg} [!]")
            input("Solve the CAPTCHA in the browser, then press ENTER here...")
            driver.get(url)
            
        # Allow HTML to render
        time.sleep(2)
        
        msn_value = None
        html_source = driver.page_source
        
        # REGEX STRIKE: Finds 'ficheapp/plane-a320-3259.htm' and extracts '3259'
        # This completely ignores malformed HTML tags and missing </a> closures.
        match = re.search(r'ficheapp/plane-[^"]+-(\d+)\.htm', html_source)
        
        if match:
            msn_value = match.group(1)
        else:
            # Fallback if the site bypasses the search grid and goes straight to the profile
            if "ficheapp/plane-" in driver.current_url:
                msn_value = driver.current_url.split('-')[-1].replace('.htm', '')
                
        status = msn_value if msn_value else "NOT FOUND IN HTML"
        print(f"[{i}/{total}] {reg} -> MSN: {status}")
        
        results.append({
            "Registration": reg,
            "MSN": msn_value
        })
        
    driver.quit()
    output_df = pd.DataFrame(results)
    output_df.to_csv(output_csv, index=False)
    print(f"\nExtraction complete. Exported to {output_csv}")

if __name__ == "__main__":
    TARGET_FILE = "flat_registrations.csv"
    OUTPUT_FILE = "airfleets_msn_master.csv"
    execute_stealth_extraction(TARGET_FILE, OUTPUT_FILE)
