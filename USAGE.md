# Usage Guide

This guide provides detailed instructions for using the Synthetic RDF Generator for Schema.org/Person.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Basic Usage](#basic-usage)
3. [Advanced Usage](#advanced-usage)
4. [Custom Providers](#custom-providers)
5. [Validation](#validation)
6. [Examples](#examples)

## Quick Start

### Installation

```bash
# Clone or navigate to the project directory
cd syntheticRDF

# Run the setup script (creates venv and installs dependencies)
./setup.sh

# Or manually install
pip install -r requirements.txt
```

### Generate Your First Dataset

```bash
# Generate 10 persons (default)
python generate_person_data.py

# Generate 100 persons with custom output
python generate_person_data.py --num-entities 100 --output my_persons.ttl
```

## Basic Usage

### Command-Line Options

The main script `generate_person_data.py` supports the following options:

```bash
python generate_person_data.py [OPTIONS]
```

**Options:**

- `--num-entities N`: Number of Person entities to generate (default: 10)
- `--output FILE`: Output file path (default: output_persons.ttl)
- `--format FORMAT`: Output RDF format - turtle, xml, n3, nt, json-ld (default: turtle)
- `--include-deceased`: Include some deceased persons with death dates/places
- `--seed N`: Random seed for reproducibility
- `--print-stats`: Print statistics about the generated graph

### Examples

**Generate 1000 persons:**
```bash
python generate_person_data.py --num-entities 1000 --output large_dataset.ttl
```

**Generate with deceased persons:**
```bash
python generate_person_data.py --num-entities 100 --include-deceased --output persons_with_deceased.ttl
```

**Generate reproducible data:**
```bash
python generate_person_data.py --num-entities 50 --seed 12345 --output reproducible.ttl
```

**Output in different formats:**
```bash
# RDF/XML
python generate_person_data.py --num-entities 100 --format xml --output persons.rdf

# JSON-LD
python generate_person_data.py --num-entities 100 --format json-ld --output persons.jsonld

# N-Triples
python generate_person_data.py --num-entities 100 --format nt --output persons.nt
```

**With statistics:**
```bash
python generate_person_data.py --num-entities 100 --print-stats --output persons.ttl
```

## Advanced Usage

### Using the Provider Directly

You can use the Person provider directly in your Python code:

```python
from faker import Faker
from providers.person_provider import SchemaOrgPersonProvider

# Create Faker instance with our provider
fake = Faker()
fake.add_provider(SchemaOrgPersonProvider)

# Generate individual properties
name = fake.person_name()
email = fake.person_email()
birth_date = fake.person_birth_date()
job_title = fake.person_job_title()
address = fake.person_address()

print(f"Name: {name}")
print(f"Email: {email}")
print(f"Birth Date: {birth_date}")
print(f"Job: {job_title}")
print(f"Address: {address}")
```

### Generate Data as Python Dictionaries

```python
from providers.person_provider import create_person_data

# Generate 10 persons as dictionaries
persons = create_person_data(num_entities=10, include_deceased=False, seed=42)

for person in persons:
    print(f"Name: {person['name']}")
    print(f"Email: {person.get('email', 'N/A')}")
    print(f"Job: {person.get('jobTitle', 'N/A')}")
    print()
```

### Customizing Property Probability

Edit the `generate_person_data.py` script to adjust the probability of including optional properties:

```python
# Example: Make email appear 95% of the time instead of 80%
if random.random() < 0.95:  # Changed from 0.8
    g.add((person_uri, SCHEMA.email, Literal(fake.person_email(), datatype=XSD.string)))
```

### Batch Generation

Use the batch generation example to create multiple datasets:

```bash
python examples/batch_generation.py
```

This creates small (10), medium (100), and large (1000) datasets in multiple formats.

## Custom Providers

### Available Provider Methods

The `SchemaOrgPersonProvider` includes methods for all Schema.org/Person properties:

**Identity:**
- `person_name()` - Full name
- `person_given_name()` - First name
- `person_family_name()` - Last name
- `person_additional_name()` - Middle name
- `person_alternate_name()` - Nickname
- `person_honorific_prefix()` - Mr., Dr., etc.
- `person_honorific_suffix()` - Jr., PhD, etc.

**Contact:**
- `person_email()` - Email address
- `person_telephone()` - Phone number
- `person_fax_number()` - Fax number
- `person_url()` - Personal website

**Biographical:**
- `person_birth_date()` - Date of birth
- `person_birth_place()` - Place of birth
- `person_death_date(birth_date)` - Date of death
- `person_death_place()` - Place of death
- `person_gender()` - Gender
- `person_nationality()` - Nationality

**Professional:**
- `person_job_title()` - Job title
- `person_works_for()` - Employer
- `person_affiliation()` - Affiliations
- `person_alumni_of()` - Educational institutions

**Physical:**
- `person_height()` - Height
- `person_weight()` - Weight

**Location:**
- `person_address()` - Full address (returns dict)

**Social:**
- `person_award()` - Awards received
- `person_knows_language()` - Languages known

**Identifiers:**
- `person_tax_id()` - Tax ID/SSN
- `person_vat_id()` - VAT ID

### Creating Additional Providers

To extend the system for other Schema.org types (e.g., Organization, Product):

1. Create a new provider file in `providers/`:

```python
# providers/organization_provider.py
from faker.providers import BaseProvider

class SchemaOrgOrganizationProvider(BaseProvider):
    def organization_name(self):
        return self.generator.company()
    
    def organization_email(self):
        return self.generator.company_email()
    
    # Add more methods...
```

2. Create a corresponding SHACL shape file in `shapes/`

3. Create a generation script similar to `generate_person_data.py`

## Validation

### Validate Generated Data

To validate that generated RDF conforms to the SHACL shapes:

```bash
# First, install pyshacl
pip install pyshacl

# Validate a generated file
python validate_rdf.py output_persons.ttl

# Specify custom shapes file
python validate_rdf.py output_persons.ttl --shapes shapes/person_shape.ttl

# Save validation report
python validate_rdf.py output_persons.ttl --output-report validation_report.ttl
```

### Understanding Validation Results

**Success:**
```
✓ VALIDATION PASSED
The RDF data conforms to all SHACL constraints.
```

**Failure:**
```
✗ VALIDATION FAILED
The RDF data does not conform to SHACL constraints.

Validation Report:
[Details of constraint violations...]
```

## Examples

### Example 1: Simple Generation

```bash
# Navigate to examples
cd examples

# Run simple example (generates 3 persons and displays them)
python simple_example.py
```

### Example 2: Batch Generation

```bash
# Generate multiple datasets in different formats
python examples/batch_generation.py

# This creates:
# - output/small_dataset.{ttl,rdf,jsonld}
# - output/medium_dataset.{ttl,rdf,jsonld}
# - output/large_dataset.{ttl,rdf,jsonld}
```

### Example 3: Integration with Existing RDF

```python
from rdflib import Graph
from generate_person_data import create_person_graph

# Create persons
person_graph = create_person_graph(num_entities=10)

# Load existing RDF data
existing_graph = Graph()
existing_graph.parse("existing_data.ttl")

# Merge graphs
combined_graph = existing_graph + person_graph

# Save combined data
combined_graph.serialize(destination="combined_data.ttl", format="turtle")
```

### Example 4: Filtering Generated Data

```python
from rdflib import Graph
from rdflib.namespace import RDF, Namespace

SCHEMA = Namespace("http://schema.org/")

# Load generated data
g = Graph()
g.parse("output_persons.ttl")

# Query for specific persons (e.g., those with email addresses)
for subject in g.subjects(predicate=SCHEMA.email):
    name = g.value(subject, SCHEMA.name)
    email = g.value(subject, SCHEMA.email)
    print(f"{name}: {email}")
```

### Example 5: Export to CSV

```python
from rdflib import Graph, Namespace
import csv

SCHEMA = Namespace("http://schema.org/")

# Load RDF data
g = Graph()
g.parse("output_persons.ttl")

# Export to CSV
with open("persons.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Name", "Email", "Job Title", "Birth Date"])
    
    for person in g.subjects(predicate=RDF.type, object=SCHEMA.Person):
        name = g.value(person, SCHEMA.name)
        email = g.value(person, SCHEMA.email)
        job = g.value(person, SCHEMA.jobTitle)
        birth = g.value(person, SCHEMA.birthDate)
        
        writer.writerow([name, email, job, birth])

print("Exported to persons.csv")
```

## Property Coverage

The provider includes comprehensive coverage of Schema.org/Person properties:

| Category | Properties | Coverage |
|----------|------------|----------|
| Identity | name, givenName, familyName, additionalName, alternateName, honorificPrefix, honorificSuffix | 100% |
| Contact | email, telephone, faxNumber, url | 100% |
| Biographical | birthDate, birthPlace, deathDate, deathPlace, gender, nationality | 100% |
| Professional | jobTitle, worksFor, affiliation, alumniOf | 100% |
| Physical | height, weight | 100% |
| Location | address (PostalAddress) | 100% |
| Social | award, knowsLanguage | 100% |
| Identifiers | taxID, vatID | 100% |

## Tips and Best Practices

1. **Use Seeds for Testing**: Always use `--seed` when generating test data for reproducibility
2. **Start Small**: Test with small datasets (10-100 entities) before generating large ones
3. **Validate Often**: Run validation after making changes to ensure data quality
4. **Customize Probabilities**: Adjust property inclusion probabilities based on your use case
5. **Version Control**: Keep your SHACL shapes in version control
6. **Document Changes**: If you modify providers, document what properties changed

## Troubleshooting

### Common Issues

**Issue: Module not found errors**
```
Solution: Make sure you're in the correct directory and dependencies are installed:
  cd syntheticRDF
  pip install -r requirements.txt
```

**Issue: Permission denied when running scripts**
```
Solution: Make scripts executable:
  chmod +x generate_person_data.py
  chmod +x setup.sh
```

**Issue: Validation fails unexpectedly**
```
Solution: Check that your SHACL shapes match the generated data structure.
Review the validation report for specific constraint violations.
```

## Next Steps

- Explore the SHACL shapes in `shapes/person_shape.ttl`
- Customize the provider methods in `providers/person_provider.py`
- Create providers for other Schema.org types (Organization, Product, etc.)
- Integrate generated data with your semantic web applications

## Support

For issues or questions:
1. Review this documentation
2. Check the examples in the `examples/` directory
3. Examine the SHACL shapes in `shapes/`
4. Review the provider code in `providers/`



