#!/usr/bin/env python3
"""
RDF Turtle Format Converter
Converts RDF Turtle (.ttl) files to JSON-LD, XML, N3, and NT formats
"""

import sys
import os
from pathlib import Path
from rdflib import Graph, plugin
from rdflib.serializer import Serializer




def convert_turtle(input_file, output_dir=None):
    """
    Convert a Turtle RDF file to multiple formats.
    
    Args:
        input_file: Path to input Turtle file
        output_dir: Optional output directory (defaults to same as input)
    """
    input_path = Path(input_file)
    
    if not input_path.exists():
        print(f"Error: File '{input_file}' not found")
        return False
    
    # Set output directory
    if output_dir:
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
    else:
        out_path = input_path.parent
    
    base_name = input_path.stem
    
    # Load the Turtle file
    print(f"Loading {input_file}...")
    g = Graph()
    try:
        g.parse(input_file, format='turtle')
        print(f"Successfully loaded {len(g)} triples")
    except Exception as e:
        print(f"Error parsing Turtle file: {e}")
        return False
    
    # Define output formats
    formats = {
        'jsonld': 'json-ld',
        'xml': 'xml',
        'n3': 'n3',
        'nt': 'nt'
    }
    
    # Convert to each format
    results = []
    for ext, fmt in formats.items():
        output_file = out_path / f"{base_name}.{ext}"
        try:
            g.serialize(destination=str(output_file), format=fmt)
            print(f"✓ Created {output_file}")
            results.append(output_file)
        except Exception as e:
            print(f"✗ Error creating {ext}: {e}")
    
    return results


def main():
    if len(sys.argv) < 2:
        print("Usage: python rdf_converter.py <input.ttl> [output_directory]")
        print("\nConverts RDF Turtle files to JSON-LD, XML, N3, and NT formats")
        print("\nExample:")
        print("  python rdf_converter.py data.ttl")
        print("  python rdf_converter.py data.ttl ./output")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    print("RDF Turtle Format Converter")
    print("=" * 50)
    
    results = convert_turtle(input_file, output_dir)
    
    if results:
        print("\n" + "=" * 50)
        print(f"Conversion complete! Created {len(results)} files.")
    else:
        print("\nConversion failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()