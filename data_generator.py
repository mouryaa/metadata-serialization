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
Both schema.org and custom vocabularies are supported.
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

class SchemaOrgPredicateConfig:
    """Configuration for Schema.org RDF predicates."""
    
    # Person predicates (Schema.org)
    PERSON_TYPE = SCHEMA.Person
    PERSON_NAME = SCHEMA.name
    PERSON_GIVEN_NAME = SCHEMA.givenName
    PERSON_FAMILY_NAME = SCHEMA.familyName
    PERSON_EMAIL = SCHEMA.email
    PERSON_TELEPHONE = SCHEMA.telephone
    PERSON_TAX_ID = SCHEMA.taxID
    PERSON_STREET_ADDRESS = SCHEMA.streetAddress
    PERSON_COUNTRY = SCHEMA.addressCountry
    
    # Bank Account predicates (Schema.org)
    ACCOUNT_TYPE = SCHEMA.BankAccount
    ACCOUNT_NAME = SCHEMA.name
    ACCOUNT_IDENTIFIER = SCHEMA.accountId
    ACCOUNT_TYPE_FIELD = SCHEMA.accountType
    ACCOUNT_BANK = SCHEMA.bankName
    ACCOUNT_BALANCE = SCHEMA.amount
    ACCOUNT_HOLDER = SCHEMA.accountHolder
    
    # Organization predicates (Schema.org)
    ORG_TYPE = SCHEMA.Organization
    ORG_NAME = SCHEMA.name
    ORG_DESCRIPTION = SCHEMA.description
    ORG_EMAIL = SCHEMA.email
    ORG_TELEPHONE = SCHEMA.telephone
    ORG_URL = SCHEMA.url
    ORG_INDUSTRY = SCHEMA.industry
    ORG_TAX_ID = SCHEMA.taxID
    ORG_STREET_ADDRESS = SCHEMA.streetAddress
    ORG_COUNTRY = SCHEMA.addressCountry
    
    # Order predicates (Schema.org)
    ORDER_TYPE = SCHEMA.Order
    ORDER_NUMBER = SCHEMA.orderNumber
    ORDER_STATUS = SCHEMA.orderStatus
    ORDER_DATE = SCHEMA.orderDate
    ORDER_TOTAL = SCHEMA.totalPrice
    ORDER_CUSTOMER = SCHEMA.customer
    ORDER_PAYMENT_METHOD = SCHEMA.paymentMethod
    ORDER_MERCHANT = SCHEMA.seller
    ORDER_ITEM = SCHEMA.orderedItem
    
    # Order Item predicates (Schema.org)
    ITEM_TYPE = SCHEMA.OrderItem
    ITEM_NUMBER = SCHEMA.orderItemNumber
    ITEM_NAME = SCHEMA.name


class CustomPredicateConfig:
    """Configuration for custom RDF predicates."""
    
    # Person/Customer predicates
    PERSON_TYPE = CUSTOM.customer           # Type: Customer instead of Person
    PERSON_NAME = CUSTOM.cust_full_name
    PERSON_GIVEN_NAME = CUSTOM.cust_first_name
    PERSON_FAMILY_NAME = CUSTOM.cust_last_name
    PERSON_EMAIL = CUSTOM.cust_email_address
    PERSON_TELEPHONE = CUSTOM.cust_phone_number
    PERSON_TAX_ID = CUSTOM.customer_id
    PERSON_STREET_ADDRESS = CUSTOM.cust_street_address
    PERSON_COUNTRY = CUSTOM.cust_country
    
    # Bank Account predicates
    ACCOUNT_TYPE = CUSTOM.bank_account
    ACCOUNT_NAME = CUSTOM.bank_account_name
    ACCOUNT_IDENTIFIER = CUSTOM.bank_account_id
    ACCOUNT_TYPE_FIELD = CUSTOM.bank_account_typ
    ACCOUNT_BANK = CUSTOM.bank_name
    ACCOUNT_BALANCE = CUSTOM.balance
    ACCOUNT_HOLDER = CUSTOM.bank_account_owner
    
    # Organization predicates
    ORG_TYPE = CUSTOM.company
    ORG_NAME = CUSTOM.compan_name
    ORG_DESCRIPTION = CUSTOM.company_description
    ORG_EMAIL = CUSTOM.company_email
    ORG_TELEPHONE = CUSTOM.company_phone
    ORG_URL = CUSTOM.company_url
    ORG_INDUSTRY = CUSTOM.company_industry
    ORG_TAX_ID = CUSTOM.company_id
    ORG_STREET_ADDRESS = CUSTOM.company_street_address
    ORG_COUNTRY = CUSTOM.company_country
    
    # Order predicates
    ORDER_TYPE = CUSTOM.transaction
    ORDER_NUMBER = CUSTOM.order_number
    ORDER_STATUS = CUSTOM.order_status
    ORDER_DATE = CUSTOM.order_date
    ORDER_TOTAL = CUSTOM.order_total
    ORDER_CUSTOMER = CUSTOM.order_customer
    ORDER_PAYMENT_METHOD = CUSTOM.order_payment_type
    ORDER_MERCHANT = CUSTOM.order_company
    ORDER_ITEM = CUSTOM.order_item
    
    # Order Item predicates
    ITEM_TYPE = CUSTOM.line_item_type
    ITEM_NUMBER = CUSTOM.item_number
    ITEM_NAME = CUSTOM.item_product_name


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
    
    @staticmethod
    def create_columns(predicate_config):
        """Create column names from a predicate configuration."""
        # Check if this is schema.org (which has duplicate predicates) or custom
        is_schema_org = str(predicate_config.PERSON_NAME).startswith('http://schema.org/')
        
        if is_schema_org:
            # For schema.org, add entity prefixes to avoid collisions
            # since schema:name, schema:email, etc. are used for multiple entities
            return {
                # Person columns
                'PERSON_ID': 'person_id',
                'PERSON_URI': 'person_uri',
                'PERSON_TYPE': CSVColumns.get_local_name(predicate_config.PERSON_TYPE),
                'PERSON_NAME': 'person_' + CSVColumns.get_local_name(predicate_config.PERSON_NAME),
                'PERSON_GIVEN_NAME': CSVColumns.get_local_name(predicate_config.PERSON_GIVEN_NAME),
                'PERSON_FAMILY_NAME': CSVColumns.get_local_name(predicate_config.PERSON_FAMILY_NAME),
                'PERSON_EMAIL': 'person_' + CSVColumns.get_local_name(predicate_config.PERSON_EMAIL),
                'PERSON_TELEPHONE': 'person_' + CSVColumns.get_local_name(predicate_config.PERSON_TELEPHONE),
                'PERSON_TAX_ID': 'person_' + CSVColumns.get_local_name(predicate_config.PERSON_TAX_ID),
                'PERSON_STREET_ADDRESS': 'person_' + CSVColumns.get_local_name(predicate_config.PERSON_STREET_ADDRESS),
                'PERSON_COUNTRY': 'person_' + CSVColumns.get_local_name(predicate_config.PERSON_COUNTRY),
                
                # Bank Account columns
                'ACCOUNT_ID': 'account_id',
                'ACCOUNT_URI': 'account_uri',
                'ACCOUNT_PERSON_ID': 'person_id',
                'ACCOUNT_NAME': 'account_' + CSVColumns.get_local_name(predicate_config.ACCOUNT_NAME),
                'ACCOUNT_IDENTIFIER': CSVColumns.get_local_name(predicate_config.ACCOUNT_IDENTIFIER),
                'ACCOUNT_TYPE_FIELD': 'account_' + CSVColumns.get_local_name(predicate_config.ACCOUNT_TYPE_FIELD),
                'ACCOUNT_BANK': CSVColumns.get_local_name(predicate_config.ACCOUNT_BANK),
                'ACCOUNT_BALANCE': 'account_' + CSVColumns.get_local_name(predicate_config.ACCOUNT_BALANCE),
                
                # Organization columns
                'ORG_ID': 'org_id',
                'ORG_URI': 'org_uri',
                'ORG_NAME': 'org_' + CSVColumns.get_local_name(predicate_config.ORG_NAME),
                'ORG_DESCRIPTION': CSVColumns.get_local_name(predicate_config.ORG_DESCRIPTION),
                'ORG_EMAIL': 'org_' + CSVColumns.get_local_name(predicate_config.ORG_EMAIL),
                'ORG_TELEPHONE': 'org_' + CSVColumns.get_local_name(predicate_config.ORG_TELEPHONE),
                'ORG_URL': CSVColumns.get_local_name(predicate_config.ORG_URL),
                'ORG_INDUSTRY': CSVColumns.get_local_name(predicate_config.ORG_INDUSTRY),
                'ORG_TAX_ID': 'org_' + CSVColumns.get_local_name(predicate_config.ORG_TAX_ID),
                'ORG_STREET_ADDRESS': 'org_' + CSVColumns.get_local_name(predicate_config.ORG_STREET_ADDRESS),
                'ORG_COUNTRY': 'org_' + CSVColumns.get_local_name(predicate_config.ORG_COUNTRY),
                
                # Order columns
                'ORDER_ID': 'order_id',
                'ORDER_URI': 'order_uri',
                'ORDER_PERSON_ID': 'person_id',
                'ORDER_ACCOUNT_ID': 'account_id',
                'ORDER_MERCHANT_ID': 'merchant_id',
                'ORDER_NUMBER': CSVColumns.get_local_name(predicate_config.ORDER_NUMBER),
                'ORDER_STATUS': CSVColumns.get_local_name(predicate_config.ORDER_STATUS),
                'ORDER_DATE': CSVColumns.get_local_name(predicate_config.ORDER_DATE),
                'ORDER_TOTAL': CSVColumns.get_local_name(predicate_config.ORDER_TOTAL),
                
                # Order Item columns
                'ITEM_ORDER_ID': 'order_id',
                'ITEM_INDEX': 'item_index',
                'ITEM_NAME': 'item_' + CSVColumns.get_local_name(predicate_config.ITEM_NAME),
            }
        else:
            # For custom vocabulary, predicates are already unique, so use them as-is
            return {
                # Person columns
                'PERSON_ID': 'person_id',
                'PERSON_URI': 'person_uri',
                'PERSON_TYPE': CSVColumns.get_local_name(predicate_config.PERSON_TYPE),
                'PERSON_NAME': CSVColumns.get_local_name(predicate_config.PERSON_NAME),
                'PERSON_GIVEN_NAME': CSVColumns.get_local_name(predicate_config.PERSON_GIVEN_NAME),
                'PERSON_FAMILY_NAME': CSVColumns.get_local_name(predicate_config.PERSON_FAMILY_NAME),
                'PERSON_EMAIL': CSVColumns.get_local_name(predicate_config.PERSON_EMAIL),
                'PERSON_TELEPHONE': CSVColumns.get_local_name(predicate_config.PERSON_TELEPHONE),
                'PERSON_TAX_ID': CSVColumns.get_local_name(predicate_config.PERSON_TAX_ID),
                'PERSON_STREET_ADDRESS': CSVColumns.get_local_name(predicate_config.PERSON_STREET_ADDRESS),
                'PERSON_COUNTRY': CSVColumns.get_local_name(predicate_config.PERSON_COUNTRY),
                
                # Bank Account columns
                'ACCOUNT_ID': 'account_id',
                'ACCOUNT_URI': 'account_uri',
                'ACCOUNT_PERSON_ID': 'person_id',
                'ACCOUNT_NAME': CSVColumns.get_local_name(predicate_config.ACCOUNT_NAME),
                'ACCOUNT_IDENTIFIER': CSVColumns.get_local_name(predicate_config.ACCOUNT_IDENTIFIER),
                'ACCOUNT_TYPE_FIELD': CSVColumns.get_local_name(predicate_config.ACCOUNT_TYPE_FIELD),
                'ACCOUNT_BANK': CSVColumns.get_local_name(predicate_config.ACCOUNT_BANK),
                'ACCOUNT_BALANCE': CSVColumns.get_local_name(predicate_config.ACCOUNT_BALANCE),
                
                # Organization columns
                'ORG_ID': 'org_id',
                'ORG_URI': 'org_uri',
                'ORG_NAME': CSVColumns.get_local_name(predicate_config.ORG_NAME),
                'ORG_DESCRIPTION': CSVColumns.get_local_name(predicate_config.ORG_DESCRIPTION),
                'ORG_EMAIL': CSVColumns.get_local_name(predicate_config.ORG_EMAIL),
                'ORG_TELEPHONE': CSVColumns.get_local_name(predicate_config.ORG_TELEPHONE),
                'ORG_URL': CSVColumns.get_local_name(predicate_config.ORG_URL),
                'ORG_INDUSTRY': CSVColumns.get_local_name(predicate_config.ORG_INDUSTRY),
                'ORG_TAX_ID': CSVColumns.get_local_name(predicate_config.ORG_TAX_ID),
                'ORG_STREET_ADDRESS': CSVColumns.get_local_name(predicate_config.ORG_STREET_ADDRESS),
                'ORG_COUNTRY': CSVColumns.get_local_name(predicate_config.ORG_COUNTRY),
                
                # Order columns
                'ORDER_ID': 'order_id',
                'ORDER_URI': 'order_uri',
                'ORDER_PERSON_ID': 'person_id',
                'ORDER_ACCOUNT_ID': 'account_id',
                'ORDER_MERCHANT_ID': 'merchant_id',
                'ORDER_NUMBER': CSVColumns.get_local_name(predicate_config.ORDER_NUMBER),
                'ORDER_STATUS': CSVColumns.get_local_name(predicate_config.ORDER_STATUS),
                'ORDER_DATE': CSVColumns.get_local_name(predicate_config.ORDER_DATE),
                'ORDER_TOTAL': CSVColumns.get_local_name(predicate_config.ORDER_TOTAL),
                
                # Order Item columns
                'ITEM_ORDER_ID': 'order_id',
                'ITEM_INDEX': 'item_index',
                'ITEM_NAME': CSVColumns.get_local_name(predicate_config.ITEM_NAME),
            }

# ============================================================================
# END PREDICATE CONFIGURATION
# ============================================================================


class DataCollector:
    """Collects data for both RDF and CSV export."""
    
    def __init__(self, column_names):
        self.column_names = column_names
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


class RawDataStore:
    """
    Stores the raw generated data values (independent of vocabulary).
    This ensures all outputs use the same underlying data.
    """
    def __init__(self):
        self.organizations = []
        self.people = []
        self.accounts = []
        self.orders = []
        self.order_items = []


def generate_raw_data(fake, num_people, max_accounts, max_orders_per_account, num_orgs, seed=None):
    """
    Generate the raw data values (independent of vocabulary/predicates).
    This data will be reused across all vocabulary outputs.
    """
    if seed is not None:
        Faker.seed(seed)
        random.seed(seed)
    
    store = RawDataStore()
    
    # Generate organizations
    print(f"Generating {num_orgs} organizations...")
    for i in range(num_orgs):
        org_id = f"org_{i+1}"
        org_uri = EX[org_id]
        
        org_data = {
            'id': org_id,
            'uri': org_uri,
            'name': fake.organization_name(),
            'description': fake.organization_description(),
            'email': fake.organization_email(),
            'telephone': fake.organization_telephone(),
            'url': fake.organization_url(),
            'industry': fake.organization_industry(),
            'tax_id': fake.organization_tax_id(),
            'street_address': fake.organization_street_address(),
            'country': fake.organization_country(),
        }
        store.organizations.append(org_data)
    
    # Generate people
    print(f"Generating {num_people} people...")
    for i in range(num_people):
        person_id = f"person_{i+1}"
        person_uri = EX[person_id]
        
        # Generate given name and family name first
        given_name = fake.person_given_name()
        family_name = fake.person_family_name()
        # Combine them to create the full name
        full_name = f"{given_name} {family_name}"
        
        person_data = {
            'id': person_id,
            'uri': person_uri,
            'name': full_name,
            'given_name': given_name,
            'family_name': family_name,
            'email': fake.person_email(),
            'telephone': fake.person_telephone(),
            'tax_id': fake.person_tax_id(),
            'street_address': fake.person_street_address(),
            'country': fake.person_country(),
        }
        store.people.append(person_data)
    
    # Generate bank accounts
    print(f"Generating bank accounts (1-{max_accounts} per person)...")
    for person_data in store.people:
        num_accounts = random.randint(1, max_accounts)
        
        for j in range(num_accounts):
            account_id = f"{person_data['id']}_account_{j+1}"
            account_uri = EX[account_id]
            
            account_data = {
                'id': account_id,
                'uri': account_uri,
                'person_id': person_data['id'],
                'person_uri': person_data['uri'],
                'name': fake.bank_account_name(),
                'identifier': fake.bank_account_identifier(),
                'type': fake.bank_account_type(),
                'bank': fake.bank_name(),
                'balance': fake.bank_balance(),
            }
            store.accounts.append(account_data)
    
    # Generate orders
    print(f"Generating orders (1-{max_orders_per_account} per account)...")
    for account_data in store.accounts:
        num_orders = random.randint(1, max_orders_per_account)
        
        for k in range(num_orders):
            order_id = f"{account_data['id']}_order_{k+1}"
            order_uri = EX[order_id]
            
            # Pick a random organization as merchant
            merchant_data = random.choice(store.organizations)
            
            order_data = {
                'id': order_id,
                'uri': order_uri,
                'person_id': account_data['person_id'],
                'person_uri': account_data['person_uri'],
                'account_id': account_data['id'],
                'account_uri': account_data['uri'],
                'merchant_id': merchant_data['id'],
                'merchant_uri': merchant_data['uri'],
                'number': fake.order_number(),
                'status': fake.order_status(),
                'date': fake.order_date(),
                'total': fake.order_total(),
            }
            store.orders.append(order_data)
            
            # Generate order items
            num_items = random.randint(1, 3)
            for item_idx in range(num_items):
                item_data = {
                    'order_id': order_id,
                    'order_uri': order_uri,
                    'index': item_idx + 1,
                    'name': fake.order_item_name(),
                }
                store.order_items.append(item_data)
    
    # Print summary
    print(f"\nGeneration Summary:")
    print(f"  Organizations: {len(store.organizations)}")
    print(f"  People: {len(store.people)}")
    print(f"  Bank Accounts: {len(store.accounts)}")
    print(f"  Orders: {len(store.orders)}")
    print(f"  Order Items: {len(store.order_items)}")
    
    return store


def populate_graph_and_collector(raw_store, graph, collector, predicate_config):
    """
    Populate a graph and/or collector using the raw data store.
    This ensures the same data is used regardless of vocabulary.
    """
    
    # Add organizations
    for org in raw_store.organizations:
        if graph is not None:
            graph.add((org['uri'], RDF.type, predicate_config.ORG_TYPE))
            graph.add((org['uri'], predicate_config.ORG_NAME, Literal(org['name'])))
            graph.add((org['uri'], predicate_config.ORG_DESCRIPTION, Literal(org['description'])))
            graph.add((org['uri'], predicate_config.ORG_EMAIL, Literal(org['email'])))
            graph.add((org['uri'], predicate_config.ORG_TELEPHONE, Literal(org['telephone'])))
            graph.add((org['uri'], predicate_config.ORG_URL, Literal(org['url'])))
            graph.add((org['uri'], predicate_config.ORG_INDUSTRY, Literal(org['industry'])))
            graph.add((org['uri'], predicate_config.ORG_TAX_ID, Literal(org['tax_id'])))
            graph.add((org['uri'], predicate_config.ORG_STREET_ADDRESS, Literal(org['street_address'])))
            graph.add((org['uri'], predicate_config.ORG_COUNTRY, Literal(org['country'])))
        
        if collector is not None:
            cols = collector.column_names
            collector.add_organization({
                cols['ORG_ID']: org['id'],
                cols['ORG_URI']: str(org['uri']),
                cols['ORG_NAME']: org['name'],
                cols['ORG_DESCRIPTION']: org['description'],
                cols['ORG_EMAIL']: org['email'],
                cols['ORG_TELEPHONE']: org['telephone'],
                cols['ORG_URL']: org['url'],
                cols['ORG_INDUSTRY']: org['industry'],
                cols['ORG_TAX_ID']: org['tax_id'],
                cols['ORG_STREET_ADDRESS']: org['street_address'],
                cols['ORG_COUNTRY']: org['country'],
            })
    
    # Add people
    for person in raw_store.people:
        if graph is not None:
            graph.add((person['uri'], RDF.type, predicate_config.PERSON_TYPE))
            graph.add((person['uri'], predicate_config.PERSON_NAME, Literal(person['name'])))
            graph.add((person['uri'], predicate_config.PERSON_GIVEN_NAME, Literal(person['given_name'])))
            graph.add((person['uri'], predicate_config.PERSON_FAMILY_NAME, Literal(person['family_name'])))
            graph.add((person['uri'], predicate_config.PERSON_EMAIL, Literal(person['email'])))
            graph.add((person['uri'], predicate_config.PERSON_TELEPHONE, Literal(person['telephone'])))
            graph.add((person['uri'], predicate_config.PERSON_TAX_ID, Literal(person['tax_id'])))
            graph.add((person['uri'], predicate_config.PERSON_STREET_ADDRESS, Literal(person['street_address'])))
            graph.add((person['uri'], predicate_config.PERSON_COUNTRY, Literal(person['country'])))
        
        if collector is not None:
            cols = collector.column_names
            collector.add_person({
                cols['PERSON_ID']: person['id'],
                cols['PERSON_URI']: str(person['uri']),
                cols['PERSON_NAME']: person['name'],
                cols['PERSON_GIVEN_NAME']: person['given_name'],
                cols['PERSON_FAMILY_NAME']: person['family_name'],
                cols['PERSON_EMAIL']: person['email'],
                cols['PERSON_TELEPHONE']: person['telephone'],
                cols['PERSON_TAX_ID']: person['tax_id'],
                cols['PERSON_STREET_ADDRESS']: person['street_address'],
                cols['PERSON_COUNTRY']: person['country'],
            })
    
    # Add accounts
    for account in raw_store.accounts:
        if graph is not None:
            graph.add((account['uri'], RDF.type, predicate_config.ACCOUNT_TYPE))
            graph.add((account['uri'], predicate_config.ACCOUNT_NAME, Literal(account['name'])))
            graph.add((account['uri'], predicate_config.ACCOUNT_IDENTIFIER, Literal(account['identifier'])))
            graph.add((account['uri'], predicate_config.ACCOUNT_TYPE_FIELD, Literal(account['type'])))
            graph.add((account['uri'], predicate_config.ACCOUNT_BANK, Literal(account['bank'])))
            graph.add((account['uri'], predicate_config.ACCOUNT_BALANCE, Literal(account['balance'], datatype=XSD.decimal)))
            graph.add((account['uri'], predicate_config.ACCOUNT_HOLDER, account['person_uri']))
        
        if collector is not None:
            cols = collector.column_names
            collector.add_account({
                cols['ACCOUNT_ID']: account['id'],
                cols['ACCOUNT_URI']: str(account['uri']),
                cols['ACCOUNT_PERSON_ID']: account['person_id'],
                cols['ACCOUNT_NAME']: account['name'],
                cols['ACCOUNT_IDENTIFIER']: account['identifier'],
                cols['ACCOUNT_TYPE_FIELD']: account['type'],
                cols['ACCOUNT_BANK']: account['bank'],
                cols['ACCOUNT_BALANCE']: str(account['balance']),
            })
    
    # Add orders
    for order in raw_store.orders:
        if graph is not None:
            graph.add((order['uri'], RDF.type, predicate_config.ORDER_TYPE))
            graph.add((order['uri'], predicate_config.ORDER_NUMBER, Literal(order['number'])))
            graph.add((order['uri'], predicate_config.ORDER_STATUS, Literal(order['status'])))
            graph.add((order['uri'], predicate_config.ORDER_DATE, Literal(order['date'], datatype=XSD.date)))
            graph.add((order['uri'], predicate_config.ORDER_TOTAL, Literal(order['total'], datatype=XSD.decimal)))
            graph.add((order['uri'], predicate_config.ORDER_CUSTOMER, order['person_uri']))
            graph.add((order['uri'], predicate_config.ORDER_PAYMENT_METHOD, order['account_uri']))
            graph.add((order['uri'], predicate_config.ORDER_MERCHANT, order['merchant_uri']))
        
        if collector is not None:
            cols = collector.column_names
            collector.add_order({
                cols['ORDER_ID']: order['id'],
                cols['ORDER_URI']: str(order['uri']),
                cols['ORDER_PERSON_ID']: order['person_id'],
                cols['ORDER_ACCOUNT_ID']: order['account_id'],
                cols['ORDER_MERCHANT_ID']: order['merchant_id'],
                cols['ORDER_NUMBER']: order['number'],
                cols['ORDER_STATUS']: order['status'],
                cols['ORDER_DATE']: str(order['date']),
                cols['ORDER_TOTAL']: str(order['total']),
            })
    
    # Add order items
    for item in raw_store.order_items:
        if graph is not None:
            item_uri = EX[f"{item['order_id']}_item_{item['index']}"]
            graph.add((item_uri, RDF.type, predicate_config.ITEM_TYPE))
            graph.add((item_uri, predicate_config.ITEM_NUMBER, Literal(item['index'])))
            graph.add((item_uri, predicate_config.ITEM_NAME, Literal(item['name'])))
            graph.add((item['order_uri'], predicate_config.ORDER_ITEM, item_uri))
        
        if collector is not None:
            cols = collector.column_names
            collector.add_order_item({
                cols['ITEM_ORDER_ID']: item['order_id'],
                cols['ITEM_INDEX']: item['index'],
                cols['ITEM_NAME']: item['name'],
            })


def export_to_csv(collector, output_file):
    """
    Export collected data to a denormalized CSV file.
    
    Creates a single CSV with all order information, including redundant person,
    account, and organization data for each order row.
    """
    print(f"Exporting denormalized data to CSV...")
    
    if not collector.orders:
        print(f"  ✗ No data to export")
        return
    
    # Create denormalized rows by joining all data
    denorm_rows = []
    cols = collector.column_names
    
    for order in collector.orders:
        # Find matching person
        person = next((p for p in collector.people if p[cols['PERSON_ID']] == order[cols['ORDER_PERSON_ID']]), None)
        
        # Find matching account
        account = next((a for a in collector.accounts if a[cols['ACCOUNT_ID']] == order[cols['ORDER_ACCOUNT_ID']]), None)
        
        # Find matching organization
        org = next((o for o in collector.organizations if o[cols['ORG_ID']] == order[cols['ORDER_MERCHANT_ID']]), None)
        
        # Find matching order items
        items = [item for item in collector.order_items if item[cols['ITEM_ORDER_ID']] == order[cols['ORDER_ID']]]
        
        # Create a row combining all data
        if person and account and org:
            # Combine item names
            item_names = '; '.join([item[cols['ITEM_NAME']] for item in items])
            
            row = {
                # Person fields
                cols['PERSON_ID']: person[cols['PERSON_ID']],
                cols['PERSON_NAME']: person[cols['PERSON_NAME']],
                cols['PERSON_GIVEN_NAME']: person[cols['PERSON_GIVEN_NAME']],
                cols['PERSON_FAMILY_NAME']: person[cols['PERSON_FAMILY_NAME']],
                cols['PERSON_EMAIL']: person[cols['PERSON_EMAIL']],
                cols['PERSON_TELEPHONE']: person[cols['PERSON_TELEPHONE']],
                cols['PERSON_TAX_ID']: person[cols['PERSON_TAX_ID']],
                cols['PERSON_STREET_ADDRESS']: person[cols['PERSON_STREET_ADDRESS']],
                cols['PERSON_COUNTRY']: person[cols['PERSON_COUNTRY']],
                
                # Account fields
                cols['ACCOUNT_ID']: account[cols['ACCOUNT_ID']],
                cols['ACCOUNT_NAME']: account[cols['ACCOUNT_NAME']],
                cols['ACCOUNT_IDENTIFIER']: account[cols['ACCOUNT_IDENTIFIER']],
                cols['ACCOUNT_TYPE_FIELD']: account[cols['ACCOUNT_TYPE_FIELD']],
                cols['ACCOUNT_BANK']: account[cols['ACCOUNT_BANK']],
                cols['ACCOUNT_BALANCE']: account[cols['ACCOUNT_BALANCE']],
                
                # Organization fields
                cols['ORG_ID']: org[cols['ORG_ID']],
                cols['ORG_NAME']: org[cols['ORG_NAME']],
                cols['ORG_DESCRIPTION']: org[cols['ORG_DESCRIPTION']],
                cols['ORG_EMAIL']: org[cols['ORG_EMAIL']],
                cols['ORG_TELEPHONE']: org[cols['ORG_TELEPHONE']],
                cols['ORG_URL']: org[cols['ORG_URL']],
                cols['ORG_INDUSTRY']: org[cols['ORG_INDUSTRY']],
                cols['ORG_TAX_ID']: org[cols['ORG_TAX_ID']],
                cols['ORG_STREET_ADDRESS']: org[cols['ORG_STREET_ADDRESS']],
                cols['ORG_COUNTRY']: org[cols['ORG_COUNTRY']],
                
                # Order fields
                cols['ORDER_ID']: order[cols['ORDER_ID']],
                cols['ORDER_NUMBER']: order[cols['ORDER_NUMBER']],
                cols['ORDER_STATUS']: order[cols['ORDER_STATUS']],
                cols['ORDER_DATE']: order[cols['ORDER_DATE']],
                cols['ORDER_TOTAL']: order[cols['ORDER_TOTAL']],
                
                # Order items (concatenated)
                cols['ITEM_NAME']: item_names,
            }
            denorm_rows.append(row)
    
    # Write to CSV
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
  # Generate turtle file with Schema.org properties
  python data_generator.py -n 10 -y 2 -x 3 -z 5 -o schema_data.ttl --vocab schema
  
  # Generate turtle file with custom properties
  python data_generator.py -n 10 -y 2 -x 3 -z 5 -o custom_data.ttl --vocab custom
  
  # Generate denormalized CSV with Schema.org column names
  python data_generator.py -n 10 -y 2 -x 3 -z 5 -o schema_denorm.csv --format csv --vocab schema
  
  # Generate denormalized CSV with custom column names
  python data_generator.py -n 10 -y 2 -x 3 -z 5 -o custom_denorm.csv --format csv --vocab custom
  
  # Generate 3NF CSVs with Schema.org column names
  python data_generator.py -n 10 -y 2 -x 3 -z 5 -o schema_3nf --format csv --vocab schema
  
  # Generate 3NF CSVs with custom column names
  python data_generator.py -n 10 -y 2 -x 3 -z 5 -o custom_3nf --format csv --vocab custom
  
  # Generate everything: turtle + all CSV formats with both vocabularies (same data!)
  python data_generator.py -n 10 -y 2 -x 3 -z 5 -o data --format all --vocab both --seed 42
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
        default="data",
        help="Output file path/prefix (default: data)"
    )
    
    parser.add_argument(
        "--format",
        type=str,
        default="turtle",
        choices=["turtle", "xml", "n3", "nt", "json-ld", "csv", "all"],
        help="Output format: RDF formats, csv, or all (default: turtle)"
    )
    
    parser.add_argument(
        "--vocab",
        type=str,
        default="schema",
        choices=["schema", "custom", "both"],
        help="Vocabulary to use: schema (schema.org), custom, or both (default: schema)"
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
        # Determine what vocabularies to use
        use_schema = args.vocab in ['schema', 'both']
        use_custom = args.vocab in ['custom', 'both']
        
        # Determine what formats to generate
        generate_rdf = args.format not in ['csv']
        generate_csv = args.format in ['csv', 'all']
        generate_all = args.format == 'all'
        
        print(f"\n{'='*70}")
        print(f"DATA GENERATION CONFIGURATION")
        print(f"{'='*70}")
        print(f"Format: {args.format}")
        print(f"Vocabulary: {args.vocab}")
        print(f"Output prefix: {args.output}")
        if args.seed:
            print(f"Seed: {args.seed}")
        print(f"{'='*70}\n")
        
        # Initialize Faker with custom providers
        fake = Faker()
        fake.add_provider(SchemaOrgPersonProvider)
        fake.add_provider(SchemaOrgOrganizationProvider)
        fake.add_provider(SchemaOrgBankAccountProvider)
        fake.add_provider(SchemaOrgOrderProvider)
        
        # STEP 1: Generate the raw data ONCE (this is the key change!)
        print(f"{'='*70}")
        print(f"GENERATING RAW DATA (will be reused for all vocabularies)")
        print(f"{'='*70}\n")
        
        raw_data_store = generate_raw_data(
            fake=fake,
            num_people=args.num_people,
            max_accounts=args.max_accounts,
            max_orders_per_account=args.max_orders,
            num_orgs=args.num_organizations,
            seed=args.seed
        )
        
        # STEP 2: Generate Schema.org vocabulary outputs (if requested)
        if use_schema:
            print(f"\n{'='*70}")
            print(f"GENERATING SCHEMA.ORG VOCABULARY OUTPUTS")
            print(f"{'='*70}\n")
            
            # Initialize schema.org graph and/or collector
            graph_schema = None if args.format == 'csv' else Graph()
            collector_schema = None
            
            if graph_schema is not None:
                graph_schema.bind("schema", SCHEMA)
                graph_schema.bind("ex", EX)
            
            if generate_csv or generate_all:
                column_names_schema = CSVColumns.create_columns(SchemaOrgPredicateConfig)
                collector_schema = DataCollector(column_names_schema)
            
            # Populate graph and collector using the SAME raw data
            print("Populating Schema.org graph and collector...")
            populate_graph_and_collector(
                raw_store=raw_data_store,
                graph=graph_schema,
                collector=collector_schema,
                predicate_config=SchemaOrgPredicateConfig
            )
            
            # Save RDF if needed
            if graph_schema is not None:
                rdf_file = f"{args.output}_schema.ttl"
                graph_schema.serialize(destination=rdf_file, format='turtle')
                print(f"\n✓ Saved Schema.org RDF to {rdf_file}")
            
            # Save CSV if needed
            if collector_schema is not None:
                # Generate denormalized CSV
                denorm_file = f"{args.output}_schema_denormalized.csv"
                export_to_csv(collector_schema, denorm_file)
                
                # Generate 3NF CSV
                export_to_3nf_csv(collector_schema, f"{args.output}_schema_3nf")
        
        # STEP 3: Generate custom vocabulary outputs (if requested)
        if use_custom:
            print(f"\n{'='*70}")
            print(f"GENERATING CUSTOM VOCABULARY OUTPUTS")
            print(f"{'='*70}\n")
            
            # Initialize custom graph and/or collector
            graph_custom = None if args.format == 'csv' else Graph()
            collector_custom = None
            
            if graph_custom is not None:
                graph_custom.bind("custom", CUSTOM)
                graph_custom.bind("ex", EX)
            
            if generate_csv or generate_all:
                column_names_custom = CSVColumns.create_columns(CustomPredicateConfig)
                collector_custom = DataCollector(column_names_custom)
            
            # Populate graph and collector using the SAME raw data
            print("Populating custom graph and collector...")
            populate_graph_and_collector(
                raw_store=raw_data_store,
                graph=graph_custom,
                collector=collector_custom,
                predicate_config=CustomPredicateConfig
            )
            
            # Save RDF if needed
            if graph_custom is not None:
                rdf_file = f"{args.output}_custom.ttl"
                graph_custom.serialize(destination=rdf_file, format='turtle')
                print(f"\n✓ Saved custom RDF to {rdf_file}")
            
            # Save CSV if needed
            if collector_custom is not None:
                # Generate denormalized CSV
                denorm_file = f"{args.output}_custom_denormalized.csv"
                export_to_csv(collector_custom, denorm_file)
                
                # Generate 3NF CSV
                export_to_3nf_csv(collector_custom, f"{args.output}_custom_3nf")
        
        print(f"\n{'='*70}")
        print(f"✓ ALL GENERATION COMPLETE!")
        print(f"{'='*70}\n")
        
        return 0
        
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())