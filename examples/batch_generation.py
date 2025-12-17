#!/usr/bin/env python3
"""
Batch generation example.

This script demonstrates how to generate multiple RDF files with different
configurations for testing purposes.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from generate_person_data import create_person_graph


def main():
    """Generate multiple datasets with different configurations."""
    
    print("=" * 80)
    print("Batch RDF Generation Example")
    print("=" * 80)
    print()
    
    # Create output directory
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    # Configuration for different datasets
    configs = [
        {
            "name": "small_dataset",
            "num_entities": 10,
            "include_deceased": False,
            "seed": 100
        },
        {
            "name": "medium_dataset",
            "num_entities": 100,
            "include_deceased": True,
            "seed": 200
        },
        {
            "name": "large_dataset",
            "num_entities": 1000,
            "include_deceased": True,
            "seed": 300
        },
    ]
    
    # Generate each dataset
    for config in configs:
        print(f"\nGenerating {config['name']}...")
        print(f"  Entities: {config['num_entities']}")
        print(f"  Include deceased: {config['include_deceased']}")
        print(f"  Seed: {config['seed']}")
        
        # Generate graph
        graph = create_person_graph(
            num_entities=config['num_entities'],
            include_deceased=config['include_deceased'],
            seed=config['seed']
        )
        
        # Save in multiple formats
        formats = {
            "turtle": "ttl",
            "xml": "rdf",
            "json-ld": "jsonld"
        }
        
        for format_name, extension in formats.items():
            output_file = output_dir / f"{config['name']}.{extension}"
            graph.serialize(destination=str(output_file), format=format_name)
            print(f"  ✓ Saved {format_name} to {output_file.name}")
        
        print(f"  Total triples: {len(graph)}")
    
    print("\n" + "=" * 80)
    print("Batch generation complete!")
    print(f"All files saved to: {output_dir}")
    print("=" * 80)


if __name__ == "__main__":
    main()



