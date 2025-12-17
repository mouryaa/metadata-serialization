"""
Base provider for common Schema.org properties.
This module contains shared property generators that can be reused across different Schema.org types.
"""

from faker import Faker
from faker.providers import BaseProvider
from datetime import datetime, timedelta
import random


class BaseSchemaOrgProvider(BaseProvider):
    """Base provider with common properties shared across Schema.org types."""
    
    def __init__(self, generator):
        super().__init__(generator)
        self.fake = generator
    
    # Common Identity Properties
    
    def common_name(self):
        """Generic name (can be person, organization, etc.)."""
        return self.fake.company()
    
    def common_identifier(self):
        """Generic identifier (UUID format)."""
        return self.fake.uuid4()
    
    def common_description(self):
        """Generic description text."""
        sentences = random.randint(2, 5)
        return self.fake.text(max_nb_chars=200)[:197] + "..."
    
    # Common Contact Properties
    
    def common_email(self):
        """Email address."""
        return self.fake.email()
    
    def common_telephone(self):
        """Telephone number."""
        return self.fake.phone_number()
    
    def common_fax_number(self):
        """Fax number."""
        return self.fake.phone_number()
    
    def common_url(self):
        """Website URL."""
        return self.fake.url()
    
    # Common Location Properties
    
    def common_address(self):
        """Physical address as a dictionary."""
        return {
            "streetAddress": self.fake.street_address(),
            "addressLocality": self.fake.city(),
            "addressRegion": self.fake.state(),
            "postalCode": self.fake.postcode(),
            "addressCountry": self.fake.country_code(),
        }
    
    # Common Temporal Properties
    
    def common_date_created(self):
        """Date created/founded."""
        start_date = datetime(1950, 1, 1)
        end_date = datetime.now()
        date = self.fake.date_between(start_date=start_date, end_date=end_date)
        return date.isoformat()
    
    def common_date_modified(self):
        """Date last modified."""
        start_date = datetime(2020, 1, 1)
        end_date = datetime.now()
        date = self.fake.date_between(start_date=start_date, end_date=end_date)
        return date.isoformat()
    
    def common_date(self, start_year=1950, end_year=None):
        """Generic date generator."""
        if end_year is None:
            end_year = datetime.now().year
        start_date = datetime(start_year, 1, 1)
        end_date = datetime(end_year, 12, 31)
        date = self.fake.date_between(start_date=start_date, end_date=end_date)
        return date.isoformat()
    
    # Common Numeric Properties
    
    def common_price(self, min_value=10, max_value=10000):
        """Price/monetary amount."""
        price = random.uniform(min_value, max_value)
        return round(price, 2)
    
    def common_quantity(self, min_value=1, max_value=100):
        """Quantity/count."""
        return random.randint(min_value, max_value)
    
    # Common Identifiers
    
    def common_tax_id(self):
        """Tax ID (generic format)."""
        return f"{random.randint(10, 99)}-{random.randint(1000000, 9999999)}"
    
    def common_vat_id(self):
        """VAT ID."""
        country_code = self.fake.country_code()
        number = random.randint(100000000, 999999999)
        return f"{country_code}{number}"
    
    def common_duns_number(self):
        """DUNS number (9 digits)."""
        return f"{random.randint(100000000, 999999999)}"
    
    def common_global_location_number(self):
        """Global Location Number (GLN - 13 digits)."""
        return f"{random.randint(1000000000000, 9999999999999)}"
    
    # Common Text Properties
    
    def common_slogan(self):
        """Slogan or tagline."""
        slogans = [
            self.fake.catch_phrase(),
            self.fake.bs(),
            " ".join(self.fake.words(nb=random.randint(2, 5))).title(),
        ]
        return random.choice(slogans)
    
    def common_legal_name(self):
        """Legal name (for organizations)."""
        suffixes = ["Inc.", "LLC", "Ltd.", "Corp.", "Co.", "GmbH", "S.A.", "Pty Ltd"]
        return f"{self.fake.company()} {random.choice(suffixes)}"
    
    # Common Currency and Financial
    
    def common_currency_code(self):
        """ISO 4217 currency code."""
        currencies = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY", "INR"]
        return random.choice(currencies)
    
    def common_account_number(self):
        """Generic account number."""
        return self.fake.bban()
    
    def common_bank_account_number(self):
        """Bank account number (IBAN)."""
        return self.fake.iban()
    
    # Common Status Values
    
    def common_status(self, statuses):
        """Generic status from a list."""
        return random.choice(statuses)


# Utility function to create a Faker instance with the base provider
def create_faker_with_base():
    """Create a Faker instance with BaseSchemaOrgProvider added."""
    fake = Faker()
    fake.add_provider(BaseSchemaOrgProvider)
    return fake


if __name__ == "__main__":
    # Test the base provider
    print("Testing Base Schema.org Provider\n")
    print("=" * 80)
    
    fake = create_faker_with_base()
    
    print("\n=== Identity Properties ===")
    print(f"Name: {fake.common_name()}")
    print(f"Identifier: {fake.common_identifier()}")
    print(f"Description: {fake.common_description()}")
    
    print("\n=== Contact Properties ===")
    print(f"Email: {fake.common_email()}")
    print(f"Telephone: {fake.common_telephone()}")
    print(f"URL: {fake.common_url()}")
    
    print("\n=== Location Properties ===")
    address = fake.common_address()
    print(f"Address:")
    for key, value in address.items():
        print(f"  {key}: {value}")
    
    print("\n=== Temporal Properties ===")
    print(f"Date Created: {fake.common_date_created()}")
    print(f"Date Modified: {fake.common_date_modified()}")
    
    print("\n=== Financial Properties ===")
    print(f"Price: ${fake.common_price()}")
    print(f"Currency: {fake.common_currency_code()}")
    print(f"Account Number: {fake.common_account_number()}")
    
    print("\n=== Identifiers ===")
    print(f"Tax ID: {fake.common_tax_id()}")
    print(f"VAT ID: {fake.common_vat_id()}")
    print(f"DUNS: {fake.common_duns_number()}")
    
    print("\n" + "=" * 80)



