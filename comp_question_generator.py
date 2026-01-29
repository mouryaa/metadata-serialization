"""
Abstract Question Generator for RDF Data Performance Benchmarking

This refactored version uses a template-based approach to generate questions
dynamically based on the discovered schema, making it more maintainable and extensible.

Usage:
    python abstract_question_generator.py <turtle_file> [output_csv] [num_questions] [--difficulty DIST]
    
Examples:
    python abstract_question_generator.py data.ttl questions.csv 100
    python abstract_question_generator.py data.ttl questions.csv 100 --difficulty 50,30,20
"""

import rdflib
from rdflib import Graph, Namespace, RDF
from collections import defaultdict, deque
import random
import csv
import sys
import json
import re
from datetime import datetime
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Callable, Optional


class SchemaDiscovery:
    """Discovers and caches the RDF schema structure."""
    
    def __init__(self, graph: Graph, schema_ns: Namespace):
        self.graph = graph
        self.schema = schema_ns
        self.entities_by_type = defaultdict(list)
        self.properties_by_type = defaultdict(set)
        self.categorical_values = defaultdict(set)
        
    def discover(self):
        """Discover all entity types, properties, and values."""
        # Find all entity types
        for subject, _, obj in self.graph.triples((None, RDF.type, None)):
            entity_type = self._simplify_uri(obj)
            self.entities_by_type[entity_type].append(subject)
        
        # Find properties for each type
        for entity_type, entities in self.entities_by_type.items():
            if entities:
                sample = entities[0]
                for pred, obj in self.graph.predicate_objects(sample):
                    prop_name = self._simplify_uri(pred)
                    self.properties_by_type[entity_type].add(prop_name)
        
        # Collect categorical values
        for entity_type, entities in self.entities_by_type.items():
            for entity in entities:
                for prop in self.properties_by_type[entity_type]:
                    value = self._get_property(entity, prop)
                    if value and self._is_categorical(value):
                        self.categorical_values[f"{entity_type}.{prop}"].add(value)
        
        return self
    
    def _get_property(self, subject, predicate):
        """Get a single property value."""
        value = self.graph.value(subject, self.schema[predicate])
        return str(value) if value else None
    
    def _simplify_uri(self, uri):
        """Simplify URIs for readable output."""
        uri_str = str(uri)
        if '#' in uri_str:
            return uri_str.split('#')[-1]
        elif '/' in uri_str:
            return uri_str.split('/')[-1]
        return uri_str
    
    def _is_categorical(self, value):
        """Check if a value is categorical (not numeric, not date, not long text)."""
        try:
            float(value)
            return False
        except:
            pass
        
        if len(str(value)) > 50:
            return False
        
        if re.match(r'\d{4}-\d{2}-\d{2}', str(value)):
            return False
        
        return True


class QuestionTemplate:
    """Represents a template for generating questions."""
    
    def __init__(self, 
                 category: str,
                 subcategory: str,
                 difficulty: str,
                 question_format: str,
                 answer_extractor: Callable,
                 constraints: Optional[Dict] = None):
        self.category = category
        self.subcategory = subcategory
        self.difficulty = difficulty
        self.question_format = question_format
        self.answer_extractor = answer_extractor
        self.constraints = constraints or {}
    
    def generate(self, graph, schema, entities, **kwargs):
        """Generate a question instance from this template."""
        try:
            answer = self.answer_extractor(graph, schema, entities, **kwargs)
            if answer is None:
                return None
            
            question_text = self.question_format.format(**kwargs)
            
            return {
                'category': self.category,
                'subcategory': self.subcategory,
                'difficulty': self.difficulty,
                'question': question_text,
                'answer': answer,
                'query_type': kwargs.get('query_type', 'unknown')
            }
        except Exception as e:
            return None


class AbstractQuestionGenerator:
    """Abstract question generator using templates and discovered schema."""
    
    def __init__(self, turtle_file: str, difficulty_distribution: Optional[Dict] = None):
        """Initialize the generator with schema discovery."""
        print(f"Loading RDF graph from {turtle_file}...")
        self.graph = Graph()
        self.graph.parse(turtle_file, format='turtle')
        
        # Namespaces
        self.schema = Namespace("http://schema.org/")
        self.ex = Namespace("http://example.org/")
        
        # Difficulty distribution
        if difficulty_distribution is None:
            self.difficulty_distribution = {'easy': 33, 'medium': 34, 'hard': 33}
        else:
            total = sum(difficulty_distribution.values())
            if abs(total - 100) > 0.1:
                raise ValueError(f"Difficulty percentages must sum to 100, got {total}")
            self.difficulty_distribution = difficulty_distribution
        
        print(f"Difficulty distribution: Easy {self.difficulty_distribution['easy']}%, "
              f"Medium {self.difficulty_distribution['medium']}%, "
              f"Hard {self.difficulty_distribution['hard']}%")
        
        # Discover schema
        print("Discovering schema...")
        self.schema_discovery = SchemaDiscovery(self.graph, self.schema).discover()
        
        print(f"\nDiscovered Schema:")
        for entity_type, entities in self.schema_discovery.entities_by_type.items():
            props = self.schema_discovery.properties_by_type[entity_type]
            print(f"  {entity_type}: {len(entities)} entities, {len(props)} properties")
        
        # Initialize template registry
        self.templates = []
        self._register_templates()
    
    def _register_templates(self):
        """Register all question templates."""
        self._register_property_search_templates()
        self._register_traversal_templates()
        self._register_collection_templates()
        self._register_mathematical_templates()
        self._register_filtering_templates()
        self._register_aggregation_templates()
        self._register_pattern_templates()
    
    # ===== TEMPLATE REGISTRATION METHODS =====
    
    def _register_property_search_templates(self):
        """Register property search question templates."""
        
        # Simple property lookup
        def simple_property_answer(graph, schema, entities, entity, property_name, **kwargs):
            value = graph.value(entity, schema[property_name])
            if not value:
                return None
            # Handle numeric properties
            if property_name in ['totalPrice', 'amount']:
                try:
                    return float(str(value))
                except:
                    return str(value)
            return str(value)
        
        self.templates.append(QuestionTemplate(
            category='Property Search',
            subcategory='Simple Property',
            difficulty='Easy',
            question_format='What is the {property_name} of {entity_id}?',
            answer_extractor=simple_property_answer
        ))
        
        # Multi-property lookup
        def multi_property_answer(graph, schema, entities, entity, properties, **kwargs):
            result = {}
            for prop in properties:
                value = graph.value(entity, schema[prop])
                if not value:
                    return None
                if prop in ['totalPrice', 'amount']:
                    try:
                        result[prop] = float(str(value))
                    except:
                        result[prop] = str(value)
                else:
                    result[prop] = str(value)
            return result
        
        self.templates.append(QuestionTemplate(
            category='Property Search',
            subcategory='Multi-Property',
            difficulty='Easy',
            question_format='What are the {property_list} of {entity_id}?',
            answer_extractor=multi_property_answer
        ))
        
        # Nested property lookup
        def nested_property_answer(graph, schema, entities, entity, relationship, target_property, **kwargs):
            related = graph.value(entity, schema[relationship])
            if not related:
                return None
            value = graph.value(related, schema[target_property])
            if not value:
                return None
            if target_property in ['totalPrice', 'amount']:
                try:
                    return float(str(value))
                except:
                    return str(value)
            return str(value)
        
        self.templates.append(QuestionTemplate(
            category='Property Search',
            subcategory='Nested Property',
            difficulty='Medium',
            question_format="What is the {relationship}'s {target_property} for {entity_type} {entity_id}?",
            answer_extractor=nested_property_answer
        ))
    
    def _register_traversal_templates(self):
        """Register depth-first and breadth-first traversal templates."""
        
        # 2-hop chain traversal
        def chain_traversal_answer(graph, schema, entities, entity, hop1, hop2, **kwargs):
            intermediate = graph.value(entity, schema[hop1])
            if not intermediate:
                return None
            result = graph.value(intermediate, schema[hop2])
            return str(result) if result else None
        
        self.templates.append(QuestionTemplate(
            category='Depth-First Search',
            subcategory='Chain Traversal',
            difficulty='Medium',
            question_format='Follow the path: {entity_id} → {hop1} → {hop2}. What is the value?',
            answer_extractor=chain_traversal_answer
        ))
        
        # Multi-hop query
        self.templates.append(QuestionTemplate(
            category='Depth-First Search',
            subcategory='Multi-Hop',
            difficulty='Medium',
            question_format='What is the {target_property} of the {relationship} for {entity_type} {entity_id}?',
            answer_extractor=lambda graph, schema, entities, entity, relationship, target_property, **kwargs:
                str(graph.value(graph.value(entity, schema[relationship]), schema[target_property]))
                if graph.value(entity, schema[relationship]) and 
                   graph.value(graph.value(entity, schema[relationship]), schema[target_property])
                else None
        ))
    
    def _register_collection_templates(self):
        """Register breadth-first search / collection templates."""
        
        # Collect all values of a property
        def collect_all_values(graph, schema, entities, entity_type, property_name, **kwargs):
            values = []
            for entity in entities.get(entity_type, []):
                value = graph.value(entity, schema[property_name])
                if value:
                    values.append(str(value))
            return sorted(set(values)) if values else None
        
        self.templates.append(QuestionTemplate(
            category='Breadth-First Search',
            subcategory='Same-Level Collection',
            difficulty='Easy',
            question_format='List all {property_name} values for all {entity_type} entities.',
            answer_extractor=collect_all_values
        ))
        
        # Count entities of a type
        def count_entities(graph, schema, entities, entity_type, **kwargs):
            return len(entities.get(entity_type, []))
        
        self.templates.append(QuestionTemplate(
            category='Breadth-First Search',
            subcategory='Entity Count',
            difficulty='Easy',
            question_format='How many {entity_type} entities are in the dataset?',
            answer_extractor=count_entities
        ))
    
    def _register_mathematical_templates(self):
        """Register mathematical aggregation templates."""
        
        # Sum of numeric property
        def sum_property(graph, schema, entities, entity_type, property_name, **kwargs):
            total = 0
            count = 0
            for entity in entities.get(entity_type, []):
                value = graph.value(entity, schema[property_name])
                if value:
                    try:
                        total += float(str(value))
                        count += 1
                    except:
                        pass
            return round(total, 2) if count > 0 else None
        
        self.templates.append(QuestionTemplate(
            category='Mathematical',
            subcategory='Basic Aggregation',
            difficulty='Easy',
            question_format='What is the total {property_name} of all {entity_type} entities?',
            answer_extractor=sum_property
        ))
        
        # Average
        def avg_property(graph, schema, entities, entity_type, property_name, **kwargs):
            values = []
            for entity in entities.get(entity_type, []):
                value = graph.value(entity, schema[property_name])
                if value:
                    try:
                        values.append(float(str(value)))
                    except:
                        pass
            return round(sum(values) / len(values), 2) if values else None
        
        self.templates.append(QuestionTemplate(
            category='Mathematical',
            subcategory='Basic Aggregation',
            difficulty='Easy',
            question_format='What is the average {property_name} of all {entity_type} entities?',
            answer_extractor=avg_property
        ))
        
        # Max/Min
        for agg_func, agg_name in [(max, 'maximum'), (min, 'minimum')]:
            def agg_property(graph, schema, entities, entity_type, property_name, func=agg_func, **kwargs):
                values = []
                for entity in entities.get(entity_type, []):
                    value = graph.value(entity, schema[property_name])
                    if value:
                        try:
                            values.append(float(str(value)))
                        except:
                            pass
                return round(func(values), 2) if values else None
            
            self.templates.append(QuestionTemplate(
                category='Mathematical',
                subcategory='Basic Aggregation',
                difficulty='Easy',
                question_format=f'What is the {agg_name} {{property_name}} of all {{entity_type}} entities?',
                answer_extractor=agg_property
            ))
    
    def _register_filtering_templates(self):
        """Register filtering question templates."""
        
        # Simple filter
        def simple_filter(graph, schema, entities, entity_type, property_name, filter_value, **kwargs):
            results = []
            for entity in entities.get(entity_type, []):
                value = graph.value(entity, schema[property_name])
                if value and str(value) == str(filter_value):
                    results.append(self._simplify_uri(entity))
            return sorted(results) if results else None
        
        self.templates.append(QuestionTemplate(
            category='Filtering',
            subcategory='Simple Filter',
            difficulty='Easy',
            question_format='Find all {entity_type} entities with {property_name} equal to "{filter_value}".',
            answer_extractor=simple_filter
        ))
        
        # Numeric comparison filter
        def numeric_filter(graph, schema, entities, entity_type, property_name, operator, threshold, **kwargs):
            results = []
            ops = {'>': lambda x, y: x > y, '<': lambda x, y: x < y, 
                   '>=': lambda x, y: x >= y, '<=': lambda x, y: x <= y}
            
            for entity in entities.get(entity_type, []):
                value = graph.value(entity, schema[property_name])
                if value:
                    try:
                        if ops[operator](float(str(value)), threshold):
                            results.append(self._simplify_uri(entity))
                    except:
                        pass
            return sorted(results) if results else None
        
        self.templates.append(QuestionTemplate(
            category='Filtering',
            subcategory='Simple Filter',
            difficulty='Easy',
            question_format='Find all {entity_type} entities with {property_name} {operator} {threshold}.',
            answer_extractor=numeric_filter
        ))
        
        # Pattern filter
        def pattern_filter(graph, schema, entities, entity_type, property_name, pattern_type, pattern, **kwargs):
            results = []
            for entity in entities.get(entity_type, []):
                value = graph.value(entity, schema[property_name])
                if value:
                    value_str = str(value)
                    match = False
                    if pattern_type == 'startswith':
                        match = value_str.startswith(pattern)
                    elif pattern_type == 'endswith':
                        match = value_str.endswith(pattern)
                    elif pattern_type == 'contains':
                        match = pattern in value_str
                    elif pattern_type == 'regex':
                        match = re.search(pattern, value_str) is not None
                    
                    if match:
                        results.append(self._simplify_uri(entity))
            return sorted(results) if results else None
        
        self.templates.append(QuestionTemplate(
            category='Filtering',
            subcategory='Pattern Filter',
            difficulty='Medium',
            question_format='Find all {entity_type} entities with {property_name} {pattern_desc}.',
            answer_extractor=pattern_filter
        ))
    
    def _register_aggregation_templates(self):
        """Register aggregation/group-by templates."""
        
        # Group by and count
        def group_by_count(graph, schema, entities, entity_type, group_property, **kwargs):
            counts = defaultdict(int)
            for entity in entities.get(entity_type, []):
                value = graph.value(entity, schema[group_property])
                if value:
                    counts[str(value)] += 1
            return dict(counts) if counts else None
        
        self.templates.append(QuestionTemplate(
            category='Aggregation',
            subcategory='Group By',
            difficulty='Medium',
            question_format='Group {entity_type} entities by {group_property} and count each group.',
            answer_extractor=group_by_count
        ))
        
        # Group by and sum
        def group_by_sum(graph, schema, entities, entity_type, group_property, sum_property, **kwargs):
            sums = defaultdict(float)
            for entity in entities.get(entity_type, []):
                group_val = graph.value(entity, schema[group_property])
                sum_val = graph.value(entity, schema[sum_property])
                if group_val and sum_val:
                    try:
                        sums[str(group_val)] += float(str(sum_val))
                    except:
                        pass
            return {k: round(v, 2) for k, v in sums.items()} if sums else None
        
        self.templates.append(QuestionTemplate(
            category='Aggregation',
            subcategory='Group By',
            difficulty='Medium',
            question_format='Group {entity_type} entities by {group_property} and sum {sum_property} for each group.',
            answer_extractor=group_by_sum
        ))
    
    def _register_pattern_templates(self):
        """Register pattern matching templates."""
        
        # Structural pattern - count related entities
        def count_related(graph, schema, entities, entity, relationship, **kwargs):
            related = list(graph.objects(entity, schema[relationship]))
            return len(related) if related else None
        
        self.templates.append(QuestionTemplate(
            category='Pattern Matching',
            subcategory='Structural Pattern',
            difficulty='Medium',
            question_format='How many {relationship} does {entity_type} {entity_id} have?',
            answer_extractor=count_related
        ))
        
        # Find entities with exact count of related items
        def filter_by_related_count(graph, schema, entities, entity_type, relationship, target_count, **kwargs):
            results = []
            for entity in entities.get(entity_type, []):
                related = list(graph.objects(entity, schema[relationship]))
                if len(related) == target_count:
                    results.append(self._simplify_uri(entity))
            return sorted(results) if results else None
        
        self.templates.append(QuestionTemplate(
            category='Pattern Matching',
            subcategory='Structural Pattern',
            difficulty='Medium',
            question_format='Find all {entity_type} entities with exactly {target_count} {relationship}.',
            answer_extractor=filter_by_related_count
        ))
    
    # ===== QUESTION GENERATION =====
    
    def _simplify_uri(self, uri):
        """Simplify URIs for readable output."""
        uri_str = str(uri)
        if '#' in uri_str:
            return uri_str.split('#')[-1]
        elif '/' in uri_str:
            return uri_str.split('/')[-1]
        return uri_str
    
    def _generate_from_template(self, template: QuestionTemplate, max_attempts: int = 50):
        """Generate a question from a specific template."""
        for _ in range(max_attempts):
            try:
                # Select appropriate entity type and entity
                entity_types = list(self.schema_discovery.entities_by_type.keys())
                if not entity_types:
                    return None
                
                entity_type = random.choice(entity_types)
                entities_of_type = self.schema_discovery.entities_by_type[entity_type]
                if not entities_of_type:
                    continue
                
                entity = random.choice(entities_of_type)
                entity_id = self._simplify_uri(entity)
                
                # Get properties for this entity type
                properties = list(self.schema_discovery.properties_by_type[entity_type])
                if not properties:
                    continue
                
                # Build kwargs based on template needs
                kwargs = {
                    'entity': entity,
                    'entity_id': entity_id,
                    'entity_type': entity_type,
                    'entities': self.schema_discovery.entities_by_type
                }
                
                # Add template-specific parameters
                if 'Simple Property' in template.subcategory or 'Basic Aggregation' in template.subcategory:
                    property_name = random.choice(properties)
                    kwargs['property_name'] = property_name
                
                elif 'Multi-Property' in template.subcategory:
                    if len(properties) < 2:
                        continue
                    selected_props = random.sample(properties, min(2, len(properties)))
                    kwargs['properties'] = selected_props
                    kwargs['property_list'] = ' and '.join(selected_props)
                
                elif 'Nested Property' in template.subcategory or 'Multi-Hop' in template.subcategory:
                    # Find relationship properties (those that link to other entities)
                    relationships = []
                    for prop in properties:
                        value = self.graph.value(entity, self.schema[prop])
                        if value and str(value).startswith('http://example.org/'):
                            relationships.append(prop)
                    
                    if not relationships:
                        continue
                    
                    relationship = random.choice(relationships)
                    related_entity = self.graph.value(entity, self.schema[relationship])
                    
                    if not related_entity:
                        continue
                    
                    # Get properties of related entity
                    related_type = None
                    for rdf_type in self.graph.objects(related_entity, RDF.type):
                        related_type = self._simplify_uri(rdf_type)
                        break
                    
                    if not related_type or related_type not in self.schema_discovery.properties_by_type:
                        continue
                    
                    related_props = list(self.schema_discovery.properties_by_type[related_type])
                    if not related_props:
                        continue
                    
                    target_property = random.choice(related_props)
                    kwargs['relationship'] = relationship
                    kwargs['target_property'] = target_property
                
                elif 'Chain Traversal' in template.subcategory:
                    # Find two sequential relationships
                    relationships = []
                    for prop in properties:
                        value = self.graph.value(entity, self.schema[prop])
                        if value and str(value).startswith('http://example.org/'):
                            relationships.append(prop)
                    
                    if not relationships:
                        continue
                    
                    hop1 = random.choice(relationships)
                    intermediate = self.graph.value(entity, self.schema[hop1])
                    
                    if not intermediate:
                        continue
                    
                    # Find properties of intermediate entity
                    intermediate_props = []
                    for prop, obj in self.graph.predicate_objects(intermediate):
                        prop_name = self._simplify_uri(prop)
                        if prop_name != 'type':
                            intermediate_props.append(prop_name)
                    
                    if not intermediate_props:
                        continue
                    
                    hop2 = random.choice(intermediate_props)
                    kwargs['hop1'] = hop1
                    kwargs['hop2'] = hop2
                
                elif 'Same-Level Collection' in template.subcategory:
                    property_name = random.choice(properties)
                    kwargs['property_name'] = property_name
                
                elif 'Simple Filter' in template.subcategory:
                    property_name = random.choice(properties)
                    kwargs['property_name'] = property_name
                    
                    # Check if numeric or categorical
                    sample_value = self.graph.value(entity, self.schema[property_name])
                    if sample_value:
                        try:
                            float(str(sample_value))
                            # Numeric - use comparison
                            kwargs['operator'] = random.choice(['>', '<', '>=', '<='])
                            kwargs['threshold'] = random.uniform(0, 10000)
                        except:
                            # Categorical - use equality
                            categorical_key = f"{entity_type}.{property_name}"
                            if categorical_key in self.schema_discovery.categorical_values:
                                possible_values = list(self.schema_discovery.categorical_values[categorical_key])
                                if possible_values:
                                    kwargs['filter_value'] = random.choice(possible_values)
                
                elif 'Pattern Filter' in template.subcategory:
                    # Find string properties
                    string_props = []
                    for prop in properties:
                        value = self.graph.value(entity, self.schema[prop])
                        if value and not str(value).replace('.', '').isdigit():
                            string_props.append(prop)
                    
                    if not string_props:
                        continue
                    
                    property_name = random.choice(string_props)
                    pattern_type = random.choice(['startswith', 'contains', 'endswith'])
                    
                    # Get a sample value to create pattern from
                    sample_value = str(self.graph.value(entity, self.schema[property_name]))
                    if len(sample_value) > 3:
                        if pattern_type == 'startswith':
                            pattern = sample_value[:3]
                            pattern_desc = f'starting with "{pattern}"'
                        elif pattern_type == 'endswith':
                            pattern = sample_value[-3:]
                            pattern_desc = f'ending with "{pattern}"'
                        else:
                            pattern = sample_value[1:4]
                            pattern_desc = f'containing "{pattern}"'
                        
                        kwargs['property_name'] = property_name
                        kwargs['pattern_type'] = pattern_type
                        kwargs['pattern'] = pattern
                        kwargs['pattern_desc'] = pattern_desc
                
                elif 'Group By' in template.subcategory:
                    # Need categorical property for grouping
                    categorical_props = []
                    for prop in properties:
                        categorical_key = f"{entity_type}.{prop}"
                        if categorical_key in self.schema_discovery.categorical_values:
                            if len(self.schema_discovery.categorical_values[categorical_key]) > 1:
                                categorical_props.append(prop)
                    
                    if not categorical_props:
                        continue
                    
                    group_property = random.choice(categorical_props)
                    kwargs['group_property'] = group_property
                    
                    if 'sum' in template.question_format.lower():
                        # Need numeric property for summing
                        numeric_props = []
                        for prop in properties:
                            value = self.graph.value(entity, self.schema[prop])
                            if value:
                                try:
                                    float(str(value))
                                    numeric_props.append(prop)
                                except:
                                    pass
                        
                        if not numeric_props:
                            continue
                        
                        kwargs['sum_property'] = random.choice(numeric_props)
                
                elif 'Structural Pattern' in template.subcategory:
                    # Find relationship properties
                    relationships = []
                    for prop in properties:
                        # Check if this property has multiple values (list-like)
                        values = list(self.graph.objects(entity, self.schema[prop]))
                        if len(values) > 0:
                            relationships.append(prop)
                    
                    if not relationships:
                        continue
                    
                    relationship = random.choice(relationships)
                    kwargs['relationship'] = relationship
                    
                    if 'exactly' in template.question_format.lower():
                        # Get actual count to use as target
                        actual_count = len(list(self.graph.objects(entity, self.schema[relationship])))
                        kwargs['target_count'] = random.choice([1, 2, 3, actual_count])
                
                # Generate the question
                question = template.generate(
                    self.graph, 
                    self.schema, 
                    self.schema_discovery.entities_by_type, 
                    **kwargs
                )
                
                if question:
                    return question
                    
            except Exception as e:
                continue
        
        return None
    
    def generate_questions(self, target_count: int = 100, generation_multiplier: float = 2.5):
        """Generate questions using templates."""
        print(f"\nGenerating {int(target_count * generation_multiplier)} questions (target: {target_count})...")
        
        all_questions = []
        attempts_per_template = int((target_count * generation_multiplier) / len(self.templates)) + 1
        
        for template in self.templates:
            print(f"  Generating from template: {template.category} - {template.subcategory}...", end='')
            template_questions = []
            
            for _ in range(attempts_per_template):
                question = self._generate_from_template(template)
                if question and question not in template_questions:
                    template_questions.append(question)
            
            all_questions.extend(template_questions)
            print(f" {len(template_questions)} generated")
        
        print(f"\nGenerated {len(all_questions)} total questions")
        
        # Apply difficulty filter
        print(f"Filtering to {target_count} questions with difficulty distribution...")
        filtered_questions = self._filter_by_difficulty(all_questions, target_count)
        
        # Shuffle
        random.shuffle(filtered_questions)
        
        print(f"Final count: {len(filtered_questions)} questions")
        return filtered_questions
    
    def _filter_by_difficulty(self, questions: List[Dict], target_count: int):
        """Filter questions to match difficulty distribution."""
        if not questions:
            return []
        
        # Separate by difficulty
        by_difficulty = {'Easy': [], 'Medium': [], 'Hard': []}
        for q in questions:
            difficulty = q.get('difficulty', 'Medium')
            if difficulty in by_difficulty:
                by_difficulty[difficulty].append(q)
        
        print(f"  Available: {len(by_difficulty['Easy'])} Easy, {len(by_difficulty['Medium'])} Medium, {len(by_difficulty['Hard'])} Hard")
        
        # Calculate targets
        easy_target = int(target_count * self.difficulty_distribution['easy'] / 100)
        medium_target = int(target_count * self.difficulty_distribution['medium'] / 100)
        hard_target = target_count - easy_target - medium_target
        
        print(f"  Target: {easy_target} Easy, {medium_target} Medium, {hard_target} Hard")
        
        # Select from each pool
        selected = []
        random.shuffle(by_difficulty['Easy'])
        random.shuffle(by_difficulty['Medium'])
        random.shuffle(by_difficulty['Hard'])
        
        selected.extend(by_difficulty['Easy'][:easy_target])
        selected.extend(by_difficulty['Medium'][:medium_target])
        selected.extend(by_difficulty['Hard'][:hard_target])
        
        # Fill gaps if needed
        if len(selected) < target_count:
            remaining_needed = target_count - len(selected)
            available = [q for q in questions if q not in selected]
            random.shuffle(available)
            selected.extend(available[:remaining_needed])
            print(f"  Added {min(remaining_needed, len(available))} additional questions to reach target")
        
        return selected[:target_count]


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Abstract question generator for RDF data benchmarking',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('turtle_file', help='Path to the turtle (.ttl) file')
    parser.add_argument('output_csv', nargs='?', default='questions.csv',
                       help='Output CSV file (default: questions.csv)')
    parser.add_argument('num_questions', nargs='?', type=int, default=100,
                       help='Number of questions to generate (default: 100)')
    parser.add_argument('--difficulty', type=str, default='33,34,33',
                       help='Difficulty distribution as "easy,medium,hard" percentages (default: 33,34,33)')
    
    args = parser.parse_args()
    
    # Parse difficulty distribution
    try:
        easy, medium, hard = map(float, args.difficulty.split(','))
        difficulty_dist = {'easy': easy, 'medium': medium, 'hard': hard}
    except ValueError:
        print("Error: --difficulty must be in format 'easy,medium,hard' (e.g., '50,30,20')")
        sys.exit(1)
    
    # Check file exists
    try:
        with open(args.turtle_file, 'r') as f:
            pass
    except FileNotFoundError:
        print(f"Error: File '{args.turtle_file}' not found.")
        sys.exit(1)
    
    print("=" * 80)
    print(f"Abstract Question Generator")
    print("=" * 80)
    
    try:
        # Generate questions
        generator = AbstractQuestionGenerator(args.turtle_file, difficulty_dist)
        questions = generator.generate_questions(target_count=args.num_questions)
        
        # Write to CSV
        with open(args.output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['category', 'subcategory', 'difficulty', 'question', 'answer', 'query_type']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for q in questions:
                writer.writerow({
                    'category': q.get('category', ''),
                    'subcategory': q.get('subcategory', ''),
                    'difficulty': q.get('difficulty', ''),
                    'question': q['question'],
                    'answer': json.dumps(q['answer']),
                    'query_type': q.get('query_type', '')
                })
        
        print("\n" + "=" * 80)
        print(f"Successfully generated {len(questions)} questions")
        print(f"Output saved to: {args.output_csv}")
        print("=" * 80)
        
        # Display summaries
        print("\nQuestion Summary by Category:")
        category_counts = defaultdict(int)
        for q in questions:
            category_counts[q['category']] += 1
        for category, count in sorted(category_counts.items()):
            print(f"  {category}: {count} questions")
        
        print("\nQuestion Summary by Difficulty:")
        difficulty_counts = defaultdict(int)
        for q in questions:
            difficulty_counts[q.get('difficulty', 'Unknown')] += 1
        for difficulty, count in sorted(difficulty_counts.items()):
            print(f"  {difficulty}: {count} questions")
        
        # Verify distribution
        total_q = len(questions)
        if total_q > 0:
            actual_easy = (difficulty_counts.get('Easy', 0) / total_q) * 100
            actual_medium = (difficulty_counts.get('Medium', 0) / total_q) * 100
            actual_hard = (difficulty_counts.get('Hard', 0) / total_q) * 100
            print(f"\nActual Distribution: {actual_easy:.1f}% Easy, {actual_medium:.1f}% Medium, {actual_hard:.1f}% Hard")
        
        # Show samples
        print("\n" + "=" * 80)
        print("Sample Questions:")
        print("=" * 80)
        for q in questions[:5]:
            print(f"\n[{q['category']} - {q.get('subcategory', 'N/A')} - {q.get('difficulty', 'N/A')}]")
            print(f"Q: {q['question']}")
            ans_str = str(q['answer'])
            if len(ans_str) > 100:
                ans_str = ans_str[:100] + "..."
            print(f"A: {ans_str}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()