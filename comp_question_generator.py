"""
Comprehensive Question Generator for Serialization Format Performance Benchmarking

This script generates questions across 7 categories to test different serialization formats:
1. Property Search (simple and nested)
2. Depth-First Search (chain traversals)
3. Breadth-First Search (same-level queries)
4. Mathematical (aggregations and calculations)
5. Filtering (simple, compound, pattern-based)
6. Aggregation (count, group by)
7. Pattern Matching (structural and temporal)

Usage:
    python comprehensive_question_generator.py <turtle_file> [output_csv] [num_questions] [--difficulty DIST]
    
Examples:
    # Default: balanced distribution
    python comprehensive_question_generator.py data_schema.ttl benchmark_questions.csv 100
    
    # 50% easy, 30% medium, 20% hard
    python comprehensive_question_generator.py data_schema.ttl output.csv 100 --difficulty 50,30,20
    
    # Only easy questions
    python comprehensive_question_generator.py data_schema.ttl output.csv 100 --difficulty 100,0,0
    
    # Challenging dataset: 20% easy, 30% medium, 50% hard
    python comprehensive_question_generator.py data_schema.ttl output.csv 100 --difficulty 20,30,50
"""

import rdflib
from rdflib import Graph, Namespace, RDF, URIRef
from collections import defaultdict, deque
import random
import csv
import sys
import json
import re
from datetime import datetime

class ComprehensiveQuestionGenerator:
    def __init__(self, turtle_file, difficulty_distribution=None):
        """
        Initialize with a Turtle format RDF file using schema.org vocabulary.
        
        Args:
            turtle_file: Path to the turtle file
            difficulty_distribution: Dict with 'easy', 'medium', 'hard' percentages (must sum to 100)
                                    Default: {'easy': 33, 'medium': 34, 'hard': 33}
        """
        print(f"Loading RDF graph from {turtle_file}...")
        self.graph = Graph()
        self.graph.parse(turtle_file, format='turtle')
        
        # Set difficulty distribution
        if difficulty_distribution is None:
            self.difficulty_distribution = {'easy': 33, 'medium': 34, 'hard': 33}
        else:
            # Validate distribution
            total = sum(difficulty_distribution.values())
            if abs(total - 100) > 0.1:
                raise ValueError(f"Difficulty percentages must sum to 100, got {total}")
            self.difficulty_distribution = difficulty_distribution
        
        print(f"Difficulty distribution: Easy {self.difficulty_distribution['easy']}%, "
              f"Medium {self.difficulty_distribution['medium']}%, "
              f"Hard {self.difficulty_distribution['hard']}%")
        
        # Define namespaces
        self.schema = Namespace("http://schema.org/")
        self.ex = Namespace("http://example.org/")
        
        # Build graph structure
        self.nodes = set()
        self.edges = defaultdict(list)
        self._build_graph_structure()
        
        # Cache entities by type
        self.persons = []
        self.organizations = []
        self.accounts = []
        self.orders = []
        self.order_items = []
        
        # Cache for specific property values
        self.order_statuses = set()
        self.industries = set()
        self.countries = set()
        self.bank_names = set()
        self.account_types = set()
        
        # Discover and cache entities
        self._discover_entities()
        
        print(f"\nDiscovered Entities:")
        print(f"  {len(self.persons)} persons")
        print(f"  {len(self.organizations)} organizations")
        print(f"  {len(self.accounts)} accounts")
        print(f"  {len(self.orders)} orders")
        print(f"  {len(self.order_items)} order items")
        print(f"  {len(self.order_statuses)} unique order statuses")
        print(f"  {len(self.industries)} unique industries")
        print(f"  {len(self.countries)} unique countries")
        print(f"  {len(self.bank_names)} unique banks")
        print(f"  {len(self.account_types)} unique account types\n")
    
    def _build_graph_structure(self):
        """Build an adjacency list from the RDF graph."""
        for s, p, o in self.graph:
            s_str = str(s)
            p_str = str(p)
            o_str = str(o)
            
            self.nodes.add(s_str)
            self.nodes.add(o_str)
            self.edges[s_str].append((p_str, o_str))
    
    def _simplify_uri(self, uri):
        """Simplify URIs for readable output."""
        uri_str = str(uri)
        if '#' in uri_str:
            return uri_str.split('#')[-1]
        elif '/' in uri_str:
            return uri_str.split('/')[-1]
        return uri_str
    
    def _get_property(self, subject, predicate):
        """Get a single property value from schema.org namespace."""
        value = self.graph.value(subject, self.schema[predicate])
        return str(value) if value else None
    
    def _get_property_list(self, subject, predicate):
        """Get all property values as a list."""
        return [str(o) for o in self.graph.objects(subject, self.schema[predicate])]
    
    def _discover_entities(self):
        """Discover all entities by type."""
        # Find persons
        for person in self.graph.subjects(RDF.type, self.schema.Person):
            self.persons.append(person)
            country = self._get_property(person, 'addressCountry')
            if country:
                self.countries.add(country)
        
        # Find organizations
        for org in self.graph.subjects(RDF.type, self.schema.Organization):
            self.organizations.append(org)
            industry = self._get_property(org, 'industry')
            if industry:
                self.industries.add(industry)
            country = self._get_property(org, 'addressCountry')
            if country:
                self.countries.add(country)
        
        # Find accounts (BankAccount type)
        for account in self.graph.subjects(RDF.type, self.schema.BankAccount):
            self.accounts.append(account)
            bank = self._get_property(account, 'bankName')
            if bank:
                self.bank_names.add(bank)
            acc_type = self._get_property(account, 'accountType')
            if acc_type:
                self.account_types.add(acc_type)
        
        # Find orders
        for order in self.graph.subjects(RDF.type, self.schema.Order):
            self.orders.append(order)
            status = self._get_property(order, 'orderStatus')
            if status:
                self.order_statuses.add(status)
        
        # Find order items
        for item in self.graph.subjects(RDF.type, self.schema.OrderItem):
            self.order_items.append(item)
    
    # ===== 1. PROPERTY SEARCH QUESTIONS =====
    
    def generate_property_search_questions(self, count=15):
        """Generate simple and nested property search questions."""
        questions = []
        max_attempts = count * 10  # Try 10x the count to ensure we get enough
        attempts = 0
        
        # Target distribution within property search
        target_simple = int(count * 0.33)
        target_multi = int(count * 0.33)
        target_nested = count - target_simple - target_multi
        
        # Simple property retrieval
        simple_questions = []
        while len(simple_questions) < target_simple and attempts < max_attempts:
            attempts += 1
            entity_type = random.choice(['person', 'account', 'order', 'org'])
            
            if entity_type == 'person' and self.persons:
                person = random.choice(self.persons)
                person_id = self._simplify_uri(person)
                prop = random.choice(['email', 'telephone', 'taxID', 'streetAddress', 'addressCountry'])
                value = self._get_property(person, prop)
                if value:
                    q = {
                        'category': 'Property Search',
                        'subcategory': 'Simple Property',
                        'difficulty': 'Easy',
                        'question': f'What is the {prop} of {person_id}?',
                        'answer': value,
                        'query_type': 'single_property'
                    }
                    if q not in simple_questions:
                        simple_questions.append(q)
            
            elif entity_type == 'account' and self.accounts:
                account = random.choice(self.accounts)
                account_id = self._simplify_uri(account)
                prop = random.choice(['bankName', 'accountType', 'amount', 'name'])
                value = self._get_property(account, prop)
                if value:
                    q = {
                        'category': 'Property Search',
                        'subcategory': 'Simple Property',
                        'difficulty': 'Easy',
                        'question': f'What is the {prop} for account {account_id}?',
                        'answer': float(value) if prop == 'amount' else value,
                        'query_type': 'single_property'
                    }
                    if q not in simple_questions:
                        simple_questions.append(q)
            
            elif entity_type == 'order' and self.orders:
                order = random.choice(self.orders)
                order_id = self._simplify_uri(order)
                prop = random.choice(['orderStatus', 'orderNumber', 'totalPrice', 'orderDate'])
                value = self._get_property(order, prop)
                if value:
                    q = {
                        'category': 'Property Search',
                        'subcategory': 'Simple Property',
                        'difficulty': 'Easy',
                        'question': f'What is the {prop} of {order_id}?',
                        'answer': float(value) if prop == 'totalPrice' else value,
                        'query_type': 'single_property'
                    }
                    if q not in simple_questions:
                        simple_questions.append(q)
            
            elif entity_type == 'org' and self.organizations:
                org = random.choice(self.organizations)
                org_id = self._simplify_uri(org)
                prop = random.choice(['taxID', 'industry', 'name', 'email', 'telephone'])
                value = self._get_property(org, prop)
                if value:
                    q = {
                        'category': 'Property Search',
                        'subcategory': 'Simple Property',
                        'difficulty': 'Easy',
                        'question': f'What is the {prop} of organization {org_id}?',
                        'answer': value,
                        'query_type': 'single_property'
                    }
                    if q not in simple_questions:
                        simple_questions.append(q)
        
        questions.extend(simple_questions[:target_simple])
        
        # Multi-property retrieval
        multi_questions = []
        attempts = 0
        while len(multi_questions) < target_multi and attempts < max_attempts:
            attempts += 1
            entity_type = random.choice(['person', 'order', 'org', 'account'])
            
            if entity_type == 'person' and self.persons:
                person = random.choice(self.persons)
                person_id = self._simplify_uri(person)
                props = random.sample(['givenName', 'familyName', 'email', 'telephone', 'streetAddress'], 2)
                values = {prop: self._get_property(person, prop) for prop in props}
                if all(values.values()):
                    q = {
                        'category': 'Property Search',
                        'subcategory': 'Multi-Property',
                        'difficulty': 'Easy',
                        'question': f'What are the {" and ".join(props)} of {person_id}?',
                        'answer': values,
                        'query_type': 'multi_property'
                    }
                    if q not in multi_questions:
                        multi_questions.append(q)
            
            elif entity_type == 'order' and self.orders:
                order = random.choice(self.orders)
                order_id = self._simplify_uri(order)
                props = random.sample(['orderNumber', 'totalPrice', 'orderStatus', 'orderDate'], 2)
                values = {}
                for prop in props:
                    val = self._get_property(order, prop)
                    if val:
                        values[prop] = float(val) if prop == 'totalPrice' else val
                if len(values) == 2:
                    q = {
                        'category': 'Property Search',
                        'subcategory': 'Multi-Property',
                        'difficulty': 'Easy',
                        'question': f'What are the {" and ".join(props)} of {order_id}?',
                        'answer': values,
                        'query_type': 'multi_property'
                    }
                    if q not in multi_questions:
                        multi_questions.append(q)
            
            elif entity_type == 'org' and self.organizations:
                org = random.choice(self.organizations)
                org_id = self._simplify_uri(org)
                props = random.sample(['industry', 'addressCountry', 'name', 'email'], 2)
                values = {prop: self._get_property(org, prop) for prop in props}
                if all(values.values()):
                    q = {
                        'category': 'Property Search',
                        'subcategory': 'Multi-Property',
                        'difficulty': 'Easy',
                        'question': f'What are the {" and ".join(props)} of {org_id}?',
                        'answer': values,
                        'query_type': 'multi_property'
                    }
                    if q not in multi_questions:
                        multi_questions.append(q)
            
            elif entity_type == 'account' and self.accounts:
                account = random.choice(self.accounts)
                account_id = self._simplify_uri(account)
                props = random.sample(['accountType', 'amount', 'bankName', 'name'], 2)
                values = {}
                for prop in props:
                    val = self._get_property(account, prop)
                    if val:
                        values[prop] = float(val) if prop == 'amount' else val
                if len(values) == 2:
                    q = {
                        'category': 'Property Search',
                        'subcategory': 'Multi-Property',
                        'difficulty': 'Easy',
                        'question': f'What are the {" and ".join(props)} for {account_id}?',
                        'answer': values,
                        'query_type': 'multi_property'
                    }
                    if q not in multi_questions:
                        multi_questions.append(q)
        
        questions.extend(multi_questions[:target_multi])
        
        # Nested property access
        nested_questions = []
        attempts = 0
        while len(nested_questions) < target_nested and attempts < max_attempts:
            attempts += 1
            
            if self.orders:
                order = random.choice(self.orders)
                order_id = self._simplify_uri(order)
                
                # Try customer properties
                if random.random() < 0.5:
                    customer_uri = self.graph.value(order, self.schema.customer)
                    if customer_uri:
                        prop = random.choice(['email', 'taxID', 'telephone', 'givenName', 'familyName', 'addressCountry'])
                        value = self._get_property(customer_uri, prop)
                        if value:
                            q = {
                                'category': 'Property Search',
                                'subcategory': 'Nested Property',
                                'difficulty': 'Medium',
                                'question': f"What is the customer's {prop} for order {order_id}?",
                                'answer': value,
                                'query_type': 'nested_property'
                            }
                            if q not in nested_questions:
                                nested_questions.append(q)
                
                # Try seller properties
                elif random.random() < 0.5:
                    seller_uri = self.graph.value(order, self.schema.seller)
                    if seller_uri:
                        prop = random.choice(['industry', 'email', 'taxID', 'telephone', 'addressCountry', 'name'])
                        value = self._get_property(seller_uri, prop)
                        if value:
                            q = {
                                'category': 'Property Search',
                                'subcategory': 'Nested Property',
                                'difficulty': 'Medium',
                                'question': f"What is the seller's {prop} for order {order_id}?",
                                'answer': value,
                                'query_type': 'nested_property'
                            }
                            if q not in nested_questions:
                                nested_questions.append(q)
                
                # Try payment method properties
                else:
                    payment_uri = self.graph.value(order, self.schema.paymentMethod)
                    if payment_uri:
                        prop = random.choice(['bankName', 'accountType', 'amount', 'name'])
                        value = self._get_property(payment_uri, prop)
                        if value:
                            q = {
                                'category': 'Property Search',
                                'subcategory': 'Nested Property',
                                'difficulty': 'Medium',
                                'question': f"What is the payment method's {prop} for order {order_id}?",
                                'answer': float(value) if prop == 'amount' else value,
                                'query_type': 'nested_property'
                            }
                            if q not in nested_questions:
                                nested_questions.append(q)
        
        questions.extend(nested_questions[:target_nested])
        
        return questions[:count]
        
        if self.organizations:
            org = random.choice(self.organizations)
            org_id = self._simplify_uri(org)
            industry = self._get_property(org, 'industry')
            country = self._get_property(org, 'addressCountry')
            if industry and country:
                questions.append({
                    'category': 'Property Search',
                    'subcategory': 'Multi-Property',
                    'difficulty': 'Easy',
                    'question': f'What are the industry and addressCountry of {org_id}?',
                    'answer': {'industry': industry, 'addressCountry': country},
                    'query_type': 'multi_property'
                })
        
        if self.accounts:
            account = random.choice(self.accounts)
            account_id = self._simplify_uri(account)
            acc_type = self._get_property(account, 'accountType')
            amount = self._get_property(account, 'amount')
            if acc_type and amount:
                questions.append({
                    'category': 'Property Search',
                    'subcategory': 'Multi-Property',
                    'difficulty': 'Easy',
                    'question': f'What are the account type and amount for {account_id}?',
                    'answer': {'accountType': acc_type, 'amount': float(amount)},
                    'query_type': 'multi_property'
                })
        
        if self.persons:
            person = random.choice(self.persons)
            person_id = self._simplify_uri(person)
            address = self._get_property(person, 'streetAddress')
            email = self._get_property(person, 'email')
            if address and email:
                questions.append({
                    'category': 'Property Search',
                    'subcategory': 'Multi-Property',
                    'difficulty': 'Easy',
                    'question': f'What are the street address and email of {person_id}?',
                    'answer': {'streetAddress': address, 'email': email},
                    'query_type': 'multi_property'
                })
        
        # Nested property access (5 questions)
        if self.orders:
            order = random.choice(self.orders)
            order_id = self._simplify_uri(order)
            customer_uri = self.graph.value(order, self.schema.customer)
            if customer_uri:
                email = self._get_property(customer_uri, 'email')
                if email:
                    questions.append({
                        'category': 'Property Search',
                        'subcategory': 'Nested Property',
                        'difficulty': 'Medium',
                        'question': f"What is the customer's email address for order {order_id}?",
                        'answer': email,
                        'query_type': 'nested_property'
                    })
        
        if self.orders:
            order = random.choice(self.orders)
            order_id = self._simplify_uri(order)
            seller_uri = self.graph.value(order, self.schema.seller)
            if seller_uri:
                industry = self._get_property(seller_uri, 'industry')
                if industry:
                    questions.append({
                        'category': 'Property Search',
                        'subcategory': 'Nested Property',
                        'difficulty': 'Medium',
                        'question': f"What is the seller's industry for order {order_id}?",
                        'answer': industry,
                        'query_type': 'nested_property'
                    })
        
        if self.orders:
            order = random.choice(self.orders)
            order_id = self._simplify_uri(order)
            payment_uri = self.graph.value(order, self.schema.paymentMethod)
            if payment_uri:
                bank = self._get_property(payment_uri, 'bankName')
                if bank:
                    questions.append({
                        'category': 'Property Search',
                        'subcategory': 'Nested Property',
                        'difficulty': 'Medium',
                        'question': f"What is the payment method's bank name for order {order_id}?",
                        'answer': bank,
                        'query_type': 'nested_property'
                    })
        
        if self.orders:
            order = random.choice(self.orders)
            order_id = self._simplify_uri(order)
            customer_uri = self.graph.value(order, self.schema.customer)
            if customer_uri:
                tax_id = self._get_property(customer_uri, 'taxID')
                if tax_id:
                    questions.append({
                        'category': 'Property Search',
                        'subcategory': 'Nested Property',
                        'difficulty': 'Medium',
                        'question': f"What is the customer's tax ID for order {order_id}?",
                        'answer': tax_id,
                        'query_type': 'nested_property'
                    })
        
        if self.orders:
            order = random.choice(self.orders)
            order_id = self._simplify_uri(order)
            seller_uri = self.graph.value(order, self.schema.seller)
            if seller_uri:
                telephone = self._get_property(seller_uri, 'telephone')
                if telephone:
                    questions.append({
                        'category': 'Property Search',
                        'subcategory': 'Nested Property',
                        'difficulty': 'Medium',
                        'question': f"What is the seller's telephone number for order {order_id}?",
                        'answer': telephone,
                        'query_type': 'nested_property'
                    })
        
        return questions[:count]
    
    # ===== 2. DEPTH-FIRST SEARCH QUESTIONS =====
    
    def generate_dfs_questions(self, count=15):
        """Generate depth-first search / chain traversal questions."""
        questions = []
        
        # Chain traversal questions
        for _ in range(5):
            if self.orders:
                order = random.choice(self.orders)
                order_id = self._simplify_uri(order)
                seller_uri = self.graph.value(order, self.schema.seller)
                if seller_uri:
                    industry = self._get_property(seller_uri, 'industry')
                    if industry:
                        questions.append({
                            'category': 'Depth-First Search',
                            'subcategory': 'Chain Traversal',
                            'difficulty': 'Medium',
                            'question': f'Follow the path: {order_id} → seller → industry. What is the value?',
                            'answer': industry,
                            'query_type': 'chain_traversal',
                            'hops': 2
                        })
                        break
        
        for _ in range(5):
            if self.orders:
                order = random.choice(self.orders)
                order_id = self._simplify_uri(order)
                customer_uri = self.graph.value(order, self.schema.customer)
                if customer_uri:
                    country = self._get_property(customer_uri, 'addressCountry')
                    if country:
                        questions.append({
                            'category': 'Depth-First Search',
                            'subcategory': 'Chain Traversal',
                            'difficulty': 'Medium',
                            'question': f'Follow the path: {order_id} → customer → addressCountry. What is the value?',
                            'answer': country,
                            'query_type': 'chain_traversal',
                            'hops': 2
                        })
                        break
        
        for _ in range(5):
            if self.orders:
                order = random.choice(self.orders)
                order_id = self._simplify_uri(order)
                payment_uri = self.graph.value(order, self.schema.paymentMethod)
                if payment_uri:
                    name = self._get_property(payment_uri, 'name')
                    if name:
                        questions.append({
                            'category': 'Depth-First Search',
                            'subcategory': 'Chain Traversal',
                            'difficulty': 'Medium',
                            'question': f'Follow the path: {order_id} → paymentMethod → name. What is the value?',
                            'answer': name,
                            'query_type': 'chain_traversal',
                            'hops': 2
                        })
                        break
        
        for _ in range(5):
            if self.orders:
                order = random.choice(self.orders)
                order_id = self._simplify_uri(order)
                seller_uri = self.graph.value(order, self.schema.seller)
                if seller_uri:
                    tax_id = self._get_property(seller_uri, 'taxID')
                    if tax_id:
                        questions.append({
                            'category': 'Depth-First Search',
                            'subcategory': 'Chain Traversal',
                            'difficulty': 'Medium',
                            'question': f'Follow the path: {order_id} → seller → taxID. What is the value?',
                            'answer': tax_id,
                            'query_type': 'chain_traversal',
                            'hops': 2
                        })
                        break
        
        for _ in range(5):
            if self.orders:
                order = random.choice(self.orders)
                order_id = self._simplify_uri(order)
                customer_uri = self.graph.value(order, self.schema.customer)
                if customer_uri:
                    family_name = self._get_property(customer_uri, 'familyName')
                    if family_name:
                        questions.append({
                            'category': 'Depth-First Search',
                            'subcategory': 'Chain Traversal',
                            'difficulty': 'Medium',
                            'question': f'Follow the path: {order_id} → customer → familyName. What is the value?',
                            'answer': family_name,
                            'query_type': 'chain_traversal',
                            'hops': 2
                        })
                        break
        
        # Deep relationship traversal (5 questions)
        for _ in range(5):
            if self.orders:
                order = random.choice(self.orders)
                order_id = self._simplify_uri(order)
                seller_uri = self.graph.value(order, self.schema.seller)
                if seller_uri:
                    street_address = self._get_property(seller_uri, 'streetAddress')
                    if street_address:
                        questions.append({
                            'category': 'Depth-First Search',
                            'subcategory': 'Deep Relationship',
                            'difficulty': 'Medium',
                            'question': f'Starting from order {order_id}, traverse to the seller, then get the seller\'s street address.',
                            'answer': street_address,
                            'query_type': 'deep_traversal',
                            'hops': 2
                        })
                        break
        
        for _ in range(5):
            if self.orders:
                order = random.choice(self.orders)
                order_id = self._simplify_uri(order)
                payment_uri = self.graph.value(order, self.schema.paymentMethod)
                if payment_uri:
                    acc_type = self._get_property(payment_uri, 'accountType')
                    if acc_type:
                        questions.append({
                            'category': 'Depth-First Search',
                            'subcategory': 'Deep Relationship',
                            'difficulty': 'Medium',
                            'question': f'Starting from order {order_id}, get the payment method\'s account type.',
                            'answer': acc_type,
                            'query_type': 'deep_traversal',
                            'hops': 2
                        })
                        break
        
        for _ in range(5):
            if self.orders:
                order = random.choice(self.orders)
                order_id = self._simplify_uri(order)
                items = self._get_property_list(order, 'orderedItem')
                if items:
                    questions.append({
                        'category': 'Depth-First Search',
                        'subcategory': 'Deep Relationship',
                        'difficulty': 'Medium',
                        'question': f'Starting from order {order_id}, get the total number of ordered items.',
                        'answer': len(items),
                        'query_type': 'deep_traversal',
                        'hops': 1
                    })
                    break
        
        for _ in range(5):
            if self.orders:
                order = random.choice(self.orders)
                order_id = self._simplify_uri(order)
                customer_uri = self.graph.value(order, self.schema.customer)
                if customer_uri:
                    telephone = self._get_property(customer_uri, 'telephone')
                    if telephone:
                        questions.append({
                            'category': 'Depth-First Search',
                            'subcategory': 'Deep Relationship',
                            'difficulty': 'Medium',
                            'question': f'Starting from order {order_id}, get the customer\'s telephone number.',
                            'answer': telephone,
                            'query_type': 'deep_traversal',
                            'hops': 2
                        })
                        break
        
        # Multi-hop queries (5 questions)
        for _ in range(5):
            if self.orders:
                order = random.choice(self.orders)
                order_id = self._simplify_uri(order)
                customer_uri = self.graph.value(order, self.schema.customer)
                if customer_uri:
                    given_name = self._get_property(customer_uri, 'givenName')
                    if given_name:
                        questions.append({
                            'category': 'Depth-First Search',
                            'subcategory': 'Multi-Hop',
                            'difficulty': 'Medium',
                            'question': f'What is the given name of the customer who placed order {order_id}?',
                            'answer': given_name,
                            'query_type': 'multi_hop',
                            'hops': 2
                        })
                        break
        
        for _ in range(5):
            if self.orders:
                order = random.choice(self.orders)
                order_id = self._simplify_uri(order)
                seller_uri = self.graph.value(order, self.schema.seller)
                if seller_uri:
                    country = self._get_property(seller_uri, 'addressCountry')
                    if country:
                        questions.append({
                            'category': 'Depth-First Search',
                            'subcategory': 'Multi-Hop',
                            'difficulty': 'Medium',
                            'question': f'What country is the seller located in for order {order_id}?',
                            'answer': country,
                            'query_type': 'multi_hop',
                            'hops': 2
                        })
                        break
        
        for _ in range(5):
            if self.orders:
                order = random.choice(self.orders)
                order_id = self._simplify_uri(order)
                seller_uri = self.graph.value(order, self.schema.seller)
                if seller_uri:
                    email = self._get_property(seller_uri, 'email')
                    if email:
                        questions.append({
                            'category': 'Depth-First Search',
                            'subcategory': 'Multi-Hop',
                            'difficulty': 'Medium',
                            'question': f'What is the email of the organization that sold items in order {order_id}?',
                            'answer': email,
                            'query_type': 'multi_hop',
                            'hops': 2
                        })
                        break
        
        for _ in range(5):
            if self.orders:
                order = random.choice(self.orders)
                order_id = self._simplify_uri(order)
                payment_uri = self.graph.value(order, self.schema.paymentMethod)
                if payment_uri:
                    amount = self._get_property(payment_uri, 'amount')
                    if amount:
                        questions.append({
                            'category': 'Depth-First Search',
                            'subcategory': 'Multi-Hop',
                            'difficulty': 'Medium',
                            'question': f'What is the account amount for the payment method used in order {order_id}?',
                            'answer': float(amount),
                            'query_type': 'multi_hop',
                            'hops': 2
                        })
                        break
        
        for _ in range(5):
            if self.orders:
                order = random.choice(self.orders)
                order_id = self._simplify_uri(order)
                seller_uri = self.graph.value(order, self.schema.seller)
                if seller_uri:
                    url = self._get_property(seller_uri, 'url')
                    if url:
                        questions.append({
                            'category': 'Depth-First Search',
                            'subcategory': 'Multi-Hop',
                            'difficulty': 'Medium',
                            'question': f'What is the URL of the seller organization for order {order_id}?',
                            'answer': url,
                            'query_type': 'multi_hop',
                            'hops': 2
                        })
                        break
        
        return questions[:count]
    
    # ===== 3. BREADTH-FIRST SEARCH QUESTIONS =====
    
    def generate_bfs_questions(self, count=15):
        """Generate breadth-first search / same-level entity questions."""
        questions = []
        
        # Same-level entity collection (5 questions)
        all_emails = [self._get_property(p, 'email') for p in self.persons]
        all_emails = [e for e in all_emails if e]
        if all_emails:
            questions.append({
                'category': 'Breadth-First Search',
                'subcategory': 'Same-Level Collection',
                'difficulty': 'Easy',
                'question': 'List all email addresses of persons in the dataset.',
                'answer': sorted(all_emails),
                'query_type': 'collection'
            })
        
        all_order_nums = [self._get_property(o, 'orderNumber') for o in self.orders]
        all_order_nums = [n for n in all_order_nums if n]
        if all_order_nums:
            questions.append({
                'category': 'Breadth-First Search',
                'subcategory': 'Same-Level Collection',
                'difficulty': 'Easy',
                'question': 'List all order numbers in the dataset.',
                'answer': sorted(all_order_nums),
                'query_type': 'collection'
            })
        
        all_org_names = [self._get_property(o, 'name') for o in self.organizations]
        all_org_names = [n for n in all_org_names if n]
        if all_org_names:
            questions.append({
                'category': 'Breadth-First Search',
                'subcategory': 'Same-Level Collection',
                'difficulty': 'Easy',
                'question': 'List all organization names in the dataset.',
                'answer': sorted(all_org_names),
                'query_type': 'collection'
            })
        
        all_account_names = [self._get_property(a, 'name') for a in self.accounts]
        all_account_names = [n for n in all_account_names if n]
        if all_account_names:
            questions.append({
                'category': 'Breadth-First Search',
                'subcategory': 'Same-Level Collection',
                'difficulty': 'Easy',
                'question': 'List all account names in the dataset.',
                'answer': sorted(all_account_names),
                'query_type': 'collection'
            })
        
        if self.order_statuses:
            questions.append({
                'category': 'Breadth-First Search',
                'subcategory': 'Same-Level Collection',
                'difficulty': 'Easy',
                'question': 'List all unique order statuses in the dataset.',
                'answer': sorted(list(self.order_statuses)),
                'query_type': 'collection'
            })
        
        # Sibling entity queries (5 questions)
        if self.persons:
            person = random.choice(self.persons)
            person_id = self._simplify_uri(person)
            person_orders = []
            for order in self.orders:
                customer_uri = self.graph.value(order, self.schema.customer)
                if customer_uri == person:
                    order_num = self._get_property(order, 'orderNumber')
                    if order_num:
                        person_orders.append(order_num)
            
            if person_orders:
                questions.append({
                    'category': 'Breadth-First Search',
                    'subcategory': 'Sibling Entities',
                    'difficulty': 'Medium',
                    'question': f'List all order numbers for {person_id}.',
                    'answer': sorted(person_orders),
                    'query_type': 'sibling_query'
                })
        
        if self.orders:
            order = random.choice(self.orders)
            order_id = self._simplify_uri(order)
            items = self._get_property_list(order, 'orderedItem')
            if items:
                item_ids = [self._simplify_uri(i) for i in items]
                questions.append({
                    'category': 'Breadth-First Search',
                    'subcategory': 'Sibling Entities',
                    'difficulty': 'Medium',
                    'question': f'List all ordered items in order {order_id}.',
                    'answer': sorted(item_ids),
                    'query_type': 'sibling_query'
                })
        
        if self.persons:
            person = random.choice(self.persons)
            person_id = self._simplify_uri(person)
            order_count = 0
            for order in self.orders:
                customer_uri = self.graph.value(order, self.schema.customer)
                if customer_uri == person:
                    order_count += 1
            
            if order_count > 0:
                questions.append({
                    'category': 'Breadth-First Search',
                    'subcategory': 'Sibling Entities',
                    'difficulty': 'Medium',
                    'question': f'How many orders does {person_id} have in total?',
                    'answer': order_count,
                    'query_type': 'sibling_count'
                })
        
        if self.orders:
            order = random.choice(self.orders)
            order_id = self._simplify_uri(order)
            items = self._get_property_list(order, 'orderedItem')
            if items:
                questions.append({
                    'category': 'Breadth-First Search',
                    'subcategory': 'Sibling Entities',
                    'difficulty': 'Medium',
                    'question': f'How many items are in order {order_id}?',
                    'answer': len(items),
                    'query_type': 'sibling_count'
                })
        
        # Cross-entity same-level queries (5 questions)
        all_person_tax_ids = [self._get_property(p, 'taxID') for p in self.persons]
        all_person_tax_ids = [t for t in all_person_tax_ids if t]
        if all_person_tax_ids:
            questions.append({
                'category': 'Breadth-First Search',
                'subcategory': 'Cross-Entity',
                'difficulty': 'Easy',
                'question': 'List all tax IDs for all persons.',
                'answer': sorted(all_person_tax_ids),
                'query_type': 'cross_entity'
            })
        
        if self.bank_names:
            questions.append({
                'category': 'Breadth-First Search',
                'subcategory': 'Cross-Entity',
                'difficulty': 'Easy',
                'question': 'List all bank names for all accounts.',
                'answer': sorted(list(self.bank_names)),
                'query_type': 'cross_entity'
            })
        
        if self.industries:
            questions.append({
                'category': 'Breadth-First Search',
                'subcategory': 'Cross-Entity',
                'difficulty': 'Easy',
                'question': 'List all industries represented by organizations.',
                'answer': sorted(list(self.industries)),
                'query_type': 'cross_entity'
            })
        
        person_countries = set()
        for person in self.persons:
            country = self._get_property(person, 'addressCountry')
            if country:
                person_countries.add(country)
        if person_countries:
            questions.append({
                'category': 'Breadth-First Search',
                'subcategory': 'Cross-Entity',
                'difficulty': 'Easy',
                'question': 'List all countries where persons reside.',
                'answer': sorted(list(person_countries)),
                'query_type': 'cross_entity'
            })
        
        org_countries = set()
        for org in self.organizations:
            country = self._get_property(org, 'addressCountry')
            if country:
                org_countries.add(country)
        if org_countries:
            questions.append({
                'category': 'Breadth-First Search',
                'subcategory': 'Cross-Entity',
                'difficulty': 'Easy',
                'question': 'List all countries where organizations are located.',
                'answer': sorted(list(org_countries)),
                'query_type': 'cross_entity'
            })
        
        return questions[:count]
    
    # ===== 4. MATHEMATICAL QUESTIONS =====
    
    def generate_mathematical_questions(self, count=15):
        """Generate mathematical aggregation and calculation questions."""
        questions = []
        
        # Basic aggregations (5 questions)
        total_price_sum = sum([float(self._get_property(o, 'totalPrice') or 0) for o in self.orders])
        if total_price_sum > 0:
            questions.append({
                'category': 'Mathematical',
                'subcategory': 'Basic Aggregation',
                'difficulty': 'Easy',
                'question': 'What is the total price of all orders combined?',
                'answer': round(total_price_sum, 2),
                'query_type': 'sum'
            })
        
        order_prices = [float(self._get_property(o, 'totalPrice') or 0) for o in self.orders]
        order_prices = [p for p in order_prices if p > 0]
        if order_prices:
            avg_price = sum(order_prices) / len(order_prices)
            questions.append({
                'category': 'Mathematical',
                'subcategory': 'Basic Aggregation',
                'difficulty': 'Easy',
                'question': 'What is the average total price of all orders?',
                'answer': round(avg_price, 2),
                'query_type': 'average'
            })
        
        if order_prices:
            max_price = max(order_prices)
            questions.append({
                'category': 'Mathematical',
                'subcategory': 'Basic Aggregation',
                'difficulty': 'Easy',
                'question': 'What is the maximum order total price in the dataset?',
                'answer': round(max_price, 2),
                'query_type': 'max'
            })
        
        if order_prices:
            min_price = min(order_prices)
            questions.append({
                'category': 'Mathematical',
                'subcategory': 'Basic Aggregation',
                'difficulty': 'Easy',
                'question': 'What is the minimum order total price in the dataset?',
                'answer': round(min_price, 2),
                'query_type': 'min'
            })
        
        account_amounts = [float(self._get_property(a, 'amount') or 0) for a in self.accounts]
        if account_amounts:
            total_accounts = sum(account_amounts)
            questions.append({
                'category': 'Mathematical',
                'subcategory': 'Basic Aggregation',
                'difficulty': 'Easy',
                'question': 'What is the sum of all account amounts?',
                'answer': round(total_accounts, 2),
                'query_type': 'sum'
            })
        
        # Filtered calculations (5 questions)
        if 'OrderDelivered' in self.order_statuses:
            delivered_total = 0
            for order in self.orders:
                status = self._get_property(order, 'orderStatus')
                if status == 'OrderDelivered':
                    price = float(self._get_property(order, 'totalPrice') or 0)
                    delivered_total += price
            
            if delivered_total > 0:
                questions.append({
                    'category': 'Mathematical',
                    'subcategory': 'Filtered Calculation',
                    'difficulty': 'Medium',
                    'question': 'What is the total value of all orders with status "OrderDelivered"?',
                    'answer': round(delivered_total, 2),
                    'query_type': 'filtered_sum'
                })
        
        if 'Personal Savings' in self.account_types:
            savings_accounts = []
            for account in self.accounts:
                acc_type = self._get_property(account, 'accountType')
                if acc_type == 'Personal Savings':
                    amount = float(self._get_property(account, 'amount') or 0)
                    savings_accounts.append(amount)
            
            if savings_accounts:
                avg_savings = sum(savings_accounts) / len(savings_accounts)
                questions.append({
                    'category': 'Mathematical',
                    'subcategory': 'Filtered Calculation',
                    'difficulty': 'Medium',
                    'question': 'What is the average account amount for accounts with type "Personal Savings"?',
                    'answer': round(avg_savings, 2),
                    'query_type': 'filtered_average'
                })
        
        if self.persons:
            person = random.choice(self.persons)
            person_id = self._simplify_uri(person)
            person_total = 0
            for order in self.orders:
                customer_uri = self.graph.value(order, self.schema.customer)
                if customer_uri == person:
                    price = float(self._get_property(order, 'totalPrice') or 0)
                    person_total += price
            
            if person_total > 0:
                questions.append({
                    'category': 'Mathematical',
                    'subcategory': 'Filtered Calculation',
                    'difficulty': 'Medium',
                    'question': f'What is the total price of all orders placed by {person_id}?',
                    'answer': round(person_total, 2),
                    'query_type': 'filtered_sum'
                })
        
        if self.organizations:
            org = random.choice(self.organizations)
            org_id = self._simplify_uri(org)
            org_total = 0
            for order in self.orders:
                seller_uri = self.graph.value(order, self.schema.seller)
                if seller_uri == org:
                    price = float(self._get_property(order, 'totalPrice') or 0)
                    org_total += price
            
            if org_total > 0:
                questions.append({
                    'category': 'Mathematical',
                    'subcategory': 'Filtered Calculation',
                    'difficulty': 'Medium',
                    'question': f'What is the sum of orders sold by {org_id}?',
                    'answer': round(org_total, 2),
                    'query_type': 'filtered_sum'
                })
        
        if 'OrderCancelled' in self.order_statuses:
            cancelled_orders = []
            for order in self.orders:
                status = self._get_property(order, 'orderStatus')
                if status == 'OrderCancelled':
                    price = float(self._get_property(order, 'totalPrice') or 0)
                    cancelled_orders.append(price)
            
            if cancelled_orders:
                avg_cancelled = sum(cancelled_orders) / len(cancelled_orders)
                questions.append({
                    'category': 'Mathematical',
                    'subcategory': 'Filtered Calculation',
                    'difficulty': 'Medium',
                    'question': 'What is the average order value for orders with status "OrderCancelled"?',
                    'answer': round(avg_cancelled, 2),
                    'query_type': 'filtered_average'
                })
        
        # Complex calculations (5 questions)
        orders_2025 = []
        for order in self.orders:
            date_str = self._get_property(order, 'orderDate')
            if date_str and '2025' in date_str:
                price = float(self._get_property(order, 'totalPrice') or 0)
                orders_2025.append(price)
        
        if orders_2025:
            total_2025 = sum(orders_2025)
            questions.append({
                'category': 'Mathematical',
                'subcategory': 'Complex Calculation',
                'difficulty': 'Hard',
                'question': 'What is the total value of all orders placed in 2025?',
                'answer': round(total_2025, 2),
                'query_type': 'temporal_aggregation'
            })
        
        if order_prices and len(self.persons) > 0:
            avg_per_customer = sum(order_prices) / len(self.persons)
            questions.append({
                'category': 'Mathematical',
                'subcategory': 'Complex Calculation',
                'difficulty': 'Hard',
                'question': 'Calculate the average order value per person (total order value divided by number of unique customers).',
                'answer': round(avg_per_customer, 2),
                'query_type': 'ratio'
            })
        
        if order_prices:
            price_range = max(order_prices) - min(order_prices)
            questions.append({
                'category': 'Mathematical',
                'subcategory': 'Complex Calculation',
                'difficulty': 'Medium',
                'question': 'What is the difference between the highest and lowest order total prices?',
                'answer': round(price_range, 2),
                'query_type': 'difference'
            })
        
        if total_price_sum > 0 and 'OrderDelivered' in self.order_statuses:
            delivered_total = 0
            for order in self.orders:
                status = self._get_property(order, 'orderStatus')
                if status == 'OrderDelivered':
                    price = float(self._get_property(order, 'totalPrice') or 0)
                    delivered_total += price
            
            percentage = (delivered_total / total_price_sum) * 100
            questions.append({
                'category': 'Mathematical',
                'subcategory': 'Complex Calculation',
                'difficulty': 'Hard',
                'question': 'What percentage of the total order value comes from orders with status "OrderDelivered"?',
                'answer': round(percentage, 2),
                'query_type': 'percentage'
            })
        
        # Orders with 3+ items
        total_3plus = 0
        for order in self.orders:
            items = self._get_property_list(order, 'orderedItem')
            if len(items) >= 3:
                price = float(self._get_property(order, 'totalPrice') or 0)
                total_3plus += price
        
        if total_3plus > 0:
            questions.append({
                'category': 'Mathematical',
                'subcategory': 'Complex Calculation',
                'difficulty': 'Hard',
                'question': 'What is the total value of orders that have 3 or more items?',
                'answer': round(total_3plus, 2),
                'query_type': 'conditional_sum'
            })
        
        return questions[:count]
    
    # ===== 5. FILTERING QUESTIONS =====
    
    def generate_filtering_questions(self, count=20):
        """Generate filtering questions with various complexity levels."""
        questions = []
        
        # Simple filters (5 questions)
        if 'OrderProcessing' in self.order_statuses:
            processing_orders = []
            for order in self.orders:
                status = self._get_property(order, 'orderStatus')
                if status == 'OrderProcessing':
                    order_id = self._simplify_uri(order)
                    processing_orders.append(order_id)
            
            if processing_orders:
                questions.append({
                    'category': 'Filtering',
                    'subcategory': 'Simple Filter',
                    'difficulty': 'Easy',
                    'question': 'Find all orders with status "OrderProcessing".',
                    'answer': sorted(processing_orders),
                    'query_type': 'simple_filter'
                })
        
        malta_persons = []
        for person in self.persons:
            country = self._get_property(person, 'addressCountry')
            if country == 'Malta':
                person_id = self._simplify_uri(person)
                malta_persons.append(person_id)
        
        if malta_persons:
            questions.append({
                'category': 'Filtering',
                'subcategory': 'Simple Filter',
                'difficulty': 'Easy',
                'question': 'Find all persons living in "Malta".',
                'answer': sorted(malta_persons),
                'query_type': 'simple_filter'
            })
        
        if 'Technology' in self.industries:
            tech_orgs = []
            for org in self.organizations:
                industry = self._get_property(org, 'industry')
                if industry == 'Technology':
                    org_id = self._simplify_uri(org)
                    tech_orgs.append(org_id)
            
            if tech_orgs:
                questions.append({
                    'category': 'Filtering',
                    'subcategory': 'Simple Filter',
                    'difficulty': 'Easy',
                    'question': 'Find all organizations in the "Technology" industry.',
                    'answer': sorted(tech_orgs),
                    'query_type': 'simple_filter'
                })
        
        if 'Business Checking' in self.account_types:
            business_accounts = []
            for account in self.accounts:
                acc_type = self._get_property(account, 'accountType')
                if acc_type == 'Business Checking':
                    account_id = self._simplify_uri(account)
                    business_accounts.append(account_id)
            
            if business_accounts:
                questions.append({
                    'category': 'Filtering',
                    'subcategory': 'Simple Filter',
                    'difficulty': 'Easy',
                    'question': 'Find all accounts with type "Business Checking".',
                    'answer': sorted(business_accounts),
                    'query_type': 'simple_filter'
                })
        
        high_value_orders = []
        for order in self.orders:
            price = float(self._get_property(order, 'totalPrice') or 0)
            if price > 2000:
                order_id = self._simplify_uri(order)
                high_value_orders.append(order_id)
        
        if high_value_orders:
            questions.append({
                'category': 'Filtering',
                'subcategory': 'Simple Filter',
                'difficulty': 'Easy',
                'question': 'Find all orders with total price greater than 2000.',
                'answer': sorted(high_value_orders),
                'query_type': 'simple_filter'
            })
        
        # Compound filters (5 questions)
        if 'OrderDelivered' in self.order_statuses:
            delivered_cheap = []
            for order in self.orders:
                status = self._get_property(order, 'orderStatus')
                price = float(self._get_property(order, 'totalPrice') or 0)
                if status == 'OrderDelivered' and price < 500:
                    order_id = self._simplify_uri(order)
                    delivered_cheap.append(order_id)
            
            if delivered_cheap:
                questions.append({
                    'category': 'Filtering',
                    'subcategory': 'Compound Filter',
                    'difficulty': 'Medium',
                    'question': 'Find all orders with status "OrderDelivered" AND total price less than 500.',
                    'answer': sorted(delivered_cheap),
                    'query_type': 'compound_filter'
                })
        
        panama_portugal_persons = []
        for person in self.persons:
            country = self._get_property(person, 'addressCountry')
            if country in ['Panama', 'Portugal']:
                person_id = self._simplify_uri(person)
                panama_portugal_persons.append(person_id)
        
        if panama_portugal_persons:
            questions.append({
                'category': 'Filtering',
                'subcategory': 'Compound Filter',
                'difficulty': 'Medium',
                'question': 'Find all persons with addressCountry "Panama" OR "Portugal".',
                'answer': sorted(panama_portugal_persons),
                'query_type': 'compound_filter'
            })
        
        if 'OrderReturned' in self.order_statuses:
            returned_after_june = []
            for order in self.orders:
                status = self._get_property(order, 'orderStatus')
                date_str = self._get_property(order, 'orderDate')
                if status == 'OrderReturned' and date_str:
                    try:
                        order_date = datetime.strptime(date_str, '%Y-%m-%d')
                        june_1_2025 = datetime(2025, 6, 1)
                        if order_date > june_1_2025:
                            order_id = self._simplify_uri(order)
                            returned_after_june.append(order_id)
                    except:
                        pass
            
            if returned_after_june:
                questions.append({
                    'category': 'Filtering',
                    'subcategory': 'Compound Filter',
                    'difficulty': 'Medium',
                    'question': 'Find all orders placed after June 1, 2025 AND with status "OrderReturned".',
                    'answer': sorted(returned_after_june),
                    'query_type': 'compound_filter'
                })
        
        large_business_accounts = []
        for account in self.accounts:
            amount = float(self._get_property(account, 'amount') or 0)
            acc_type = self._get_property(account, 'accountType')
            if amount > 400000 and acc_type and 'Business' in acc_type:
                account_id = self._simplify_uri(account)
                large_business_accounts.append(account_id)
        
        if large_business_accounts:
            questions.append({
                'category': 'Filtering',
                'subcategory': 'Compound Filter',
                'difficulty': 'Medium',
                'question': 'Find all accounts with amount greater than 400000 AND accountType containing "Business".',
                'answer': sorted(large_business_accounts),
                'query_type': 'compound_filter'
            })
        
        banking_healthcare_orgs = []
        for org in self.organizations:
            industry = self._get_property(org, 'industry')
            if industry in ['Banking', 'Healthcare']:
                org_id = self._simplify_uri(org)
                banking_healthcare_orgs.append(org_id)
        
        if banking_healthcare_orgs:
            questions.append({
                'category': 'Filtering',
                'subcategory': 'Compound Filter',
                'difficulty': 'Medium',
                'question': 'Find all organizations in "Banking" OR "Healthcare" industries.',
                'answer': sorted(banking_healthcare_orgs),
                'query_type': 'compound_filter'
            })
        
        # Pattern-based filters (5 questions)
        po_orders = []
        for order in self.orders:
            order_num = self._get_property(order, 'orderNumber')
            if order_num and order_num.startswith('PO-'):
                order_id = self._simplify_uri(order)
                po_orders.append(order_id)
        
        if po_orders:
            questions.append({
                'category': 'Filtering',
                'subcategory': 'Pattern Filter',
                'difficulty': 'Medium',
                'question': 'Find all orders with order numbers starting with "PO-".',
                'answer': sorted(po_orders),
                'query_type': 'pattern_filter'
            })
        
        org_emails = []
        for person in self.persons:
            email = self._get_property(person, 'email')
            if email and email.endswith('@example.org'):
                person_id = self._simplify_uri(person)
                org_emails.append(person_id)
        
        if org_emails:
            questions.append({
                'category': 'Filtering',
                'subcategory': 'Pattern Filter',
                'difficulty': 'Medium',
                'question': 'Find all persons with email addresses ending in "@example.org".',
                'answer': sorted(org_emails),
                'query_type': 'pattern_filter'
            })
        
        inv_orders = []
        for order in self.orders:
            order_num = self._get_property(order, 'orderNumber')
            if order_num and 'INV' in order_num:
                order_id = self._simplify_uri(order)
                inv_orders.append(order_id)
        
        if inv_orders:
            questions.append({
                'category': 'Filtering',
                'subcategory': 'Pattern Filter',
                'difficulty': 'Medium',
                'question': 'Find all orders with order numbers containing "INV".',
                'answer': sorted(inv_orders),
                'query_type': 'pattern_filter'
            })
        
        ext_phones = []
        for person in self.persons:
            phone = self._get_property(person, 'telephone')
            if phone and 'x' in phone:
                person_id = self._simplify_uri(person)
                ext_phones.append(person_id)
        
        if ext_phones:
            questions.append({
                'category': 'Filtering',
                'subcategory': 'Pattern Filter',
                'difficulty': 'Medium',
                'question': 'Find all telephone numbers containing extension "x".',
                'answer': sorted(ext_phones),
                'query_type': 'pattern_filter'
            })
        
        llc_orgs = []
        for org in self.organizations:
            name = self._get_property(org, 'name')
            if name and 'LLC' in name:
                org_id = self._simplify_uri(org)
                llc_orgs.append(org_id)
        
        if llc_orgs:
            questions.append({
                'category': 'Filtering',
                'subcategory': 'Pattern Filter',
                'difficulty': 'Medium',
                'question': 'Find all organizations with names containing "LLC".',
                'answer': sorted(llc_orgs),
                'query_type': 'pattern_filter'
            })
        
        # Relationship-based filters (5 questions)
        french_territory_orders = []
        for order in self.orders:
            customer_uri = self.graph.value(order, self.schema.customer)
            if customer_uri:
                country = self._get_property(customer_uri, 'addressCountry')
                if country == 'French Southern Territories':
                    order_id = self._simplify_uri(order)
                    french_territory_orders.append(order_id)
        
        if french_territory_orders:
            questions.append({
                'category': 'Filtering',
                'subcategory': 'Relationship Filter',
                'difficulty': 'Hard',
                'question': 'Find all orders placed by customers living in "French Southern Territories".',
                'answer': sorted(french_territory_orders),
                'query_type': 'relationship_filter'
            })
        
        if 'Retail' in self.industries:
            retail_orders = []
            for order in self.orders:
                seller_uri = self.graph.value(order, self.schema.seller)
                if seller_uri:
                    industry = self._get_property(seller_uri, 'industry')
                    if industry == 'Retail':
                        order_id = self._simplify_uri(order)
                        retail_orders.append(order_id)
            
            if retail_orders:
                questions.append({
                    'category': 'Filtering',
                    'subcategory': 'Relationship Filter',
                    'difficulty': 'Hard',
                    'question': 'Find all orders sold by organizations in the "Retail" industry.',
                    'answer': sorted(retail_orders),
                    'query_type': 'relationship_filter'
                })
        
        if 'Personal Savings' in self.account_types:
            savings_orders = []
            for order in self.orders:
                payment_uri = self.graph.value(order, self.schema.paymentMethod)
                if payment_uri:
                    acc_type = self._get_property(payment_uri, 'accountType')
                    if acc_type == 'Personal Savings':
                        order_id = self._simplify_uri(order)
                        savings_orders.append(order_id)
            
            if savings_orders:
                questions.append({
                    'category': 'Filtering',
                    'subcategory': 'Relationship Filter',
                    'difficulty': 'Hard',
                    'question': 'Find all orders paid for using accounts with type "Personal Savings".',
                    'answer': sorted(savings_orders),
                    'query_type': 'relationship_filter'
                })
        
        montenegro_orders = []
        for order in self.orders:
            seller_uri = self.graph.value(order, self.schema.seller)
            if seller_uri:
                country = self._get_property(seller_uri, 'addressCountry')
                if country == 'Montenegro':
                    order_id = self._simplify_uri(order)
                    montenegro_orders.append(order_id)
        
        if montenegro_orders:
            questions.append({
                'category': 'Filtering',
                'subcategory': 'Relationship Filter',
                'difficulty': 'Hard',
                'question': 'Find all orders with sellers located in "Montenegro".',
                'answer': sorted(montenegro_orders),
                'query_type': 'relationship_filter'
            })
        
        johnson_orders = []
        for order in self.orders:
            customer_uri = self.graph.value(order, self.schema.customer)
            if customer_uri:
                family_name = self._get_property(customer_uri, 'familyName')
                if family_name == 'Johnson':
                    order_id = self._simplify_uri(order)
                    johnson_orders.append(order_id)
        
        if johnson_orders:
            questions.append({
                'category': 'Filtering',
                'subcategory': 'Relationship Filter',
                'difficulty': 'Hard',
                'question': 'Find all orders where the customer\'s family name is "Johnson".',
                'answer': sorted(johnson_orders),
                'query_type': 'relationship_filter'
            })
        
        return questions[:count]
    
    # ===== 6. AGGREGATION QUESTIONS =====
    
    def generate_aggregation_questions(self, count=20):
        """Generate count and group-by aggregation questions."""
        questions = []
        
        # Count aggregations (5 questions)
        questions.append({
            'category': 'Aggregation',
            'subcategory': 'Count',
            'difficulty': 'Easy',
            'question': 'How many total orders are in the dataset?',
            'answer': len(self.orders),
            'query_type': 'count'
        })
        
        unique_customers = set()
        for order in self.orders:
            customer_uri = self.graph.value(order, self.schema.customer)
            if customer_uri:
                unique_customers.add(customer_uri)
        
        questions.append({
            'category': 'Aggregation',
            'subcategory': 'Count',
            'difficulty': 'Easy',
            'question': 'How many unique customers are there?',
            'answer': len(unique_customers),
            'query_type': 'count_distinct'
        })
        
        unique_sellers = set()
        for order in self.orders:
            seller_uri = self.graph.value(order, self.schema.seller)
            if seller_uri:
                unique_sellers.add(seller_uri)
        
        questions.append({
            'category': 'Aggregation',
            'subcategory': 'Count',
            'difficulty': 'Easy',
            'question': 'How many organizations are sellers?',
            'answer': len(unique_sellers),
            'query_type': 'count_distinct'
        })
        
        questions.append({
            'category': 'Aggregation',
            'subcategory': 'Count',
            'difficulty': 'Easy',
            'question': 'How many accounts are in the dataset?',
            'answer': len(self.accounts),
            'query_type': 'count'
        })
        
        if 'OrderReturned' in self.order_statuses:
            returned_count = 0
            for order in self.orders:
                status = self._get_property(order, 'orderStatus')
                if status == 'OrderReturned':
                    returned_count += 1
            
            questions.append({
                'category': 'Aggregation',
                'subcategory': 'Count',
                'difficulty': 'Easy',
                'question': 'Count the number of orders with status "OrderReturned".',
                'answer': returned_count,
                'query_type': 'filtered_count'
            })
        
        # Group by aggregations (10 questions)
        status_counts = defaultdict(int)
        for order in self.orders:
            status = self._get_property(order, 'orderStatus')
            if status:
                status_counts[status] += 1
        
        if status_counts:
            questions.append({
                'category': 'Aggregation',
                'subcategory': 'Group By',
                'difficulty': 'Medium',
                'question': 'Group orders by status and count how many orders are in each status category.',
                'answer': dict(status_counts),
                'query_type': 'group_by_count'
            })
        
        account_type_totals = defaultdict(float)
        for account in self.accounts:
            acc_type = self._get_property(account, 'accountType')
            amount = float(self._get_property(account, 'amount') or 0)
            if acc_type:
                account_type_totals[acc_type] += amount
        
        if account_type_totals:
            account_type_totals = {k: round(v, 2) for k, v in account_type_totals.items()}
            questions.append({
                'category': 'Aggregation',
                'subcategory': 'Group By',
                'difficulty': 'Medium',
                'question': 'Group accounts by account type and sum the total amount in each type.',
                'answer': dict(account_type_totals),
                'query_type': 'group_by_sum'
            })
        
        seller_totals = defaultdict(float)
        for order in self.orders:
            seller_uri = self.graph.value(order, self.schema.seller)
            if seller_uri:
                seller_id = self._simplify_uri(seller_uri)
                price = float(self._get_property(order, 'totalPrice') or 0)
                seller_totals[seller_id] += price
        
        if seller_totals:
            seller_totals = {k: round(v, 2) for k, v in seller_totals.items()}
            questions.append({
                'category': 'Aggregation',
                'subcategory': 'Group By',
                'difficulty': 'Medium',
                'question': 'Group orders by seller organization and calculate total sales per organization.',
                'answer': dict(seller_totals),
                'query_type': 'group_by_sum'
            })
        
        customer_orders = defaultdict(list)
        for order in self.orders:
            customer_uri = self.graph.value(order, self.schema.customer)
            if customer_uri:
                customer_id = self._simplify_uri(customer_uri)
                price = float(self._get_property(order, 'totalPrice') or 0)
                customer_orders[customer_id].append(price)
        
        customer_avgs = {k: round(sum(v) / len(v), 2) for k, v in customer_orders.items() if v}
        if customer_avgs:
            questions.append({
                'category': 'Aggregation',
                'subcategory': 'Group By',
                'difficulty': 'Medium',
                'question': 'Group orders by customer and calculate average order value per customer.',
                'answer': dict(customer_avgs),
                'query_type': 'group_by_average'
            })
        
        industry_counts = defaultdict(int)
        for org in self.organizations:
            industry = self._get_property(org, 'industry')
            if industry:
                industry_counts[industry] += 1
        
        if industry_counts:
            questions.append({
                'category': 'Aggregation',
                'subcategory': 'Group By',
                'difficulty': 'Easy',
                'question': 'Group organizations by industry and count how many organizations are in each industry.',
                'answer': dict(industry_counts),
                'query_type': 'group_by_count'
            })
        
        # Complex grouping (5 questions)
        monthly_revenue = defaultdict(float)
        for order in self.orders:
            date_str = self._get_property(order, 'orderDate')
            price = float(self._get_property(order, 'totalPrice') or 0)
            if date_str:
                try:
                    month_key = date_str[:7]  # YYYY-MM
                    monthly_revenue[month_key] += price
                except:
                    pass
        
        if monthly_revenue:
            monthly_revenue = {k: round(v, 2) for k, v in monthly_revenue.items()}
            questions.append({
                'category': 'Aggregation',
                'subcategory': 'Complex Grouping',
                'difficulty': 'Hard',
                'question': 'Group orders by month (based on orderDate) and calculate total revenue per month.',
                'answer': dict(sorted(monthly_revenue.items())),
                'query_type': 'temporal_grouping'
            })
        
        country_revenue = defaultdict(float)
        for order in self.orders:
            customer_uri = self.graph.value(order, self.schema.customer)
            if customer_uri:
                country = self._get_property(customer_uri, 'addressCountry')
                price = float(self._get_property(order, 'totalPrice') or 0)
                if country:
                    country_revenue[country] += price
        
        if country_revenue:
            country_revenue = {k: round(v, 2) for k, v in country_revenue.items()}
            questions.append({
                'category': 'Aggregation',
                'subcategory': 'Complex Grouping',
                'difficulty': 'Hard',
                'question': 'Group orders by customer country and calculate the total order value per country.',
                'answer': dict(country_revenue),
                'query_type': 'relationship_grouping'
            })
        
        industry_revenue = defaultdict(list)
        for order in self.orders:
            seller_uri = self.graph.value(order, self.schema.seller)
            if seller_uri:
                industry = self._get_property(seller_uri, 'industry')
                price = float(self._get_property(order, 'totalPrice') or 0)
                if industry:
                    industry_revenue[industry].append(price)
        
        industry_avgs = {k: round(sum(v) / len(v), 2) for k, v in industry_revenue.items() if v}
        if industry_avgs:
            questions.append({
                'category': 'Aggregation',
                'subcategory': 'Complex Grouping',
                'difficulty': 'Hard',
                'question': 'Group orders by seller industry and calculate average order value per industry.',
                'answer': dict(industry_avgs),
                'query_type': 'relationship_grouping'
            })
        
        person_account_counts = defaultdict(int)
        for account in self.accounts:
            # Extract person ID from account URI
            account_uri_str = str(account)
            person_match = re.search(r'person_\d+', account_uri_str)
            if person_match:
                person_id = person_match.group(0)
                person_account_counts[person_id] += 1
        
        if person_account_counts:
            questions.append({
                'category': 'Aggregation',
                'subcategory': 'Complex Grouping',
                'difficulty': 'Medium',
                'question': 'For each person, count how many total accounts they have.',
                'answer': dict(person_account_counts),
                'query_type': 'entity_count'
            })
        
        org_order_counts = defaultdict(int)
        for order in self.orders:
            seller_uri = self.graph.value(order, self.schema.seller)
            if seller_uri:
                seller_id = self._simplify_uri(seller_uri)
                org_order_counts[seller_id] += 1
        
        if org_order_counts:
            questions.append({
                'category': 'Aggregation',
                'subcategory': 'Complex Grouping',
                'difficulty': 'Medium',
                'question': 'For each organization, count how many orders they have fulfilled.',
                'answer': dict(org_order_counts),
                'query_type': 'entity_count'
            })
        
        return questions[:count]
    
    # ===== 7. PATTERN MATCHING QUESTIONS =====
    
    def generate_pattern_matching_questions(self, count=15):
        """Generate structural and temporal pattern matching questions."""
        questions = []
        
        # Structural patterns (5 questions)
        two_item_orders = []
        for order in self.orders:
            items = self._get_property_list(order, 'orderedItem')
            if len(items) == 2:
                order_id = self._simplify_uri(order)
                two_item_orders.append(order_id)
        
        if two_item_orders:
            questions.append({
                'category': 'Pattern Matching',
                'subcategory': 'Structural Pattern',
                'difficulty': 'Medium',
                'question': 'Find all orders that have exactly 2 ordered items.',
                'answer': sorted(two_item_orders),
                'query_type': 'structural_pattern'
            })
        
        one_account_persons = []
        person_account_map = defaultdict(int)
        for account in self.accounts:
            account_uri_str = str(account)
            person_match = re.search(r'person_\d+', account_uri_str)
            if person_match:
                person_id = person_match.group(0)
                person_account_map[person_id] += 1
        
        for person_id, count in person_account_map.items():
            if count == 1:
                one_account_persons.append(person_id)
        
        if one_account_persons:
            questions.append({
                'category': 'Pattern Matching',
                'subcategory': 'Structural Pattern',
                'difficulty': 'Medium',
                'question': 'Find all persons who have exactly 1 account.',
                'answer': sorted(one_account_persons),
                'query_type': 'structural_pattern'
            })
        
        j_name_accounts = []
        for account in self.accounts:
            account_uri_str = str(account)
            person_match = re.search(r'person_\d+', account_uri_str)
            if person_match:
                person_id = person_match.group(0)
                person_uri = self.ex[person_id]
                given_name = self._get_property(person_uri, 'givenName')
                if given_name and given_name.startswith('J'):
                    account_id = self._simplify_uri(account)
                    j_name_accounts.append(account_id)
        
        if j_name_accounts:
            questions.append({
                'category': 'Pattern Matching',
                'subcategory': 'Structural Pattern',
                'difficulty': 'Hard',
                'question': 'Find all accounts belonging to persons whose given name starts with "J".',
                'answer': sorted(j_name_accounts),
                'query_type': 'structural_pattern'
            })
        
        matching_country_orders = []
        for order in self.orders:
            customer_uri = self.graph.value(order, self.schema.customer)
            seller_uri = self.graph.value(order, self.schema.seller)
            if customer_uri and seller_uri:
                cust_country = self._get_property(customer_uri, 'addressCountry')
                seller_country = self._get_property(seller_uri, 'addressCountry')
                if cust_country and seller_country and cust_country == seller_country:
                    order_id = self._simplify_uri(order)
                    matching_country_orders.append(order_id)
        
        if matching_country_orders:
            questions.append({
                'category': 'Pattern Matching',
                'subcategory': 'Structural Pattern',
                'difficulty': 'Hard',
                'question': 'Find all orders where the seller\'s country matches the customer\'s country.',
                'answer': sorted(matching_country_orders),
                'query_type': 'structural_pattern'
            })
        
        # Additional pattern questions (5 questions)
        ord_6digit_orders = []
        for order in self.orders:
            order_num = self._get_property(order, 'orderNumber')
            if order_num and re.match(r'ORD-\d{6}', order_num):
                order_id = self._simplify_uri(order)
                ord_6digit_orders.append(order_id)
        
        if ord_6digit_orders:
            questions.append({
                'category': 'Pattern Matching',
                'subcategory': 'Format Pattern',
                'difficulty': 'Medium',
                'question': 'Find all orders with order numbers following the format "ORD-" followed by 6 digits.',
                'answer': sorted(ord_6digit_orders),
                'query_type': 'regex_pattern'
            })
        
        ssn_format_persons = []
        for person in self.persons:
            tax_id = self._get_property(person, 'taxID')
            if tax_id and re.match(r'\d{3}-\d{2}-\d{4}', tax_id):
                person_id = self._simplify_uri(person)
                ssn_format_persons.append(person_id)
        
        if ssn_format_persons:
            questions.append({
                'category': 'Pattern Matching',
                'subcategory': 'Format Pattern',
                'difficulty': 'Medium',
                'question': 'Find all tax IDs (for persons) following the SSN format (XXX-XX-XXXX).',
                'answer': sorted(ssn_format_persons),
                'query_type': 'regex_pattern'
            })
        
        mid_range_orders = []
        for order in self.orders:
            price = float(self._get_property(order, 'totalPrice') or 0)
            if 1000 <= price <= 1500:
                order_id = self._simplify_uri(order)
                mid_range_orders.append(order_id)
        
        if mid_range_orders:
            questions.append({
                'category': 'Pattern Matching',
                'subcategory': 'Range Pattern',
                'difficulty': 'Easy',
                'question': 'Find all orders where total price is between 1000 and 1500.',
                'answer': sorted(mid_range_orders),
                'query_type': 'range_pattern'
            })
        
        name_mismatch_persons = []
        for person in self.persons:
            name = self._get_property(person, 'name')
            given_name = self._get_property(person, 'givenName')
            family_name = self._get_property(person, 'familyName')
            if name and given_name and family_name:
                expected_name = f"{given_name} {family_name}"
                if name != expected_name:
                    person_id = self._simplify_uri(person)
                    name_mismatch_persons.append(person_id)
        
        if name_mismatch_persons:
            questions.append({
                'category': 'Pattern Matching',
                'subcategory': 'Data Consistency',
                'difficulty': 'Hard',
                'question': 'Find all persons whose name field differs from their given name and family name combination.',
                'answer': sorted(name_mismatch_persons),
                'query_type': 'consistency_check'
            })
        
        same_person_orders = []
        for order in self.orders:
            customer_uri = self.graph.value(order, self.schema.customer)
            payment_uri = self.graph.value(order, self.schema.paymentMethod)
            if customer_uri and payment_uri:
                # Extract person ID from both
                customer_id = self._simplify_uri(customer_uri)
                payment_id_str = str(payment_uri)
                person_match = re.search(r'person_\d+', payment_id_str)
                if person_match:
                    payment_person_id = person_match.group(0)
                    if customer_id == payment_person_id:
                        order_id = self._simplify_uri(order)
                        same_person_orders.append(order_id)
        
        if same_person_orders:
            questions.append({
                'category': 'Pattern Matching',
                'subcategory': 'Relationship Pattern',
                'difficulty': 'Hard',
                'question': 'Find orders where the payment method account belongs to the same person as the customer.',
                'answer': sorted(same_person_orders),
                'query_type': 'relationship_pattern'
            })
        
        # Temporal patterns (5 questions)
        q2_2025_orders = []
        for order in self.orders:
            date_str = self._get_property(order, 'orderDate')
            if date_str:
                try:
                    order_date = datetime.strptime(date_str, '%Y-%m-%d')
                    if order_date.year == 2025 and 4 <= order_date.month <= 6:
                        order_id = self._simplify_uri(order)
                        q2_2025_orders.append(order_id)
                except:
                    pass
        
        if q2_2025_orders:
            questions.append({
                'category': 'Pattern Matching',
                'subcategory': 'Temporal Pattern',
                'difficulty': 'Medium',
                'question': 'Find all orders placed in Q2 2025 (April-June).',
                'answer': sorted(q2_2025_orders),
                'query_type': 'temporal_filter'
            })
        
        h2_2025_orders = []
        for order in self.orders:
            date_str = self._get_property(order, 'orderDate')
            if date_str:
                try:
                    order_date = datetime.strptime(date_str, '%Y-%m-%d')
                    if order_date.year == 2025 and order_date.month >= 7:
                        order_id = self._simplify_uri(order)
                        h2_2025_orders.append(order_id)
                except:
                    pass
        
        if h2_2025_orders:
            questions.append({
                'category': 'Pattern Matching',
                'subcategory': 'Temporal Pattern',
                'difficulty': 'Medium',
                'question': 'Find all orders placed in the second half of 2025.',
                'answer': sorted(h2_2025_orders),
                'query_type': 'temporal_filter'
            })
        
        return questions[:count]
    
    # ===== MAIN GENERATION METHOD =====
    
    def _filter_by_difficulty(self, questions, target_count):
        """
        Filter questions to match the desired difficulty distribution.
        
        Args:
            questions: List of question dicts with 'difficulty' field
            target_count: Total number of questions desired
            
        Returns:
            List of questions matching the difficulty distribution
        """
        if not questions:
            return []
        
        # Separate by difficulty
        by_difficulty = {'Easy': [], 'Medium': [], 'Hard': []}
        for q in questions:
            difficulty = q.get('difficulty', 'Medium')
            if difficulty in by_difficulty:
                by_difficulty[difficulty].append(q)
        
        print(f"  Available: {len(by_difficulty['Easy'])} Easy, {len(by_difficulty['Medium'])} Medium, {len(by_difficulty['Hard'])} Hard")
        
        # Calculate target counts
        easy_target = int(target_count * self.difficulty_distribution['easy'] / 100)
        medium_target = int(target_count * self.difficulty_distribution['medium'] / 100)
        hard_target = target_count - easy_target - medium_target  # Ensure exact total
        
        print(f"  Target: {easy_target} Easy, {medium_target} Medium, {hard_target} Hard")
        
        selected = []
        
        # Select Easy questions
        available_easy = by_difficulty['Easy'][:]
        random.shuffle(available_easy)
        selected.extend(available_easy[:easy_target])
        
        # Select Medium questions
        available_medium = by_difficulty['Medium'][:]
        random.shuffle(available_medium)
        selected.extend(available_medium[:medium_target])
        
        # Select Hard questions
        available_hard = by_difficulty['Hard'][:]
        random.shuffle(available_hard)
        selected.extend(available_hard[:hard_target])
        
        # If we don't have enough, fill with whatever is available
        if len(selected) < target_count:
            remaining_needed = target_count - len(selected)
            available_remaining = [q for q in questions if q not in selected]
            random.shuffle(available_remaining)
            selected.extend(available_remaining[:remaining_needed])
            print(f"  Note: Added {min(remaining_needed, len(available_remaining))} additional questions to reach target")
        
        print(f"  Selected: {len(selected)} questions")
        
        return selected[:target_count]
    
    def generate_all_questions(self, target_count=100):
        """Generate target_count questions across all categories."""
        all_questions = []
        
        # Generate MORE questions than needed to ensure we have enough after difficulty filtering
        # We'll generate 2x the target to have a good pool to select from
        generation_multiplier = 2.0
        
        # Calculate questions per category (baseline proportions)
        questions_per_category = {
            'Property Search': 15,
            'Depth-First Search': 15,
            'Breadth-First Search': 15,
            'Mathematical': 15,
            'Filtering': 20,
            'Aggregation': 20,
            'Pattern Matching': 15
        }
        
        # Scale up to generate more questions
        total_baseline = sum(questions_per_category.values())
        scale = (target_count * generation_multiplier) / total_baseline
        questions_per_category = {k: max(5, int(v * scale)) 
                                 for k, v in questions_per_category.items()}
        
        print("Generating Property Search questions...")
        all_questions.extend(self.generate_property_search_questions(
            questions_per_category['Property Search']))
        
        print("Generating Depth-First Search questions...")
        all_questions.extend(self.generate_dfs_questions(
            questions_per_category['Depth-First Search']))
        
        print("Generating Breadth-First Search questions...")
        all_questions.extend(self.generate_bfs_questions(
            questions_per_category['Breadth-First Search']))
        
        print("Generating Mathematical questions...")
        all_questions.extend(self.generate_mathematical_questions(
            questions_per_category['Mathematical']))
        
        print("Generating Filtering questions...")
        all_questions.extend(self.generate_filtering_questions(
            questions_per_category['Filtering']))
        
        print("Generating Aggregation questions...")
        all_questions.extend(self.generate_aggregation_questions(
            questions_per_category['Aggregation']))
        
        print("Generating Pattern Matching questions...")
        all_questions.extend(self.generate_pattern_matching_questions(
            questions_per_category['Pattern Matching']))
        
        print(f"\nGenerated {len(all_questions)} questions in total")
        
        # If we still don't have enough questions, warn the user
        if len(all_questions) < target_count:
            print(f"WARNING: Only generated {len(all_questions)} questions, less than target of {target_count}")
            print(f"This may be due to limited data in the dataset.")
            return all_questions
        
        # Apply difficulty distribution filter
        print(f"Filtering to {target_count} questions matching difficulty distribution...")
        filtered_questions = self._filter_by_difficulty(all_questions, target_count)
        
        # Shuffle to mix categories
        random.shuffle(filtered_questions)
        
        print(f"Final question count: {len(filtered_questions)}")
        
        return filtered_questions


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate benchmark questions for serialization format testing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Default balanced distribution
  python comprehensive_question_generator.py data.ttl questions.csv 100
  
  # 50%% easy, 30%% medium, 20%% hard
  python comprehensive_question_generator.py data.ttl questions.csv 100 --difficulty 50,30,20
  
  # Only easy questions
  python comprehensive_question_generator.py data.ttl questions.csv 100 --difficulty 100,0,0
  
  # Challenging: 20%% easy, 30%% medium, 50%% hard
  python comprehensive_question_generator.py data.ttl questions.csv 100 --difficulty 20,30,50
        '''
    )
    
    parser.add_argument('turtle_file', help='Path to the turtle (.ttl) file')
    parser.add_argument('output_csv', nargs='?', default='comprehensive_questions.csv',
                       help='Output CSV file (default: comprehensive_questions.csv)')
    parser.add_argument('num_questions', nargs='?', type=int, default=100,
                       help='Number of questions to generate (default: 100)')
    parser.add_argument('--difficulty', type=str, default='33,34,33',
                       help='Difficulty distribution as "easy,medium,hard" percentages (default: 33,34,33)')
    
    args = parser.parse_args()
    
    # Parse difficulty distribution
    try:
        easy, medium, hard = map(float, args.difficulty.split(','))
        difficulty_dist = {'easy': easy, 'medium': medium, 'hard': hard}
        
        # Validate
        total = easy + medium + hard
        if abs(total - 100) > 0.1:
            print(f"Error: Difficulty percentages must sum to 100, got {total}")
            sys.exit(1)
    except ValueError:
        print("Error: --difficulty must be in format 'easy,medium,hard' (e.g., '50,30,20')")
        sys.exit(1)
    
    try:
        with open(args.turtle_file, 'r') as f:
            pass
    except FileNotFoundError:
        print(f"Error: File '{args.turtle_file}' not found.")
        sys.exit(1)
    
    print(f"Reading graph from: {args.turtle_file}")
    print(f"Target number of questions: {args.num_questions}")
    print(f"Difficulty distribution: {easy}% easy, {medium}% medium, {hard}% hard")
    print("=" * 80)
    
    try:
        qa_gen = ComprehensiveQuestionGenerator(args.turtle_file, difficulty_dist)
        questions = qa_gen.generate_all_questions(target_count=args.num_questions)
        
        # Write to CSV
        with open(args.output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['category', 'subcategory', 'difficulty', 'question', 
                         'answer', 'query_type', 'hops']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for q in questions:
                writer.writerow({
                    'category': q.get('category', ''),
                    'subcategory': q.get('subcategory', ''),
                    'difficulty': q.get('difficulty', ''),
                    'question': q['question'],
                    'answer': json.dumps(q['answer']),
                    'query_type': q.get('query_type', ''),
                    'hops': q.get('hops', '')
                })
        
        print("\n" + "=" * 80)
        print(f"Successfully generated {len(questions)} questions")
        print(f"Output saved to: {args.output_csv}")
        print("=" * 80)
        
        # Display summary by category
        print("\nQuestion Summary by Category:")
        category_counts = defaultdict(int)
        for q in questions:
            category_counts[q['category']] += 1
        
        for category, count in sorted(category_counts.items()):
            print(f"  {category}: {count} questions")
        
        # Display summary by difficulty
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
            print(f"\nActual Distribution: {actual_easy:.1f}% easy, {actual_medium:.1f}% medium, {actual_hard:.1f}% hard")
        
        # Show sample questions
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
        print(f"Error processing file: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()