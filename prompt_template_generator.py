import csv
import sys
import json

def create_prompt_templates(graph_file_path, questions_csv_path, output_csv_path):
    """
    Creates a CSV file with prompt templates combining base prompt, graph, and questions.
    Output format is designed for JSON payload injection.
    
    Args:
        graph_file_path: Path to the graph file (e.g., .ttl, .rdf, etc.)
        questions_csv_path: Path to CSV file containing questions
        output_csv_path: Path for the output CSV file
    """
    
    # Base prompt template
    base_prompt = "You will be given customer data. You will be given operations to perform on the data and you should answer the questions only using information from the dataset."
    
    # Read the graph file
    try:
        with open(graph_file_path, 'r', encoding='utf-8') as f:
            graph_content = f.read()
    except FileNotFoundError:
        print(f"Error: Graph file '{graph_file_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading graph file: {e}")
        sys.exit(1)
    
    # Read questions from CSV
    questions = []
    try:
        with open(questions_csv_path, 'r', encoding='utf-8') as f:
            csv_reader = csv.DictReader(f)
            
            # Try to find the question column (case-insensitive)
            if csv_reader.fieldnames:
                question_col = None
                for field in csv_reader.fieldnames:
                    if field.lower() in ['question', 'questions']:
                        question_col = field
                        break
                
                if question_col is None:
                    # If no matching column found, use the first column
                    question_col = csv_reader.fieldnames[0]
                    print(f"Warning: No 'question' column found. Using '{question_col}' instead.")
                
                for row in csv_reader:
                    if row[question_col].strip():  # Skip empty questions
                        questions.append(row[question_col].strip())
            
            if not questions:
                print("Error: No questions found in the CSV file.")
                sys.exit(1)
                
    except FileNotFoundError:
        print(f"Error: Questions CSV file '{questions_csv_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading questions CSV: {e}")
        sys.exit(1)
    
    # Create output CSV with prompts
    try:
        with open(output_csv_path, 'w', newline='', encoding='utf-8') as f:
            csv_writer = csv.writer(f)
            
            # Write header
            csv_writer.writerow(['prompt'])
            
            # Create a prompt for each question
            for question in questions:
                # Build the triple-quoted prompt string
                prompt_content = f"{base_prompt}\n\nHere is the data to operate on:\n\n{graph_content}\n\nOperation:\n{question}"
                
                # Create the JSON-ready string format
                json_string = f'"Question": """{prompt_content}"""'
                
                csv_writer.writerow([json_string])
        
        print(f"Successfully created {len(questions)} prompt templates in '{output_csv_path}'")
        
    except Exception as e:
        print(f"Error writing output CSV: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python prompt_template_generator.py <graph_file> <questions_csv> <output_csv>")
        print("\nExample:")
        print("  python prompt_template_generator.py graph.ttl questions.csv output_prompts.csv")
        sys.exit(1)
    
    graph_file = sys.argv[1]
    questions_csv = sys.argv[2]
    output_csv = sys.argv[3]
    
    create_prompt_templates(graph_file, questions_csv, output_csv)