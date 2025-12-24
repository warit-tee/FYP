import requests
import os
import csv
import json
import time

# Define directories
current_dir = os.path.dirname(__file__)
essays_dir = os.path.join(current_dir, '..', 'datasets', 'essays')
output_csv_path = os.path.join(current_dir, 'zerogpt_results.csv')

print(f"Reading files from: {essays_dir}")

# Read already processed files
done = []
if os.path.isfile(output_csv_path):
    try:
        with open(output_csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None) # Skip header
            for row in reader:
                if len(row) > 1:
                    done.append(row[1])
    except Exception:
        pass

# Check if file exists
file_exists = os.path.isfile(output_csv_path)

# Open CSV file for appending
with open(output_csv_path, mode='a', newline='', encoding='utf-8') as csv_file:
    writer = csv.writer(csv_file)
    # Write the header row if file is new
    if not file_exists:
        writer.writerow(['filepath', 'filename', 'fakePercentage', 'isHuman', 'feedback', 'aiWords', 'textWords'])

    # Iterate over all files in the directory
    for filename in os.listdir(essays_dir):
        # Skip hidden files
        if filename.startswith('.'):
            continue

        if filename in done:
            print(f"Skipping already processed file: {filename}")
            continue

        file_path = os.path.join(essays_dir, filename)

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                file_content = file.read()

            # ZeroGPT API endpoint
            url = "https://api.zerogpt.com/api/detect/detectText"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Content-Type': 'application/json',
                'Origin': 'https://www.zerogpt.com',
                'Referer': 'https://www.zerogpt.com/'
            }
            
            payload = {
                "text": file_content,
                "input_text": file_content
            }

            response = requests.post(url, headers=headers, json=payload)

            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    result_data = data.get('data', {})
                    row = [
                        file_path,
                        filename,
                        result_data.get('fakePercentage'),
                        result_data.get('isHuman'),
                        result_data.get('feedback'),
                        result_data.get('aiWords'),
                        result_data.get('textWords')
                    ]
                    writer.writerow(row)
                    print(f"Successfully processed: {filename}")
                else:
                    print(f"API returned success=False for: {filename}")
                    print(data)
            else:
                print(f"Failed API request for: {filename}")
                print('Error: ', response.status_code, response.text)
            
            # Add a small delay to avoid rate limiting
            time.sleep(1)

        except Exception as e:
            print(f"Failed processing file: {filename}")
            print(f"Error details: {e}")

print(f"Processing complete. Results saved to {output_csv_path}")
