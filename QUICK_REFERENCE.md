# Quick Reference Guide

## Installation

```bash
# Option 1: Automated setup
./setup.sh

# Option 2: Manual setup
pip install -r requirements.txt
```

## Basic Commands

### Generate Person Data

```bash
# Default (10 persons)
python generate_person_data.py

# Specify number of entities
python generate_person_data.py --num-entities 100

# Custom output file
python generate_person_data.py --output my_persons.ttl

# With statistics
python generate_person_data.py --num-entities 100 --print-stats

# Reproducible (with seed)
python generate_person_data.py --num-entities 50 --seed 12345
```

### Output Formats

```bash
# Turtle (default)
python generate_person_data.py --format turtle --output persons.ttl

# RDF/XML
python generate_person_data.py --format xml --output persons.rdf

# JSON-LD
python generate_person_data.py --format json-ld --output persons.jsonld

# N-Triples
python generate_person_data.py --format nt --output persons.nt
```

### Special Options

```bash
# Include deceased persons
python generate_person_data.py --include-deceased

# Full command with all options
python generate_person_data.py \
  --num-entities 1000 \
  --output large_dataset.ttl \
  --format turtle \
  --include-deceased \
  --seed 42 \
  --print-stats
```

## Examples

### Run Simple Example
```bash
python examples/simple_example.py
```

### Batch Generation
```bash
python examples/batch_generation.py
```

## Validation

```bash
# Install pyshacl first
pip install pyshacl

# Validate generated data
python validate_rdf.py output_persons.ttl

# With custom shapes
python validate_rdf.py output_persons.ttl --shapes shapes/person_shape.ttl

# Save validation report
python validate_rdf.py output_persons.ttl --output-report report.ttl
```

## Using in Python Code

### Import and Use Provider

```python
from faker import Faker
from providers.person_provider import SchemaOrgPersonProvider

# Setup
fake = Faker()
fake.add_provider(SchemaOrgPersonProvider)

# Generate individual properties
name = fake.person_name()
email = fake.person_email()
job = fake.person_job_title()
```

### Generate Dictionary Data

```python
from providers.person_provider import create_person_data

persons = create_person_data(num_entities=10, seed=42)

for person in persons:
    print(person['name'], person.get('email'))
```

### Generate RDF Graph

```python
from generate_person_data import create_person_graph

graph = create_person_graph(num_entities=100, seed=42)
graph.serialize(destination="persons.ttl", format="turtle")
```

## Provider Methods

### Identity
- `person_name()` - Full name
- `person_given_name()` - First name
- `person_family_name()` - Last name
- `person_additional_name()` - Middle name
- `person_alternate_name()` - Nickname/alias
- `person_honorific_prefix()` - Mr., Dr., etc.
- `person_honorific_suffix()` - Jr., PhD, etc.

### Contact
- `person_email()` - Email address
- `person_telephone()` - Phone number
- `person_fax_number()` - Fax number
- `person_url()` - Personal website

### Biographical
- `person_birth_date()` - Birth date
- `person_birth_place()` - Place of birth
- `person_death_date(birth_date)` - Death date
- `person_death_place()` - Place of death
- `person_gender()` - Gender
- `person_nationality()` - Nationality

### Professional
- `person_job_title()` - Job title
- `person_works_for()` - Employer
- `person_affiliation()` - Affiliations
- `person_alumni_of()` - Educational institution

### Physical
- `person_height()` - Height
- `person_weight()` - Weight

### Location
- `person_address()` - Full address (dict)

### Social
- `person_award()` - Award received
- `person_knows_language()` - Language(s) known

### Identifiers
- `person_tax_id()` - Tax ID/SSN
- `person_vat_id()` - VAT ID

## File Structure

```
syntheticRDF/
├── shapes/                    # SHACL shape definitions
│   └── person_shape.ttl
├── providers/                 # Faker providers
│   ├── __init__.py
│   └── person_provider.py
├── examples/                  # Usage examples
│   ├── __init__.py
│   ├── simple_example.py
│   └── batch_generation.py
├── generate_person_data.py   # Main CLI tool
├── validate_rdf.py           # Validation tool
├── setup.sh                  # Setup script
├── requirements.txt          # Dependencies
├── README.md                 # Overview
├── USAGE.md                  # Detailed guide
├── QUICK_REFERENCE.md        # This file
├── PROJECT_OVERVIEW.md       # Architecture
└── CONTRIBUTING.md           # Contributing guide
```

## Common Patterns

### Generate Test Data
```bash
# Small test set
python generate_person_data.py --num-entities 10 --seed 1 --output test.ttl

# Medium test set
python generate_person_data.py --num-entities 100 --seed 1 --output test.ttl

# Large test set
python generate_person_data.py --num-entities 1000 --seed 1 --output test.ttl
```

### Generate Multiple Formats
```bash
# Generate all formats
for format in turtle xml json-ld nt n3; do
  python generate_person_data.py \
    --num-entities 100 \
    --format $format \
    --seed 42 \
    --output persons.$format
done
```

### Query Generated Data
```python
from rdflib import Graph, Namespace

SCHEMA = Namespace("http://schema.org/")

# Load data
g = Graph()
g.parse("persons.ttl")

# Query for emails
for person in g.subjects(predicate=SCHEMA.email):
    name = g.value(person, SCHEMA.name)
    email = g.value(person, SCHEMA.email)
    print(f"{name}: {email}")
```

## Tips

1. **Always use `--seed` for reproducible data**
2. **Start with small datasets (10-100) for testing**
3. **Use `--print-stats` to verify generation**
4. **Validate data with `validate_rdf.py` after generation**
5. **Check `examples/` for more usage patterns**

## Troubleshooting

### Import Errors
```bash
# Make sure you're in the right directory
cd syntheticRDF

# Reinstall dependencies
pip install -r requirements.txt
```

### Permission Errors
```bash
# Make scripts executable
chmod +x generate_person_data.py setup.sh validate_rdf.py
```

### Memory Issues (Large Datasets)
```bash
# Generate in smaller batches
for i in {1..10}; do
  python generate_person_data.py \
    --num-entities 10000 \
    --output batch_$i.ttl \
    --seed $i
done
```

## Help

```bash
# Get help for generation script
python generate_person_data.py --help

# Get help for validation
python validate_rdf.py --help
```

## Resources

- **README.md** - Project overview and quick start
- **USAGE.md** - Comprehensive usage guide
- **PROJECT_OVERVIEW.md** - Architecture and design
- **CONTRIBUTING.md** - How to contribute
- **shapes/person_shape.ttl** - SHACL definitions

## Schema.org References

- Person: https://schema.org/Person
- PostalAddress: https://schema.org/PostalAddress

---

For more details, see **USAGE.md** and **PROJECT_OVERVIEW.md**.



