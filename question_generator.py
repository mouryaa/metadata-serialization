import rdflib
from rdflib import Graph, URIRef
from collections import deque
import random
import csv
import sys
import json

class GraphTraversalQA:
    def __init__(self, turtle_file):
        """Initialize with a Turtle format RDF file."""
        self.graph = Graph()
        self.graph.parse(turtle_file, format='turtle')
        self.nodes = set()
        self.edges = {}
        self._build_graph_structure()
    
    def _build_graph_structure(self):
        """Build an adjacency list from the RDF graph."""
        for s, p, o in self.graph:
            self.nodes.add(str(s))
            self.nodes.add(str(o))
            
            if str(s) not in self.edges:
                self.edges[str(s)] = []
            self.edges[str(s)].append((str(p), str(o)))
    
    def _simplify_uri(self, uri):
        """Simplify URIs for readable output."""
        if '#' in uri:
            return uri.split('#')[-1]
        elif '/' in uri:
            return uri.split('/')[-1]
        return uri
    
    def _get_subjects(self):
        """Get all subjects (nodes that have outgoing edges)."""
        return list(self.edges.keys())
    
    def _get_predicates(self):
        """Get all unique predicates in the graph."""
        predicates = set()
        for edges_list in self.edges.values():
            for pred, _ in edges_list:
                predicates.add(pred)
        return list(predicates)
    
    def find_objects_by_predicate(self, subject, predicate, max_depth=1):
        """
        Find all objects reachable from subject via predicate within max_depth hops.
        Returns list of objects found.
        """
        results = []
        visited = set()
        
        def dfs(node, depth):
            if depth > max_depth:
                return
            
            visited.add(node)
            
            if node in self.edges:
                for prop, neighbor in self.edges[node]:
                    if prop == predicate and neighbor not in visited:
                        results.append(neighbor)
                    
                    # Continue traversal for multi-hop
                    if depth < max_depth and neighbor not in visited:
                        dfs(neighbor, depth + 1)
        
        dfs(subject, 0)
        return results
    
    def find_path_to_predicate(self, subject, target_predicate, max_depth=2, use_bfs=False):
        """
        Find a path from subject that eventually uses target_predicate.
        Returns the path and the final object(s) connected by target_predicate.
        """
        if use_bfs:
            return self._bfs_path_to_predicate(subject, target_predicate, max_depth)
        else:
            return self._dfs_path_to_predicate(subject, target_predicate, max_depth)
    
    def _dfs_path_to_predicate(self, subject, target_predicate, max_depth):
        """DFS to find path ending with target_predicate."""
        visited = set()
        result = {'path': [], 'objects': []}
        
        def dfs(node, path, depth):
            if depth > max_depth:
                return False
            
            visited.add(node)
            
            if node in self.edges:
                for prop, neighbor in self.edges[node]:
                    if prop == target_predicate and neighbor not in visited:
                        result['path'] = path + [(node, prop, neighbor)]
                        result['objects'].append(neighbor)
                        return True
                    
                    if neighbor not in visited and depth < max_depth:
                        if dfs(neighbor, path + [(node, prop, neighbor)], depth + 1):
                            return True
            
            visited.discard(node)
            return False
        
        dfs(subject, [], 0)
        return result if result['objects'] else None
    
    def _bfs_path_to_predicate(self, subject, target_predicate, max_depth):
        """BFS to find shortest path ending with target_predicate."""
        queue = deque([(subject, [], 0)])
        visited = {subject}
        
        while queue:
            node, path, depth = queue.popleft()
            
            if depth > max_depth:
                continue
            
            if node in self.edges:
                for prop, neighbor in self.edges[node]:
                    if prop == target_predicate:
                        return {
                            'path': path + [(node, prop, neighbor)],
                            'objects': [neighbor]
                        }
                    
                    if neighbor not in visited and depth < max_depth:
                        visited.add(neighbor)
                        queue.append((neighbor, path + [(node, prop, neighbor)], depth + 1))
        
        return None
    
    def generate_questions(self):
        """Generate traversal questions asking for predicates from subjects."""
        questions = {
            '1-node Property Search': [],
            '2-node Property Search': [],
            '1-node Depth-First Search': [],
            '2-node Depth-First Search': [],
            'Breadth-First Search': []
        }
        
        subjects = self._get_subjects()
        predicates = self._get_predicates()
        
        if not subjects or not predicates:
            return []
        
        # Generate 5 1-node property search questions
        attempts = 0
        while len(questions['1-node Property Search']) < 5 and attempts < 100:
            attempts += 1
            subject = random.choice(subjects)
            predicate = random.choice(predicates)
            
            objects = self.find_objects_by_predicate(subject, predicate, max_depth=1)
            
            if objects:
                questions['1-node Property Search'].append({
                    'type': '1-node Property Search',
                    'question': f'For {self._simplify_uri(subject)}, return the {self._simplify_uri(predicate)}',
                    'answer': [self._simplify_uri(obj) for obj in objects],
                    'subject': self._simplify_uri(subject),
                    'predicate': self._simplify_uri(predicate)
                })
        
        # Generate 5 2-node property search questions
        attempts = 0
        while len(questions['2-node Property Search']) < 5 and attempts < 100:
            attempts += 1
            subject = random.choice(subjects)
            predicate = random.choice(predicates)
            
            objects = self.find_objects_by_predicate(subject, predicate, max_depth=2)
            
            if objects:
                questions['2-node Property Search'].append({
                    'type': '2-node Property Search',
                    'question': f'For {self._simplify_uri(subject)}, return the {self._simplify_uri(predicate)}',
                    'answer': [self._simplify_uri(obj) for obj in objects],
                    'subject': self._simplify_uri(subject),
                    'predicate': self._simplify_uri(predicate)
                })
        
        # Generate 5 1-node DFS questions
        attempts = 0
        while len(questions['1-node Depth-First Search']) < 5 and attempts < 100:
            attempts += 1
            subject = random.choice(subjects)
            predicate = random.choice(predicates)
            
            result = self.find_path_to_predicate(subject, predicate, max_depth=1, use_bfs=False)
            
            if result:
                questions['1-node Depth-First Search'].append({
                    'type': '1-node Depth-First Search',
                    'question': f'For {self._simplify_uri(subject)}, find the {self._simplify_uri(predicate)}',
                    'answer': {
                        'path': [(self._simplify_uri(s), self._simplify_uri(p), self._simplify_uri(o)) 
                                for s, p, o in result['path']],
                        'values': [self._simplify_uri(obj) for obj in result['objects']]
                    },
                    'subject': self._simplify_uri(subject),
                    'predicate': self._simplify_uri(predicate)
                })
        
        # Generate 5 2-node DFS questions
        attempts = 0
        while len(questions['2-node Depth-First Search']) < 5 and attempts < 100:
            attempts += 1
            subject = random.choice(subjects)
            predicate = random.choice(predicates)
            
            result = self.find_path_to_predicate(subject, predicate, max_depth=2, use_bfs=False)
            
            if result:
                questions['2-node Depth-First Search'].append({
                    'type': '2-node Depth-First Search',
                    'question': f'For {self._simplify_uri(subject)}, find the {self._simplify_uri(predicate)}',
                    'answer': {
                        'path': [(self._simplify_uri(s), self._simplify_uri(p), self._simplify_uri(o)) 
                                for s, p, o in result['path']],
                        'values': [self._simplify_uri(obj) for obj in result['objects']]
                    },
                    'subject': self._simplify_uri(subject),
                    'predicate': self._simplify_uri(predicate)
                })
        
        # Generate 5 BFS questions
        attempts = 0
        while len(questions['Breadth-First Search']) < 5 and attempts < 100:
            attempts += 1
            subject = random.choice(subjects)
            predicate = random.choice(predicates)
            
            result = self.find_path_to_predicate(subject, predicate, max_depth=2, use_bfs=True)
            
            if result:
                questions['Breadth-First Search'].append({
                    'type': 'Breadth-First Search',
                    'question': f'For {self._simplify_uri(subject)}, find the shortest path to {self._simplify_uri(predicate)}',
                    'answer': {
                        'path': [(self._simplify_uri(s), self._simplify_uri(p), self._simplify_uri(o)) 
                                for s, p, o in result['path']],
                        'values': [self._simplify_uri(obj) for obj in result['objects']]
                    },
                    'subject': self._simplify_uri(subject),
                    'predicate': self._simplify_uri(predicate)
                })
        
        # Flatten questions into a single list
        all_questions = []
        for category in questions.values():
            all_questions.extend(category)
        
        return all_questions

def main():
    # Check for command line argument
    if len(sys.argv) < 2:
        print("Usage: python script.py <turtle_file> [output_csv]")
        print("Example: python script.py graph.ttl questions.csv")
        sys.exit(1)
    
    turtle_file = sys.argv[1]
    output_csv = sys.argv[2] if len(sys.argv) > 2 else 'questions.csv'
    
    # Check if turtle file exists
    try:
        with open(turtle_file, 'r') as f:
            pass
    except FileNotFoundError:
        print(f"Error: File '{turtle_file}' not found.")
        sys.exit(1)
    
    print(f"Reading graph from: {turtle_file}")
    
    try:
        # Initialize and generate questions
        qa_gen = GraphTraversalQA(turtle_file)
        questions = qa_gen.generate_questions()
        
        # Write questions to CSV
        with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['type', 'question', 'subject', 'predicate', 'answer']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for q in questions:
                # Convert answer to JSON string for complex structures
                answer_str = json.dumps(q['answer']) if isinstance(q['answer'], dict) else json.dumps(q['answer'])
                
                writer.writerow({
                    'type': q['type'],
                    'question': q['question'],
                    'subject': q['subject'],
                    'predicate': q['predicate'],
                    'answer': answer_str
                })
        
        print(f"\n{'=' * 80}")
        print(f"Successfully generated {len(questions)} questions")
        print(f"Output saved to: {output_csv}")
        print('=' * 80)
        
        # Display summary
        question_types = [
            '1-node Property Search',
            '2-node Property Search',
            '1-node Depth-First Search',
            '2-node Depth-First Search',
            'Breadth-First Search'
        ]
        
        print("\nQuestion Summary:")
        for qtype in question_types:
            count = len([q for q in questions if q['type'] == qtype])
            print(f"  {qtype}: {count} questions")
        
    except Exception as e:
        print(f"Error processing file: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()