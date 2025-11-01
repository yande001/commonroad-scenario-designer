#!/bin/bash
# Minimal setup for OpenDRIVE to Lanelet2 conversion on macOS
# This creates a virtual environment with only the dependencies needed for map conversion

set -e

echo "========================================================================"
echo "Minimal Environment Setup for Map Conversion (macOS)"
echo "========================================================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$MAJOR" -eq 3 ] && [ "$MINOR" -ge 10 ] && [ "$MINOR" -le 13 ]; then
    echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION found"
else
    echo -e "${RED}✗${NC} Python $PYTHON_VERSION not supported. Please use Python 3.10-3.13"
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ -d "venv_minimal" ]; then
    echo "Removing existing venv_minimal..."
    rm -rf venv_minimal
fi
python3 -m venv venv_minimal
echo -e "${GREEN}✓${NC} Virtual environment created"

# Activate virtual environment
source venv_minimal/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install only the packages needed for odr_to_ll2 conversion
echo ""
echo "Installing required packages for map conversion..."
echo "This may take a few minutes..."
echo ""

pip install \
    "commonroad-io>=2024.2,<=2024.3" \
    "commonroad-clcs>=2025.1" \
    "pyqt6>=6.6.0" \
    "lxml>=6.0.2" \
    "numpy>=1.26.1" \
    "matplotlib>=3.6.0" \
    "scipy>=1.11.3" \
    "shapely>=2.0.1" \
    "pyproj>=3.4.1" \
    "utm>=0.7.0" \
    "networkx>=3.0" \
    "omegaconf>=2.3.0" \
    "iso3166>=2.1.1" \
    "ordered-set>=4.1.0" \
    "mgrs>=1.4.5" \
    "pygeodesy>=23.3.23" \
    "mercantile>=1.2.1" \
    "urllib3>=2.0.3" \
    "typer>=0.9.0" \
    "typing-extensions>=4.8.0" \
    "antlr4-python3-runtime==4.9.3" \
    "pymetis>=2020.1" \
    "similaritymeasures>=0.4.4" \
    "kdtree>=0.16" \
    "pandas>=2.0.2" \
    "requests>=2.31.0" \
    "pyclothoids>=0.1.5"

echo ""
echo -e "${GREEN}========================================================================"
echo -e "✓ Minimal environment setup completed!"
echo -e "========================================================================${NC}"
echo ""
echo "To use the environment:"
echo ""
echo "1. Activate the virtual environment:"
echo -e "   ${YELLOW}source venv_minimal/bin/activate${NC}"
echo ""
echo "2. Run the map conversion:"
echo -e "   ${YELLOW}python odr_to_ll2_with_postprocessing.py input.xodr output.osm${NC}"
echo ""
echo "3. Deactivate when done:"
echo -e "   ${YELLOW}deactivate${NC}"
echo ""
