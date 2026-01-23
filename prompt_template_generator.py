import csv
import sys
import json
import os

def create_prompt_templates(graph_file_paths, questions_csv_path, output_json_path):
    """
    Creates a JSON file with prompt templates combining base prompt, multiple graphs, and questions.
    
    Args:
        graph_file_paths: List of paths to graph files (e.g., .ttl, .rdf, etc.)
        questions_csv_path: Path to CSV file containing questions
        output_json_path: Path for the output JSON file
    """
    
    # Base prompt template
    base_prompt = "You will be given customer data. You will be given operations to perform on the data and you should answer the questions only using information from the dataset."
    
    # Read all graph files
    graph_contents = []
    for graph_file_path in graph_file_paths:
        try:
            with open(graph_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Store with filename for reference
                graph_contents.append({
                    'filename': os.path.basename(graph_file_path),
                    'content': content
                })
        except FileNotFoundError:
            print(f"Error: Graph file '{graph_file_path}' not found.")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading graph file '{graph_file_path}': {e}")
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
    
    # Create output JSON with prompts
    try:
        prompts = []
        
        # Combine all graph contents
        combined_graphs = "Here is the data to operate on:\n\n"
        for i, graph_data in enumerate(graph_contents, 1):
            if len(graph_contents) > 1:
                combined_graphs += f"=== Data Source {i}: {graph_data['filename']} ===\n\n"
            combined_graphs += graph_data['content']
            if i < len(graph_contents):
                combined_graphs += "\n\n"
        
        # Create a prompt for each question
        for question in questions:
            # Combine all parts into a single prompt
            full_prompt = f"{base_prompt}\n\n{combined_graphs}\n\nOperation:\n{question}"
            
            # Create JSON object with "Question" key
            prompt_obj = {"Question": full_prompt}
            prompts.append(prompt_obj)
        
        # Write to JSON file
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(prompts, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully created {len(questions)} prompt templates in '{output_json_path}'")
        print(f"Using {len(graph_contents)} graph file(s): {', '.join([g['filename'] for g in graph_contents])}")
        
    except Exception as e:
        print(f"Error writing output JSON: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python prompt_template_generator.py <graph_file1> [graph_file2 ...] <questions_csv> <output_json>")
        print("\nExample with single graph file:")
        print("  python prompt_template_generator.py graph.ttl questions.csv output_prompts.json")
        print("\nExample with multiple graph files:")
        print("  python prompt_template_generator.py graph1.ttl graph2.rdf graph3.ttl questions.csv output_prompts.json")
        sys.exit(1)
    
    # All arguments except the last two are graph files
    graph_files = sys.argv[1:-2]
    questions_csv = sys.argv[-2]
    output_json = sys.argv[-1]
    
    create_prompt_templates(graph_files, questions_csv, output_json)
