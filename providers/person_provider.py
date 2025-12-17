"""
Custom Faker provider for Schema.org/Person properties.
Generates realistic data for all Person properties defined in the Schema.org ontology.
"""

from faker import Faker
from faker.providers import BaseProvider
from .base_provider import BaseSchemaOrgProvider
from datetime import datetime, timedelta
import random


class SchemaOrgPersonProvider(BaseSchemaOrgProvider):
    """Provider for Schema.org/Person properties using Faker."""
    
    # Class-level data for various properties
    HONORIFIC_PREFIXES = ["Mr.", "Mrs.", "Ms.", "Miss", "Dr.", "Prof.", "Rev.", "Hon."]
    HONORIFIC_SUFFIXES = ["Jr.", "Sr.", "II", "III", "PhD", "MD", "Esq.", "DDS"]
    GENDERS = ["Male", "Female", "Non-binary", "Prefer not to say"]
    LANGUAGES = ["English", "Spanish", "French", "German", "Italian", "Portuguese", 
                 "Chinese", "Japanese", "Arabic", "Russian", "Hindi", "Korean"]
    AWARDS = [
        "Employee of the Year",
        "Outstanding Achievement Award",
        "Excellence in Leadership",
        "Innovation Award",
        "Best Paper Award",
        "Lifetime Achievement Award",
        "Distinguished Service Award",
        "Presidential Medal",
    ]
    
    # Basic Identity Properties
    
    def person_name(self):
        """Full name of the person."""
        return self.fake.name()
    
    def person_given_name(self):
        """Given name (first name)."""
        return self.fake.first_name()
    
    def person_family_name(self):
        """Family name (last name)."""
        return self.fake.last_name()
    
    def person_additional_name(self):
        """Middle name or initial."""
        if random.random() < 0.7:  # 70% chance of having a middle name
            return self.fake.first_name()
        else:
            return self.fake.random_uppercase_letter() + "."
    
    def person_alternate_name(self):
        """Alternate name or nickname."""
        nicknames = [
            self.fake.first_name(),
            self.fake.first_name()[:3] + "y",
            self.fake.last_name() + "son",
        ]
        return random.choice(nicknames)
    
    def person_honorific_prefix(self):
        """Honorific prefix (Mr., Mrs., Dr., etc.)."""
        return random.choice(self.HONORIFIC_PREFIXES)
    
    def person_honorific_suffix(self):
        """Honorific suffix (Jr., Sr., PhD, etc.)."""
        return random.choice(self.HONORIFIC_SUFFIXES)
    
    # Contact Information (reusing base provider methods)
    
    def person_email(self):
        """Email address."""
        return self.common_email()
    
    def person_telephone(self):
        """Telephone number."""
        return self.common_telephone()
    
    def person_fax_number(self):
        """Fax number."""
        return self.common_fax_number()
    
    def person_url(self):
        """Personal website URL."""
        return self.common_url()
    
    # Biographical Information
    
    def person_birth_date(self):
        """Date of birth."""
        start_date = datetime(1940, 1, 1)
        end_date = datetime(2005, 12, 31)
        birth_date = self.fake.date_between(start_date=start_date, end_date=end_date)
        return birth_date.isoformat()
    
    def person_birth_place(self):
        """Place of birth."""
        return f"{self.fake.city()}, {self.fake.country()}"
    
    def person_death_date(self, birth_date_str=None):
        """Date of death (only for deceased persons)."""
        if birth_date_str:
            try:
                birth_date = datetime.fromisoformat(birth_date_str)
                # Person lived between 50-100 years
                min_death = birth_date + timedelta(days=365*50)
                max_death = birth_date + timedelta(days=365*100)
                death_date = self.fake.date_between(start_date=min_death, end_date=max_death)
                return death_date.isoformat()
            except:
                pass
        
        # Fallback
        start_date = datetime(1990, 1, 1)
        end_date = datetime(2024, 12, 31)
        death_date = self.fake.date_between(start_date=start_date, end_date=end_date)
        return death_date.isoformat()
    
    def person_death_place(self):
        """Place of death."""
        return f"{self.fake.city()}, {self.fake.country()}"
    
    def person_gender(self):
        """Gender."""
        return random.choice(self.GENDERS)
    
    def person_nationality(self):
        """Nationality."""
        return self.fake.country()
    
    # Professional Information
    
    def person_job_title(self):
        """Job title or profession."""
        return self.fake.job()
    
    def person_works_for(self):
        """Organization the person works for."""
        return self.fake.company()
    
    def person_affiliation(self):
        """Organization affiliations."""
        # Can have multiple affiliations
        return self.fake.company()
    
    def person_alumni_of(self):
        """Educational institutions attended."""
        universities = [
            "Harvard University",
            "Stanford University",
            "MIT",
            "Oxford University",
            "Cambridge University",
            "Yale University",
            "Princeton University",
            "Columbia University",
            "UC Berkeley",
            "University of Chicago",
        ]
        return random.choice(universities)
    
    # Physical Characteristics
    
    def person_height(self):
        """Height in centimeters or feet/inches."""
        # Return in metric (cm)
        height_cm = random.randint(150, 200)
        return f"{height_cm} cm"
    
    def person_weight(self):
        """Weight in kilograms or pounds."""
        # Return in metric (kg)
        weight_kg = random.randint(50, 120)
        return f"{weight_kg} kg"
    
    # Address (reusing base provider method)
    
    def person_address(self):
        """Physical address as a dictionary."""
        return self.common_address()
    
    # Social and Recognition
    
    def person_award(self):
        """Awards received."""
        return random.choice(self.AWARDS)
    
    def person_knows_language(self):
        """Languages known."""
        # Return 1-3 languages
        num_languages = random.randint(1, 3)
        languages = random.sample(self.LANGUAGES, num_languages)
        return languages[0] if num_languages == 1 else languages
    
    # Identifiers (reusing base provider methods)
    
    def person_tax_id(self):
        """Tax ID (SSN, etc.)."""
        # Generate a format like SSN: XXX-XX-XXXX
        return f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(1000, 9999)}"
    
    def person_vat_id(self):
        """VAT ID."""
        return self.common_vat_id()


def create_person_data(num_entities=10, include_deceased=False, seed=None):
    """
    Generate person data using the custom provider.
    
    Args:
        num_entities: Number of person entities to generate
        include_deceased: Whether to include death date/place for some persons
        seed: Random seed for reproducibility
    
    Returns:
        List of dictionaries containing person data
    """
    if seed is not None:
        Faker.seed(seed)
        random.seed(seed)
    
    fake = Faker()
    fake.add_provider(SchemaOrgPersonProvider)
    
    persons = []
    
    for i in range(num_entities):
        # Determine if this person is deceased (10% chance if enabled)
        is_deceased = include_deceased and random.random() < 0.1
        
        # Generate birth date first (needed for death date calculation)
        birth_date = fake.person_birth_date()
        
        person = {
            "@type": "Person",
            "name": fake.person_name(),
            "givenName": fake.person_given_name(),
            "familyName": fake.person_family_name(),
        }
        
        # Add optional properties with varying probability
        if random.random() < 0.5:
            person["additionalName"] = fake.person_additional_name()
        
        if random.random() < 0.3:
            person["alternateName"] = fake.person_alternate_name()
        
        if random.random() < 0.6:
            person["honorificPrefix"] = fake.person_honorific_prefix()
        
        if random.random() < 0.2:
            person["honorificSuffix"] = fake.person_honorific_suffix()
        
        # Contact information
        person["email"] = fake.person_email()
        
        if random.random() < 0.8:
            person["telephone"] = fake.person_telephone()
        
        if random.random() < 0.2:
            person["faxNumber"] = fake.person_fax_number()
        
        if random.random() < 0.4:
            person["url"] = fake.person_url()
        
        # Biographical
        person["birthDate"] = birth_date
        
        if random.random() < 0.5:
            person["birthPlace"] = fake.person_birth_place()
        
        if is_deceased:
            person["deathDate"] = fake.person_death_date(birth_date)
            person["deathPlace"] = fake.person_death_place()
        
        person["gender"] = fake.person_gender()
        
        if random.random() < 0.7:
            person["nationality"] = fake.person_nationality()
        
        # Professional
        if random.random() < 0.8:
            person["jobTitle"] = fake.person_job_title()
        
        if random.random() < 0.7:
            person["worksFor"] = fake.person_works_for()
        
        if random.random() < 0.4:
            person["affiliation"] = fake.person_affiliation()
        
        if random.random() < 0.6:
            person["alumniOf"] = fake.person_alumni_of()
        
        # Physical
        if random.random() < 0.3:
            person["height"] = fake.person_height()
        
        if random.random() < 0.2:
            person["weight"] = fake.person_weight()
        
        # Address
        if random.random() < 0.6:
            person["address"] = fake.person_address()
        
        # Social
        if random.random() < 0.3:
            person["award"] = fake.person_award()
        
        if random.random() < 0.5:
            languages = fake.person_knows_language()
            person["knowsLanguage"] = languages
        
        # Identifiers
        if random.random() < 0.5:
            person["taxID"] = fake.person_tax_id()
        
        if random.random() < 0.2:
            person["vatID"] = fake.person_vat_id()
        
        persons.append(person)
    
    return persons


if __name__ == "__main__":
    # Test the provider
    print("Testing Schema.org Person Provider\n")
    print("=" * 80)
    
    persons = create_person_data(num_entities=3, include_deceased=True, seed=42)
    
    for i, person in enumerate(persons, 1):
        print(f"\nPerson {i}:")
        print("-" * 80)
        for key, value in person.items():
            if isinstance(value, dict):
                print(f"  {key}:")
                for k, v in value.items():
                    print(f"    {k}: {v}")
            elif isinstance(value, list):
                print(f"  {key}: {', '.join(value)}")
            else:
                print(f"  {key}: {value}")

