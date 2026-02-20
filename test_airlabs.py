import requests
import json
import sys

def fetch_single_aircraft_data(api_key, registration):
    url = f"https://airlabs.co/api/v9/fleets?reg_number={registration}&api_key={api_key}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        print(json.dumps(data, indent=4))
        
    except requests.exceptions.RequestException as e:
        print("HTTP Request failed.")
        print(e)
        sys.exit(1)

if __name__ == "__main__":
    API_KEY = "9450caac-a853-46ef-bde1-d6cfdf0b4f0a"
    TEST_REGISTRATION = "9H-IBJ"
    
    fetch_single_aircraft_data(API_KEY, TEST_REGISTRATION)
