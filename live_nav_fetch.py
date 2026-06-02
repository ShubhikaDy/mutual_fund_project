import os
import requests
import pandas as pd

# Define the scheme codes from your task sheet
HDFC_SCHEME = "125497"
KEY_SCHEMES = {
    "SBI_Bluechip": "119551",
    "ICICI_Bluechip": "120503",
    "Nippon_Large_Cap": "118632",
    "Axis_Bluechip": "119092",
    "Kotak_Bluechip": "120841"
}

RAW_DATA_DIR = os.path.join("data", "raw")

def fetch_and_save_nav(scheme_code, filename):
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    print(f"Fetching data for scheme code: {scheme_code}...")
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            
            # Extract meta information and historical data arrays
            meta = data.get("meta", {})
            nav_list = data.get("data", [])
            
            # Convert the list of dictionaries into a DataFrame table
            df = pd.DataFrame(nav_list)
            
            # Add scheme metadata details into every row for easier future tracking
            df["scheme_code"] = meta.get("scheme_code")
            df["scheme_name"] = meta.get("scheme_name")
            
            # Save it to data/raw/ filename.csv
            output_path = os.path.join(RAW_DATA_DIR, f"{filename}.csv")
            df.to_csv(output_path, index=False)
            print(f"Successfully saved to {output_path}")
        else:
            print(f"Failed to fetch {scheme_code}. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Fetch HDFC Top 100 Direct
    fetch_and_save_nav(HDFC_SCHEME, "hdfc_top_100_live")
    
    # Fetch the other 5 Key Schemes
    for name, code in KEY_SCHEMES.items():
        fetch_and_save_nav(code, f"{name.lower()}_live")