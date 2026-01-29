"""
Simplified Abstract Question Generator - Guaranteed to work with schema.org data

This version focuses on reliability over complexity. It generates questions that
are guaranteed to work with any schema.org RDF data.
"""

import rdflib
from rdflib import Graph, Namespace, RDF, URIRef
from collections import defaultdict
import random
import csv
import sys
import json
import re


class SimpleQuestionGenerator:
    """Simplified question generator that works reliably with schema.org data."""
    
    def __init__(self, turtle_file, difficulty_distribution=None):
        """Initialize and discover schema."""
        print(f"Loading {turtle_file}...")
        self.graph = Graph()
        self.graph.parse(turtle_file, format='turtle')
        
        # Setup namespaces
        self.schema = Namespace("http://schema.org/")
        self.ex = Namespace("http://example.org/")
        
        # Difficulty distribution
        if difficulty_distribution is None:
            self.difficulty_distribution = {'easy': 33, 'medium': 34, 'hard': 33}
        else:
            self.difficulty_distribution = difficulty_distribution
        
        # Discover schema
        print("Discovering schema...")
        self.entities_by_type = defaultdict(list)
        self.properties_by_type = defaultdict(set)
        self.property_values = defaultdict(set)
        
        self._discover_schema()
        
        print(f"\nDiscovered:")
        for etype, entities in self.entities_by_type.items():
            props = len(self.properties_by_type[etype])
            print(f"  {etype}: {len(entities)} entities, {props} properties")
    
    def _discover_schema(self):
        """Discover all entities and properties."""
        # Find all typed entities
        for subj, _, obj in self.graph.triples((None, RDF.type, None)):
            etype = self._simplify(obj)
            self.entities_by_type[etype].append(subj)
        
        # Find properties for each type
        for etype, entities in self.entities_by_type.items():
            # Sample multiple entities to get full property list
            for entity in entities[:min(5, len(entities))]:
                for pred, obj in self.graph.predicate_objects(entity):
                    # Extract property name from predicate URI
                    prop = self._simplify(pred)
                    if prop and prop != 'type':
                        self.properties_by_type[etype].add(prop)
                        
                        # Collect sample values
                        val = str(obj)
                        if len(val) < 100:  # Only short values
                            self.property_values[f"{etype}.{prop}"].add(val)
    
    def _simplify(self, uri):
        """Extract the last part of a URI."""
        s = str(uri)
        if '/' in s:
            return s.split('/')[-1]
        if '#' in s:
            return s.split('#')[-1]
        return s
    
    def _get_value(self, entity, prop_name):
        """Get a property value from an entity."""
        # Try with schema namespace
        val = self.graph.value(entity, self.schema[prop_name])
        if val:
            return str(val)
        
        # Try as full URI
        val = self.graph.value(entity, URIRef(f"http://schema.org/{prop_name}"))
        if val:
            return str(val)
        
        return None
    
    def _get_related(self, entity, prop_name):
        """Get a related entity through a property."""
        val = self.graph.value(entity, self.schema[prop_name])
        if val and str(val).startswith('http://example.org/'):
            return val
        return None
    
    # === QUESTION GENERATORS ===
    
    def generate_simple_property_questions(self, count):
        """Generate simple property lookup questions."""
        questions = []
        attempts = 0
        max_attempts = count * 20
        
        while len(questions) < count and attempts < max_attempts:
            attempts += 1
            
            # Pick random entity type and entity
            etype = random.choice(list(self.entities_by_type.keys()))
            entities = self.entities_by_type[etype]
            entity = random.choice(entities)
            entity_id = self._simplify(entity)
            
            # Pick random property
            props = list(self.properties_by_type[etype])
            if not props:
                continue
            
            prop = random.choice(props)
            value = self._get_value(entity, prop)
            
            if value:
                # Handle numeric properties
                if prop in ['totalPrice', 'amount']:
                    try:
                        value = float(value)
                    except:
                        pass
                
                q = {
                    'category': 'Property Search',
                    'subcategory': 'Simple Property',
                    'difficulty': 'Easy',
                    'question': f'What is the {prop} of {entity_id}?',
                    'answer': value,
                    'query_type': 'single_property'
                }
                
                # Avoid duplicates
                if q not in questions:
                    questions.append(q)
        
        return questions
    
    def generate_multi_property_questions(self, count):
        """Generate multi-property lookup questions."""
        questions = []
        attempts = 0
        max_attempts = count * 20
        
        while len(questions) < count and attempts < max_attempts:
            attempts += 1
            
            etype = random.choice(list(self.entities_by_type.keys()))
            entities = self.entities_by_type[etype]
            entity = random.choice(entities)
            entity_id = self._simplify(entity)
            
            props = list(self.properties_by_type[etype])
            if len(props) < 2:
                continue
            
            selected_props = random.sample(props, 2)
            values = {}
            
            for prop in selected_props:
                val = self._get_value(entity, prop)
                if val:
                    if prop in ['totalPrice', 'amount']:
                        try:
                            values[prop] = float(val)
                        except:
                            values[prop] = val
                    else:
                        values[prop] = val
            
            if len(values) == 2:
                q = {
                    'category': 'Property Search',
                    'subcategory': 'Multi-Property',
                    'difficulty': 'Easy',
                    'question': f'What are the {" and ".join(selected_props)} of {entity_id}?',
                    'answer': values,
                    'query_type': 'multi_property'
                }
                
                if q not in questions:
                    questions.append(q)
        
        return questions
    
    def generate_nested_property_questions(self, count):
        """Generate nested property questions (following relationships)."""
        questions = []
        attempts = 0
        max_attempts = count * 20
        
        while len(questions) < count and attempts < max_attempts:
            attempts += 1
            
            etype = random.choice(list(self.entities_by_type.keys()))
            entities = self.entities_by_type[etype]
            entity = random.choice(entities)
            entity_id = self._simplify(entity)
            
            # Find relationship properties (those pointing to other entities)
            rel_props = []
            for prop in self.properties_by_type[etype]:
                related = self._get_related(entity, prop)
                if related:
                    rel_props.append((prop, related))
            
            if not rel_props:
                continue
            
            # Pick a relationship
            rel_prop, related_entity = random.choice(rel_props)
            
            # Find type of related entity
            related_type = None
            for obj in self.graph.objects(related_entity, RDF.type):
                related_type = self._simplify(obj)
                break
            
            if not related_type or related_type not in self.properties_by_type:
                continue
            
            # Get properties of related entity
            related_props = list(self.properties_by_type[related_type])
            if not related_props:
                continue
            
            target_prop = random.choice(related_props)
            value = self._get_value(related_entity, target_prop)
            
            if value:
                if target_prop in ['totalPrice', 'amount']:
                    try:
                        value = float(value)
                    except:
                        pass
                
                q = {
                    'category': 'Property Search',
                    'subcategory': 'Nested Property',
                    'difficulty': 'Medium',
                    'question': f"What is the {rel_prop}'s {target_prop} for {etype} {entity_id}?",
                    'answer': value,
                    'query_type': 'nested_property'
                }
                
                if q not in questions:
                    questions.append(q)
        
        return questions
    
    def generate_collection_questions(self, count):
        """Generate collection questions."""
        questions = []
        
        for etype in list(self.entities_by_type.keys())[:count]:
            props = list(self.properties_by_type[etype])
            if not props:
                continue
            
            prop = random.choice(props)
            values = []
            
            for entity in self.entities_by_type[etype]:
                val = self._get_value(entity, prop)
                if val:
                    values.append(val)
            
            if values:
                q = {
                    'category': 'Breadth-First Search',
                    'subcategory': 'Collection',
                    'difficulty': 'Easy',
                    'question': f'List all unique {prop} values for {etype} entities.',
                    'answer': sorted(set(values)),
                    'query_type': 'collection'
                }
                questions.append(q)
        
        return questions[:count]
    
    def generate_count_questions(self, count):
        """Generate counting questions."""
        questions = []
        
        for etype in list(self.entities_by_type.keys())[:count]:
            q = {
                'category': 'Aggregation',
                'subcategory': 'Count',
                'difficulty': 'Easy',
                'question': f'How many {etype} entities are in the dataset?',
                'answer': len(self.entities_by_type[etype]),
                'query_type': 'count'
            }
            questions.append(q)
        
        return questions[:count]
    
    def generate_filter_questions(self, count):
        """Generate filter questions."""
        questions = []
        attempts = 0
        max_attempts = count * 20
        
        while len(questions) < count and attempts < max_attempts:
            attempts += 1
            
            etype = random.choice(list(self.entities_by_type.keys()))
            props = list(self.properties_by_type[etype])
            if not props:
                continue
            
            prop = random.choice(props)
            
            # Get possible values for this property
            values = self.property_values.get(f"{etype}.{prop}", set())
            if not values or len(values) < 2:
                continue
            
            filter_val = random.choice(list(values))
            
            # Find matching entities
            matches = []
            for entity in self.entities_by_type[etype]:
                val = self._get_value(entity, prop)
                if val == filter_val:
                    matches.append(self._simplify(entity))
            
            if matches:
                q = {
                    'category': 'Filtering',
                    'subcategory': 'Simple Filter',
                    'difficulty': 'Easy',
                    'question': f'Find all {etype} entities with {prop} equal to "{filter_val}".',
                    'answer': sorted(matches),
                    'query_type': 'filter'
                }
                
                if q not in questions:
                    questions.append(q)
        
        return questions
    
    def generate_aggregation_questions(self, count):
        """Generate aggregation questions."""
        questions = []
        attempts = 0
        max_attempts = count * 20
        
        while len(questions) < count and attempts < max_attempts:
            attempts += 1
            
            etype = random.choice(list(self.entities_by_type.keys()))
            props = list(self.properties_by_type[etype])
            
            # Find numeric properties
            numeric_props = []
            for prop in props:
                sample_val = None
                for entity in self.entities_by_type[etype][:1]:
                    sample_val = self._get_value(entity, prop)
                    break
                
                if sample_val:
                    try:
                        float(sample_val)
                        numeric_props.append(prop)
                    except:
                        pass
            
            if not numeric_props:
                continue
            
            prop = random.choice(numeric_props)
            
            # Calculate sum
            total = 0
            count_vals = 0
            for entity in self.entities_by_type[etype]:
                val = self._get_value(entity, prop)
                if val:
                    try:
                        total += float(val)
                        count_vals += 1
                    except:
                        pass
            
            if count_vals > 0:
                q = {
                    'category': 'Mathematical',
                    'subcategory': 'Aggregation',
                    'difficulty': 'Easy',
                    'question': f'What is the total {prop} of all {etype} entities?',
                    'answer': round(total, 2),
                    'query_type': 'sum'
                }
                
                if q not in questions:
                    questions.append(q)
        
        return questions
    
    # === MAIN GENERATION ===
    
    def generate_questions(self, target_count=100):
        """Generate all questions."""
        print(f"\nGenerating {target_count} questions...")
        
        # Calculate distribution
        per_type = target_count // 7
        
        all_questions = []
        
        print("  Generating simple property questions...")
        all_questions.extend(self.generate_simple_property_questions(per_type))
        
        print("  Generating multi-property questions...")
        all_questions.extend(self.generate_multi_property_questions(per_type))
        
        print("  Generating nested property questions...")
        all_questions.extend(self.generate_nested_property_questions(per_type))
        
        print("  Generating collection questions...")
        all_questions.extend(self.generate_collection_questions(per_type))
        
        print("  Generating count questions...")
        all_questions.extend(self.generate_count_questions(per_type))
        
        print("  Generating filter questions...")
        all_questions.extend(self.generate_filter_questions(per_type))
        
        print("  Generating aggregation questions...")
        all_questions.extend(self.generate_aggregation_questions(per_type))
        
        print(f"\nGenerated {len(all_questions)} questions total")
        
        # Apply difficulty filter
        filtered = self._filter_by_difficulty(all_questions, target_count)
        
        # Shuffle
        random.shuffle(filtered)
        
        print(f"Final count: {len(filtered)} questions")
        return filtered
    
    def _filter_by_difficulty(self, questions, target):
        """Filter to match difficulty distribution."""
        by_diff = {'Easy': [], 'Medium': [], 'Hard': []}
        for q in questions:
            diff = q.get('difficulty', 'Medium')
            if diff in by_diff:
                by_diff[diff].append(q)
        
        easy_target = int(target * self.difficulty_distribution['easy'] / 100)
        medium_target = int(target * self.difficulty_distribution['medium'] / 100)
        hard_target = target - easy_target - medium_target
        
        selected = []
        random.shuffle(by_diff['Easy'])
        random.shuffle(by_diff['Medium'])
        random.shuffle(by_diff['Hard'])
        
        selected.extend(by_diff['Easy'][:easy_target])
        selected.extend(by_diff['Medium'][:medium_target])
        selected.extend(by_diff['Hard'][:hard_target])
        
        # Fill gaps
        if len(selected) < target:
            remaining = [q for q in questions if q not in selected]
            random.shuffle(remaining)
            selected.extend(remaining[:target - len(selected)])
        
        return selected[:target]


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Simple question generator for RDF data')
    parser.add_argument('turtle_file', help='Path to turtle file')
    parser.add_argument('output_csv', nargs='?', default='questions.csv',
                       help='Output CSV (default: questions.csv)')
    parser.add_argument('num_questions', nargs='?', type=int, default=100,
                       help='Number of questions (default: 100)')
    parser.add_argument('--difficulty', type=str, default='33,34,33',
                       help='Difficulty distribution (default: 33,34,33)')
    
    args = parser.parse_args()
    
    # Parse difficulty
    try:
        easy, medium, hard = map(float, args.difficulty.split(','))
        diff_dist = {'easy': easy, 'medium': medium, 'hard': hard}
    except:
        print("Error parsing difficulty distribution")
        sys.exit(1)
    
    try:
        # Generate
        generator = SimpleQuestionGenerator(args.turtle_file, diff_dist)
        questions = generator.generate_questions(args.num_questions)
        
        # Write CSV
        with open(args.output_csv, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['category', 'subcategory', 'difficulty', 'question', 'answer', 'query_type']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for q in questions:
                writer.writerow({
                    'category': q['category'],
                    'subcategory': q['subcategory'],
                    'difficulty': q['difficulty'],
                    'question': q['question'],
                    'answer': json.dumps(q['answer']),
                    'query_type': q['query_type']
                })
        
        print(f"\n{'=' * 80}")
        print(f"Success! Generated {len(questions)} questions")
        print(f"Output: {args.output_csv}")
        print('=' * 80)
        
        # Summary
        print("\nBy Category:")
        cats = defaultdict(int)
        for q in questions:
            cats[q['category']] += 1
        for cat, count in sorted(cats.items()):
            print(f"  {cat}: {count}")
        
        print("\nBy Difficulty:")
        diffs = defaultdict(int)
        for q in questions:
            diffs[q['difficulty']] += 1
        for diff, count in sorted(diffs.items()):
            print(f"  {diff}: {count}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()