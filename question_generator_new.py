"""
Enhanced Schema-Adaptive Question Generator for Graph vs Tabular Data Experiments

This script automatically discovers the schema of your RDF data and generates
realistic business questions that demonstrate graph database advantages.

Features:
- Automatically discovers entity types and their properties
- Adapts to any field names in your data (handles underscores, typos, variations)
- Generates questions based on actual relationships in your data

Usage:
    pip install rdflib
    python enhanced_question_generator.py <turtle_file> [output_csv] [num_questions]
    
Example:
    python enhanced_question_generator.py linked_data.ttl questions.csv 100
"""

import random
import csv
import sys
import json
from collections import defaultdict
from rdflib import Graph, Namespace, RDF, Literal

class SchemaAdaptiveQuestionGenerator:
    def __init__(self, turtle_file):
        """Initialize with a Turtle format RDF file and discover schema."""
        print(f"Loading RDF graph from {turtle_file}...")
        self.graph = Graph()
        self.graph.parse(turtle_file, format='turtle')
        
        # Define namespaces
        self.custom = Namespace("http://mycompany.com/vocab/")
        self.ex = Namespace("http://example.org/")
        
        # Storage for discovered schema
        self.entity_types = {}
        self.property_map = defaultdict(set)
        
        # Cache entities by type
        self.customers = []
        self.accounts = []
        self.orders = []
        self.companies = []
        self.line_items = []
        self.banks = set()
        self.industries = set()
        self.countries = set()
        
        # Discover schema and cache entities
        self._discover_schema()
        self._cache_entities()
        
        print(f"\nDiscovered Schema:")
        print(f"  Entity Types: {list(self.entity_types.keys())}")
        print(f"\nFound Entities:")
        print(f"  {len(self.customers)} customers")
        print(f"  {len(self.companies)} companies") 
        print(f"  {len(self.accounts)} accounts")
        print(f"  {len(self.orders)} orders")
        print(f"  {len(self.line_items)} line items")
        print(f"  {len(self.banks)} unique banks")
        print(f"  {len(self.industries)} unique industries")
        print(f"  {len(self.countries)} unique countries\n")
    
    def _discover_schema(self):
        """Automatically discover entity types and their properties."""
        # Find all entity types
        for s, p, o in self.graph.triples((None, RDF.type, None)):
            entity_type = str(o).split('/')[-1]
            if entity_type not in self.entity_types:
                self.entity_types[entity_type] = []
            self.entity_types[entity_type].append(s)
        
        # Find all properties for each entity type
        for entity_type, entities in self.entity_types.items():
            for entity in entities[:1]:  # Sample first entity of each type
                for p, o in self.graph.predicate_objects(entity):
                    prop_name = str(p).split('/')[-1]
                    self.property_map[entity_type].add(prop_name)
        
        print(f"Discovered properties:")
        for entity_type, props in self.property_map.items():
            print(f"  {entity_type}: {sorted(list(props))[:5]}...")  # Show first 5
    
    def _cache_entities(self):
        """Cache all entities by type for efficient querying."""
        # Get entities by type - handle both CamelCase and lowercase
        for entity_type, entities in self.entity_types.items():
            lower_type = entity_type.lower()
            if 'customer' in lower_type:
                self.customers = entities
            elif 'company' in lower_type or 'compan' in lower_type:
                self.companies = entities
            elif 'account' in lower_type and 'bank' in lower_type:
                self.accounts = entities
            elif 'transaction' in lower_type or 'order' in lower_type or 'purchase' in lower_type:
                self.orders = entities
            elif 'item' in lower_type and 'line' in lower_type:
                self.line_items = entities
        
        # Extract unique values for categorical properties
        for account in self.accounts:
            bank_name = self._get_property_flexible(account, ['bank_name', 'bankName', 'bankname'])
            if bank_name:
                self.banks.add(bank_name)
        
        for company in self.companies:
            industry = self._get_property_flexible(company, ['company_industry', 'companyIndustry', 'industry'])
            if industry:
                self.industries.add(industry)
            
            country = self._get_property_flexible(company, ['company_country', 'companyCountry', 'country'])
            if country:
                self.countries.add(country)
        
        for customer in self.customers:
            country = self._get_property_flexible(customer, ['cust_country', 'customer_country', 'country'])
            if country:
                self.countries.add(country)
    
    def _get_property_flexible(self, subject, property_variations):
        """Try multiple property name variations and return first match."""
        for prop_name in property_variations:
            value = self.graph.value(subject, self.custom[prop_name])
            if value:
                return str(value)
        return None
    
    def _get_all_property_values(self, subject, property_variations):
        """Get all property values, trying variations."""
        for prop_name in property_variations:
            values = [str(o) for o in self.graph.objects(subject, self.custom[prop_name])]
            if values:
                return values
        return []
    
    def _get_subjects_with_property(self, property_variations, obj):
        """Get all subjects with given property and object, trying variations."""
        for prop_name in property_variations:
            subjects = list(self.graph.subjects(self.custom[prop_name], obj))
            if subjects:
                return subjects
        return []
    
    def _get_display_name(self, entity_uri):
        """Get a human-readable name for any entity."""
        # Try customer name variations
        name = self._get_property_flexible(entity_uri, [
            'cust_full_name', 'fullName', 'full_name', 'name',
            'customer_full_name', 'customerFullName'
        ])
        if name:
            return name
        
        # Try company name variations (note: there's a typo in the data "compan_name")
        name = self._get_property_flexible(entity_uri, [
            'compan_name', 'company_name', 'companyName', 'name'
        ])
        if name:
            return name
        
        # Fallback to URI simplification
        return str(entity_uri).split('/')[-1]
    
    # ===== MULTI-HOP RELATIONSHIP QUERIES =====
    
    def generate_companies_by_customer_bank(self):
        """Which companies have received orders from customers who bank at [specific bank]?"""
        questions = []
        
        for bank in list(self.banks)[:5]:
            # Find customers with accounts at this bank
            customers_at_bank = set()
            for account in self.accounts:
                account_bank = self._get_property_flexible(account, ['bank_name', 'bankName'])
                if account_bank == bank:
                    owner = self._get_property_flexible(account, [
                        'bank_account_owner', 'bankAccountOwner', 'account_owner', 'owner'
                    ])
                    if owner:
                        # Owner is a string URI, convert to URIRef
                        customers_at_bank.add(self.ex[owner.split('/')[-1]])
            
            # Find companies these customers ordered from
            companies = set()
            for customer in customers_at_bank:
                orders = self._get_subjects_with_property(
                    ['order_customer', 'orderCustomer', 'customer'], 
                    customer
                )
                for order in orders:
                    company_uri = self._get_property_flexible(order, [
                        'order_company', 'orderCompany', 'company'
                    ])
                    if company_uri:
                        companies.add(self._get_display_name(self.ex[company_uri.split('/')[-1]]))
            
            if companies:
                questions.append({
                    'type': 'Multi-hop Relationship',
                    'difficulty': 'Hard',
                    'hops': 3,
                    'question': f'Which companies have received orders from customers who bank at {bank}?',
                    'answer': sorted(list(companies)),
                    'entities': {'bank': bank}
                })
        
        return questions
    
    def generate_shared_bank_queries(self):
        """Find all customers who share the same bank as [specific customer]."""
        questions = []
        
        for customer in random.sample(self.customers, min(5, len(self.customers))):
            customer_name = self._get_display_name(customer)
            
            # Find this customer's banks
            customer_banks = set()
            accounts = self._get_subjects_with_property(
                ['bank_account_owner', 'bankAccountOwner', 'account_owner'],
                customer
            )
            for account in accounts:
                bank = self._get_property_flexible(account, ['bank_name', 'bankName'])
                if bank:
                    customer_banks.add(bank)
            
            # Find other customers with same banks
            shared_customers = set()
            for bank in customer_banks:
                for account in self.accounts:
                    if self._get_property_flexible(account, ['bank_name', 'bankName']) == bank:
                        owner_uri = self._get_property_flexible(account, [
                            'bank_account_owner', 'bankAccountOwner'
                        ])
                        if owner_uri:
                            owner = self.ex[owner_uri.split('/')[-1]]
                            if owner != customer:
                                shared_customers.add(self._get_display_name(owner))
            
            if shared_customers:
                questions.append({
                    'type': 'Multi-hop Relationship',
                    'difficulty': 'Medium',
                    'hops': 2,
                    'question': f'Find all customers who share the same bank as {customer_name}',
                    'answer': sorted(list(shared_customers)),
                    'entities': {'customer': customer_name}
                })
        
        return questions
    
    def generate_spending_by_bank(self):
        """Total spending across all orders by customers at [specific bank]."""
        questions = []
        
        for bank in list(self.banks)[:5]:
            # Find customers at this bank
            customers_at_bank = set()
            for account in self.accounts:
                if self._get_property_flexible(account, ['bank_name', 'bankName']) == bank:
                    owner_uri = self._get_property_flexible(account, [
                        'bank_account_owner', 'bankAccountOwner'
                    ])
                    if owner_uri:
                        customers_at_bank.add(self.ex[owner_uri.split('/')[-1]])
            
            # Calculate total spending
            total = 0.0
            for customer in customers_at_bank:
                orders = self._get_subjects_with_property(
                    ['order_customer', 'orderCustomer'], 
                    customer
                )
                for order in orders:
                    order_total = self._get_property_flexible(order, [
                        'order_total', 'orderTotal', 'total'
                    ])
                    if order_total:
                        try:
                            total += float(order_total)
                        except:
                            pass
            
            if total > 0:
                questions.append({
                    'type': 'Aggregation Across Relationships',
                    'difficulty': 'Hard',
                    'hops': 3,
                    'question': f'What is the total spending across all orders placed by customers who bank at {bank}?',
                    'answer': round(total, 2),
                    'entities': {'bank': bank}
                })
        
        return questions
    
    def generate_multi_account_company_queries(self):
        """Which companies have done business with customers who have multiple bank accounts?"""
        questions = []
        
        # Find customers with multiple accounts
        customer_account_count = defaultdict(int)
        for account in self.accounts:
            owner_uri = self._get_property_flexible(account, [
                'bank_account_owner', 'bankAccountOwner'
            ])
            if owner_uri:
                owner = self.ex[owner_uri.split('/')[-1]]
                customer_account_count[owner] += 1
        
        multi_account_customers = [c for c, count in customer_account_count.items() if count > 1]
        
        # Find companies these customers ordered from
        companies = set()
        for customer in multi_account_customers:
            orders = self._get_subjects_with_property(
                ['order_customer', 'orderCustomer'], 
                customer
            )
            for order in orders:
                company_uri = self._get_property_flexible(order, [
                    'order_company', 'orderCompany'
                ])
                if company_uri:
                    companies.add(self._get_display_name(self.ex[company_uri.split('/')[-1]]))
        
        if companies:
            questions.append({
                'type': 'Multi-hop Relationship',
                'difficulty': 'Medium',
                'hops': 2,
                'question': 'Which companies have done business with customers who have multiple bank accounts?',
                'answer': sorted(list(companies)),
                'entities': {}
            })
        
        return questions
    
    def generate_companies_by_customer_country(self):
        """Which companies have received orders from customers in [specific country]?"""
        questions = []
        
        # Get customer countries
        customer_countries = set()
        for customer in self.customers:
            country = self._get_property_flexible(customer, [
                'cust_country', 'customer_country', 'country'
            ])
            if country:
                customer_countries.add(country)
        
        for country in list(customer_countries)[:3]:
            # Find customers in this country
            customers_in_country = set()
            for customer in self.customers:
                cust_country = self._get_property_flexible(customer, [
                    'cust_country', 'customer_country', 'country'
                ])
                if cust_country == country:
                    customers_in_country.add(customer)
            
            # Find companies these customers ordered from
            companies = set()
            for customer in customers_in_country:
                orders = self._get_subjects_with_property(
                    ['order_customer', 'orderCustomer'], 
                    customer
                )
                for order in orders:
                    company_uri = self._get_property_flexible(order, [
                        'order_company', 'orderCompany'
                    ])
                    if company_uri:
                        companies.add(self._get_display_name(self.ex[company_uri.split('/')[-1]]))
            
            if companies:
                questions.append({
                    'type': 'Multi-hop Relationship',
                    'difficulty': 'Medium',
                    'hops': 2,
                    'question': f'Which companies have received orders from customers in {country}?',
                    'answer': sorted(list(companies)),
                    'entities': {'country': country}
                })
        
        return questions
    
    # ===== PATTERN MATCHING QUERIES =====
    
    def generate_different_account_same_company(self):
        """Find customers who ordered from the same company using different payment accounts."""
        questions = []
        
        for customer in random.sample(self.customers, min(5, len(self.customers))):
            customer_name = self._get_display_name(customer)
            
            # Group orders by company
            company_accounts = defaultdict(set)
            orders = self._get_subjects_with_property(
                ['order_customer', 'orderCustomer'], 
                customer
            )
            for order in orders:
                company_uri = self._get_property_flexible(order, [
                    'order_company', 'orderCompany'
                ])
                payment_uri = self._get_property_flexible(order, [
                    'order_payment_type', 'order_payment', 'orderPayment', 'payment'
                ])
                if company_uri and payment_uri:
                    company_accounts[company_uri].add(payment_uri)
            
            # Find companies with multiple accounts used
            companies_with_multi_accounts = [
                self._get_display_name(self.ex[comp.split('/')[-1]]) 
                for comp, accounts in company_accounts.items() 
                if len(accounts) > 1
            ]
            
            if companies_with_multi_accounts:
                questions.append({
                    'type': 'Pattern Matching',
                    'difficulty': 'Hard',
                    'hops': 2,
                    'question': f'Which companies did {customer_name} order from using different payment accounts?',
                    'answer': sorted(companies_with_multi_accounts),
                    'entities': {'customer': customer_name}
                })
        
        return questions
    
    def generate_shared_company_and_bank(self):
        """Customers who ordered from [company] AND have accounts at [bank]."""
        questions = []
        
        for company in random.sample(self.companies, min(3, len(self.companies))):
            company_name = self._get_display_name(company)
            
            # Find customers who ordered from this company
            customers_ordered = set()
            orders = self._get_subjects_with_property(
                ['order_company', 'orderCompany'], 
                company
            )
            for order in orders:
                customer_uri = self._get_property_flexible(order, [
                    'order_customer', 'orderCustomer'
                ])
                if customer_uri:
                    customers_ordered.add(self.ex[customer_uri.split('/')[-1]])
            
            # For each bank, find overlap
            for bank in list(self.banks)[:3]:
                customers_at_bank = set()
                for account in self.accounts:
                    if self._get_property_flexible(account, ['bank_name', 'bankName']) == bank:
                        owner_uri = self._get_property_flexible(account, [
                            'bank_account_owner', 'bankAccountOwner'
                        ])
                        if owner_uri:
                            customers_at_bank.add(self.ex[owner_uri.split('/')[-1]])
                
                overlap = customers_ordered & customers_at_bank
                if overlap:
                    customer_names = [self._get_display_name(c) for c in overlap]
                    questions.append({
                        'type': 'Pattern Matching',
                        'difficulty': 'Hard',
                        'hops': 3,
                        'question': f'Which customers have both ordered from {company_name} AND have accounts at {bank}?',
                        'answer': sorted(customer_names),
                        'entities': {'company': company_name, 'bank': bank}
                    })
        
        return questions
    
    def generate_similar_ordering_patterns(self):
        """Find customers with similar ordering patterns (same companies)."""
        questions = []
        
        # Build customer -> companies mapping
        customer_companies = defaultdict(set)
        for order in self.orders:
            customer_uri = self._get_property_flexible(order, [
                'order_customer', 'orderCustomer'
            ])
            company_uri = self._get_property_flexible(order, [
                'order_company', 'orderCompany'
            ])
            if customer_uri and company_uri:
                customer = self.ex[customer_uri.split('/')[-1]]
                company = self.ex[company_uri.split('/')[-1]]
                customer_companies[customer].add(company)
        
        # Find customers with overlapping companies
        for customer in random.sample(self.customers, min(3, len(self.customers))):
            customer_name = self._get_display_name(customer)
            customer_cos = customer_companies.get(customer, set())
            
            if len(customer_cos) < 2:
                continue
            
            similar_customers = []
            for other_customer in self.customers:
                if other_customer == customer:
                    continue
                other_cos = customer_companies.get(other_customer, set())
                overlap = customer_cos & other_cos
                if len(overlap) >= 2:
                    similar_customers.append(self._get_display_name(other_customer))
            
            if similar_customers:
                questions.append({
                    'type': 'Pattern Matching',
                    'difficulty': 'Medium',
                    'hops': 2,
                    'question': f'Which customers have ordered from at least 2 of the same companies as {customer_name}?',
                    'answer': sorted(similar_customers),
                    'entities': {'customer': customer_name}
                })
        
        return questions
    
    def generate_cross_country_patterns(self):
        """Find customers in same country who order from same companies."""
        questions = []
        
        # Build country -> customers mapping
        country_customers = defaultdict(set)
        for customer in self.customers:
            country = self._get_property_flexible(customer, [
                'cust_country', 'customer_country', 'country'
            ])
            if country:
                country_customers[country].add(customer)
        
        # Build customer -> companies mapping
        customer_companies = defaultdict(set)
        for order in self.orders:
            customer_uri = self._get_property_flexible(order, [
                'order_customer', 'orderCustomer'
            ])
            company_uri = self._get_property_flexible(order, [
                'order_company', 'orderCompany'
            ])
            if customer_uri and company_uri:
                customer = self.ex[customer_uri.split('/')[-1]]
                company = self.ex[company_uri.split('/')[-1]]
                customer_companies[customer].add(company)
        
        for country, customers in list(country_customers.items())[:2]:
            if len(customers) < 2:
                continue
            
            # Find companies popular in this country
            company_counts = defaultdict(int)
            for customer in customers:
                for company in customer_companies.get(customer, set()):
                    company_counts[company] += 1
            
            popular_companies = [
                self._get_display_name(comp)
                for comp, count in company_counts.items()
                if count >= 2
            ]
            
            if popular_companies:
                questions.append({
                    'type': 'Pattern Matching',
                    'difficulty': 'Medium',
                    'hops': 2,
                    'question': f'Which companies have received orders from 2 or more customers in {country}?',
                    'answer': sorted(popular_companies),
                    'entities': {'country': country}
                })
        
        return questions
    
    # ===== AGGREGATION QUERIES =====
    
    def generate_bank_total_orders(self):
        """For each bank, what's the total order value of all orders by account holders?"""
        questions = []
        
        bank_totals = defaultdict(float)
        
        for account in self.accounts:
            bank = self._get_property_flexible(account, ['bank_name', 'bankName'])
            owner_uri = self._get_property_flexible(account, [
                'bank_account_owner', 'bankAccountOwner'
            ])
            
            if bank and owner_uri:
                owner = self.ex[owner_uri.split('/')[-1]]
                orders = self._get_subjects_with_property(
                    ['order_customer', 'orderCustomer'], 
                    owner
                )
                for order in orders:
                    total = self._get_property_flexible(order, [
                        'order_total', 'orderTotal', 'total'
                    ])
                    if total:
                        try:
                            bank_totals[bank] += float(total)
                        except:
                            pass
        
        for bank, total in sorted(bank_totals.items(), key=lambda x: x[1], reverse=True)[:5]:
            questions.append({
                'type': 'Aggregation Across Relationships',
                'difficulty': 'Hard',
                'hops': 3,
                'question': f'What is the total order value of all orders placed by customers who have accounts at {bank}?',
                'answer': round(total, 2),
                'entities': {'bank': bank}
            })
        
        return questions
    
    def generate_high_balance_company_orders(self):
        """Which company has highest total orders from customers with balance > threshold?"""
        questions = []
        
        threshold = 10000
        
        # Find customers with high balance accounts
        high_balance_customers = set()
        for account in self.accounts:
            balance = self._get_property_flexible(account, ['balance'])
            if balance:
                try:
                    if float(balance) > threshold:
                        owner_uri = self._get_property_flexible(account, [
                            'bank_account_owner', 'bankAccountOwner'
                        ])
                        if owner_uri:
                            high_balance_customers.add(self.ex[owner_uri.split('/')[-1]])
                except:
                    pass
        
        # Calculate totals per company
        company_totals = defaultdict(float)
        for customer in high_balance_customers:
            orders = self._get_subjects_with_property(
                ['order_customer', 'orderCustomer'], 
                customer
            )
            for order in orders:
                company_uri = self._get_property_flexible(order, [
                    'order_company', 'orderCompany'
                ])
                total = self._get_property_flexible(order, [
                    'order_total', 'orderTotal', 'total'
                ])
                if company_uri and total:
                    try:
                        company = self.ex[company_uri.split('/')[-1]]
                        company_totals[company] += float(total)
                    except:
                        pass
        
        if company_totals:
            top_company, top_total = max(company_totals.items(), key=lambda x: x[1])
            questions.append({
                'type': 'Aggregation Across Relationships',
                'difficulty': 'Hard',
                'hops': 3,
                'question': f'Which company has the highest total order value from customers who have accounts with balances over ${threshold:,}?',
                'answer': {
                    'company': self._get_display_name(top_company),
                    'total': round(top_total, 2)
                },
                'entities': {'threshold': threshold}
            })
        
        return questions
    
    def generate_industry_average_balance(self):
        """Average account balance for customers who ordered from [industry]."""
        questions = []
        
        for industry in list(self.industries):
            # Find companies in this industry
            industry_companies = []
            for company in self.companies:
                comp_industry = self._get_property_flexible(company, [
                    'company_industry', 'companyIndustry', 'industry'
                ])
                if comp_industry == industry:
                    industry_companies.append(company)
            
            # Find customers who ordered from these companies
            customers = set()
            for company in industry_companies:
                orders = self._get_subjects_with_property(
                    ['order_company', 'orderCompany'], 
                    company
                )
                for order in orders:
                    customer_uri = self._get_property_flexible(order, [
                        'order_customer', 'orderCustomer'
                    ])
                    if customer_uri:
                        customers.add(self.ex[customer_uri.split('/')[-1]])
            
            # Calculate average balance
            total_balance = 0.0
            account_count = 0
            for customer in customers:
                accounts = self._get_subjects_with_property(
                    ['bank_account_owner', 'bankAccountOwner'], 
                    customer
                )
                for account in accounts:
                    balance = self._get_property_flexible(account, ['balance'])
                    if balance:
                        try:
                            total_balance += float(balance)
                            account_count += 1
                        except:
                            pass
            
            if account_count > 0:
                avg_balance = total_balance / account_count
                questions.append({
                    'type': 'Aggregation Across Relationships',
                    'difficulty': 'Hard',
                    'hops': 3,
                    'question': f'What is the average account balance for customers who have placed orders with companies in the {industry} industry?',
                    'answer': round(avg_balance, 2),
                    'entities': {'industry': industry}
                })
        
        return questions
    
    def generate_country_spending_analysis(self):
        """Total spending by customers in each country."""
        questions = []
        
        # Group customers by country
        country_customers = defaultdict(set)
        for customer in self.customers:
            country = self._get_property_flexible(customer, [
                'cust_country', 'customer_country', 'country'
            ])
            if country:
                country_customers[country].add(customer)
        
        country_totals = {}
        for country, customers in country_customers.items():
            total = 0.0
            for customer in customers:
                orders = self._get_subjects_with_property(
                    ['order_customer', 'orderCustomer'], 
                    customer
                )
                for order in orders:
                    order_total = self._get_property_flexible(order, [
                        'order_total', 'orderTotal', 'total'
                    ])
                    if order_total:
                        try:
                            total += float(order_total)
                        except:
                            pass
            if total > 0:
                country_totals[country] = total
        
        # Get top 3 countries by spending
        for country, total in sorted(country_totals.items(), key=lambda x: x[1], reverse=True)[:3]:
            questions.append({
                'type': 'Aggregation Across Relationships',
                'difficulty': 'Medium',
                'hops': 2,
                'question': f'What is the total order value from all customers in {country}?',
                'answer': round(total, 2),
                'entities': {'country': country}
            })
        
        return questions
    
    # ===== PATH FINDING QUERIES =====
    
    def generate_customer_connection_paths(self):
        """Find connections between two customers through shared entities."""
        questions = []
        
        for _ in range(3):
            if len(self.customers) < 2:
                break
            
            customer1, customer2 = random.sample(self.customers, 2)
            name1 = self._get_display_name(customer1)
            name2 = self._get_display_name(customer2)
            
            # Find shared banks
            banks1 = set()
            accounts1 = self._get_subjects_with_property(
                ['bank_account_owner', 'bankAccountOwner'], 
                customer1
            )
            for account in accounts1:
                bank = self._get_property_flexible(account, ['bank_name', 'bankName'])
                if bank:
                    banks1.add(bank)
            
            banks2 = set()
            accounts2 = self._get_subjects_with_property(
                ['bank_account_owner', 'bankAccountOwner'], 
                customer2
            )
            for account in accounts2:
                bank = self._get_property_flexible(account, ['bank_name', 'bankName'])
                if bank:
                    banks2.add(bank)
            
            shared_banks = banks1 & banks2
            
            # Find shared companies
            companies1 = set()
            orders1 = self._get_subjects_with_property(
                ['order_customer', 'orderCustomer'], 
                customer1
            )
            for order in orders1:
                company_uri = self._get_property_flexible(order, [
                    'order_company', 'orderCompany'
                ])
                if company_uri:
                    companies1.add(self._get_display_name(self.ex[company_uri.split('/')[-1]]))
            
            companies2 = set()
            orders2 = self._get_subjects_with_property(
                ['order_customer', 'orderCustomer'], 
                customer2
            )
            for order in orders2:
                company_uri = self._get_property_flexible(order, [
                    'order_company', 'orderCompany'
                ])
                if company_uri:
                    companies2.add(self._get_display_name(self.ex[company_uri.split('/')[-1]]))
            
            shared_companies = companies1 & companies2
            
            # Check if same country
            country1 = self._get_property_flexible(customer1, [
                'cust_country', 'customer_country', 'country'
            ])
            country2 = self._get_property_flexible(customer2, [
                'cust_country', 'customer_country', 'country'
            ])
            
            connections = []
            if shared_banks:
                connections.extend([f'Both bank at {bank}' for bank in shared_banks])
            if shared_companies:
                connections.extend([f'Both ordered from {company}' for company in shared_companies])
            if country1 and country2 and country1 == country2:
                connections.append(f'Both located in {country1}')
            
            if connections:
                questions.append({
                    'type': 'Path Finding',
                    'difficulty': 'Medium',
                    'hops': 2,
                    'question': f'What connections exist between {name1} and {name2}?',
                    'answer': sorted(connections),
                    'entities': {'customer1': name1, 'customer2': name2}
                })
        
        return questions
    
    # ===== SIMPLE QUERIES =====
    
    def generate_simple_queries(self):
        """Generate simple 1-hop queries for baseline comparison."""
        questions = []
        
        # Customer's orders
        for customer in random.sample(self.customers, min(5, len(self.customers))):
            customer_name = self._get_display_name(customer)
            order_numbers = []
            orders = self._get_subjects_with_property(
                ['order_customer', 'orderCustomer'], 
                customer
            )
            for order in orders:
                order_num = self._get_property_flexible(order, [
                    'order_number', 'orderNumber'
                ])
                if order_num:
                    order_numbers.append(order_num)
            
            if order_numbers:
                questions.append({
                    'type': 'Simple Property Lookup',
                    'difficulty': 'Easy',
                    'hops': 1,
                    'question': f'What are the order numbers for {customer_name}?',
                    'answer': sorted(order_numbers),
                    'entities': {'customer': customer_name}
                })
        
        # Company orders
        for company in random.sample(self.companies, min(3, len(self.companies))):
            company_name = self._get_display_name(company)
            orders = self._get_subjects_with_property(
                ['order_company', 'orderCompany'], 
                company
            )
            order_count = len(orders)
            
            questions.append({
                'type': 'Simple Property Lookup',
                'difficulty': 'Easy',
                'hops': 1,
                'question': f'How many orders has {company_name} received?',
                'answer': order_count,
                'entities': {'company': company_name}
            })
        
        # Customer's bank accounts
        for customer in random.sample(self.customers, min(5, len(self.customers))):
            customer_name = self._get_display_name(customer)
            banks = set()
            accounts = self._get_subjects_with_property(
                ['bank_account_owner', 'bankAccountOwner'], 
                customer
            )
            for account in accounts:
                bank = self._get_property_flexible(account, ['bank_name', 'bankName'])
                if bank:
                    banks.add(bank)
            
            if banks:
                questions.append({
                    'type': 'Simple Property Lookup',
                    'difficulty': 'Easy',
                    'hops': 1,
                    'question': f'Which banks does {customer_name} have accounts at?',
                    'answer': sorted(list(banks)),
                    'entities': {'customer': customer_name}
                })
        
        # Customer country
        for customer in random.sample(self.customers, min(3, len(self.customers))):
            customer_name = self._get_display_name(customer)
            country = self._get_property_flexible(customer, [
                'cust_country', 'customer_country', 'country'
            ])
            
            if country:
                questions.append({
                    'type': 'Simple Property Lookup',
                    'difficulty': 'Easy',
                    'hops': 1,
                    'question': f'What country is {customer_name} located in?',
                    'answer': country,
                    'entities': {'customer': customer_name}
                })
        
        # Company industry
        for company in random.sample(self.companies, min(3, len(self.companies))):
            company_name = self._get_display_name(company)
            industry = self._get_property_flexible(company, [
                'company_industry', 'companyIndustry', 'industry'
            ])
            
            if industry:
                questions.append({
                    'type': 'Simple Property Lookup',
                    'difficulty': 'Easy',
                    'hops': 1,
                    'question': f'What industry is {company_name} in?',
                    'answer': industry,
                    'entities': {'company': company_name}
                })
        
        return questions
    
    def generate_all_questions(self, target_count=100):
        """Generate approximately target_count questions across all types."""
        all_questions = []
        
        print("Generating Multi-hop Relationship queries...")
        all_questions.extend(self.generate_companies_by_customer_bank())
        all_questions.extend(self.generate_shared_bank_queries())
        all_questions.extend(self.generate_spending_by_bank())
        all_questions.extend(self.generate_multi_account_company_queries())
        all_questions.extend(self.generate_companies_by_customer_country())
        
        print("Generating Pattern Matching queries...")
        all_questions.extend(self.generate_different_account_same_company())
        all_questions.extend(self.generate_shared_company_and_bank())
        all_questions.extend(self.generate_similar_ordering_patterns())
        all_questions.extend(self.generate_cross_country_patterns())
        
        print("Generating Aggregation queries...")
        all_questions.extend(self.generate_bank_total_orders())
        all_questions.extend(self.generate_high_balance_company_orders())
        all_questions.extend(self.generate_industry_average_balance())
        all_questions.extend(self.generate_country_spending_analysis())
        
        print("Generating Path Finding queries...")
        all_questions.extend(self.generate_customer_connection_paths())
        
        print("Generating Simple queries for baseline...")
        all_questions.extend(self.generate_simple_queries())
        
        # If we need more questions, repeat some categories
        while len(all_questions) < target_count:
            all_questions.extend(self.generate_simple_queries()[:5])
            all_questions.extend(self.generate_shared_bank_queries()[:3])
            if len(all_questions) >= target_count:
                break
        
        # Shuffle and limit to target count
        random.shuffle(all_questions)
        return all_questions[:target_count]


def main():
    if len(sys.argv) < 2:
        print("Usage: python enhanced_question_generator.py <turtle_file> [output_csv] [num_questions]")
        print("Example: python enhanced_question_generator.py linked_data.ttl questions.csv 100")
        sys.exit(1)
    
    turtle_file = sys.argv[1]
    output_csv = sys.argv[2] if len(sys.argv) > 2 else 'enhanced_questions.csv'
    num_questions = int(sys.argv[3]) if len(sys.argv) > 3 else 100
    
    try:
        with open(turtle_file, 'r') as f:
            pass
    except FileNotFoundError:
        print(f"Error: File '{turtle_file}' not found.")
        sys.exit(1)
    
    print(f"Reading graph from: {turtle_file}")
    print(f"Target number of questions: {num_questions}")
    print("=" * 80)
    
    try:
        qa_gen = SchemaAdaptiveQuestionGenerator(turtle_file)
        questions = qa_gen.generate_all_questions(target_count=num_questions)
        
        # Write to CSV
        with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['type', 'difficulty', 'hops', 'question', 'answer', 'entities']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for q in questions:
                writer.writerow({
                    'type': q['type'],
                    'difficulty': q['difficulty'],
                    'hops': q['hops'],
                    'question': q['question'],
                    'answer': json.dumps(q['answer']),
                    'entities': json.dumps(q['entities'])
                })
        
        print("\n" + "=" * 80)
        print(f"Successfully generated {len(questions)} questions")
        print(f"Output saved to: {output_csv}")
        print("=" * 80)
        
        # Display summary
        print("\nQuestion Summary by Type:")
        type_counts = defaultdict(int)
        for q in questions:
            type_counts[q['type']] += 1
        
        for qtype, count in sorted(type_counts.items()):
            print(f"  {qtype}: {count} questions")
        
        print("\nQuestion Summary by Difficulty:")
        difficulty_counts = defaultdict(int)
        for q in questions:
            difficulty_counts[q['difficulty']] += 1
        
        for difficulty, count in sorted(difficulty_counts.items()):
            print(f"  {difficulty}: {count} questions")
        
        print("\nQuestion Summary by Hops:")
        hop_counts = defaultdict(int)
        for q in questions:
            hop_counts[q['hops']] += 1
        
        for hops, count in sorted(hop_counts.items()):
            print(f"  {hops}-hop: {count} questions")
        
        # Show sample questions
        print("\n" + "=" * 80)
        print("Sample Questions:")
        print("=" * 80)
        for q in questions[:5]:
            print(f"\n[{q['type']} - {q['difficulty']} - {q['hops']}-hop]")
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
