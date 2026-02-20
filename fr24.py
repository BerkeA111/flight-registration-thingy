from curl_cffi import requests
import pandas as pd
import time
import sys

def fetch_fr24_msn(registration):
    url = f"https://www.flightradar24.com/v1/search/web/find?query={registration}&limit=1"
    
    headers = {
        "Accept": "application/json",
        "Referer": "https://www.flightradar24.com/"
    }
    
    try:
        response = requests.get(url, headers=headers, impersonate="chrome", timeout=10)
        
        if response.status_code != 200:
            return None, None
            
        data = response.json()
        
        if "results" in data and len(data["results"]) > 0:
            result = data["results"][0]
            if result.get("type") == "aircraft":
                details = result.get("detail", {})
                return details.get("msn"), details.get("equip")
                
        return None, None
        
    except Exception as e:
        print(f"[{registration}] Network Exception: {e}")
        return None, None

def process_live_extraction(input_file, output_file):
    print("Loading flat registration list...")
    try:
        df = pd.read_csv(input_file, header=None, names=['registration'])
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
        sys.exit(1)
        
    registrations = df['registration'].dropna().astype(str).str.strip().str.upper().tolist()
    
    results = []
    total = len(registrations)
    
    print(f"Initiating TLS-Spoofed FR24 API extraction for {total} aircraft...")
    
    for i, reg in enumerate(registrations, 1):
        msn, model = fetch_fr24_msn(reg)
        
        status = msn if msn else "NO DATA ON FR24"
        print(f"[{i}/{total}] {reg} -> MSN: {status}")
        
        results.append({
            "Registration": reg,
            "Aircraft_Model": model,
            "MSN": msn
        })
        
        time.sleep(1.5)
        
    output_df = pd.DataFrame(results)
    output_df.to_csv(output_file, index=False)
    
    found_count = output_df['MSN'].notna().sum()
    print("EXTRACTION COMPLETE")
    print(f"Total Processed: {total}")
    print(f"MSNs Successfully Ripped: {found_count}")
    print(f"Output saved to: {output_file}")

if __name__ == "__main__":
    INPUT_FILE = "flat_registrations.csv"
    OUTPUT_FILE = "fr24_master_msn_list.csv"
    
    process_live_extraction(INPUT_FILE, OUTPUT_FILE)
