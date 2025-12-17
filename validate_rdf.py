#!/usr/bin/env python3
"""
Validate generated RDF data against SHACL shapes.

This script validates that the generated RDF data conforms to the
Schema.org/Person SHACL constraints.
"""

import argparse
import sys
from pathlib import Path
from rdflib import Graph

try:
    from pyshacl import validate
    PYSHACL_AVAILABLE = True
except ImportError:
    PYSHACL_AVAILABLE = False
    print("Warning: pyshacl not installed. Install with: pip install pyshacl")


def validate_rdf_file(data_file, shapes_file):
    """
    Validate an RDF data file against SHACL shapes.
    
    Args:
        data_file: Path to RDF data file to validate
        shapes_file: Path to SHACL shapes file
    
    Returns:
        Tuple of (conforms, results_graph, results_text)
    """
    if not PYSHACL_AVAILABLE:
        print("Error: pyshacl package is required for validation")
        print("Install it with: pip install pyshacl")
        return None, None, None
    
    print(f"Loading data from {data_file}...")
    data_graph = Graph()
    data_graph.parse(data_file)
    print(f"  ✓ Loaded {len(data_graph)} triples")
    
    print(f"\nLoading shapes from {shapes_file}...")
    shapes_graph = Graph()
    shapes_graph.parse(shapes_file)
    print(f"  ✓ Loaded {len(shapes_graph)} triples")
    
    print("\nValidating...")
    conforms, results_graph, results_text = validate(
        data_graph,
        shacl_graph=shapes_graph,
        inference='rdfs',
        abort_on_first=False,
    )
    
    return conforms, results_graph, results_text


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate RDF data against SHACL shapes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "data_file",
        type=str,
        help="Path to RDF data file to validate"
    )
    
    parser.add_argument(
        "--shapes",
        type=str,
        default="shapes/person_shape.ttl",
        help="Path to SHACL shapes file (default: shapes/person_shape.ttl)"
    )
    
    parser.add_argument(
        "--output-report",
        type=str,
        help="Save validation report to file"
    )
    
    args = parser.parse_args()
    
    # Check if files exist
    data_path = Path(args.data_file)
    shapes_path = Path(args.shapes)
    
    if not data_path.exists():
        print(f"Error: Data file not found: {data_path}", file=sys.stderr)
        return 1
    
    if not shapes_path.exists():
        print(f"Error: Shapes file not found: {shapes_path}", file=sys.stderr)
        return 1
    
    # Validate
    print("=" * 80)
    print("RDF Validation Tool")
    print("=" * 80)
    print()
    
    conforms, results_graph, results_text = validate_rdf_file(
        str(data_path),
        str(shapes_path)
    )
    
    if conforms is None:
        return 1
    
    # Display results
    print("\n" + "=" * 80)
    print("Validation Results")
    print("=" * 80)
    
    if conforms:
        print("\n✓ VALIDATION PASSED")
        print("The RDF data conforms to all SHACL constraints.")
    else:
        print("\n✗ VALIDATION FAILED")
        print("The RDF data does not conform to SHACL constraints.")
        print("\nValidation Report:")
        print("-" * 80)
        print(results_text)
    
    # Save report if requested
    if args.output_report and results_graph:
        print(f"\nSaving validation report to {args.output_report}...")
        results_graph.serialize(destination=args.output_report, format='turtle')
        print("✓ Report saved")
    
    print("\n" + "=" * 80)
    
    return 0 if conforms else 1


if __name__ == "__main__":
    sys.exit(main())



