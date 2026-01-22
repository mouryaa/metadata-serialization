import re

def clean_output(text):
    """
    Extract question number, question, and answer from the formatted text.
    Pattern: \n followed by number is the question, **Answer:** is the answer
    """
    results = []
    
    # Split by line breaks and process
    lines = text.split('\\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Look for pattern: number followed by **question**
        question_match = re.match(r'^\*\*(\d+)\.\s+(.+?)\*\*\s*$', line)
        
        if question_match:
            question_num = question_match.group(1)
            question_text = question_match.group(2)
            
            # Look ahead for the answer
            answer = "N/A"
            for j in range(i+1, min(i+10, len(lines))):  # Look in next few lines
                answer_match = re.search(r'\*\*Answer:\*\*\s+(.+)', lines[j])
                if answer_match:
                    answer = answer_match.group(1).strip()
                    break
                # Also check for "Shortest path:" pattern
                path_match = re.search(r'\*\*Shortest path:\*\*\s+(.+)', lines[j])
                if path_match:
                    answer = path_match.group(1).strip()
                    break
            
            results.append({
                'number': question_num,
                'question': question_text,
                'answer': answer
            })
        
        i += 1
    
    return results

def format_as_table(results):
    """
    Format results as a clean table.
    """
    if not results:
        return "No results found"
    
    # Calculate column widths
    num_width = max(len(r['number']) for r in results) + 2
    num_width = max(num_width, 4)
    
    question_width = max(len(r['question']) for r in results) + 2
    question_width = min(question_width, 10)
    question_width = max(question_width, 80)  # Max width
    
    answer_width = max(len(r['answer']) for r in results) + 2
    answer_width = min(answer_width, 10)
    answer_width = max(answer_width, 60)  # Max width
    
    # Create header
    output = []
    header = f"{'#':<{num_width}} {'Question':<{question_width}} {'Answer':<{answer_width}}"
    output.append(header)
    output.append('-' * len(header))
    
    # Add rows
    for r in results:
        num = r['number']
        question = r['question'][:question_width-2] + '..' if len(r['question']) > question_width else r['question']
        answer = r['answer'][:answer_width-2] + '..' if len(r['answer']) > answer_width else r['answer']
        
        output.append(f"{num:<{num_width}} {question:<{question_width}} {answer:<{answer_width}}")
    
    return '\n'.join(output)

# Your input text
raw_text = 'Here are the answers to your operations, using only the provided data:\\n\\n---\\n\\n**1. For person_3_account_1_order_3, return the companyName** \\n- `person_3_account_1_order_3` → `custom:orderCompany ex:org_1` \\n- `ex:org_1` → `custom:companyName "Gonzalez Group"` \\n**Answer:** Gonzalez Group\\n\\n---\\n\\n**2. For person_9_account_2_order_3, return the firstName** \\n- `person_9_account_2_order_3` → `custom:orderCustomer ex:person_9` \\n- `ex:person_9` → `custom:firstName "Sandra"` \\n**Answer:** Sandra\\n\\n---\\n\\n**3. For person_8_account_1_order_2, return the companyName** \\n- `person_8_account_1_order_2` → `custom:orderCompany ex:org_4` \\n- `ex:org_4` → `custom:companyName "Blair, Webster and Ferrell"` \\n**Answer:** Blair, Webster and Ferrell\\n\\n---\\n\\n**4. For person_1_account_1_order_2, return the lastName** \\n- `person_1_account_1_order_2` → `custom:orderCustomer ex:person_1` \\n- `ex:person_1` → `custom:lastName "Simpson"` \\n**Answer:** Simpson'

# Process and display
results = clean_output(raw_text)
print(format_as_table(results))
