"""
Custom Faker provider for Schema.org/BankAccount properties.
Generates realistic data for bank accounts.
"""

from faker import Faker
from faker.providers import BaseProvider
from .base_provider import BaseSchemaOrgProvider
from datetime import datetime
import random


class SchemaOrgBankAccountProvider(BaseSchemaOrgProvider):
    """Provider for Schema.org/BankAccount properties."""
    
    # Bank account-specific data
    ACCOUNT_TYPES = [
        "Checking Account",
        "Savings Account",
        "Business Checking",
        "Business Savings",
        "Money Market Account",
        "Certificate of Deposit",
        "Individual Retirement Account",
        "Joint Account"
    ]
    
    BANKS = [
        "Chase Bank",
        "Bank of America",
        "Wells Fargo",
        "Citibank",
        "US Bank",
        "PNC Bank",
        "Capital One",
        "TD Bank",
        "BB&T",
        "SunTrust Bank",
        "Fifth Third Bank",
        "Regions Bank",
        "KeyBank",
        "Santander Bank",
        "HSBC Bank"
    ]
    
    ACCOUNT_STATUSES = [
        "Active",
        "Inactive",
        "Closed",
        "Frozen",
        "Dormant"
    ]
    
    def bank_account_name(self):
        """Account name/description."""
        types = ["Primary", "Secondary", "Business", "Savings", "Emergency Fund"]
        return f"{random.choice(types)} Account"
    
    def bank_account_identifier(self):
        """Account identifier (UUID)."""
        return self.common_identifier()
    
    def bank_account_account_number(self):
        """Bank account number."""
        # US bank accounts are typically 8-12 digits
        return f"{random.randint(10000000, 999999999999)}"
    
    def bank_account_account_type(self):
        """Type of bank account."""
        return random.choice(self.ACCOUNT_TYPES)
    
    def bank_account_bank_name(self):
        """Name of the bank."""
        return random.choice(self.BANKS)
    
    def bank_account_branch_code(self):
        """Bank branch code."""
        return f"{random.randint(1000, 9999)}"
    
    def bank_account_routing_number(self):
        """Bank routing number (ABA routing number - 9 digits)."""
        return f"{random.randint(100000000, 999999999)}"
    
    def bank_account_swift_code(self):
        """SWIFT/BIC code."""
        # SWIFT codes are 8 or 11 characters
        bank_code = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=4))
        country_code = self.fake.country_code()
        location_code = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=2))
        
        if random.random() < 0.5:
            # 11 character version with branch code
            branch_code = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=3))
            return f"{bank_code}{country_code}{location_code}{branch_code}"
        else:
            # 8 character version
            return f"{bank_code}{country_code}{location_code}"
    
    def bank_account_iban(self):
        """IBAN (International Bank Account Number)."""
        return self.fake.iban()
    
    def bank_account_currency(self):
        """Account currency."""
        return self.common_currency_code()
    
    def bank_account_balance(self):
        """Current account balance."""
        # Realistic distribution of balances
        balance_ranges = [
            (0, 1000, 0.2),
            (1000, 10000, 0.3),
            (10000, 50000, 0.25),
            (50000, 100000, 0.15),
            (100000, 500000, 0.07),
            (500000, 1000000, 0.03)
        ]
        
        rand = random.random()
        cumulative = 0
        for min_bal, max_bal, prob in balance_ranges:
            cumulative += prob
            if rand <= cumulative:
                return round(random.uniform(min_bal, max_bal), 2)
        
        return round(random.uniform(0, 10000), 2)
    
    def bank_account_minimum_balance(self):
        """Minimum balance requirement."""
        minimums = [0, 25, 100, 500, 1000, 2500, 5000]
        return random.choice(minimums)
    
    def bank_account_interest_rate(self):
        """Interest rate (percentage)."""
        # Realistic interest rates
        return round(random.uniform(0.01, 5.0), 2)
    
    def bank_account_opening_date(self):
        """Date account was opened."""
        return self.common_date(start_year=1990, end_year=2024)
    
    def bank_account_closing_date(self):
        """Date account was closed."""
        return self.common_date(start_year=2020, end_year=2024)
    
    def bank_account_status(self):
        """Account status."""
        return random.choice(self.ACCOUNT_STATUSES)
    
    def bank_account_account_holder(self):
        """Name of account holder."""
        return self.fake.name()
    
    def bank_account_account_holder_email(self):
        """Email of account holder."""
        return self.common_email()
    
    def bank_account_account_holder_telephone(self):
        """Phone number of account holder."""
        return self.common_telephone()
    
    def bank_account_monthly_fee(self):
        """Monthly maintenance fee."""
        fees = [0, 5.00, 10.00, 12.00, 15.00, 25.00]
        return random.choice(fees)
    
    def bank_account_overdraft_limit(self):
        """Overdraft protection limit."""
        limits = [0, 100, 250, 500, 1000, 2000]
        return random.choice(limits)


def create_bank_account_data(num_entities=10, include_closed=False, seed=None):
    """
    Generate bank account data using the custom provider.
    
    Args:
        num_entities: Number of bank account entities to generate
        include_closed: Whether to include closed accounts
        seed: Random seed for reproducibility
    
    Returns:
        List of dictionaries containing bank account data
    """
    if seed is not None:
        Faker.seed(seed)
        random.seed(seed)
    
    fake = Faker()
    fake.add_provider(SchemaOrgBankAccountProvider)
    
    accounts = []
    
    for i in range(num_entities):
        # Determine if closed (10% chance if enabled)
        is_closed = include_closed and random.random() < 0.1
        
        account = {
            "@type": "BankAccount",
            "name": fake.bank_account_name(),
            "identifier": fake.bank_account_identifier(),
            "accountNumber": fake.bank_account_account_number(),
            "accountType": fake.bank_account_account_type(),
            "bankName": fake.bank_account_bank_name(),
        }
        
        # Optional properties with varying probability
        if random.random() < 0.7:
            account["routingNumber"] = fake.bank_account_routing_number()
        
        if random.random() < 0.5:
            account["branchCode"] = fake.bank_account_branch_code()
        
        if random.random() < 0.4:
            account["swiftCode"] = fake.bank_account_swift_code()
        
        if random.random() < 0.6:
            account["iban"] = fake.bank_account_iban()
        
        account["currency"] = fake.bank_account_currency()
        
        if random.random() < 0.8:
            account["balance"] = fake.bank_account_balance()
        
        if random.random() < 0.5:
            account["minimumBalance"] = fake.bank_account_minimum_balance()
        
        if random.random() < 0.6:
            account["interestRate"] = fake.bank_account_interest_rate()
        
        account["openingDate"] = fake.bank_account_opening_date()
        
        # Status
        if is_closed:
            account["status"] = "Closed"
            account["closingDate"] = fake.bank_account_closing_date()
        else:
            account["status"] = fake.bank_account_status()
        
        # Account holder info
        account["accountHolder"] = fake.bank_account_account_holder()
        
        if random.random() < 0.7:
            account["accountHolderEmail"] = fake.bank_account_account_holder_email()
        
        if random.random() < 0.6:
            account["accountHolderTelephone"] = fake.bank_account_account_holder_telephone()
        
        # Fees and limits
        if random.random() < 0.5:
            account["monthlyFee"] = fake.bank_account_monthly_fee()
        
        if random.random() < 0.4:
            account["overdraftLimit"] = fake.bank_account_overdraft_limit()
        
        accounts.append(account)
    
    return accounts


if __name__ == "__main__":
    # Test the provider
    print("Testing Schema.org BankAccount Provider\n")
    print("=" * 80)
    
    accounts = create_bank_account_data(num_entities=3, include_closed=False, seed=42)
    
    for i, account in enumerate(accounts, 1):
        print(f"\nBank Account {i}:")
        print("-" * 80)
        for key, value in account.items():
            if isinstance(value, dict):
                print(f"  {key}:")
                for k, v in value.items():
                    print(f"    {k}: {v}")
            else:
                print(f"  {key}: {value}")



