import pandas as pd
import re
import sys

def sanitize_registration(reg_string):
    if pd.isna(reg_string):
        return ""
    
    raw_string = str(reg_string).upper()
    cleaned_string = re.sub(r'[^A-Z0-9\-]', '', raw_string)
    
    return cleaned_string

def process_extraction(input_file, sheet, column_name, output_file):
    try:
        df = pd.read_excel(input_file, sheet_name=sheet)
    except FileNotFoundError:
        print("Error: File not found.")
        sys.exit(1)
    except Exception as e:
        print(e)
        sys.exit(1)

    if column_name not in df.columns:
        print("Error: Column missing.")
        sys.exit(1)

    df['Sanitized'] = df[column_name].apply(sanitize_registration)
    
    clean_df = df[df['Sanitized'] != '']
    
    clean_df['Sanitized'].to_csv(output_file, index=False, header=False)
    print("Extraction complete.")

if __name__ == "__main__":
    INPUT_FILE = "table.xlsx"
    SHEET_NAME = "FLOTA ACTUAL"
    TARGET_COLUMN = "MATRÍCULA"
    OUTPUT_FILE = "flat_registrations.csv"
    
    process_extraction(INPUT_FILE, SHEET_NAME, TARGET_COLUMN, OUTPUT_FILE)
