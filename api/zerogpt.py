import requests
import os
import csv
import json
import time

# Define directories
current_dir = os.path.dirname(__file__)
essays_dir = os.path.join(current_dir, '..', 'datasets', 'humanized_essays', 'writehuman.ai')
output_csv_path = os.path.join(current_dir, 'zerogpt_results.csv')

def get_score(file_content):
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
            return data.get('data', {})
        else:
            print("API returned success=False")
            print(data)
    else:
        print("Failed API request")
        print('Error: ', response.status_code, response.text)
    
    return None


def save_score(output_csv_path, relative_path, filename, result_data):
    file_exists = os.path.isfile(output_csv_path)
    with open(output_csv_path, mode='a', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        if not file_exists:
            writer.writerow(['filepath', 'filename', 'fakePercentage', 'isHuman', 'feedback', 'aiWords', 'textWords'])
        row = [
            relative_path,
            filename,
            result_data.get('fakePercentage'),
            result_data.get('isHuman'),
            result_data.get('feedback'),
            result_data.get('aiWords'),
            result_data.get('textWords')
        ]
        writer.writerow(row)

def main():
    print(f"Reading files from: {essays_dir}")
    done = []
    if os.path.isfile(output_csv_path):
        try:
            with open(output_csv_path, mode='r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader, None) # Skip header
                for row in reader:
                    if len(row) > 1:
                        done.append(row[0])
        except Exception:
            pass

    for filename in os.listdir(essays_dir):
        if filename.startswith('.'):
            continue
        
        filepath = os.path.join(essays_dir, filename)
        relative_path = os.path.relpath(filepath, start=current_dir)

        if relative_path in done:
            print(f"Skipping already processed file: {filename}")
            continue

        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                file_content = file.read()

            result_data = get_score(file_content)
            if result_data:
                save_score(output_csv_path, relative_path, filename, result_data)
                print(f"Successfully processed: {filename}")

            time.sleep(1)

        except Exception as e:
            print(f"Failed processing file: {filename}")
            print(f"Error details: {e}")

    print(f"Processing {essays_dir} completed.")

if __name__ == "__main__":
    main()