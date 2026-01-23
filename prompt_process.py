import json
import requests
from datetime import datetime
import time

# Configuration
invoke_chat_url = "YOUR_API_ENDPOINT_HERE"  # Replace with your actual API endpoint
headers = {
    "Content-Type": "application/json",
    # Add any other headers you need (e.g., authentication tokens)
    # "Authorization": "Bearer YOUR_TOKEN_HERE"
}

# Load prompts from JSON file
with open('output_prompts.json', 'r') as f:
    prompts = json.load(f)

# Store results
results = []

# Process each prompt
print(f"Processing {len(prompts)} prompts...")
for idx, prompt_item in enumerate(prompts, 1):
    print(f"\nProcessing prompt {idx}/{len(prompts)}")
    print(f"Prompt: {prompt_item['prompt'][:50]}...")  # Show first 50 chars
    
    try:
        # Inject the prompt into the payload
        payload = {
            "prompt": prompt_item['prompt'],
            # Add any other fields your API expects
            # "model": "your-model-name",
            # "temperature": 0.7,
            # etc.
        }
        
        # Make the API request
        res = requests.post(invoke_chat_url, json=payload, headers=headers)
        
        # Check if request was successful
        res.raise_for_status()
        
        # Get the response JSON
        response_data = res.json()
        
        # Store the result with original prompt info
        result = {
            "prompt_id": idx,
            "prompt": prompt_item['prompt'],
            "response": response_data,
            "status": "success",
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"✓ Success")
        
    except requests.exceptions.RequestException as e:
        # Handle request errors
        result = {
            "prompt_id": idx,
            "prompt": prompt_item['prompt'],
            "error": str(e),
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }
        print(f"✗ Error: {e}")
    
    results.append(result)
    
    # Optional: Add a small delay to avoid rate limiting
    # time.sleep(1)

# Save results to a JSON file
output_filename = f"api_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(output_filename, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n{'='*50}")
print(f"Processing complete!")
print(f"Total prompts: {len(prompts)}")
print(f"Successful: {sum(1 for r in results if r['status'] == 'success')}")
print(f"Failed: {sum(1 for r in results if r['status'] == 'error')}")
print(f"Results saved to: {output_filename}")
