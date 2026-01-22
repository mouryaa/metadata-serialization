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
                'org_id': org_id,
                'org_uri': str(org_uri),
                'name': org_name,
                'description': description,
                'email': email,
                'telephone': telephone,
                'url': url,
                'industry': industry,
                'tax_id': tax_id
            })
        
        # Add to RDF graph
        if graph is not None:
            graph.add((org_uri, RDF.type, SCHEMA.Organization))
            graph.add((org_uri, SCHEMA.name, Literal(org_name, datatype=XSD.string)))
            graph.add((org_uri, SCHEMA.description, Literal(description, datatype=XSD.string)))
            graph.add((org_uri, SCHEMA.email, Literal(email, datatype=XSD.string)))
            graph.add((org_uri, SCHEMA.telephone, Literal(telephone, datatype=XSD.string)))
            graph.add((org_uri, SCHEMA.url, Literal(url, datatype=XSD.anyURI)))
            graph.add((org_uri, SCHEMA.industry, Literal(industry, datatype=XSD.string)))
            
            if tax_id:
                graph.add((org_uri, SCHEMA.taxID, Literal(tax_id, datatype=XSD.string)))
        
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
            'person_id': f"person_{person_id}",
            'person_uri': str(person_uri),
            'full_name': full_name,
            'given_name': first_name,
            'family_name': last_name,
            'email': email,
            'telephone': telephone,
            'tax_id': tax_id
        })
    
    # Add to RDF graph
    if graph is not None:
        graph.add((person_uri, RDF.type, SCHEMA.Person))
        graph.add((person_uri, SCHEMA.name, Literal(full_name, datatype=XSD.string)))
        graph.add((person_uri, SCHEMA.givenName, Literal(first_name, datatype=XSD.string)))
        graph.add((person_uri, SCHEMA.familyName, Literal(last_name, datatype=XSD.string)))
        graph.add((person_uri, SCHEMA.email, Literal(email, datatype=XSD.string)))
        graph.add((person_uri, SCHEMA.telephone, Literal(telephone, datatype=XSD.string)))
        graph.add((person_uri, SCHEMA.identifier, Literal(tax_id, datatype=XSD.string)))
    
    # Generate 1 to max_accounts bank accounts
    num_accounts = random.randint(1, max_accounts)
    total_orders = 0
    
    for account_idx in range(num_accounts):
        account_id = f"person_{person_id}_account_{account_idx+1}"
        account_uri = EX[account_id]
        
        # Generate account data
        account_name = fake.bank_account_name()
        identifier = fake.bank_account_identifier()
        account_number = fake.bank_account_account_number()
        account_type = fake.bank_account_account_type()
        bank_name = fake.bank_account_bank_name()
        balance = fake.bank_account_balance()
        
        # Store account data for CSV
        if collector:
            collector.add_account({
                'account_id': account_id,
                'account_uri': str(account_uri),
                'person_id': f"person_{person_id}",
                'account_name': account_name,
                'identifier': identifier,
                'account_number': account_number,
                'account_type': account_type,
                'bank_name': bank_name,
                'balance': str(balance)
            })
        
        # Add to RDF graph
        if graph is not None:
            graph.add((account_uri, RDF.type, SCHEMA.BankAccount))
            graph.add((account_uri, SCHEMA.name, Literal(account_name, datatype=XSD.string)))
            graph.add((account_uri, SCHEMA.identifier, Literal(identifier, datatype=XSD.string)))
            graph.add((account_uri, SCHEMA.accountId, Literal(account_number, datatype=XSD.string)))
            graph.add((account_uri, SCHEMA.bankAccountType, Literal(account_type, datatype=XSD.string)))
            graph.add((account_uri, SCHEMA.servicer, Literal(bank_name, datatype=XSD.string)))
            graph.add((account_uri, SCHEMA.accountMinimumInflow, Literal(balance, datatype=XSD.decimal)))
            graph.add((account_uri, SCHEMA.accountHolder, person_uri))
        
        # Generate 1 to max_orders_per_account orders for this account
        num_orders = random.randint(1, max_orders_per_account)
        total_orders += num_orders
        
        for order_idx in range(num_orders):
            # Select random organization as merchant
            merchant_data = random.choice(org_data_list)
            
            # Generate order data
            order_id = f"person_{person_id}_account_{account_idx+1}_order_{order_idx+1}"
            order_uri = EX[order_id]
            order_number = fake.order_order_number()
            order_status = fake.order_order_status()
            order_date = fake.order_order_date()
            total_payment = fake.order_total_payment()
            
            # Store order data for CSV
            if collector:
                collector.add_order({
                    'order_id': order_id,
                    'order_uri': str(order_uri),
                    'person_id': f"person_{person_id}",
                    'account_id': account_id,
                    'merchant_id': merchant_data['id'],
                    'order_number': order_number,
                    'order_status': order_status,
                    'order_date': order_date,
                    'total_payment': str(total_payment)
                })
            
            # Add to RDF graph
            if graph is not None:
                graph.add((order_uri, RDF.type, SCHEMA.Order))
                graph.add((order_uri, SCHEMA.orderNumber, Literal(order_number, datatype=XSD.string)))
                graph.add((order_uri, SCHEMA.orderStatus, Literal(order_status, datatype=XSD.string)))
                graph.add((order_uri, SCHEMA.orderDate, Literal(order_date, datatype=XSD.date)))
                graph.add((order_uri, SCHEMA.totalPaymentDue, Literal(total_payment, datatype=XSD.decimal)))
                graph.add((order_uri, SCHEMA.customer, person_uri))
                graph.add((order_uri, SCHEMA.paymentMethod, account_uri))
                graph.add((order_uri, SCHEMA.merchant, merchant_data['uri']))
            
            # Generate 1-5 order items
            num_items = random.randint(1, 5)
            for item_idx in range(num_items):
                item_name = fake.order_item_name()
                
                # Store order item for CSV
                if collector:
                    collector.add_order_item({
                        'order_id': order_id,
                        'item_index': item_idx + 1,
                        'item_name': item_name
                    })
                
                # Add to RDF graph
                if graph is not None:
                    item_uri = EX[f"{order_id}_item_{item_idx+1}"]
                    graph.add((item_uri, RDF.type, SCHEMA.OrderItem))
                    graph.add((item_uri, SCHEMA.orderItemNumber, Literal(item_idx + 1, datatype=XSD.integer)))
                    graph.add((item_uri, SCHEMA.orderItemStatus, Literal(item_name, datatype=XSD.string)))
                    graph.add((order_uri, SCHEMA.orderedItem, item_uri))
    
    return person_uri, num_accounts, total_orders


def create_linked_graph(num_people, max_accounts, max_orders_per_account, num_orgs, seed=None, collect_csv_data=False):
    """
    Create a complete linked RDF graph with all entities.
    
    Args:
        num_people: Number of people to generate
        max_accounts: Maximum bank accounts per person (will generate 1-max_accounts)
        max_orders_per_account: Maximum orders per account (will generate 1-max)
        num_orgs: Number of organizations to generate
        seed: Random seed for reproducibility
        collect_csv_data: If True, also collect data for CSV export
    
    Returns:
        tuple: (graph, collector) where collector is None if collect_csv_data is False
    """
    # Initialize based on mode
    if collect_csv_data == 'both':
        graph = Graph()
        collector = DataCollector()
    elif collect_csv_data:
        graph = None
        collector = DataCollector()
    else:
        graph = Graph()
        collector = None
    
    # Bind namespaces for prettier output
    if graph is not None:
        graph.bind("schema", SCHEMA)
        graph.bind("ex", EX)
    
    # Initialize Faker with custom providers
    fake = Faker()
    fake.add_provider(SchemaOrgPersonProvider)
    fake.add_provider(SchemaOrgOrganizationProvider)
    fake.add_provider(SchemaOrgBankAccountProvider)
    fake.add_provider(SchemaOrgOrderProvider)
    
    # Generate organizations first
    org_data_list = generate_organizations(fake, num_orgs, graph, collector, seed)
    
    # Generate people with accounts and orders
    print(f"Generating {num_people} people with their accounts and orders...")
    total_accounts = 0
    total_orders = 0
    
    for i in range(num_people):
        person_uri, num_accounts, num_orders = generate_person_with_accounts_and_orders(
            fake, i+1, max_accounts, max_orders_per_account, 
            org_data_list, graph, collector
        )
        total_accounts += num_accounts
        total_orders += num_orders
    
    print(f"  ✓ Generated {num_people} people")
    print(f"  ✓ Generated {total_accounts} bank accounts")
    print(f"  ✓ Generated {total_orders} orders")
    if collector:
        print(f"  ✓ Generated {len(collector.order_items)} order items")
    
    return graph, collector


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
    people_lookup = {p['person_id']: p for p in collector.people}
    accounts_lookup = {a['account_id']: a for a in collector.accounts}
    orgs_lookup = {o['org_id']: o for o in collector.organizations}
    
    # Build fully denormalized rows (one row per order item)
    denorm_rows = []
    
    for order in collector.orders:
        person = people_lookup.get(order['person_id'], {})
        account = accounts_lookup.get(order['account_id'], {})
        merchant = orgs_lookup.get(order['merchant_id'], {})
        
        # Get all items for this order
        order_items = [item for item in collector.order_items if item['order_id'] == order['order_id']]
        
        # If no items, create one row anyway
        if not order_items:
            order_items = [{'item_index': None, 'item_name': None}]
        
        for item in order_items:
            row = {
                # Order info
                'order_id': order['order_id'],
                'order_uri': order['order_uri'],
                'order_number': order['order_number'],
                'order_status': order['order_status'],
                'order_date': order['order_date'],
                'total_payment': order['total_payment'],
                
                # Person/Customer info
                'person_id': order['person_id'],
                'person_uri': person.get('person_uri', ''),
                'person_name': person.get('full_name', ''),
                'person_given_name': person.get('given_name', ''),
                'person_family_name': person.get('family_name', ''),
                'person_email': person.get('email', ''),
                'person_tax_id': person.get('tax_id', ''),
                'person_telephone': person.get('telephone', ''),
                
                # Bank Account info
                'account_id': order['account_id'],
                'account_uri': account.get('account_uri', ''),
                'account_name': account.get('account_name', ''),
                'account_identifier': account.get('identifier', ''),
                'account_number': account.get('account_number', ''),
                'account_type': account.get('account_type', ''),
                'bank_name': account.get('bank_name', ''),
                'account_balance': account.get('balance', ''),
                
                # Merchant/Organization info
                'merchant_id': order['merchant_id'],
                'merchant_uri': merchant.get('org_uri', ''),
                'merchant_name': merchant.get('name', ''),
                'merchant_description': merchant.get('description', ''),
                'merchant_email': merchant.get('email', ''),
                'merchant_telephone': merchant.get('telephone', ''),
                'merchant_url': merchant.get('url', ''),
                'merchant_industry': merchant.get('industry', ''),
                'merchant_tax_id': merchant.get('tax_id', ''),
                
                # Order Item info
                'item_index': item.get('item_index', ''),
                'item_name': item.get('item_name', ''),
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
            fieldnames = ['person_id', 'person_uri', 'full_name', 'given_name', 
                         'family_name', 'email', 'telephone', 'tax_id']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(collector.people)
        print(f"  ✓ Saved {len(collector.people)} people to {people_file}")
    
    # 2. Bank Accounts table (with person_id as foreign key)
    accounts_file = f"{output_prefix}_bank_accounts.csv"
    if collector.accounts:
        with open(accounts_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['account_id', 'account_uri', 'person_id', 'account_name', 
                         'identifier', 'account_number', 'account_type', 'bank_name', 'balance']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(collector.accounts)
        print(f"  ✓ Saved {len(collector.accounts)} bank accounts to {accounts_file}")
    
    # 3. Organizations table
    orgs_file = f"{output_prefix}_organizations.csv"
    if collector.organizations:
        with open(orgs_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['org_id', 'org_uri', 'name', 'description', 'email', 
                         'telephone', 'url', 'industry', 'tax_id']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(collector.organizations)
        print(f"  ✓ Saved {len(collector.organizations)} organizations to {orgs_file}")
    
    # 4. Orders table (with person_id, account_id, merchant_id as foreign keys)
    orders_file = f"{output_prefix}_orders.csv"
    if collector.orders:
        with open(orders_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['order_id', 'order_uri', 'person_id', 'account_id', 'merchant_id',
                         'order_number', 'order_status', 'order_date', 'total_payment']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(collector.orders)
        print(f"  ✓ Saved {len(collector.orders)} orders to {orders_file}")
    
    # 5. Order Items table (with order_id as foreign key)
    items_file = f"{output_prefix}_order_items.csv"
    if collector.order_items:
        with open(items_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['order_id', 'item_index', 'item_name']
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