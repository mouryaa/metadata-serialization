#!/bin/bash
# Setup script for Synthetic RDF Generator

echo "========================================="
echo "Synthetic RDF Generator - Setup"
echo "========================================="
echo

# Check Python version
echo "Checking Python version..."
python_version=$(python --version 2>&1)
echo "Found: $python_version"
echo

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
echo "✓ Virtual environment created"
echo

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip
echo

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo

# Create output directory
echo "Creating directories..."
mkdir -p output
mkdir -p examples
echo "✓ Directories created"
echo

echo "========================================="
echo "Setup complete!"
echo "========================================="
echo
echo "To get started:"
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo
echo "  2. Run the example:"
echo "     python examples/simple_example.py"
echo
echo "  3. Generate Person data:"
echo "     python generate_person_data.py --num-entities 100 --output output/persons.ttl"
echo



