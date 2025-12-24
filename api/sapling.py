import requests
import os
import csv
import json
from dotenv import load_dotenv
load_dotenv()

SAPLING_API_KEY = os.getenv('SAPLING_API_KEY1')
# Define directories
current_dir = os.path.dirname(__file__)
essays_dir = os.path.join(current_dir, '..', 'datasets', 'essays')
output_csv_path = os.path.join(current_dir, 'sapling_results.csv')

print(f"Reading files from: {essays_dir}")

done =[
"TOPIC3_2_GPT4.0.txt",
"TOPIC4_2_GPT4.0.txt",
"TOPIC1_1_GPT4.0.txt",
"TOPIC5_3_GEMINI2.5PRO.txt",
"TOPIC2_1_GEMINI2.5PRO.txt",
"TOPIC3_2_GEMINI2.5PRO.txt",
"TOPIC1_1_GEMINI2.5PRO.txt",
"TOPIC5_2_GPT4.0.txt",
"TOPIC2_2_GPT4.0.txt",
"TOPIC1_3_GPT4.0.txt",
"TOPIC5_2_GEMINI2.5PRO.txt",
"TOPIC4_1_GEMINI2.5PRO.txt",
"TOPIC3_3_GEMINI2.5PRO.txt",
"TOPIC5_3_GPT4.0.txt",
"TOPIC2_3_GPT4.0.txt",
"TOPIC2_3_GEMINI2.5PRO.txt",
"TOPIC5_1_GEMINI2.5PRO.txt",
"TOPIC3_3_GPT4.0.txt",
"TOPIC4_3_GPT4.0.txt",
"TOPIC1_3_GEMINI2.5PRO.txt",
"TOPIC4_2_GEMINI2.5PRO.txt",
"TOPIC5_1_GPT4.0.txt",
"TOPIC2_2_GEMINI2.5PRO.txt",
"TOPIC2_1_GPT4.0.txt"
]

# Check if file exists
file_exists = os.path.isfile(output_csv_path)

# Open CSV file for appending
with open(output_csv_path, mode='a', newline='', encoding='utf-8') as csv_file:
    writer = csv.writer(csv_file)
    # Write the header row if file is new
    if not file_exists:
        writer.writerow(['filepath', 'filename', 'score', 'sentence_score', 'token_probs', 'token'])

    # Iterate over all files in the directory
    for filename in os.listdir(essays_dir):
        # Skip hidden files (like .DS_Store on Mac)
        if filename.startswith('.'):
            continue

        if filename in done:
            print(f"Skipping already processed file: {filename}")
            continue

        file_path = os.path.join(essays_dir, filename)

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                file_content = file.read()

            response = requests.post(
                "https://api.sapling.ai/api/v1/aidetect",
                json={
                    "key": SAPLING_API_KEY,
                    "text": file_content
                }
            )

            if 200 <= response.status_code < 300:
                data = response.json()
                
                # Extract fields. We use json.dumps for lists to store them in a single CSV cell
                # Note: API usually returns 'sentence_scores' (plural) and 'tokens' (plural)
                row = [
                    file_path,
                    filename,
                    data.get('score'),
                    json.dumps(data.get('sentence_scores')), 
                    json.dumps(data.get('token_probs')),
                    json.dumps(data.get('tokens'))
                ]
                writer.writerow(row)
                print(f"Successfully processed: {filename}")
            else:
                print(f"Failed API request for: {filename}")
                print('Error: ', response.status_code, response.text)

        except Exception as e:
            print(f"Failed processing file: {filename}")
            print(f"Error details: {e}")

print(f"Processing complete. Results saved to {output_csv_path}")