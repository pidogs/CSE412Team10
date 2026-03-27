#!/usr/bin/env nix-shell
#! nix-shell -i python3 -p python3 python3Packages.requests

import requests
import csv
import os
import time

def get_existing_ids(filename):
    """Reads the CSV and returns a set of recordNumbers already processed."""
    if not os.path.exists(filename):
        return set()
    
    existing_ids = set()
    try:
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if "recordNumber" in row:
                    existing_ids.add(str(row["recordNumber"]))
    except Exception as e:
        print(f"Could not read existing file: {e}")
    return existing_ids

def fetch_records(start_id, end_id, output_file="naa_records.csv"):
    url = "https://naa.aero/wp-admin/admin-ajax.php"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0",
    }

    existing_ids = get_existing_ids(output_file)
    print(f"Found {len(existing_ids)} existing records. Scanning range {start_id} to {end_id}...")

    current_id = start_id
    step = 1
    miss_count = 0
    last_found_id = start_id

    while current_id <= end_id:
        str_num = str(current_id)
        
        if str_num in existing_ids:
            print(f"Skipping {str_num} (already exists).")
            last_found_id = current_id
            current_id += step
            continue

        payload = {"action": "retrieve_record", "recordNumber": current_id}

        try:
            response = requests.post(url, data=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

            if data.get("success") and data.get("record"):
                # HIT: We found a record
                if step > 1:
                    # If we were jumping, go back to the ID after the last success 
                    # to make sure we didn't skip anything in the gap.
                    print(f"Hit found at {current_id} after jumping! Backtracking...")
                    current_id = current_id - step

                    step = step//2
                    miss_count = 0
                    continue

                record = data["record"]
                holders = data.get("recordholders", [])
                holder_names = [
                    f"{h.get('nameFirst', '')} {h.get('nameLast', '')}".strip()
                    for h in holders
                ]
                record["recordHolders"] = "; ".join(holder_names)

                # Save record
                file_is_empty = not os.path.exists(output_file) or os.stat(output_file).st_size == 0
                with open(output_file, "a", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=record.keys())
                    if file_is_empty:
                        writer.writeheader()
                    writer.writerow(record)
                
                print(f"Successfully saved record: {current_id}")
                
                # Reset logic on success
                last_found_id = current_id
                miss_count = 0
                step = 1
                current_id += 1
                time.sleep(0.05) 

            else:
                # MISS: No data found
                print(f"No data for ID: {current_id}")
                miss_count += 1
                
                # If we miss 10 times in a row, increase the jump size
                if miss_count >= 5:
                    step = min(step*2,1000)
                    miss_count = 0 # Reset counter for the new step size
                    print(f"Increased step size to: {step}")
                
                current_id += step

        except Exception as e:
            print(f"Error fetching record {current_id}: {e}")
            time.sleep(5) # Wait longer on network errors
            current_id += 1 

if __name__ == "__main__":
    # Your requested range
    START = 800
    END = 200000
    fetch_records(START, END)