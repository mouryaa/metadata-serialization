#!/usr/bin/env python3
"""
Demonstration of code reuse through BaseSchemaOrgProvider.

This script shows how common properties (email, telephone, address, etc.)
are shared across different Schema.org types through inheritance from
BaseSchemaOrgProvider.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from faker import Faker
from providers.person_provider import SchemaOrgPersonProvider
from providers.organization_provider import SchemaOrgOrganizationProvider
from providers.bank_account_provider import SchemaOrgBankAccountProvider
from providers.order_provider import SchemaOrgOrderProvider


def main():
    print("=" * 80)
    print("Code Reuse Demonstration: BaseSchemaOrgProvider")
    print("=" * 80)
    print()
    print("This demonstration shows how common Schema.org properties are")
    print("generated using shared methods from BaseSchemaOrgProvider.")
    print()
    
    # Create Faker instance with all providers
    fake = Faker()
    fake.add_provider(SchemaOrgPersonProvider)
    fake.add_provider(SchemaOrgOrganizationProvider)
    fake.add_provider(SchemaOrgBankAccountProvider)
    fake.add_provider(SchemaOrgOrderProvider)
    
    Faker.seed(12345)
    
    print("=" * 80)
    print("Common Email Property")
    print("=" * 80)
    print("All providers use the same underlying common_email() method:")
    print()
    print(f"  Person email:       {fake.person_email()}")
    print(f"  Organization email: {fake.organization_email()}")
    print(f"  Order customer email: {fake.order_customer_email()}")
    print(f"  Bank account holder email: {fake.bank_account_account_holder_email()}")
    print()
    
    print("=" * 80)
    print("Common Telephone Property")
    print("=" * 80)
    print("All providers use the same underlying common_telephone() method:")
    print()
    print(f"  Person telephone:   {fake.person_telephone()}")
    print(f"  Organization telephone: {fake.organization_telephone()}")
    print(f"  Order customer telephone: {fake.order_customer_telephone()}")
    print(f"  Bank account holder telephone: {fake.bank_account_account_holder_telephone()}")
    print()
    
    print("=" * 80)
    print("Common Address Property")
    print("=" * 80)
    print("All providers use the same underlying common_address() method:")
    print()
    
    print("  Person address:")
    person_addr = fake.person_address()
    for key, value in person_addr.items():
        print(f"    {key}: {value}")
    print()
    
    print("  Organization address:")
    org_addr = fake.organization_address()
    for key, value in org_addr.items():
        print(f"    {key}: {value}")
    print()
    
    print("  Order billing address:")
    order_addr = fake.order_billing_address()
    for key, value in order_addr.items():
        print(f"    {key}: {value}")
    print()
    
    print("=" * 80)
    print("Common URL Property")
    print("=" * 80)
    print("All providers use the same underlying common_url() method:")
    print()
    print(f"  Person URL:         {fake.person_url()}")
    print(f"  Organization URL:   {fake.organization_url()}")
    print(f"  Order merchant URL: {fake.order_merchant_url()}")
    print()
    
    print("=" * 80)
    print("Common Identifier Properties")
    print("=" * 80)
    print("Financial identifiers use shared methods:")
    print()
    print(f"  Person VAT ID:      {fake.person_vat_id()}")
    print(f"  Organization VAT ID: {fake.organization_vat_id()}")
    print(f"  Organization Tax ID: {fake.organization_tax_id()}")
    print(f"  Organization DUNS:   {fake.organization_duns()}")
    print()
    
    print("=" * 80)
    print("Common Currency Property")
    print("=" * 80)
    print("Currency codes use shared method:")
    print()
    print(f"  Bank account currency: {fake.bank_account_currency()}")
    print(f"  Order currency:        {fake.order_currency()}")
    print()
    
    print("=" * 80)
    print("Benefits of Code Reuse")
    print("=" * 80)
    print()
    print("✓ Consistency: All email addresses follow the same format")
    print("✓ Maintainability: Update one method to affect all types")
    print("✓ DRY Principle: Don't Repeat Yourself")
    print("✓ Extensibility: New types inherit common functionality")
    print("✓ Testing: Test common methods once, use everywhere")
    print()
    
    print("=" * 80)
    print("Provider Inheritance Structure")
    print("=" * 80)
    print()
    print("BaseSchemaOrgProvider (common properties)")
    print("  ├─ SchemaOrgPersonProvider (person-specific)")
    print("  ├─ SchemaOrgOrganizationProvider (org-specific)")
    print("  ├─ SchemaOrgBankAccountProvider (account-specific)")
    print("  └─ SchemaOrgOrderProvider (order-specific)")
    print()
    
    print("=" * 80)
    print("Common Methods in BaseSchemaOrgProvider")
    print("=" * 80)
    print()
    print("Identity & Contact:")
    print("  • common_name()           • common_email()")
    print("  • common_identifier()     • common_telephone()")
    print("  • common_description()    • common_fax_number()")
    print("  • common_url()            • common_address()")
    print()
    print("Financial:")
    print("  • common_price()          • common_currency_code()")
    print("  • common_tax_id()         • common_account_number()")
    print("  • common_vat_id()         • common_bank_account_number()")
    print("  • common_duns_number()    • common_global_location_number()")
    print()
    print("Temporal:")
    print("  • common_date_created()   • common_date()")
    print("  • common_date_modified()")
    print()
    print("Other:")
    print("  • common_quantity()       • common_legal_name()")
    print("  • common_slogan()         • common_status()")
    print()
    
    print("=" * 80)
    print("Demonstration Complete!")
    print("=" * 80)
    print()
    print("See providers/base_provider.py for all common methods.")
    print("Each specific provider extends BaseSchemaOrgProvider and adds")
    print("type-specific properties while reusing common functionality.")
    print()


if __name__ == "__main__":
    main()



