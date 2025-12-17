#!/usr/bin/env python3
"""
Generate linked Schema.org data with relationships between entities.

This script generates a realistic e-commerce scenario:
- N People
- Each person has 1-Y bank accounts
- Each account is used for 1-X orders
- Orders are placed with Z organizations

All entities are properly linked with URIs showing real-world relationships.
"""

import argparse
import sys
import random
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


def generate_organizations(fake, num_orgs, graph, seed=None):
    """
    Generate organization entities.
    
    Returns:
        list: List of organization URIs
    """
    if seed is not None:
        Faker.seed(seed)
        random.seed(seed)
    
    print(f"Generating {num_orgs} organizations...")
    org_uris = []
    
    for i in range(num_orgs):
        org_id = f"org_{i+1}"
        org_uri = EX[org_id]
        org_uris.append(org_uri)
        
        # Add type
        graph.add((org_uri, RDF.type, SCHEMA.Organization))
        
        # Basic properties
        graph.add((org_uri, SCHEMA.name, Literal(fake.organization_name(), datatype=XSD.string)))
        graph.add((org_uri, SCHEMA.legalName, Literal(fake.organization_legal_name(), datatype=XSD.string)))
        graph.add((org_uri, SCHEMA.description, Literal(fake.organization_description(), datatype=XSD.string)))
        
        # Contact
        graph.add((org_uri, SCHEMA.email, Literal(fake.organization_email(), datatype=XSD.string)))
        graph.add((org_uri, SCHEMA.telephone, Literal(fake.organization_telephone(), datatype=XSD.string)))
        graph.add((org_uri, SCHEMA.url, Literal(fake.organization_url(), datatype=XSD.anyURI)))
        
        # Other properties
        #graph.add((org_uri, SCHEMA.foundingDate, Literal(fake.organization_founding_date(), datatype=XSD.date)))
        graph.add((org_uri, SCHEMA.industry, Literal(fake.organization_industry(), datatype=XSD.string)))
        #graph.add((org_uri, SCHEMA.numberOfEmployees, Literal(fake.organization_number_of_employees(), datatype=XSD.integer)))
        
        if random.random() < 0.7:
            graph.add((org_uri, SCHEMA.taxID, Literal(fake.organization_tax_id(), datatype=XSD.string)))
        
        # Address
        """ if random.random() < 0.8:
            address_data = fake.organization_address()
            address_uri = EX[f"{org_id}_address"]
            
            graph.add((org_uri, SCHEMA.address, address_uri))
            graph.add((address_uri, RDF.type, SCHEMA.PostalAddress))
            graph.add((address_uri, SCHEMA.streetAddress, Literal(address_data["streetAddress"], datatype=XSD.string)))
            graph.add((address_uri, SCHEMA.addressLocality, Literal(address_data["addressLocality"], datatype=XSD.string)))
            graph.add((address_uri, SCHEMA.addressRegion, Literal(address_data["addressRegion"], datatype=XSD.string)))
            graph.add((address_uri, SCHEMA.postalCode, Literal(address_data["postalCode"], datatype=XSD.string)))
            graph.add((address_uri, SCHEMA.addressCountry, Literal(address_data["addressCountry"], datatype=XSD.string))) """
    
    print(f"  ✓ Generated {num_orgs} organizations")
    return org_uris


def generate_person_with_accounts_and_orders(fake, person_id, max_accounts, max_orders_per_account, org_uris, graph):
    """
    Generate a person with their bank accounts and orders.
    
    Args:
        fake: Faker instance
        person_id: Person identifier number
        max_accounts: Maximum number of bank accounts (will generate 1 to max_accounts)
        max_orders_per_account: Maximum orders per account (will generate 1 to max)
        org_uris: List of organization URIs to use as merchants
        graph: RDF graph to add to
    
    Returns:
        tuple: (person_uri, num_accounts, num_orders)
    """
    # Generate person
    person_uri = EX[f"person_{person_id}"]
    graph.add((person_uri, RDF.type, SCHEMA.Person))
    
    # Person properties
    first_name = fake.person_given_name()
    last_name = fake.person_family_name()
    full_name = f"{first_name} {last_name}"
    graph.add((person_uri, SCHEMA.name, Literal(full_name, datatype=XSD.string)))
    graph.add((person_uri, SCHEMA.givenName, Literal(first_name, datatype=XSD.string)))
    graph.add((person_uri, SCHEMA.familyName, Literal(last_name, datatype=XSD.string)))
    graph.add((person_uri, SCHEMA.email, Literal(fake.person_email(), datatype=XSD.string)))
    graph.add((person_uri, SCHEMA.identifier, Literal(fake.person_tax_id(), datatype=XSD.string)))
    #graph.add((person_uri, SCHEMA.telephone, Literal(fake.person_telephone(), datatype=XSD.string)))
    #graph.add((person_uri, SCHEMA.birthDate, Literal(fake.person_birth_date(), datatype=XSD.date)))
    #graph.add((person_uri, SCHEMA.gender, Literal(fake.person_gender(), datatype=XSD.string)))
    
    """ if random.random() < 0.6:
        graph.add((person_uri, SCHEMA.jobTitle, Literal(fake.person_job_title(), datatype=XSD.string)))
    
    # Person address
    if random.random() < 0.7:
        address_data = fake.person_address()
        address_uri = EX[f"person_{person_id}_address"]
        
        graph.add((person_uri, SCHEMA.address, address_uri))
        graph.add((address_uri, RDF.type, SCHEMA.PostalAddress))
        graph.add((address_uri, SCHEMA.streetAddress, Literal(address_data["streetAddress"], datatype=XSD.string)))
        graph.add((address_uri, SCHEMA.addressLocality, Literal(address_data["addressLocality"], datatype=XSD.string)))
        graph.add((address_uri, SCHEMA.addressRegion, Literal(address_data["addressRegion"], datatype=XSD.string)))
        graph.add((address_uri, SCHEMA.postalCode, Literal(address_data["postalCode"], datatype=XSD.string)))
        graph.add((address_uri, SCHEMA.addressCountry, Literal(address_data["addressCountry"], datatype=XSD.string))) """
    
    # Generate 1 to max_accounts bank accounts
    num_accounts = random.randint(1, max_accounts)
    total_orders = 0
    
    for account_idx in range(num_accounts):
        account_id = f"person_{person_id}_account_{account_idx+1}"
        account_uri = EX[account_id]
        
        # Bank account properties
        graph.add((account_uri, RDF.type, SCHEMA.BankAccount))
        graph.add((account_uri, SCHEMA.name, Literal(fake.bank_account_name(), datatype=XSD.string)))
        graph.add((account_uri, SCHEMA.identifier, Literal(fake.bank_account_identifier(), datatype=XSD.string)))
        graph.add((account_uri, SCHEMA.accountId, Literal(fake.bank_account_account_number(), datatype=XSD.string)))
        graph.add((account_uri, SCHEMA.bankAccountType, Literal(fake.bank_account_account_type(), datatype=XSD.string)))
        graph.add((account_uri, SCHEMA.servicer, Literal(fake.bank_account_bank_name(), datatype=XSD.string)))
        #graph.add((account_uri, SCHEMA.currency, Literal(fake.bank_account_currency(), datatype=XSD.string)))
        
        balance = fake.bank_account_balance()
        graph.add((account_uri, SCHEMA.accountMinimumInflow, Literal(balance, datatype=XSD.decimal)))
        
        #graph.add((account_uri, SCHEMA.openingHours, Literal(fake.bank_account_opening_date(), datatype=XSD.date)))
        
        # Link account to person
        graph.add((account_uri, SCHEMA.accountHolder, person_uri))
        
        # Generate 1 to max_orders_per_account orders for this account
        num_orders = random.randint(1, max_orders_per_account)
        total_orders += num_orders
        
        for order_idx in range(num_orders):
            order_id = f"person_{person_id}_account_{account_idx+1}_order_{order_idx+1}"
            order_uri = EX[order_id]
            
            # Order properties
            graph.add((order_uri, RDF.type, SCHEMA.Order))
            graph.add((order_uri, SCHEMA.orderNumber, Literal(fake.order_identifier(), datatype=XSD.string)))
            graph.add((order_uri, SCHEMA.orderStatus, Literal(fake.order_status(), datatype=XSD.string)))
            graph.add((order_uri, SCHEMA.orderDate, Literal(fake.order_date(), datatype=XSD.date)))
            
            if random.random() < 0.7:
                graph.add((order_uri, SCHEMA.confirmationNumber, Literal(fake.order_confirmation_number(), datatype=XSD.string)))
            
            # Link order to customer (person)
            graph.add((order_uri, SCHEMA.customer, person_uri))
            
            # Link order to payment method (bank account)
            graph.add((order_uri, SCHEMA.paymentMethod, account_uri))
            
            # Link order to merchant (random organization)
            merchant_uri = random.choice(org_uris)
            graph.add((order_uri, SCHEMA.seller, merchant_uri))
            
            # Order financial details
            total = fake.order_total()
            graph.add((order_uri, SCHEMA.totalPaymentDue, Literal(total, datatype=XSD.decimal)))
            
            # Ordered items (simplified - just add item names)
            num_items = random.randint(1, 3)
            for item_idx in range(num_items):
                item_name = fake.order_item_name()
                graph.add((order_uri, SCHEMA.orderedItem, Literal(item_name, datatype=XSD.string)))
            
            # Billing address (reference person's address if exists, or create new)
            """ if random.random() < 0.8:
                billing_addr_data = fake.order_billing_address()
                billing_addr_uri = EX[f"{order_id}_billing"]
                
                graph.add((order_uri, SCHEMA.billingAddress, billing_addr_uri))
                graph.add((billing_addr_uri, RDF.type, SCHEMA.PostalAddress))
                graph.add((billing_addr_uri, SCHEMA.streetAddress, Literal(billing_addr_data["streetAddress"], datatype=XSD.string)))
                graph.add((billing_addr_uri, SCHEMA.addressLocality, Literal(billing_addr_data["addressLocality"], datatype=XSD.string)))
                graph.add((billing_addr_uri, SCHEMA.addressRegion, Literal(billing_addr_data["addressRegion"], datatype=XSD.string)))
                graph.add((billing_addr_uri, SCHEMA.postalCode, Literal(billing_addr_data["postalCode"], datatype=XSD.string)))
                graph.add((billing_addr_uri, SCHEMA.addressCountry, Literal(billing_addr_data["addressCountry"], datatype=XSD.string))) """
    
    return person_uri, num_accounts, total_orders


def create_linked_graph(num_people, max_accounts, max_orders_per_account, num_orgs, seed=None):
    """
    Create an RDF graph with linked People, BankAccounts, Orders, and Organizations.
    
    Args:
        num_people: Number of people to generate (N)
        max_accounts: Maximum bank accounts per person (Y in 1-Y)
        max_orders_per_account: Maximum orders per account (X in 1-X)
        num_orgs: Number of organizations to generate (Z)
        seed: Random seed for reproducibility
    
    Returns:
        rdflib.Graph: RDF graph with linked data
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
    
    # Create graph
    g = Graph()
    g.bind("schema", SCHEMA)
    g.bind("ex", EX)
    
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
    org_uris = generate_organizations(fake, num_orgs, g, seed)
    
    # Step 2: Generate people with their accounts and orders
    print(f"\nGenerating {num_people} people with accounts and orders...")
    
    total_accounts = 0
    total_orders = 0
    
    for i in range(num_people):
        person_uri, num_accounts, num_orders = generate_person_with_accounts_and_orders(
            fake, i+1, max_accounts, max_orders_per_account, org_uris, g
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
    print(f"  Total triples: {len(g)}")
    print(f"{'='*80}\n")
    
    return g


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Generate linked Schema.org data with People, BankAccounts, Orders, and Organizations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate 10 people, each with 1-2 accounts, each account with 1-3 orders, at 5 organizations
  python generate_linked_data.py -n 10 -y 2 -x 3 -z 5 -o linked_data.ttl
  
  # Generate 100 people with up to 3 accounts, up to 5 orders per account, at 20 organizations
  python generate_linked_data.py -n 100 -y 3 -x 5 -z 20 -o large_linked.ttl
  
  # Use seed for reproducibility
  python generate_linked_data.py -n 50 -y 2 -x 4 -z 10 --seed 42 -o reproducible.ttl
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
        help="Output file path (default: linked_data.ttl)"
    )
    
    parser.add_argument(
        "--format",
        type=str,
        default="turtle",
        choices=["turtle", "xml", "n3", "nt", "json-ld"],
        help="Output RDF format (default: turtle)"
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
        # Generate the graph
        graph = create_linked_graph(
            num_people=args.num_people,
            max_accounts=args.max_accounts,
            max_orders_per_account=args.max_orders,
            num_orgs=args.num_organizations,
            seed=args.seed
        )
        
        # Save to file
        print(f"Saving to {args.output}...")
        graph.serialize(destination=args.output, format=args.format)
        print(f"✓ Successfully saved to {args.output}\n")
        
        return 0
        
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())



