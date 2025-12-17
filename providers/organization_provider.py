"""
Custom Faker provider for Schema.org/Organization properties.
Generates realistic data for organizations including companies, NGOs, and institutions.
"""

from faker import Faker
from faker.providers import BaseProvider
from .base_provider import BaseSchemaOrgProvider
from datetime import datetime
import random


class SchemaOrgOrganizationProvider(BaseSchemaOrgProvider):
    """Provider for Schema.org/Organization properties."""
    
    # Organization-specific data
    ORGANIZATION_TYPES = [
        "Corporation", "NGO", "Educational Organization", "Government Organization",
        "Local Business", "Performing Group", "Sports Organization", "Airline",
        "Consortium", "FundingScheme", "Library System", "Medical Organization",
        "NewsMediaOrganization", "Project", "ResearchOrganization", "WorkersUnion"
    ]
    
    INDUSTRIES = [
        "Technology", "Healthcare", "Finance", "Education", "Manufacturing",
        "Retail", "Hospitality", "Transportation", "Energy", "Telecommunications",
        "Real Estate", "Media", "Entertainment", "Agriculture", "Construction",
        "Legal Services", "Consulting", "Pharmaceuticals", "Biotechnology",
        "Aerospace", "Automotive", "Insurance", "Banking"
    ]
    
    AWARDS = [
        "Best Employer Award",
        "Innovation Excellence Award",
        "Industry Leadership Award",
        "Sustainability Award",
        "Corporate Social Responsibility Award",
        "Best Product Award",
        "Customer Service Excellence Award",
        "Technology Pioneer Award"
    ]
    
    def organization_name(self):
        """Organization name."""
        return self.fake.company()
    
    def organization_legal_name(self):
        """Legal name of the organization."""
        return self.common_legal_name()
    
    def organization_alternate_name(self):
        """Alternate name or acronym."""
        company = self.fake.company()
        # Create acronym from company name
        words = company.split()
        if len(words) >= 2:
            acronym = "".join(word[0].upper() for word in words[:3])
            return acronym
        return company[:3].upper()
    
    def organization_description(self):
        """Organization description."""
        return self.common_description()
    
    def organization_slogan(self):
        """Organization slogan."""
        return self.common_slogan()
    
    # Contact Information
    
    def organization_email(self):
        """Organization email."""
        return self.common_email()
    
    def organization_telephone(self):
        """Organization telephone."""
        return self.common_telephone()
    
    def organization_fax_number(self):
        """Organization fax number."""
        return self.common_fax_number()
    
    def organization_url(self):
        """Organization website URL."""
        return self.common_url()
    
    # Dates and History
    
    def organization_founding_date(self):
        """Organization founding date."""
        return self.common_date(start_year=1800, end_year=2020)
    
    def organization_dissolution_date(self):
        """Organization dissolution date (for dissolved organizations)."""
        return self.common_date(start_year=2015, end_year=2024)
    
    # Classification
    
    def organization_industry(self):
        """Industry sector."""
        return random.choice(self.INDUSTRIES)
    
    def organization_type(self):
        """Organization type."""
        return random.choice(self.ORGANIZATION_TYPES)
    
    # Size and Structure
    
    def organization_number_of_employees(self):
        """Number of employees."""
        # Use realistic distribution
        ranges = [
            (1, 10, 0.3),      # Small: 30%
            (11, 50, 0.25),    # Medium-small: 25%
            (51, 250, 0.20),   # Medium: 20%
            (251, 1000, 0.15), # Large: 15%
            (1001, 10000, 0.07), # Very large: 7%
            (10001, 100000, 0.03) # Enterprise: 3%
        ]
        
        rand = random.random()
        cumulative = 0
        for min_emp, max_emp, prob in ranges:
            cumulative += prob
            if rand <= cumulative:
                return random.randint(min_emp, max_emp)
        
        return random.randint(1, 100)
    
    # Financial
    
    def organization_annual_revenue(self):
        """Annual revenue in dollars."""
        # Revenue roughly correlated with size
        return self.common_price(min_value=100000, max_value=100000000)
    
    def organization_duns(self):
        """DUNS number."""
        return self.common_duns_number()
    
    def organization_tax_id(self):
        """Tax ID / EIN."""
        return self.common_tax_id()
    
    def organization_vat_id(self):
        """VAT ID."""
        return self.common_vat_id()
    
    def organization_global_location_number(self):
        """Global Location Number."""
        return self.common_global_location_number()
    
    # People and Relationships
    
    def organization_founder(self):
        """Founder name."""
        return self.fake.name()
    
    def organization_ceo(self):
        """CEO name."""
        return self.fake.name()
    
    # Recognition
    
    def organization_award(self):
        """Award received."""
        return random.choice(self.AWARDS)
    
    # Location
    
    def organization_address(self):
        """Organization address."""
        return self.common_address()
    
    def organization_area_served(self):
        """Geographic area served."""
        areas = [
            "Global",
            "North America",
            "Europe",
            "Asia Pacific",
            self.fake.country(),
            self.fake.state()
        ]
        return random.choice(areas)
    
    # Brand
    
    def organization_logo_url(self):
        """URL to logo image."""
        company = self.fake.company().lower().replace(" ", "").replace(",", "")
        return f"https://www.{company}.com/logo.png"
    
    def organization_brand(self):
        """Brand name."""
        return self.fake.company()


def create_organization_data(num_entities=10, include_dissolved=False, seed=None):
    """
    Generate organization data using the custom provider.
    
    Args:
        num_entities: Number of organization entities to generate
        include_dissolved: Whether to include dissolved organizations
        seed: Random seed for reproducibility
    
    Returns:
        List of dictionaries containing organization data
    """
    if seed is not None:
        Faker.seed(seed)
        random.seed(seed)
    
    fake = Faker()
    fake.add_provider(SchemaOrgOrganizationProvider)
    
    organizations = []
    
    for i in range(num_entities):
        # Determine if dissolved (5% chance if enabled)
        is_dissolved = include_dissolved and random.random() < 0.05
        
        org = {
            "@type": "Organization",
            "name": fake.organization_name(),
            "legalName": fake.organization_legal_name(),
        }
        
        # Optional properties with varying probability
        if random.random() < 0.4:
            org["alternateName"] = fake.organization_alternate_name()
        
        org["description"] = fake.organization_description()
        
        if random.random() < 0.3:
            org["slogan"] = fake.organization_slogan()
        
        # Contact info
        org["email"] = fake.organization_email()
        org["telephone"] = fake.organization_telephone()
        org["url"] = fake.organization_url()
        
        if random.random() < 0.3:
            org["faxNumber"] = fake.organization_fax_number()
        
        # Dates
        org["foundingDate"] = fake.organization_founding_date()
        
        if is_dissolved:
            org["dissolutionDate"] = fake.organization_dissolution_date()
        
        # Classification
        org["industry"] = fake.organization_industry()
        
        if random.random() < 0.6:
            org["organizationType"] = fake.organization_type()
        
        # Size
        org["numberOfEmployees"] = fake.organization_number_of_employees()
        
        if random.random() < 0.5:
            org["annualRevenue"] = fake.organization_annual_revenue()
        
        # Identifiers
        if random.random() < 0.7:
            org["taxID"] = fake.organization_tax_id()
        
        if random.random() < 0.4:
            org["vatID"] = fake.organization_vat_id()
        
        if random.random() < 0.3:
            org["duns"] = fake.organization_duns()
        
        if random.random() < 0.2:
            org["globalLocationNumber"] = fake.organization_global_location_number()
        
        # People
        if random.random() < 0.5:
            org["founder"] = fake.organization_founder()
        
        if random.random() < 0.6:
            org["ceo"] = fake.organization_ceo()
        
        # Location
        if random.random() < 0.8:
            org["address"] = fake.organization_address()
        
        if random.random() < 0.5:
            org["areaServed"] = fake.organization_area_served()
        
        # Brand
        if random.random() < 0.4:
            org["logo"] = fake.organization_logo_url()
        
        if random.random() < 0.3:
            org["brand"] = fake.organization_brand()
        
        # Recognition
        if random.random() < 0.2:
            org["award"] = fake.organization_award()
        
        organizations.append(org)
    
    return organizations


if __name__ == "__main__":
    # Test the provider
    print("Testing Schema.org Organization Provider\n")
    print("=" * 80)
    
    orgs = create_organization_data(num_entities=3, include_dissolved=False, seed=42)
    
    for i, org in enumerate(orgs, 1):
        print(f"\nOrganization {i}:")
        print("-" * 80)
        for key, value in org.items():
            if isinstance(value, dict):
                print(f"  {key}:")
                for k, v in value.items():
                    print(f"    {k}: {v}")
            else:
                print(f"  {key}: {value}")



