import pandas as pd
from pathlib import Path
import os
from datetime import datetime

def sync_google_form(url):
    csv_path = Path(r"C:\Users\chalu\Downloads\PyAutomate_v2_updated\PyAutomate\data\recipients.csv")
    
    # Read Google Form CSV
    print(f"Fetching data from Google Form CSV...")
    try:
        df_google = pd.read_csv(url)
    except Exception as e:
        print(f"Failed to fetch Google Form data: {e}")
        return
        
    # Read existing recipients to avoid duplicates
    existing_emails = set()
    if csv_path.exists():
        try:
            df_existing = pd.read_csv(csv_path)
            if 'Email' in df_existing.columns:
                existing_emails = set(df_existing['Email'].dropna().str.strip().str.lower())
        except Exception as e:
            print(f"Warning: Could not read existing recipients.csv: {e}")
            
    excel_path = Path(r"C:\Users\chalu\Downloads\PyAutomate_v2_updated\PyAutomate\data\visitors.xlsx")
    new_visitors = []

    # Open CSV for appending
    os.makedirs(csv_path.parent, exist_ok=True)
    with open(csv_path, 'a', encoding='utf-8') as f:
        # If file is empty, write headers
        if not csv_path.exists() or os.path.getsize(csv_path) == 0:
            f.write("Name,Email,Subject,Message,\n")
            
        added_count = 0
        for _, row in df_google.iterrows():
            email = str(row.get('Email Address', '')).strip()
            if not email or email.lower() == 'nan':
                continue
                
            email_lower = email.lower()
            if email_lower in existing_emails:
                continue # Skip duplicates
                
            name = str(row.get('Name', '')).replace(',', '').strip()
            reason = str(row.get('Reason for Visit', '')).replace(',', '').strip()
            if reason.lower() == 'nan':
                reason = "Not specified"
            
            subject = "Visitor Web Registration"
            message = f"Hi {name} thank you for registering! Reason: {reason}"
            
            timestamp_str = str(row.get('Timestamp', '')).strip()
            if not timestamp_str or timestamp_str.lower() == 'nan':
                 timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            new_visitors.append({
                "Timestamp": timestamp_str,
                "Name": name,
                "Email": email,
                "Reason": reason
            })
            
            f.write(f"{name},{email},{subject},{message},\n")
            existing_emails.add(email_lower)
            added_count += 1
            
    if new_visitors:
        try:
            df_new = pd.DataFrame(new_visitors)
            if excel_path.exists():
                df_old = pd.read_excel(excel_path)
                df_final = pd.concat([df_old, df_new], ignore_index=True)
            else:
                df_final = df_new
            df_final.to_excel(excel_path, index=False)
            print(f"Successfully synced {len(new_visitors)} new registrations to visitors.xlsx (Dashboard).")
        except Exception as e:
            print(f"Failed to sync to visitors.xlsx: {e}")

    print(f"Successfully synced {added_count} new registrations to recipients.csv!")

if __name__ == "__main__":
    PUBLISHED_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSp09fg76OTDxkun8UCEPZbnoa18WYPNFmd-RCcmffC2NnWaGXtkmL8fgqoAhs1iGHNR_KDirMv_5aH/pub?output=csv"
    sync_google_form(PUBLISHED_CSV_URL)
