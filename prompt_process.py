import csv
import json
import requests
from datetime import datetime
import time

# Configuration
CSV_INPUT_FILE = '/mnt/user-data/uploads/output_prompts.csv'
RESULTS_OUTPUT_FILE = f'/mnt/user-data/outputs/api_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
LOG_FILE = f'/mnt/user-data/outputs/processing_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'

# API Configuration - UPDATE THESE VALUES
invoke_chat_url = "YOUR_API_ENDPOINT_HERE"  # Replace with your actual API endpoint
headers = {
    "Content-Type": "application/json",
    # Add any additional headers like API keys here
    # "Authorization": "Bearer YOUR_API_KEY"
}

def log_message(message, print_to_console=True):
    """Log messages to both file and console"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    
    if print_to_console:
        print(log_entry)
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_entry + '\n')

def process_prompt(prompt, index):
    """Process a single prompt through the API"""
    try:
        # Create the payload with the prompt
        payload = {
            "prompt": prompt
            # Add any other required fields for your API here
        }
        
        # Make the API request
        res = requests.post(invoke_chat_url, json=payload, headers=headers)
        
        # Check if request was successful
        res.raise_for_status()
        
        # Get the JSON response
        result = res.json()
        
        return {
            "index": index,
            "prompt": prompt,
            "status": "success",
            "response": result,
            "timestamp": datetime.now().isoformat()
        }
    
    except requests.exceptions.RequestException as e:
        log_message(f"Error processing prompt {index}: {str(e)}")
        return {
            "index": index,
            "prompt": prompt,
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def main():
    """Main function to process all prompts"""
    log_message("Starting prompt processing...")
    
    results = []
    
    try:
        # Read prompts from CSV
        with open(CSV_INPUT_FILE, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            prompts = list(reader)
            
        total_prompts = len(prompts)
        log_message(f"Found {total_prompts} prompts to process")
        
        # Process each prompt
        for index, row in enumerate(prompts, start=1):
            prompt = row['prompt']
            
            log_message(f"Processing prompt {index}/{total_prompts}...")
            
            # Process the prompt
            result = process_prompt(prompt, index)
            results.append(result)
            
            # Optional: Add a small delay between requests to avoid rate limiting
            # time.sleep(0.5)
            
            # Save intermediate results every 100 prompts
            if index % 100 == 0:
                with open(RESULTS_OUTPUT_FILE, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                log_message(f"Saved intermediate results ({index} prompts processed)")
        
        # Save final results
        with open(RESULTS_OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Calculate statistics
        successful = sum(1 for r in results if r['status'] == 'success')
        failed = sum(1 for r in results if r['status'] == 'error')
        
        log_message(f"\n{'='*50}")
        log_message(f"Processing complete!")
        log_message(f"Total prompts: {total_prompts}")
        log_message(f"Successful: {successful}")
        log_message(f"Failed: {failed}")
        log_message(f"Results saved to: {RESULTS_OUTPUT_FILE}")
        log_message(f"Log saved to: {LOG_FILE}")
        log_message(f"{'='*50}")
        
    except FileNotFoundError:
        log_message(f"Error: Could not find CSV file at {CSV_INPUT_FILE}")
    except Exception as e:
        log_message(f"Unexpected error: {str(e)}")
        # Save whatever results we have so far
        if results:
            with open(RESULTS_OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            log_message(f"Partial results saved to: {RESULTS_OUTPUT_FILE}")

if __name__ == "__main__":
    main()
