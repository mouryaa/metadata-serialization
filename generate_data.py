#!/usr/bin/env python3
"""
Generate linked Schema.org data with relationships between entities.

This script generates a realistic e-commerce scenario:
- N People
- Each person has 1-Y bank accounts
- Each account is used for 1-X orders
- Orders are placed with Z organizations

All entities are properly linked with URIs showing real-world relationships.
Can output as RDF (turtle, etc.), denormalized CSV, or normalized CSV (3NF).
"""

import argparse
import sys
import random
import csv
from pathlib import Path
from rdflib import Graph, Namespace, Literal, URIRef, RDF, XSD
from rdflib.namespace import RDFS
from faker import Faker

# Import our custom providers
from providers import (
    SchemaOrgPersonProvider,
    SchemaOrgOrganizationProvider,
    SchemaOrgBankAccountProvider,
    SchemaOrgOrderProvider
)


# Define namespaces
SCHEMA = Namespace("http://schema.org/")
EX = Namespace("http://example.org/")
CUSTOM = Namespace("http://mycompany.com/vocab/")


# ============================================================================
# PREDICATE CONFIGURATION
# ============================================================================
# Customize the RDF predicates used in the generated turtle files here.
# Change these to customize your vocabulary. CSV column names will automatically
# match the predicate names.
#
# Examples:
#   PERSON_TYPE = SCHEMA.Customer    → RDF: schema:Customer, CSV: "Customer"
#   PERSON_NAME = CUSTOM.fullName    → RDF: custom:fullName, CSV: "fullName"
# ============================================================================

class PredicateConfig:
    """Configuration for RDF predicates. Modify these to change the output."""
    
    # Person/Customer predicates
    PERSON_TYPE = CUSTOM.Customer           # Type: Customer instead of Person
    PERSON_NAME = CUSTOM.fullName
    PERSON_GIVEN_NAME = CUSTOM.firstName
    PERSON_FAMILY_NAME = CUSTOM.lastName
    PERSON_EMAIL = CUSTOM.emailAddress
    PERSON_TELEPHONE = CUSTOM.phoneNumber
    PERSON_TAX_ID = CUSTOM.customerID
    
    # Bank Account predicates
    ACCOUNT_TYPE = CUSTOM.BankAccount
    ACCOUNT_NAME = CUSTOM.bankAccountName
    ACCOUNT_IDENTIFIER = CUSTOM.bankAccountId
    ACCOUNT_TYPE_FIELD = CUSTOM.bankAccountType
    ACCOUNT_BANK = CUSTOM.bankName
    ACCOUNT_BALANCE = CUSTOM.balance
    ACCOUNT_HOLDER = CUSTOM.bankAccountOwner
    
    # Organization predicates
    ORG_TYPE = CUSTOM.Company
    ORG_NAME = CUSTOM.companyName
    ORG_DESCRIPTION = CUSTOM.description
    ORG_EMAIL = CUSTOM.companyEmail
    ORG_TELEPHONE = CUSTOM.companyPhone
    ORG_URL = CUSTOM.companyURL
    ORG_INDUSTRY = CUSTOM.companyIndustry
    ORG_TAX_ID = CUSTOM.companyID
    
    # Order predicates
    ORDER_TYPE = CUSTOM.PurchaseOrder
    ORDER_NUMBER = CUSTOM.orderNumber
    ORDER_STATUS = CUSTOM.orderStatus
    ORDER_DATE = CUSTOM.orderDate
    ORDER_TOTAL = CUSTOM.orderTotal
    ORDER_CUSTOMER = CUSTOM.orderCustomer
    ORDER_PAYMENT_METHOD = CUSTOM.orderPayment
    ORDER_MERCHANT = CUSTOM.orderCompany
    ORDER_ITEM = CUSTOM.orderItem
    
    # Order Item predicates
    ITEM_TYPE = CUSTOM.LineItem
    ITEM_NUMBER = CUSTOM.itemNumber
    ITEM_NAME = CUSTOM.productName


class CSVColumns:
    """
    CSV column names that match the RDF predicate names.
    Automatically extracts the local name from each predicate URI.
    """
    
    @staticmethod
    def get_local_name(predicate):
        """Extract the local name from a predicate URI."""
        uri_str = str(predicate)
        return uri_str.split('/')[-1].split('#')[-1]
    
    # Person columns (extracted from predicates)
    PERSON_ID = 'person_id'
    PERSON_URI = 'person_uri'
    PERSON_TYPE = get_local_name.__func__(PredicateConfig.PERSON_TYPE)
    PERSON_NAME = get_local_name.__func__(PredicateConfig.PERSON_NAME)
    PERSON_GIVEN_NAME = get_local_name.__func__(PredicateConfig.PERSON_GIVEN_NAME)
    PERSON_FAMILY_NAME = get_local_name.__func__(PredicateConfig.PERSON_FAMILY_NAME)
    PERSON_EMAIL = get_local_name.__func__(PredicateConfig.PERSON_EMAIL)
    PERSON_TELEPHONE = get_local_name.__func__(PredicateConfig.PERSON_TELEPHONE)
    PERSON_TAX_ID = get_local_name.__func__(PredicateConfig.PERSON_TAX_ID)
    
    # Bank Account columns
    ACCOUNT_ID = 'account_id'
    ACCOUNT_URI = 'account_uri'
    ACCOUNT_PERSON_ID = 'person_id'
    ACCOUNT_NAME = get_local_name.__func__(PredicateConfig.ACCOUNT_NAME)
    ACCOUNT_IDENTIFIER = get_local_name.__func__(PredicateConfig.ACCOUNT_IDENTIFIER)
    ACCOUNT_TYPE_FIELD = get_local_name.__func__(PredicateConfig.ACCOUNT_TYPE_FIELD)
    ACCOUNT_BANK = get_local_name.__func__(PredicateConfig.ACCOUNT_BANK)
    ACCOUNT_BALANCE = get_local_name.__func__(PredicateConfig.ACCOUNT_BALANCE)
    
    # Organization columns
    ORG_ID = 'org_id'
    ORG_URI = 'org_uri'
    ORG_NAME = get_local_name.__func__(PredicateConfig.ORG_NAME)
    ORG_DESCRIPTION = get_local_name.__func__(PredicateConfig.ORG_DESCRIPTION)
    ORG_EMAIL = get_local_name.__func__(PredicateConfig.ORG_EMAIL)
    ORG_TELEPHONE = get_local_name.__func__(PredicateConfig.ORG_TELEPHONE)
    ORG_URL = get_local_name.__func__(PredicateConfig.ORG_URL)
    ORG_INDUSTRY = get_local_name.__func__(PredicateConfig.ORG_INDUSTRY)
    ORG_TAX_ID = get_local_name.__func__(PredicateConfig.ORG_TAX_ID)
    
    # Order columns
    ORDER_ID = 'order_id'
    ORDER_URI = 'order_uri'
    ORDER_PERSON_ID = 'person_id'
    ORDER_ACCOUNT_ID = 'account_id'
    ORDER_MERCHANT_ID = 'merchant_id'
    ORDER_NUMBER = get_local_name.__func__(PredicateConfig.ORDER_NUMBER)
    ORDER_STATUS = get_local_name.__func__(PredicateConfig.ORDER_STATUS)
    ORDER_DATE = get_local_name.__func__(PredicateConfig.ORDER_DATE)
    ORDER_TOTAL = get_local_name.__func__(PredicateConfig.ORDER_TOTAL)
    
    # Order Item columns
    ITEM_ORDER_ID = 'order_id'
    ITEM_INDEX = 'item_index'
    ITEM_NAME = get_local_name.__func__(PredicateConfig.ITEM_NAME)

# ============================================================================
# END PREDICATE CONFIGURATION
# ============================================================================


class DataCollector:
    """Collects data for both RDF and CSV export."""
    
    def __init__(self):
        self.organizations = []
        self.people = []
        self.accounts = []
        self.orders = []
        self.order_items = []
    
    def add_organization(self, org_data):
        self.organizations.append(org_data)
    
    def add_person(self, person_data):
        self.people.append(person_data)
    
    def add_account(self, account_data):
        self.accounts.append(account_data)
    
    def add_order(self, order_data):
        self.orders.append(order_data)
    
    def add_order_item(self, item_data):
        self.order_items.append(item_data)


def generate_organizations(fake, num_orgs, graph, collector, seed=None):
    """
    Generate organization entities.
    
    Returns:
        list: List of organization URIs and IDs
    """
    if seed is not None:
        Faker.seed(seed)
        random.seed(seed)
    
    print(f"Generating {num_orgs} organizations...")
    org_data_list = []
    
    for i in range(num_orgs):
        org_id = f"org_{i+1}"
        org_uri = EX[org_id]
        
        # Generate organization data
        org_name = fake.organization_name()
        description = fake.organization_description()
        email = fake.organization_email()
        telephone = fake.organization_telephone()
        url = fake.organization_url()
        industry = fake.organization_industry()
        tax_id = fake.organization_tax_id() if random.random() < 0.7 else None
        
        # Store for CSV
        if collector:
            collector.add_organization({
                CSVColumns.ORG_ID: org_id,
                CSVColumns.ORG_URI: str(org_uri),
                CSVColumns.ORG_NAME: org_name,
                CSVColumns.ORG_DESCRIPTION: description,
                CSVColumns.ORG_EMAIL: email,
                CSVColumns.ORG_TELEPHONE: telephone,
                CSVColumns.ORG_URL: url,
                CSVColumns.ORG_INDUSTRY: industry,
                CSVColumns.ORG_TAX_ID: tax_id
            })
        
        # Add to RDF graph
        if graph is not None:
            graph.add((org_uri, RDF.type, PredicateConfig.ORG_TYPE))
            graph.add((org_uri, PredicateConfig.ORG_NAME, Literal(org_name, datatype=XSD.string)))
            graph.add((org_uri, PredicateConfig.ORG_DESCRIPTION, Literal(description, datatype=XSD.string)))
            graph.add((org_uri, PredicateConfig.ORG_EMAIL, Literal(email, datatype=XSD.string)))
            graph.add((org_uri, PredicateConfig.ORG_TELEPHONE, Literal(telephone, datatype=XSD.string)))
            graph.add((org_uri, PredicateConfig.ORG_URL, Literal(url, datatype=XSD.anyURI)))
            graph.add((org_uri, PredicateConfig.ORG_INDUSTRY, Literal(industry, datatype=XSD.string)))
            
            if tax_id:
                graph.add((org_uri, PredicateConfig.ORG_TAX_ID, Literal(tax_id, datatype=XSD.string)))
        
        org_data_list.append({'id': org_id, 'uri': org_uri})
    
    print(f"  ✓ Generated {num_orgs} organizations")
    return org_data_list


def generate_person_with_accounts_and_orders(fake, person_id, max_accounts, max_orders_per_account, 
                                             org_data_list, graph, collector):
    """
    Generate a person with their bank accounts and orders.
    
    Args:
        fake: Faker instance
        person_id: Person identifier number
        max_accounts: Maximum number of bank accounts (will generate 1 to max_accounts)
        max_orders_per_account: Maximum orders per account (will generate 1 to max)
        org_data_list: List of organization data dicts
        graph: RDF graph to add to (None if CSV-only)
        collector: DataCollector instance (None if RDF-only)
    
    Returns:
        tuple: (person_uri, num_accounts, num_orders)
    """
    # Generate person data
    person_uri = EX[f"person_{person_id}"]
    first_name = fake.person_given_name()
    last_name = fake.person_family_name()
    full_name = f"{first_name} {last_name}"
    email = fake.person_email()
    telephone = fake.person_telephone()
    tax_id = fake.person_tax_id()
    
    # Store person data for CSV
    if collector:
        collector.add_person({
            CSVColumns.PERSON_ID: f"person_{person_id}",
            CSVColumns.PERSON_URI: str(person_uri),
            CSVColumns.PERSON_NAME: full_name,
            CSVColumns.PERSON_GIVEN_NAME: first_name,
            CSVColumns.PERSON_FAMILY_NAME: last_name,
            CSVColumns.PERSON_EMAIL: email,
            CSVColumns.PERSON_TELEPHONE: telephone,
            CSVColumns.PERSON_TAX_ID: tax_id
        })
    
    # Add to RDF graph
    if graph is not None:
        graph.add((person_uri, RDF.type, PredicateConfig.PERSON_TYPE))
        graph.add((person_uri, PredicateConfig.PERSON_NAME, Literal(full_name, datatype=XSD.string)))
        graph.add((person_uri, PredicateConfig.PERSON_GIVEN_NAME, Literal(first_name, datatype=XSD.string)))
        graph.add((person_uri, PredicateConfig.PERSON_FAMILY_NAME, Literal(last_name, datatype=XSD.string)))
        graph.add((person_uri, PredicateConfig.PERSON_EMAIL, Literal(email, datatype=XSD.string)))
        graph.add((person_uri, PredicateConfig.PERSON_TELEPHONE, Literal(telephone, datatype=XSD.string)))
        graph.add((person_uri, PredicateConfig.PERSON_TAX_ID, Literal(tax_id, datatype=XSD.string)))
    
    # Generate 1 to max_accounts bank accounts
    num_accounts = random.randint(1, max_accounts)
    total_orders = 0
    
    for account_idx in range(num_accounts):
        account_id = f"person_{person_id}_account_{account_idx+1}"
        account_uri = EX[account_id]
        
        # Generate account data
        account_name = fake.bank_account_name()
        identifier = fake.bank_account_identifier()
        account_type = fake.bank_account_account_type()
        bank_name = fake.bank_account_bank_name()
        balance = fake.bank_account_balance()
        
        # Store account data for CSV
        if collector:
            collector.add_account({
                CSVColumns.ACCOUNT_ID: account_id,
                CSVColumns.ACCOUNT_URI: str(account_uri),
                CSVColumns.ACCOUNT_PERSON_ID: f"person_{person_id}",
                CSVColumns.ACCOUNT_NAME: account_name,
                CSVColumns.ACCOUNT_IDENTIFIER: identifier,
                CSVColumns.ACCOUNT_TYPE_FIELD: account_type,
                CSVColumns.ACCOUNT_BANK: bank_name,
                CSVColumns.ACCOUNT_BALANCE: str(balance)
            })
        
        # Add to RDF graph
        if graph is not None:
            graph.add((account_uri, RDF.type, PredicateConfig.ACCOUNT_TYPE))
            graph.add((account_uri, PredicateConfig.ACCOUNT_NAME, Literal(account_name, datatype=XSD.string)))
            graph.add((account_uri, PredicateConfig.ACCOUNT_IDENTIFIER, Literal(identifier, datatype=XSD.string)))
            graph.add((account_uri, PredicateConfig.ACCOUNT_TYPE_FIELD, Literal(account_type, datatype=XSD.string)))
            graph.add((account_uri, PredicateConfig.ACCOUNT_BANK, Literal(bank_name, datatype=XSD.string)))
            graph.add((account_uri, PredicateConfig.ACCOUNT_BALANCE, Literal(balance, datatype=XSD.decimal)))
            graph.add((account_uri, PredicateConfig.ACCOUNT_HOLDER, person_uri))
        
        # Generate 1 to max_orders_per_account orders for this account
        num_orders = random.randint(1, max_orders_per_account)
        total_orders += num_orders
        
        for order_idx in range(num_orders):
            order_id = f"person_{person_id}_account_{account_idx+1}_order_{order_idx+1}"
            order_uri = EX[order_id]
            
            # Generate order data
            order_number = fake.order_identifier()
            order_status = fake.order_status()
            order_date = fake.order_date()
            total_payment = fake.order_total()
            
            # Select random merchant
            merchant = random.choice(org_data_list)
            merchant_id = merchant['id']
            merchant_uri = merchant['uri']
            
            # Store order data for CSV
            if collector:
                collector.add_order({
                    CSVColumns.ORDER_ID: order_id,
                    CSVColumns.ORDER_URI: str(order_uri),
                    CSVColumns.ORDER_PERSON_ID: f"person_{person_id}",
                    CSVColumns.ORDER_ACCOUNT_ID: account_id,
                    CSVColumns.ORDER_MERCHANT_ID: merchant_id,
                    CSVColumns.ORDER_NUMBER: order_number,
                    CSVColumns.ORDER_STATUS: order_status,
                    CSVColumns.ORDER_DATE: str(order_date),
                    CSVColumns.ORDER_TOTAL: str(total_payment)
                })
            
            # Add to RDF graph
            if graph is not None:
                graph.add((order_uri, RDF.type, PredicateConfig.ORDER_TYPE))
                graph.add((order_uri, PredicateConfig.ORDER_NUMBER, Literal(order_number, datatype=XSD.string)))
                graph.add((order_uri, PredicateConfig.ORDER_STATUS, Literal(order_status, datatype=XSD.string)))
                graph.add((order_uri, PredicateConfig.ORDER_DATE, Literal(order_date, datatype=XSD.date)))               
                graph.add((order_uri, PredicateConfig.ORDER_CUSTOMER, person_uri))
                graph.add((order_uri, PredicateConfig.ORDER_PAYMENT_METHOD, account_uri))
                graph.add((order_uri, PredicateConfig.ORDER_MERCHANT, merchant_uri))
                graph.add((order_uri, PredicateConfig.ORDER_TOTAL, Literal(total_payment, datatype=XSD.decimal)))
            
            # Generate ordered items
            num_items = random.randint(1, 3)
            for item_idx in range(num_items):
                # Generate item name using the correct provider method
                try:
                    item_name = fake.order_item_name()
                except AttributeError:
                    # Fallback to generic product names
                    products = ['Laptop', 'Smartphone', 'Headphones', 'Monitor', 'Keyboard', 
                               'Mouse', 'Tablet', 'Charger', 'USB Cable', 'Webcam',
                               'Desk Lamp', 'Office Chair', 'Notebook', 'Pen Set', 'Backpack']
                    item_name = random.choice(products)
                
                # Store item data for CSV
                if collector:
                    collector.add_order_item({
                        CSVColumns.ITEM_ORDER_ID: order_id,
                        CSVColumns.ITEM_INDEX: item_idx + 1,
                        CSVColumns.ITEM_NAME: item_name
                    })
                
                # Add to RDF graph
                if graph is not None:
                    item_uri = EX[f"{order_id}_item_{item_idx+1}"]
                    graph.add((item_uri, RDF.type, PredicateConfig.ITEM_TYPE))
                    graph.add((item_uri, PredicateConfig.ITEM_NUMBER, Literal(item_idx + 1, datatype=XSD.integer)))
                    graph.add((item_uri, PredicateConfig.ITEM_NAME, Literal(item_name, datatype=XSD.string)))
                    graph.add((order_uri, PredicateConfig.ORDER_ITEM, item_uri))
    
    return person_uri, num_accounts, total_orders


def create_linked_graph(num_people, max_accounts, max_orders_per_account, num_orgs, 
                       seed=None, collect_csv_data=False):
    """
    Create an RDF graph with linked People, BankAccounts, Orders, and Organizations.
    
    Args:
        num_people: Number of people to generate (N)
        max_accounts: Maximum bank accounts per person (Y in 1-Y)
        max_orders_per_account: Maximum orders per account (X in 1-X)
        num_orgs: Number of organizations to generate (Z)
        seed: Random seed for reproducibility
        collect_csv_data: Whether to collect data for CSV export
    
    Returns:
        tuple: (rdflib.Graph or None, DataCollector or None)
    """
    # Initialize Faker with all providers
    if seed is not None:
        Faker.seed(seed)
        random.seed(seed)
    
    fake = Faker()
    fake.add_provider(SchemaOrgPersonProvider)
    fake.add_provider(SchemaOrgOrganizationProvider)
    fake.add_provider(SchemaOrgBankAccountProvider)
    fake.add_provider(SchemaOrgOrderProvider)
    
    # Create graph (if needed for RDF output)
    # graph is needed when collect_csv_data is False (RDF only) or 'both'
    need_graph = (collect_csv_data == False) or (collect_csv_data == 'both')
    g = Graph() if need_graph else None
    if g is not None:
        g.bind("schema", SCHEMA)
        g.bind("custom", CUSTOM)
        g.bind("ex", EX)
    
    # Create collector (if needed for CSV output)
    # collector is needed when collect_csv_data is True or 'both'
    need_collector = (collect_csv_data == True) or (collect_csv_data == 'both')
    collector = DataCollector() if need_collector else None
    
    print(f"\n{'='*80}")
    print("Generating Linked Schema.org Data")
    print(f"{'='*80}")
    print(f"Configuration:")
    print(f"  People: {num_people}")
    print(f"  Bank accounts per person: 1-{max_accounts}")
    print(f"  Orders per account: 1-{max_orders_per_account}")
    print(f"  Organizations: {num_orgs}")
    print(f"{'='*80}\n")
    
    # Step 1: Generate organizations first (they're referenced by orders)
    org_data_list = generate_organizations(fake, num_orgs, g, collector, seed)
    
    # Step 2: Generate people with their accounts and orders
    print(f"\nGenerating {num_people} people with accounts and orders...")
    
    total_accounts = 0
    total_orders = 0
    
    for i in range(num_people):
        person_uri, num_accounts, num_orders = generate_person_with_accounts_and_orders(
            fake, i+1, max_accounts, max_orders_per_account, org_data_list, g, collector
        )
        
        total_accounts += num_accounts
        total_orders += num_orders
        
        if (i + 1) % 10 == 0:
            print(f"  Generated {i + 1}/{num_people} people...")
    
    print(f"  ✓ Generated {num_people} people")
    print(f"\n{'='*80}")
    print("Generation Summary")
    print(f"{'='*80}")
    print(f"  People: {num_people}")
    print(f"  Bank Accounts: {total_accounts} (avg {total_accounts/num_people:.1f} per person)")
    print(f"  Orders: {total_orders} (avg {total_orders/total_accounts:.1f} per account)")
    print(f"  Organizations: {num_orgs}")
    print(f"  Total entities: {num_people + total_accounts + total_orders + num_orgs}")
    if g is not None:
        print(f"  Total triples: {len(g)}")
    print(f"{'='*80}\n")
    
    return g, collector


def export_to_csv(collector, output_file):
    """
    Export collected data to a single denormalized CSV file.
    
    Each row represents an order item with all related data:
    - Order details
    - Person/customer details
    - Bank account details
    - Merchant/organization details
    - Order item details
    """
    # Create lookup dictionaries
    people_lookup = {p[CSVColumns.PERSON_ID]: p for p in collector.people}
    accounts_lookup = {a[CSVColumns.ACCOUNT_ID]: a for a in collector.accounts}
    orgs_lookup = {o[CSVColumns.ORG_ID]: o for o in collector.organizations}
    
    # Build fully denormalized rows (one row per order item)
    denorm_rows = []
    
    for order in collector.orders:
        person = people_lookup.get(order[CSVColumns.ORDER_PERSON_ID], {})
        account = accounts_lookup.get(order[CSVColumns.ORDER_ACCOUNT_ID], {})
        merchant = orgs_lookup.get(order[CSVColumns.ORDER_MERCHANT_ID], {})
        
        # Get all items for this order
        order_items = [item for item in collector.order_items if item[CSVColumns.ITEM_ORDER_ID] == order[CSVColumns.ORDER_ID]]
        
        # If no items, create one row anyway
        if not order_items:
            order_items = [{CSVColumns.ITEM_INDEX: None, CSVColumns.ITEM_NAME: None}]
        
        for item in order_items:
            row = {
                # Order info
                CSVColumns.ORDER_ID: order[CSVColumns.ORDER_ID],
                CSVColumns.ORDER_URI: order[CSVColumns.ORDER_URI],
                CSVColumns.ORDER_NUMBER: order[CSVColumns.ORDER_NUMBER],
                CSVColumns.ORDER_STATUS: order[CSVColumns.ORDER_STATUS],
                CSVColumns.ORDER_DATE: order[CSVColumns.ORDER_DATE],
                CSVColumns.ORDER_TOTAL: order[CSVColumns.ORDER_TOTAL],
                
                # Person/Customer info
                CSVColumns.PERSON_ID: order[CSVColumns.ORDER_PERSON_ID],
                CSVColumns.PERSON_URI: person.get(CSVColumns.PERSON_URI, ''),
                CSVColumns.PERSON_NAME: person.get(CSVColumns.PERSON_NAME, ''),
                CSVColumns.PERSON_GIVEN_NAME: person.get(CSVColumns.PERSON_GIVEN_NAME, ''),
                CSVColumns.PERSON_FAMILY_NAME: person.get(CSVColumns.PERSON_FAMILY_NAME, ''),
                CSVColumns.PERSON_EMAIL: person.get(CSVColumns.PERSON_EMAIL, ''),
                CSVColumns.PERSON_TAX_ID: person.get(CSVColumns.PERSON_TAX_ID, ''),
                CSVColumns.PERSON_TELEPHONE: person.get(CSVColumns.PERSON_TELEPHONE, ''),
                
                # Bank Account info
                CSVColumns.ACCOUNT_ID: order[CSVColumns.ORDER_ACCOUNT_ID],
                CSVColumns.ACCOUNT_URI: account.get(CSVColumns.ACCOUNT_URI, ''),
                CSVColumns.ACCOUNT_NAME: account.get(CSVColumns.ACCOUNT_NAME, ''),
                CSVColumns.ACCOUNT_IDENTIFIER: account.get(CSVColumns.ACCOUNT_IDENTIFIER, ''),

                CSVColumns.ACCOUNT_TYPE_FIELD: account.get(CSVColumns.ACCOUNT_TYPE_FIELD, ''),
                CSVColumns.ACCOUNT_BANK: account.get(CSVColumns.ACCOUNT_BANK, ''),
                CSVColumns.ACCOUNT_BALANCE: account.get(CSVColumns.ACCOUNT_BALANCE, ''),
                
                # Merchant/Organization info
                CSVColumns.ORDER_MERCHANT_ID: order[CSVColumns.ORDER_MERCHANT_ID],
                CSVColumns.ORG_URI: merchant.get(CSVColumns.ORG_URI, ''),
                CSVColumns.ORG_NAME: merchant.get(CSVColumns.ORG_NAME, ''),
                CSVColumns.ORG_DESCRIPTION: merchant.get(CSVColumns.ORG_DESCRIPTION, ''),
                CSVColumns.ORG_EMAIL: merchant.get(CSVColumns.ORG_EMAIL, ''),
                CSVColumns.ORG_TELEPHONE: merchant.get(CSVColumns.ORG_TELEPHONE, ''),
                CSVColumns.ORG_URL: merchant.get(CSVColumns.ORG_URL, ''),
                CSVColumns.ORG_INDUSTRY: merchant.get(CSVColumns.ORG_INDUSTRY, ''),
                CSVColumns.ORG_TAX_ID: merchant.get(CSVColumns.ORG_TAX_ID, ''),
                
                # Order Item info
                CSVColumns.ITEM_INDEX: item.get(CSVColumns.ITEM_INDEX, ''),
                CSVColumns.ITEM_NAME: item.get(CSVColumns.ITEM_NAME, ''),
            }
            denorm_rows.append(row)
    
    # Write to single CSV file
    if denorm_rows:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=denorm_rows[0].keys())
            writer.writeheader()
            writer.writerows(denorm_rows)
        print(f"  ✓ Saved denormalized data to {output_file}")
        print(f"    Total rows: {len(denorm_rows)}")
    else:
        print(f"  ✗ No data to export")


def export_to_3nf_csv(collector, output_prefix):
    """
    Export collected data to multiple normalized CSV files in Third Normal Form (3NF).
    
    Creates separate files for each entity type with proper foreign key relationships:
    - people.csv: Person entities
    - bank_accounts.csv: Bank account entities (with person_id foreign key)
    - organizations.csv: Organization entities
    - orders.csv: Order entities (with person_id, account_id, merchant_id foreign keys)
    - order_items.csv: Order item entities (with order_id foreign key)
    
    This eliminates redundancy and ensures each non-key attribute depends only on the primary key.
    """
    print(f"Exporting data in Third Normal Form (3NF)...")
    
    # Ensure output directory exists
    output_dir = Path(output_prefix).parent
    if output_dir and output_dir != Path('.'):
        output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. People table
    people_file = f"{output_prefix}_people.csv"
    if collector.people:
        with open(people_file, 'w', newline='', encoding='utf-8') as f:
            # Get field names from the first person record
            fieldnames = list(collector.people[0].keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(collector.people)
        print(f"  ✓ Saved {len(collector.people)} people to {people_file}")
    
    # 2. Bank Accounts table (with person_id as foreign key)
    accounts_file = f"{output_prefix}_bank_accounts.csv"
    if collector.accounts:
        with open(accounts_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = list(collector.accounts[0].keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(collector.accounts)
        print(f"  ✓ Saved {len(collector.accounts)} bank accounts to {accounts_file}")
    
    # 3. Organizations table
    orgs_file = f"{output_prefix}_organizations.csv"
    if collector.organizations:
        with open(orgs_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = list(collector.organizations[0].keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(collector.organizations)
        print(f"  ✓ Saved {len(collector.organizations)} organizations to {orgs_file}")
    
    # 4. Orders table (with person_id, account_id, merchant_id as foreign keys)
    orders_file = f"{output_prefix}_orders.csv"
    if collector.orders:
        with open(orders_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = list(collector.orders[0].keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(collector.orders)
        print(f"  ✓ Saved {len(collector.orders)} orders to {orders_file}")
    
    # 5. Order Items table (with order_id as foreign key)
    items_file = f"{output_prefix}_order_items.csv"
    if collector.order_items:
        with open(items_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = list(collector.order_items[0].keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(collector.order_items)
        print(f"  ✓ Saved {len(collector.order_items)} order items to {items_file}")
    
    print(f"\n  ✓ 3NF export complete!")
    print(f"    Created 5 normalized tables with proper foreign key relationships")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Generate linked Schema.org data with People, BankAccounts, Orders, and Organizations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate RDF turtle file
  python generate_data.py -n 10 -y 2 -x 3 -z 5 -o linked_data.ttl
  
  # Generate CSV files (both denormalized and 3NF normalized)
  python generate_data.py -n 10 -y 2 -x 3 -z 5 -o data --format csv
  
  # Generate both RDF and CSV
  python generate_data.py -n 10 -y 2 -x 3 -z 5 -o data --format both
  
  # Use seed for reproducibility
  python generate_data.py -n 50 -y 2 -x 4 -z 10 --seed 42 -o reproducible --format csv
        """
    )
    
    parser.add_argument(
        "-n", "--num-people",
        type=int,
        default=10,
        help="Number of people to generate (default: 10)"
    )
    
    parser.add_argument(
        "-y", "--max-accounts",
        type=int,
        default=2,
        help="Maximum bank accounts per person (generates 1-Y accounts, default: 2)"
    )
    
    parser.add_argument(
        "-x", "--max-orders",
        type=int,
        default=3,
        help="Maximum orders per account (generates 1-X orders, default: 3)"
    )
    
    parser.add_argument(
        "-z", "--num-organizations",
        type=int,
        default=5,
        help="Number of organizations to generate (default: 5)"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="linked_data",
        help="Output file path/prefix (default: linked_data)"
    )
    
    parser.add_argument(
        "--format",
        type=str,
        default="turtle",
        choices=["turtle", "xml", "n3", "nt", "json-ld", "csv", "both"],
        help="Output format: RDF formats, csv (denormalized + 3NF), or both (default: turtle)"
    )
    
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.num_people <= 0:
        print("Error: num-people must be positive", file=sys.stderr)
        return 1
    
    if args.max_accounts <= 0:
        print("Error: max-accounts must be positive", file=sys.stderr)
        return 1
    
    if args.max_orders <= 0:
        print("Error: max-orders must be positive", file=sys.stderr)
        return 1
    
    if args.num_organizations <= 0:
        print("Error: num-organizations must be positive", file=sys.stderr)
        return 1
    
    try:
        # Determine what to generate
        generate_rdf = args.format not in ['csv']
        generate_csv = args.format in ['csv', 'both']
        
        # Generate the data
        collect_mode = 'both' if args.format == 'both' else (True if generate_csv else False)
        graph, collector = create_linked_graph(
            num_people=args.num_people,
            max_accounts=args.max_accounts,
            max_orders_per_account=args.max_orders,
            num_orgs=args.num_organizations,
            seed=args.seed,
            collect_csv_data=collect_mode
        )
        
        # Save outputs
        print(f"\nSaving outputs...")
        
        if generate_rdf and graph is not None:
            rdf_output_file = args.output if args.output.endswith(('.ttl', '.xml', '.n3', '.nt', '.jsonld')) else f"{args.output}.ttl"
            graph.serialize(destination=rdf_output_file, format=args.format if args.format != 'both' else 'turtle')
            print(f"  ✓ Saved RDF to {rdf_output_file}")
        
        if generate_csv and collector:
            # Generate denormalized CSV
            csv_output_file = args.output if args.output.endswith('.csv') else f"{args.output}_denormalized.csv"
            export_to_csv(collector, csv_output_file)
            
            # Generate 3NF normalized CSVs
            export_to_3nf_csv(collector, args.output)
        
        print(f"\n✓ Generation complete!\n")
        
        return 0
        
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())