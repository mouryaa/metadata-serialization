#!/usr/bin/env python3
"""
Simple example demonstrating the Person data generator.

This script shows how to:
1. Generate a small number of Person entities
2. Display the generated data
3. Save to an RDF file
"""

import sys
from pathlib import Path

# Add parent directory to path to import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from providers.person_provider import create_person_data
import json


def main():
    print("=" * 80)
    print("Schema.org Person Generator - Simple Example")
    print("=" * 80)
    print()
    
    # Generate 3 persons with a fixed seed for reproducibility
    print("Generating 3 sample persons...\n")
    persons = create_person_data(num_entities=3, include_deceased=False, seed=12345)
    
    # Display the generated data
    for i, person in enumerate(persons, 1):
        print(f"\nPerson {i}:")
        print("-" * 80)
        
        for key, value in person.items():
            if key == "@type":
                continue
                
            if isinstance(value, dict):
                print(f"  {key}:")
                for k, v in value.items():
                    print(f"    {k}: {v}")
            elif isinstance(value, list):
                print(f"  {key}: {', '.join(str(v) for v in value)}")
            else:
                print(f"  {key}: {value}")
    
    print("\n" + "=" * 80)
    print("Example complete!")
    print("=" * 80)
    print()
    print("To generate RDF data, use the main script:")
    print("  python generate_person_data.py --num-entities 100 --output persons.ttl")
    print()


if __name__ == "__main__":
    main()



