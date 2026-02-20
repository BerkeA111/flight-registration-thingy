import pandas as pd
import sys

def process_msn_mapping(target_file, opensky_db_file, output_file):
    print("Loading datasets...")
    
    try:
        # Read the flat list of registrations. We assign the column name 'registration' manually.
        target_df = pd.read_csv(target_file, header=None, names=['registration'])
    except FileNotFoundError:
        print(f"Error: {target_file} not found.")
        sys.exit(1)

    try:
        # Read the OpenSky database. We only load the columns we need to save RAM.
        # low_memory=False prevents DtypeWarnings on massive CSVs.
        opensky_df = pd.read_csv(opensky_db_file, usecols=['registration', 'serialnumber', 'model'], low_memory=False)
    except FileNotFoundError:
        print(f"Error: {opensky_db_file} not found. Did you run the curl command?")
        sys.exit(1)

    # Normalize both dataframes to ensure perfect matching
    # Drop NaN registrations from OpenSky to prevent matching errors
    opensky_df = opensky_df.dropna(subset=['registration'])
    
    # Force everything to uppercase and strip accidental spaces
    target_df['registration'] = target_df['registration'].astype(str).str.strip().str.upper()
    opensky_df['registration'] = opensky_df['registration'].astype(str).str.strip().str.upper()

    print(f"Mapping {len(target_df)} registrations against the OpenSky database...")

    # Perform a Left Join: Keep all our target registrations, pull in MSN and model if available
    merged_df = target_df.merge(opensky_df, on='registration', how='left')

    # Rename columns for clarity in the final output
    merged_df.rename(columns={'serialnumber': 'MSN', 'model': 'Aircraft_Model'}, inplace=True)

    # Export to CSV
    merged_df.to_csv(output_file, index=False)
    
    # Calculate success rate for immediate analytical feedback
    total = len(merged_df)
    found = merged_df['MSN'].notna().sum()
    
    print("==================================================")
    print("EXTRACTION COMPLETE")
    print(f"Total Registrations Processed: {total}")
    print(f"MSNs Successfully Found: {found}")
    print(f"Missing Data: {total - found}")
    print(f"Output saved to: {output_file}")
    print("==================================================")

if __name__ == "__main__":
    TARGET_REGISTRATIONS = "flat_registrations.csv"
    OPENSKY_DATABASE = "aircraftDatabase.csv"
    OUTPUT_FILE = "final_registration_msn.csv"
    
    process_msn_mapping(TARGET_REGISTRATIONS, OPENSKY_DATABASE, OUTPUT_FILE)
