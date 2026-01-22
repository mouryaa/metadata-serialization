import re

def clean_output(text):
    """
    Clean up the formatted output and extract just the question numbers and answers.
    """
    # Split by the separator lines
    sections = text.split('---')
    
    results = []
    
    for section in sections:
        section = section.strip()
        if not section:
            continue
            
        # Extract question number and description
        question_match = re.search(r'\*\*(\d+)\.\s+(.+?)\*\*', section)
        if not question_match:
            continue
            
        question_num = question_match.group(1)
        question_desc = question_match.group(2)
        
        # Extract answer
        answer_match = re.search(r'\*\*Answer:\*\*\s+(.+?)(?:\n|$)', section)
        if answer_match:
            answer = answer_match.group(1).strip()
        else:
            # For "shortest path" questions, extract the path description
            path_match = re.search(r'\*\*Shortest path:\*\*\s+(.+?)(?:\n|$)', section)
            if path_match:
                answer = path_match.group(1).strip()
            else:
                answer = "N/A"
        
        results.append({
            'number': question_num,
            'question': question_desc,
            'answer': answer
        })
    
    return results

def format_results(results, output_format='simple'):
    """
    Format the results in different styles.
    
    Args:
        results: List of dicts with 'number', 'question', 'answer'
        output_format: 'simple', 'table', or 'json'
    """
    if output_format == 'simple':
        output = []
        for r in results:
            output.append(f"{r['number']}. {r['answer']}")
        return '\n'.join(output)
    
    elif output_format == 'table':
        output = []
        output.append(f"{'#':<4} {'Question':<60} {'Answer':<40}")
        output.append('-' * 105)
        for r in results:
            question = r['question'][:57] + '...' if len(r['question']) > 60 else r['question']
            answer = r['answer'][:37] + '...' if len(r['answer']) > 40 else r['answer']
            output.append(f"{r['number']:<4} {question:<60} {answer:<40}")
        return '\n'.join(output)
    
    elif output_format == 'json':
        import json
        return json.dumps(results, indent=2)
    
    else:
        raise ValueError(f"Unknown format: {output_format}")

# Example usage
raw_output = '''Here are the answers to your operations, using only the provided data:

---

**1. For person_3_account_1_order_3, return the companyName** 
- `person_3_account_1_order_3` → `custom:orderCompany ex:org_1` 
- `ex:org_1` → `custom:companyName "Gonzalez Group"` 
**Answer:** Gonzalez Group

---

**2. For person_9_account_2_order_3, return the firstName** 
- `person_9_account_2_order_3` → `custom:orderCustomer ex:person_9` 
- `ex:person_9` → `custom:firstName "Sandra"` 
**Answer:** Sandra

---'''

if __name__ == "__main__":
    # Clean the output
    cleaned = clean_output(raw_output)
    
    # Display in different formats
    print("SIMPLE FORMAT:")
    print(format_results(cleaned, 'simple'))
    print("\n" + "="*80 + "\n")
    
    print("TABLE FORMAT:")
    print(format_results(cleaned, 'table'))
    print("\n" + "="*80 + "\n")
    
    print("JSON FORMAT:")
    print(format_results(cleaned, 'json'))
