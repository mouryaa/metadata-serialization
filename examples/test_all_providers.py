#!/usr/bin/env python3
"""
Test script to verify all providers work correctly together.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from faker import Faker
from providers import (
    SchemaOrgPersonProvider,
    SchemaOrgOrganizationProvider,
    SchemaOrgBankAccountProvider,
    SchemaOrgOrderProvider
)


def test_person():
    """Test Person provider."""
    print("Testing Person Provider...")
    fake = Faker()
    fake.add_provider(SchemaOrgPersonProvider)
    Faker.seed(42)
    
    assert fake.person_name() is not None
    assert fake.person_email() is not None
    assert fake.person_address() is not None
    print("  ✓ Person provider works!")


def test_organization():
    """Test Organization provider."""
    print("Testing Organization Provider...")
    fake = Faker()
    fake.add_provider(SchemaOrgOrganizationProvider)
    Faker.seed(42)
    
    assert fake.organization_name() is not None
    assert fake.organization_email() is not None
    assert fake.organization_industry() is not None
    print("  ✓ Organization provider works!")


def test_bank_account():
    """Test BankAccount provider."""
    print("Testing BankAccount Provider...")
    fake = Faker()
    fake.add_provider(SchemaOrgBankAccountProvider)
    Faker.seed(42)
    
    assert fake.bank_account_account_number() is not None
    assert fake.bank_account_balance() is not None
    assert fake.bank_account_bank_name() is not None
    print("  ✓ BankAccount provider works!")


def test_order():
    """Test Order provider."""
    print("Testing Order Provider...")
    fake = Faker()
    fake.add_provider(SchemaOrgOrderProvider)
    Faker.seed(42)
    
    assert fake.order_identifier() is not None
    assert fake.order_status() is not None
    assert fake.order_total() is not None
    print("  ✓ Order provider works!")


def test_all_together():
    """Test all providers together."""
    print("Testing All Providers Together...")
    fake = Faker()
    fake.add_provider(SchemaOrgPersonProvider)
    fake.add_provider(SchemaOrgOrganizationProvider)
    fake.add_provider(SchemaOrgBankAccountProvider)
    fake.add_provider(SchemaOrgOrderProvider)
    Faker.seed(42)
    
    # Generate one of each
    person_name = fake.person_name()
    org_name = fake.organization_name()
    account_num = fake.bank_account_account_number()
    order_num = fake.order_identifier()
    
    assert person_name is not None
    assert org_name is not None
    assert account_num is not None
    assert order_num is not None
    
    print(f"  Person: {person_name}")
    print(f"  Organization: {org_name}")
    print(f"  Account: {account_num}")
    print(f"  Order: {order_num}")
    print("  ✓ All providers work together!")


def test_code_reuse():
    """Test that code reuse works correctly."""
    print("Testing Code Reuse...")
    fake = Faker()
    fake.add_provider(SchemaOrgPersonProvider)
    fake.add_provider(SchemaOrgOrganizationProvider)
    fake.add_provider(SchemaOrgBankAccountProvider)
    fake.add_provider(SchemaOrgOrderProvider)
    Faker.seed(42)
    
    # All of these should use the same underlying common_email() method
    person_email = fake.person_email()
    org_email = fake.organization_email()
    account_email = fake.bank_account_account_holder_email()
    order_email = fake.order_customer_email()
    
    # Verify they're all valid emails (basic check)
    assert "@" in person_email
    assert "@" in org_email
    assert "@" in account_email
    assert "@" in order_email
    
    print("  ✓ Code reuse works correctly!")


def main():
    print("=" * 80)
    print("Provider Test Suite")
    print("=" * 80)
    print()
    
    try:
        test_person()
        test_organization()
        test_bank_account()
        test_order()
        test_all_together()
        test_code_reuse()
        
        print()
        print("=" * 80)
        print("✓ ALL TESTS PASSED!")
        print("=" * 80)
        print()
        print("Summary:")
        print("  • Person provider: Working")
        print("  • Organization provider: Working")
        print("  • BankAccount provider: Working")
        print("  • Order provider: Working")
        print("  • Code reuse: Working")
        print("  • All providers together: Working")
        print()
        return 0
        
    except Exception as e:
        print()
        print("=" * 80)
        print("✗ TESTS FAILED!")
        print("=" * 80)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())



