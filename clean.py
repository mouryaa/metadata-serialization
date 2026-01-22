import re

def clean_output(text):
    """
    Extract questions and answers based on pattern:
    - Question starts after \n followed by a number
    - Answer is the text after **Answer:**
    """
    results = []
    
    # Split by \n followed by number pattern to get each question block
    # Pattern: \n\d+ or start of string followed by number
    blocks = re.split(r'\\n(?=\d+\.)', text)
    
    for block in blocks:
        if not block.strip():
            continue
        
        # Extract question number (first number followed by period)
        num_match = re.match(r'^(\d+)\.', block)
        if not num_match:
            continue
        
        question_num = num_match.group(1)
        
        # Extract question text (everything from number until **Answer:**)
        question_match = re.search(r'^\d+\.\s+\*\*(.+?)\*\*', block)
        if question_match:
            question_text = question_match.group(1).strip()
        else:
            # Fallback: get text between number and **Answer:**
            question_parts = re.split(r'\*\*Answer:\*\*', block)
            if len(question_parts) > 0:
                question_text = re.sub(r'^\d+\.\s*\*\*', '', question_parts[0])
                question_text = re.sub(r'\*\*', '', question_text)
                question_text = re.sub(r'\\n.*', '', question_text).strip()
            else:
                question_text = "N/A"
        
        # Extract answer (text after **Answer:**)
        answer_match = re.search(r'\*\*Answer:\*\*\s*(.+?)(?:\\n\\n|$)', block, re.DOTALL)
        if answer_match:
            answer = answer_match.group(1).strip()
            # Clean up any trailing \\n--- or similar
            answer = re.sub(r'\\n---.*$', '', answer).strip()
        else:
            # Check for **Shortest path:** pattern
            path_match = re.search(r'\*\*Shortest path:\*\*\s*(.+?)(?:\\n\\n|$)', block, re.DOTALL)
            if path_match:
                answer = path_match.group(1).strip()
                answer = re.sub(r'\\n---.*$', '', answer).strip()
            else:
                answer = "N/A"
        
        results.append({
            'number': question_num,
            'question': question_text,
            'answer': answer
        })
    
    return results

def format_as_table(results):
    """
    Format results as a clean table.
    """
    if not results:
        return "No results found"
    
    # Print header
    print(f"{'#':<5} {'Question':<70} {'Answer':<50}")
    print('-' * 125)
    
    # Print rows
    for r in results:
        num = r['number']
        question = r['question'][:67] + '...' if len(r['question']) > 70 else r['question']
        answer = r['answer'][:47] + '...' if len(r['answer']) > 50 else r['answer']
        print(f"{num:<5} {question:<70} {answer:<50}")

# Your input text
raw_text = 'Here are the answers to your operations, using only the provided data:\\n\\n---\\n\\n**1. For person_3_account_1_order_3, return the companyName** \\n- `person_3_account_1_order_3` → `custom:orderCompany ex:org_1` \\n- `ex:org_1` → `custom:companyName "Gonzalez Group"` \\n**Answer:** Gonzalez Group\\n\\n---\\n\\n**2. For person_9_account_2_order_3, return the firstName** \\n- `person_9_account_2_order_3` → `custom:orderCustomer ex:person_9` \\n- `ex:person_9` → `custom:firstName "Sandra"` \\n**Answer:** Sandra\\n\\n---\\n\\n**3. For person_8_account_1_order_2, return the companyName** \\n- `person_8_account_1_order_2` → `custom:orderCompany ex:org_4` \\n- `ex:org_4` → `custom:companyName "Blair, Webster and Ferrell"` \\n**Answer:** Blair, Webster and Ferrell\\n\\n---\\n\\n**4. For person_1_account_1_order_2, return the lastName** \\n- `person_1_account_1_order_2` → `custom:orderCustomer ex:person_1` \\n- `ex:person_1` → `custom:lastName "Simpson"` \\n**Answer:** Simpson'

# Process and display
results = clean_output(raw_text)
format_as_table(results)
