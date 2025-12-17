# Synthetic RDF Generator for Schema.org

Generate realistic synthetic RDF data for Schema.org ontologies using Faker-based providers.

## 🎯 Features

- **Multiple Schema.org Types**: Support for Person, Organization, BankAccount, and Order
- **Code Reuse Architecture**: BaseSchemaOrgProvider enables sharing of common properties
- **Realistic Data**: Powered by Faker for human-like names, addresses, emails, jobs, and more
- **Multiple Formats**: Export to Turtle, RDF/XML, JSON-LD, N-Triples, and N3
- **SHACL Validation**: Built-in shape definitions for data validation
- **Easy to Use**: Simple CLI and Python API
- **Extensible**: Easy to add support for additional Schema.org types

## 📦 Installation

### Quick Setup

```bash
# Run automated setup
./setup.sh
```

### Manual Setup

```bash
# Install Python 3.8 or higher, then:
pip install -r requirements.txt
```

## 🚀 Quick Start

### Generate Individual Entities

```bash
# Generate 10 persons (default)
python generate_person_data.py

# Generate 100 persons with custom output
python generate_person_data.py --num-entities 100 --output persons.ttl

# With statistics
python generate_person_data.py --num-entities 100 --print-stats

# Reproducible data (using seed)
python generate_person_data.py --num-entities 50 --seed 42 --output persons.ttl
```

### Generate Linked Data (NEW!)

Generate **interconnected** data with People, BankAccounts, Orders, and Organizations:

```bash
# Generate 10 people, each with 1-2 accounts, 1-3 orders per account, at 5 organizations
python generate_linked_data.py -n 10 -y 2 -x 3 -z 5 -o linked_data.ttl

# Large realistic dataset
python generate_linked_data.py -n 100 -y 3 -x 4 -z 20 -o ecommerce_data.ttl
```

See **[LINKED_DATA_GUIDE.md](LINKED_DATA_GUIDE.md)** for complete documentation.

### Run Examples

```bash
# Simple example (generates and displays 3 persons)
python examples/simple_example.py

# Batch generation (creates multiple datasets)
python examples/batch_generation.py
```

### Using in Python

```python
from faker import Faker
from providers.person_provider import SchemaOrgPersonProvider

# Setup
fake = Faker()
fake.add_provider(SchemaOrgPersonProvider)

# Generate properties
name = fake.person_name()
email = fake.person_email()
job = fake.person_job_title()
address = fake.person_address()
```

## 📊 Example Output

```turtle
@prefix schema: <http://schema.org/> .
@prefix ex: <http://example.org/person/> .

ex:person_1 a schema:Person ;
    schema:name "Donald Walker" ;
    schema:givenName "Jill" ;
    schema:familyName "Rhodes" ;
    schema:email "garzaanthony@example.org" ;
    schema:jobTitle "Armed forces logistics officer" ;
    schema:birthDate "1982-03-15"^^xsd:date ;
    schema:nationality "Estonia" ;
    schema:alumniOf "Cambridge University" ;
    schema:knowsLanguage "Korean", "Spanish" .
```

## 📚 Documentation

- **[LINKED_DATA_GUIDE.md](LINKED_DATA_GUIDE.md)** - **NEW!** Generate interconnected data with relationships
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Command cheat sheet and common patterns
- **[USAGE.md](USAGE.md)** - Comprehensive usage guide with examples
- **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** - Architecture, design, and roadmap
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - How to contribute and extend

## 🏗️ Project Structure

```
syntheticRDF/
├── shapes/                      # SHACL shape definitions
│   └── person_shape.ttl        # Schema.org/Person constraints
├── providers/                   # Custom Faker providers
│   ├── __init__.py
│   └── person_provider.py      # Person property providers
├── examples/                    # Usage examples
│   ├── simple_example.py
│   └── batch_generation.py
├── generate_person_data.py     # Main CLI tool
├── validate_rdf.py             # SHACL validation tool
├── setup.sh                    # Automated setup script
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🎨 Supported Schema.org Types

### Person (30+ properties)

| Category | Properties |
|----------|------------|
| **Identity** | name, givenName, familyName, additionalName, alternateName, honorificPrefix, honorificSuffix |
| **Contact** | email, telephone, faxNumber, url |
| **Biographical** | birthDate, birthPlace, deathDate, deathPlace, gender, nationality |
| **Professional** | jobTitle, worksFor, affiliation, alumniOf |
| **Physical** | height, weight |
| **Location** | address (PostalAddress) |
| **Social** | award, knowsLanguage |
| **Identifiers** | taxID, vatID |

### Organization (25+ properties)

| Category | Properties |
|----------|------------|
| **Identity** | name, legalName, alternateName, description, slogan |
| **Contact** | email, telephone, faxNumber, url |
| **Dates** | foundingDate, dissolutionDate |
| **Classification** | industry, organizationType |
| **Size** | numberOfEmployees, annualRevenue |
| **People** | founder, CEO |
| **Location** | address, areaServed |
| **Brand** | logo, brand |
| **Identifiers** | taxID, vatID, duns, globalLocationNumber |

### BankAccount (20+ properties)

| Category | Properties |
|----------|------------|
| **Identity** | name, identifier, accountNumber, accountType |
| **Bank Info** | bankName, branchCode, routingNumber, swiftCode, iban |
| **Financial** | currency, balance, minimumBalance, interestRate |
| **Dates** | openingDate, closingDate |
| **Status** | status |
| **Account Holder** | accountHolder, accountHolderEmail, accountHolderTelephone |
| **Fees** | monthlyFee, overdraftLimit |

### Order (25+ properties)

| Category | Properties |
|----------|------------|
| **Identity** | orderNumber, confirmationNumber |
| **Status** | orderStatus, paymentStatus |
| **Dates** | orderDate, deliveryDate |
| **Customer** | customer (name, email, telephone) |
| **Addresses** | billingAddress, shippingAddress |
| **Items** | orderedItems (name, quantity, price) |
| **Financial** | subtotal, tax, shippingCost, discount, total, currency |
| **Payment** | paymentMethod, paymentStatus |
| **Shipping** | deliveryMethod, trackingNumber |
| **Merchant** | merchant, merchantUrl |

## 🔧 Advanced Usage

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

### Validation

```bash
# Install validation support
pip install pyshacl

# Validate generated data
python validate_rdf.py persons.ttl

# With custom shapes
python validate_rdf.py persons.ttl --shapes shapes/person_shape.ttl
```

### Generate with Options

```bash
# Include deceased persons
python generate_person_data.py --num-entities 100 --include-deceased

# Full featured generation
python generate_person_data.py \
  --num-entities 1000 \
  --output large_dataset.ttl \
  --format turtle \
  --include-deceased \
  --seed 42 \
  --print-stats
```

## 🤝 Contributing

We welcome contributions! To add support for other Schema.org types:

1. Create a SHACL shape file in `shapes/`
2. Create a Faker provider in `providers/`
3. Create a generation script
4. Add examples and tests

See **[CONTRIBUTING.md](CONTRIBUTING.md)** for detailed guidelines.

## 🎯 Use Cases

- **Testing**: Generate realistic test data for semantic web applications
- **Benchmarking**: Create datasets of various sizes for performance testing
- **Development**: Provide sample data during ontology development
- **Education**: Teaching RDF, SPARQL, and semantic technologies
- **Research**: Reproducible synthetic datasets for research

## 📈 Performance

| Entities | Generation Time | File Size (Turtle) |
|----------|----------------|-------------------|
| 10       | < 1 second     | ~5 KB            |
| 100      | ~1 second      | ~50 KB           |
| 1,000    | ~10 seconds    | ~500 KB          |
| 10,000   | ~100 seconds   | ~5 MB            |

## 🏗️ Code Reuse Architecture

The project uses a **base provider pattern** for code reuse:

```python
BaseSchemaOrgProvider (common properties)
  ├─ SchemaOrgPersonProvider
  ├─ SchemaOrgOrganizationProvider  
  ├─ SchemaOrgBankAccountProvider
  └─ SchemaOrgOrderProvider
```

**Common properties** (email, telephone, address, url, identifiers, etc.) are defined once in `BaseSchemaOrgProvider` and reused across all types. This ensures:

- ✓ **Consistency**: Same format across all types
- ✓ **Maintainability**: Update once, applies everywhere
- ✓ **DRY Principle**: No code duplication
- ✓ **Extensibility**: New types inherit common functionality

See `examples/demonstrate_code_reuse.py` for a detailed demonstration.

## 🔮 Roadmap

- [x] Add Organization provider
- [x] Add BankAccount provider
- [x] Add Order provider
- [x] Implement base provider for code reuse
- [x] **Generate linked data with relationships**
- [x] **SHACL shapes for all types**
- [ ] Add Product provider
- [ ] Add Event provider
- [ ] Add Place provider
- [ ] Support more relationship types (Person knows Person, etc.)
- [ ] Web UI for generation
- [ ] Direct triple store integration
- [ ] Multi-language support

## 📝 Requirements

- Python 3.8+
- Faker >= 20.0.0
- rdflib >= 7.0.0
- rdf-graph-gen >= 0.1.0
- pyshacl >= 0.25.0 (optional, for validation)

## 📄 License

This project is provided as-is for educational and development purposes.

## 🙏 Acknowledgments

- Built with [Faker](https://faker.readthedocs.io/) for realistic data generation
- Uses [rdflib](https://rdflib.readthedocs.io/) for RDF manipulation
- Inspired by [rdf-graph-gen](https://github.com/etnc/RDFGraphGen/)
- Based on [Schema.org](https://schema.org/) vocabulary

## 📞 Support

- **Documentation**: See USAGE.md and PROJECT_OVERVIEW.md
- **Examples**: Check the `examples/` directory
- **Issues**: Open an issue on GitHub
- **Contributing**: See CONTRIBUTING.md

---

**Happy RDF Generating! 🎉**

