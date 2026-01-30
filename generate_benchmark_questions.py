#!/usr/bin/env python3
"""
Benchmark Question Generator for Serialization Format Testing

This script parses a Turtle/RDF file and automatically generates benchmark questions
across different categories to test the performance of various serialization formats.

The script is fully abstract and adapts to any RDF schema by dynamically discovering
entity types, properties, and relationships.
"""

import argparse
import random
import re
from datetime import datetime, timedelta
from typing import Dict, List, Set, Tuple, Any, Optional
from collections import defaultdict
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, XSD
import json


class BenchmarkQuestionGenerator:
    """Generates benchmark questions from RDF/Turtle data"""
    
    def __init__(self, turtle_file: str):
        """Initialize with a turtle file"""
        self.graph = Graph()
        self.graph.parse(turtle_file, format='turtle')
        
        # Dynamic data structures
        self.entities_by_type = defaultdict(list)  # type -> [entities]
        self.properties_by_type = defaultdict(set)  # type -> {properties}
        self.property_values = defaultdict(lambda: defaultdict(set))  # type -> property -> {values}
        self.relationships = defaultdict(set)  # type -> {(property, target_type)}
        self.numeric_properties = defaultdict(set)  # type -> {numeric properties}
        self.date_properties = defaultdict(set)  # type -> {date properties}
        self.string_properties = defaultdict(set)  # type -> {string properties}
        
        # Entity type metadata
        self.entity_types = []
        self.primary_entity_type = None  # Most common entity type
        
        # Parse the graph
        self._parse_graph()
        self._analyze_properties()
        self._detect_relationships()
        
    def _parse_graph(self):
        """Parse the RDF graph and extract all entities dynamically"""
        # Get all types
        for subj, pred, obj in self.graph.triples((None, RDF.type, None)):
            entity_type = str(obj).split('/')[-1]
            entity_uri = str(subj)
            
            # Collect properties for this entity
            properties = {}
            for s, p, o in self.graph.triples((subj, None, None)):
                if p != RDF.type:
                    prop_name = str(p).split('/')[-1]
                    prop_value = str(o)
                    properties[prop_name] = prop_value
                    self.properties_by_type[entity_type].add(prop_name)
                    
                    # Collect unique values for this property
                    self.property_values[entity_type][prop_name].add(prop_value)
            
            # Store entity
            entity_data = {
                'uri': entity_uri,
                'type': entity_type,
                'properties': properties
            }
            self.entities_by_type[entity_type].append(entity_data)
        
        # Determine entity types and primary type
        self.entity_types = sorted(self.entities_by_type.keys())
        if self.entity_types:
            # Primary type is the one with most instances
            self.primary_entity_type = max(
                self.entity_types,
                key=lambda t: len(self.entities_by_type[t])
            )
    
    def _analyze_properties(self):
        """Analyze properties to determine their types (numeric, date, string, etc.)"""
        for entity_type, entities in self.entities_by_type.items():
            for entity in entities:
                for prop_name, prop_value in entity['properties'].items():
                    # Check if numeric
                    try:
                        float(prop_value)
                        self.numeric_properties[entity_type].add(prop_name)
                    except (ValueError, TypeError):
                        pass
                    
                    # Check if date
                    if self._is_date(prop_value):
                        self.date_properties[entity_type].add(prop_name)
                    
                    # Check if reference to another entity (URI)
                    if prop_value.startswith('http://') or prop_value.startswith('https://'):
                        # Could be a relationship - we'll analyze this separately
                        pass
                    else:
                        # String property
                        self.string_properties[entity_type].add(prop_name)
    
    def _is_date(self, value: str) -> bool:
        """Check if a string value looks like a date"""
        # Common date patterns
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{4}/\d{2}/\d{2}',  # YYYY/MM/DD
        ]
        return any(re.match(pattern, str(value)) for pattern in date_patterns)
    
    def _detect_relationships(self):
        """Detect relationships between entity types"""
        for entity_type, entities in self.entities_by_type.items():
            for entity in entities:
                for prop_name, prop_value in entity['properties'].items():
                    # Check if this property value is a URI pointing to another entity
                    for target_type in self.entity_types:
                        target_entities = self.entities_by_type[target_type]
                        if any(e['uri'] == prop_value for e in target_entities):
                            self.relationships[entity_type].add((prop_name, target_type))
                            break
    
    def _get_entities_of_type(self, entity_type: str) -> List[Dict]:
        """Get all entities of a specific type"""
        return self.entities_by_type.get(entity_type, [])
    
    def _get_sample_entities(self, entity_type: str, count: int) -> List[Dict]:
        """Get a random sample of entities of a specific type"""
        entities = self._get_entities_of_type(entity_type)
        if not entities:
            return []
        return random.sample(entities, min(count, len(entities)))
    
    def generate_all_questions(self, num_questions: int = 100) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Generate all benchmark questions dynamically based on discovered schema"""
        questions = []
        
        # Validate we have data
        if not self.entity_types:
            raise ValueError("No entity types found in the Turtle file")
        
        # Distribution of questions across categories
        distribution = {
            'property_search': 15,
            'depth_first_search': 15,
            'breadth_first_search': 15,
            'mathematical': 15,
            'filtering': 20,
            'aggregation': 20,
        }
        
        # Adjust distribution if we don't have enough data
        total_entities = sum(len(entities) for entities in self.entities_by_type.values())
        if total_entities < 10:
            print(f"Warning: Only {total_entities} entities found. Reducing question count.")
            for key in distribution:
                distribution[key] = max(1, distribution[key] // 5)
        
        # Generate questions for each category
        questions.extend(self.generate_property_search_questions(distribution['property_search']))
        questions.extend(self.generate_depth_first_search_questions(distribution['depth_first_search']))
        questions.extend(self.generate_breadth_first_search_questions(distribution['breadth_first_search']))
        questions.extend(self.generate_mathematical_questions(distribution['mathematical']))
        questions.extend(self.generate_filtering_questions(distribution['filtering']))
        questions.extend(self.generate_aggregation_questions(distribution['aggregation']))
        
        # Add pattern matching as bonus
        bonus_questions = self.generate_pattern_matching_questions(15)
        
        return questions, bonus_questions
    
    def generate_property_search_questions(self, count: int) -> List[Dict[str, Any]]:
        """Generate simple property lookup questions dynamically"""
        questions = []
        question_id = 1
        
        # Create questions by iterating through entity types
        for entity_type in self.entity_types:
            entities = self._get_entities_of_type(entity_type)
            if not entities:
                continue
            
            properties = list(self.properties_by_type[entity_type])
            if not properties:
                continue
            
            # Generate questions for this entity type
            for prop in properties[:5]:  # Limit properties per type
                if len(questions) >= count:
                    break
                
                # Pick a random entity of this type
                entity = random.choice(entities)
                if prop in entity['properties']:
                    questions.append({
                        'id': question_id,
                        'category': 'property_search',
                        'question': f"Find the {prop} for {entity_type} `{entity['uri']}`",
                        'entity_type': entity_type,
                        'entity_id': entity['uri'],
                        'property': prop,
                        'expected_answer': entity['properties'].get(prop)
                    })
                    question_id += 1
            
            if len(questions) >= count:
                break
        
        return questions[:count]
    
    def generate_depth_first_search_questions(self, count: int) -> List[Dict[str, Any]]:
        """Generate questions that require traversing relationships"""
        questions = []
        question_id = 16  # Continue from property search
        
        # Find entity types that have relationships
        for entity_type in self.entity_types:
            if entity_type not in self.relationships:
                continue
            
            relationships = list(self.relationships[entity_type])
            if not relationships:
                continue
            
            entities = self._get_sample_entities(entity_type, count)
            
            for entity in entities:
                if len(questions) >= count:
                    break
                
                # Pick a random relationship
                for rel_prop, target_type in relationships:
                    if len(questions) >= count:
                        break
                    
                    if rel_prop not in entity['properties']:
                        continue
                    
                    # Get properties of the target type
                    target_props = list(self.properties_by_type.get(target_type, []))
                    if not target_props:
                        continue
                    
                    # Create question about getting target entity details
                    sample_props = target_props[:min(3, len(target_props))]
                    questions.append({
                        'id': question_id,
                        'category': 'depth_first_search',
                        'question': f"Find the {', '.join(sample_props)} of the {target_type} referenced by {rel_prop} in {entity_type} `{entity['uri']}`",
                        'entity_type': entity_type,
                        'entity_id': entity['uri'],
                        'traversal_path': [rel_prop, target_type],
                        'required_properties': sample_props
                    })
                    question_id += 1
                    
                    if len(questions) >= count:
                        break
            
            if len(questions) >= count:
                break
        
        return questions[:count]
    
    def generate_breadth_first_search_questions(self, count: int) -> List[Dict[str, Any]]:
        """Generate questions that retrieve collections of related entities"""
        questions = []
        question_id = 31  # Continue from depth-first search
        
        # Look for one-to-many relationships (reverse lookup)
        for source_type in self.entity_types:
            for target_type in self.entity_types:
                if target_type not in self.relationships:
                    continue
                
                # Check if target_type has a relationship to source_type
                related_props = [
                    prop for prop, t in self.relationships[target_type]
                    if t == source_type
                ]
                
                if not related_props:
                    continue
                
                # Get sample entities of source type
                source_entities = self._get_sample_entities(source_type, 3)
                
                for source_entity in source_entities:
                    if len(questions) >= count:
                        break
                    
                    for rel_prop in related_props[:2]:  # Limit properties
                        if len(questions) >= count:
                            break
                        
                        # Get a sample property from target type to collect
                        target_props = list(self.properties_by_type.get(target_type, []))
                        if not target_props:
                            continue
                        
                        collect_prop = random.choice(target_props)
                        
                        questions.append({
                            'id': question_id,
                            'category': 'breadth_first_search',
                            'question': f"List all {collect_prop} values from {target_type} entities that reference {source_type} `{source_entity['uri']}` via {rel_prop}",
                            'entity_type': source_type,
                            'entity_id': source_entity['uri'],
                            'collection_type': target_type,
                            'collection_property': rel_prop,
                            'return_property': collect_prop
                        })
                        question_id += 1
                
                if len(questions) >= count:
                    break
            
            if len(questions) >= count:
                break
        
        return questions[:count]
    
    def generate_mathematical_questions(self, count: int) -> List[Dict[str, Any]]:
        """Generate mathematical computation questions"""
        questions = []
        question_id = 46  # Continue from breadth-first search
        
        # Find entity types with numeric properties
        math_operations = ['sum', 'average', 'max', 'min', 'median', 'stddev']
        
        for entity_type in self.entity_types:
            numeric_props = list(self.numeric_properties.get(entity_type, []))
            if not numeric_props:
                continue
            
            for num_prop in numeric_props:
                if len(questions) >= count:
                    break
                
                # Generate different types of math questions
                for operation in math_operations:
                    if len(questions) >= count:
                        break
                    
                    questions.append({
                        'id': question_id,
                        'category': 'mathematical',
                        'question': f"Calculate the {operation} of {num_prop} across all {entity_type} entities",
                        'operation': operation,
                        'entity_type': entity_type,
                        'property': num_prop
                    })
                    question_id += 1
                
                # Add filtered math questions using string properties as filters
                string_props = list(self.string_properties.get(entity_type, []))
                if string_props and len(questions) < count:
                    filter_prop = random.choice(string_props)
                    filter_values = list(self.property_values[entity_type][filter_prop])
                    if filter_values:
                        filter_value = random.choice(list(filter_values))
                        questions.append({
                            'id': question_id,
                            'category': 'mathematical',
                            'question': f"Calculate the sum of {num_prop} for {entity_type} entities where {filter_prop} is '{filter_value}'",
                            'operation': 'sum',
                            'entity_type': entity_type,
                            'property': num_prop,
                            'filter': {filter_prop: filter_value}
                        })
                        question_id += 1
            
            if len(questions) >= count:
                break
        
        return questions[:count]
    
    def generate_filtering_questions(self, count: int) -> List[Dict[str, Any]]:
        """Generate filtering/conditional queries"""
        questions = []
        question_id = 61  # Continue from mathematical
        
        for entity_type in self.entity_types:
            if len(questions) >= count:
                break
            
            # String property filters (equality)
            string_props = list(self.string_properties.get(entity_type, []))
            for prop in string_props[:3]:  # Limit properties
                if len(questions) >= count:
                    break
                
                # Get unique values for this property
                prop_values = list(self.property_values[entity_type].get(prop, []))
                if not prop_values:
                    continue
                
                # Create equality filter question
                filter_value = random.choice(prop_values)
                questions.append({
                    'id': question_id,
                    'category': 'filtering',
                    'question': f"Find all {entity_type} entities where {prop} is '{filter_value}'",
                    'entity_type': entity_type,
                    'filter': {prop: filter_value}
                })
                question_id += 1
                
                # Create pattern matching filter (startswith/contains)
                if len(questions) < count and len(str(filter_value)) > 3:
                    prefix = str(filter_value)[:3]
                    questions.append({
                        'id': question_id,
                        'category': 'filtering',
                        'question': f"Find all {entity_type} entities where {prop} starts with '{prefix}'",
                        'entity_type': entity_type,
                        'filter': {prop: {'operator': 'startswith', 'value': prefix}}
                    })
                    question_id += 1
            
            # Numeric property filters
            numeric_props = list(self.numeric_properties.get(entity_type, []))
            for prop in numeric_props[:2]:  # Limit properties
                if len(questions) >= count:
                    break
                
                # Get numeric values
                prop_values = [
                    float(v) for v in self.property_values[entity_type].get(prop, [])
                    if v and v.replace('.', '').replace('-', '').isdigit()
                ]
                
                if not prop_values:
                    continue
                
                # Calculate threshold values
                avg_value = sum(prop_values) / len(prop_values)
                
                # Greater than filter
                questions.append({
                    'id': question_id,
                    'category': 'filtering',
                    'question': f"Find all {entity_type} entities where {prop} is greater than {avg_value:.2f}",
                    'entity_type': entity_type,
                    'filter': {prop: {'operator': '>', 'value': avg_value}}
                })
                question_id += 1
                
                # Range filter
                if len(questions) < count:
                    min_val = min(prop_values)
                    max_val = max(prop_values)
                    mid_low = min_val + (max_val - min_val) * 0.33
                    mid_high = min_val + (max_val - min_val) * 0.66
                    
                    questions.append({
                        'id': question_id,
                        'category': 'filtering',
                        'question': f"Find all {entity_type} entities where {prop} is between {mid_low:.2f} and {mid_high:.2f}",
                        'entity_type': entity_type,
                        'filter': {prop: {'operator': 'between', 'min': mid_low, 'max': mid_high}}
                    })
                    question_id += 1
            
            # Date property filters
            date_props = list(self.date_properties.get(entity_type, []))
            for prop in date_props[:1]:  # Limit properties
                if len(questions) >= count:
                    break
                
                # Get date values
                date_values = list(self.property_values[entity_type].get(prop, []))
                if not date_values:
                    continue
                
                # Extract month from a sample date
                sample_date = random.choice(date_values)
                if '-' in sample_date:
                    year_month = '-'.join(sample_date.split('-')[:2])
                    questions.append({
                        'id': question_id,
                        'category': 'filtering',
                        'question': f"Find all {entity_type} entities where {prop} is in {year_month}",
                        'entity_type': entity_type,
                        'filter': {prop: {'operator': 'month', 'value': year_month}}
                    })
                    question_id += 1
        
        return questions[:count]
    
    def generate_aggregation_questions(self, count: int) -> List[Dict[str, Any]]:
        """Generate aggregation/grouping questions"""
        questions = []
        question_id = 81  # Continue from filtering
        
        for entity_type in self.entity_types:
            if len(questions) >= count:
                break
            
            # Basic count
            questions.append({
                'id': question_id,
                'category': 'aggregation',
                'question': f"Count the total number of {entity_type} entities",
                'operation': 'count',
                'entity_type': entity_type
            })
            question_id += 1
            
            # Group by string properties
            string_props = list(self.string_properties.get(entity_type, []))
            for prop in string_props[:3]:  # Limit properties
                if len(questions) >= count:
                    break
                
                # Count by group
                questions.append({
                    'id': question_id,
                    'category': 'aggregation',
                    'question': f"Count the number of {entity_type} entities grouped by {prop}",
                    'operation': 'group_count',
                    'entity_type': entity_type,
                    'group_by': prop
                })
                question_id += 1
            
            # Group by and sum numeric properties
            numeric_props = list(self.numeric_properties.get(entity_type, []))
            if numeric_props and string_props and len(questions) < count:
                num_prop = numeric_props[0]
                group_prop = string_props[0]
                
                questions.append({
                    'id': question_id,
                    'category': 'aggregation',
                    'question': f"Calculate the total {num_prop} grouped by {group_prop} for {entity_type}",
                    'operation': 'group_sum',
                    'entity_type': entity_type,
                    'group_by': group_prop,
                    'sum_property': num_prop
                })
                question_id += 1
                
                # Average by group
                if len(questions) < count:
                    questions.append({
                        'id': question_id,
                        'category': 'aggregation',
                        'question': f"Calculate the average {num_prop} grouped by {group_prop} for {entity_type}",
                        'operation': 'group_average',
                        'entity_type': entity_type,
                        'group_by': group_prop,
                        'average_property': num_prop
                    })
                    question_id += 1
            
            # Date-based grouping
            date_props = list(self.date_properties.get(entity_type, []))
            if date_props and len(questions) < count:
                date_prop = date_props[0]
                
                # Count by month
                questions.append({
                    'id': question_id,
                    'category': 'aggregation',
                    'question': f"Count the number of {entity_type} entities per month based on {date_prop}",
                    'operation': 'group_count',
                    'entity_type': entity_type,
                    'group_by': date_prop,
                    'group_function': 'extract_month'
                })
                question_id += 1
                
                # Sum by month if numeric property exists
                if numeric_props and len(questions) < count:
                    num_prop = numeric_props[0]
                    questions.append({
                        'id': question_id,
                        'category': 'aggregation',
                        'question': f"Calculate the total {num_prop} per month based on {date_prop} for {entity_type}",
                        'operation': 'group_sum',
                        'entity_type': entity_type,
                        'group_by': date_prop,
                        'group_function': 'extract_month',
                        'sum_property': num_prop
                    })
                    question_id += 1
            
            # Percentage distribution
            if string_props and len(questions) < count:
                prop = string_props[0]
                questions.append({
                    'id': question_id,
                    'category': 'aggregation',
                    'question': f"Calculate the percentage distribution of {entity_type} entities across different {prop} values",
                    'operation': 'group_percentage',
                    'entity_type': entity_type,
                    'group_by': prop
                })
                question_id += 1
        
        return questions[:count]
    
    def generate_pattern_matching_questions(self, count: int) -> List[Dict[str, Any]]:
        """Generate complex pattern matching questions"""
        questions = []
        question_id = 101  # Bonus questions start at 101
        
        # Pattern 1: Find entities where two related entities are different
        for entity_type in self.entity_types:
            if len(questions) >= count:
                break
            
            rels = list(self.relationships.get(entity_type, []))
            if len(rels) >= 2:
                rel1, target1 = rels[0]
                rel2, target2 = rels[1]
                
                questions.append({
                    'id': question_id,
                    'category': 'pattern_matching',
                    'question': f"Find all {entity_type} entities where the {target1} referenced by {rel1} is different from the {target2} referenced by {rel2}",
                    'pattern': 'inequality_join',
                    'entity_type': entity_type,
                    'condition': f'{rel1} != {rel2}'
                })
                question_id += 1
        
        # Pattern 2: Regex patterns on string properties
        for entity_type in self.entity_types:
            if len(questions) >= count:
                break
            
            string_props = list(self.string_properties.get(entity_type, []))
            for prop in string_props[:2]:
                if len(questions) >= count:
                    break
                
                # Get sample values to create meaningful patterns
                sample_values = list(self.property_values[entity_type].get(prop, []))
                if sample_values:
                    sample = str(sample_values[0])
                    # Look for digits in the sample
                    if any(c.isdigit() for c in sample):
                        questions.append({
                            'id': question_id,
                            'category': 'pattern_matching',
                            'question': f"Find all {entity_type} entities where {prop} contains exactly 6 consecutive digits",
                            'pattern': 'regex',
                            'entity_type': entity_type,
                            'property': prop,
                            'regex': r'\d{6}'
                        })
                        question_id += 1
        
        # Pattern 3: Substring matching
        for entity_type in self.entity_types:
            if len(questions) >= count:
                break
            
            string_props = list(self.string_properties.get(entity_type, []))
            for prop in string_props[:1]:
                if len(questions) >= count:
                    break
                
                # Find common substrings in values
                sample_values = list(self.property_values[entity_type].get(prop, []))
                if sample_values and len(sample_values) > 0:
                    # Look for common words
                    sample = str(sample_values[0])
                    if ' ' in sample:
                        words = sample.split()
                        if words:
                            search_word = words[0]
                            questions.append({
                                'id': question_id,
                                'category': 'pattern_matching',
                                'question': f"Find all {entity_type} entities where {prop} contains the word '{search_word}'",
                                'pattern': 'substring_match',
                                'entity_type': entity_type,
                                'property': prop,
                                'contains': search_word
                            })
                            question_id += 1
        
        # Pattern 4: Multi-condition filters
        for entity_type in self.entity_types:
            if len(questions) >= count:
                break
            
            numeric_props = list(self.numeric_properties.get(entity_type, []))
            string_props = list(self.string_properties.get(entity_type, []))
            
            if numeric_props and string_props:
                num_prop = numeric_props[0]
                str_prop = string_props[0]
                str_values = list(self.property_values[entity_type].get(str_prop, []))
                
                if str_values:
                    str_val = random.choice(list(str_values))
                    questions.append({
                        'id': question_id,
                        'category': 'pattern_matching',
                        'question': f"Find all {entity_type} entities where {num_prop} is less than 1000 AND {str_prop} is not '{str_val}'",
                        'pattern': 'compound_filter',
                        'entity_type': entity_type,
                        'condition': f'{num_prop} < 1000 AND {str_prop} != "{str_val}"'
                    })
                    question_id += 1
        
        # Pattern 5: Aggregated filters
        for entity_type in self.entity_types:
            if len(questions) >= count:
                break
            
            # Look for relationships to create aggregated conditions
            if entity_type in self.relationships:
                rels = list(self.relationships[entity_type])
                if rels:
                    rel_prop, target_type = rels[0]
                    # Find numeric property in current entity type
                    numeric_props = list(self.numeric_properties.get(entity_type, []))
                    if numeric_props:
                        num_prop = numeric_props[0]
                        questions.append({
                            'id': question_id,
                            'category': 'pattern_matching',
                            'question': f"Find all {target_type} entities that are referenced by {entity_type} entities with total {num_prop} greater than 5000",
                            'pattern': 'aggregate_filter',
                            'entity_type': target_type,
                            'condition': f'sum({entity_type}.{num_prop}) > 5000'
                        })
                        question_id += 1
        
        # Pattern 6: Prefix matching
        for entity_type in self.entity_types:
            if len(questions) >= count:
                break
            
            string_props = list(self.string_properties.get(entity_type, []))
            for prop in string_props[:1]:
                if len(questions) >= count:
                    break
                
                sample_values = list(self.property_values[entity_type].get(prop, []))
                if sample_values:
                    sample = str(sample_values[0])
                    if len(sample) > 1:
                        prefix = sample[0]
                        questions.append({
                            'id': question_id,
                            'category': 'pattern_matching',
                            'question': f"Find all {entity_type} entities where {prop} starts with '{prefix}'",
                            'pattern': 'prefix_match',
                            'entity_type': entity_type,
                            'property': prop,
                            'startswith': prefix
                        })
                        question_id += 1
        
        # Pattern 7: Duplicate detection
        for entity_type in self.entity_types:
            if len(questions) >= count:
                break
            
            string_props = list(self.string_properties.get(entity_type, []))
            if string_props:
                prop = string_props[0]
                questions.append({
                    'id': question_id,
                    'category': 'pattern_matching',
                    'question': f"Find all {prop} values that appear in multiple {entity_type} entities",
                    'pattern': 'duplicate_detection',
                    'entity_type': entity_type,
                    'property': prop,
                    'condition': f'count({entity_type}) > 1 grouped by {prop}'
                })
                question_id += 1
        
        return questions[:count]
    
    def export_to_json(self, questions: List[Dict], bonus_questions: List[Dict], filename: str):
        """Export questions to JSON file"""
        # Count entities by type
        entity_counts = {
            entity_type: len(entities)
            for entity_type, entities in self.entities_by_type.items()
        }
        
        output = {
            'metadata': {
                'total_questions': len(questions),
                'total_bonus_questions': len(bonus_questions),
                'entity_types': self.entity_types,
                'entity_counts': entity_counts,
                'property_types': {
                    entity_type: {
                        'all': list(self.properties_by_type[entity_type]),
                        'numeric': list(self.numeric_properties.get(entity_type, [])),
                        'date': list(self.date_properties.get(entity_type, [])),
                        'string': list(self.string_properties.get(entity_type, []))
                    }
                    for entity_type in self.entity_types
                },
                'relationships': {
                    entity_type: [
                        {'property': prop, 'target_type': target}
                        for prop, target in rels
                    ]
                    for entity_type, rels in self.relationships.items()
                },
                'categories': {
                    'property_search': sum(1 for q in questions if q['category'] == 'property_search'),
                    'depth_first_search': sum(1 for q in questions if q['category'] == 'depth_first_search'),
                    'breadth_first_search': sum(1 for q in questions if q['category'] == 'breadth_first_search'),
                    'mathematical': sum(1 for q in questions if q['category'] == 'mathematical'),
                    'filtering': sum(1 for q in questions if q['category'] == 'filtering'),
                    'aggregation': sum(1 for q in questions if q['category'] == 'aggregation'),
                    'pattern_matching': len(bonus_questions)
                }
            },
            'main_questions': questions,
            'bonus_questions': bonus_questions
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
    
    def export_to_markdown(self, questions: List[Dict], bonus_questions: List[Dict], filename: str):
        """Export questions to Markdown file"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# Benchmark Questions for Serialization Format Testing\n\n")
            f.write("## Dataset Statistics\n\n")
            
            # Write entity counts dynamically
            for entity_type in self.entity_types:
                count = len(self.entities_by_type[entity_type])
                f.write(f"- **{entity_type}**: {count}\n")
            
            f.write(f"\n**Total Entities**: {sum(len(e) for e in self.entities_by_type.values())}\n")
            f.write(f"**Entity Types**: {len(self.entity_types)}\n\n")
            
            # Write schema information
            f.write("## Schema Overview\n\n")
            for entity_type in self.entity_types:
                f.write(f"### {entity_type}\n\n")
                f.write(f"**Properties**: {len(self.properties_by_type[entity_type])}\n")
                
                # List properties by type
                if self.numeric_properties.get(entity_type):
                    f.write(f"- Numeric: {', '.join(self.numeric_properties[entity_type])}\n")
                if self.date_properties.get(entity_type):
                    f.write(f"- Date: {', '.join(self.date_properties[entity_type])}\n")
                if self.string_properties.get(entity_type):
                    num_str_props = len(self.string_properties[entity_type])
                    f.write(f"- String: {num_str_props} properties\n")
                
                # List relationships
                if entity_type in self.relationships:
                    f.write(f"\n**Relationships**:\n")
                    for prop, target in self.relationships[entity_type]:
                        f.write(f"- {prop} → {target}\n")
                
                f.write("\n")
            
            # Group questions by category
            by_category = defaultdict(list)
            for q in questions:
                by_category[q['category']].append(q)
            
            # Write main questions
            f.write("## Main Questions ({})\n\n".format(len(questions)))
            for category in ['property_search', 'depth_first_search', 'breadth_first_search', 
                           'mathematical', 'filtering', 'aggregation']:
                if category in by_category:
                    category_name = category.replace('_', ' ').title()
                    f.write(f"### {category_name} ({len(by_category[category])} questions)\n\n")
                    for q in by_category[category]:
                        f.write(f"{q['id']}. {q['question']}\n")
                    f.write("\n")
            
            # Write bonus questions
            if bonus_questions:
                f.write(f"## Bonus: Pattern Matching Questions ({len(bonus_questions)})\n\n")
                for q in bonus_questions:
                    f.write(f"{q['id']}. {q['question']}\n")
                f.write("\n")


def main():
    parser = argparse.ArgumentParser(
        description='Generate benchmark questions from a Turtle/RDF file'
    )
    parser.add_argument(
        'turtle_file',
        help='Path to the input Turtle (.ttl) file'
    )
    parser.add_argument(
        '-o', '--output',
        default='benchmark_questions',
        help='Output filename prefix (default: benchmark_questions)'
    )
    parser.add_argument(
        '-f', '--format',
        choices=['json', 'markdown', 'both'],
        default='both',
        help='Output format (default: both)'
    )
    parser.add_argument(
        '-n', '--num-questions',
        type=int,
        default=100,
        help='Number of main questions to generate (default: 100)'
    )
    
    args = parser.parse_args()
    
    # Generate questions
    print(f"Parsing {args.turtle_file}...")
    generator = BenchmarkQuestionGenerator(args.turtle_file)
    
    print(f"Generating {args.num_questions} benchmark questions...")
    questions, bonus_questions = generator.generate_all_questions(args.num_questions)
    
    # Export
    if args.format in ['json', 'both']:
        json_file = f"{args.output}.json"
        generator.export_to_json(questions, bonus_questions, json_file)
        print(f"Exported to {json_file}")
    
    if args.format in ['markdown', 'both']:
        md_file = f"{args.output}.md"
        generator.export_to_markdown(questions, bonus_questions, md_file)
        print(f"Exported to {md_file}")
    
    print(f"\nGeneration complete!")
    print(f"Main questions: {len(questions)}")
    print(f"Bonus questions: {len(bonus_questions)}")
    print(f"\nQuestion distribution:")
    category_counts = defaultdict(int)
    for q in questions:
        category_counts[q['category']] += 1
    for category, count in sorted(category_counts.items()):
        print(f"  {category}: {count}")


if __name__ == '__main__':
    main()