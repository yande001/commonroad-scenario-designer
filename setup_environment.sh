#!/bin/bash
# CommonRoad Scenario Designer - Environment Setup Script
# Automated setup for OpenDRIVE to Lanelet2 conversion with 3D elevation support

set -e  # Exit on any error

echo "========================================================================"
echo "CommonRoad Scenario Designer - Environment Setup"
echo "========================================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$MAJOR" -eq 3 ] && [ "$MINOR" -ge 10 ] && [ "$MINOR" -le 13 ]; then
    echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION found (supported: 3.10-3.13)"
else
    echo -e "${RED}✗${NC} Python $PYTHON_VERSION not supported. Please install Python 3.10-3.13"
    exit 1
fi

# Check if poetry is installed
echo ""
echo "Checking Poetry..."
if ! command -v poetry &> /dev/null; then
    echo -e "${YELLOW}⚠${NC} Poetry not found. Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -

    # Add Poetry to PATH for current session
    export PATH="$HOME/.local/bin:$PATH"

    echo -e "${GREEN}✓${NC} Poetry installed successfully"
    echo ""
    echo -e "${YELLOW}Note:${NC} Add Poetry to your PATH permanently by adding this to your ~/.bashrc or ~/.zshrc:"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
else
    POETRY_VERSION=$(poetry --version 2>&1)
    echo -e "${GREEN}✓${NC} $POETRY_VERSION found"
fi

# Check for system dependencies
echo ""
echo "Checking system dependencies..."
MISSING_DEPS=()

# Check for essential libraries
if ! ldconfig -p | grep -q libxcb; then
    MISSING_DEPS+=("libxcb-xinerama0")
fi

if ! ldconfig -p | grep -q libxkbcommon; then
    MISSING_DEPS+=("libxkbcommon-x11-0")
fi

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠${NC} Missing system dependencies: ${MISSING_DEPS[*]}"
    echo ""
    echo "Please install them using:"
    echo "  sudo apt install ${MISSING_DEPS[*]}"
    echo ""
    read -p "Do you want to continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${GREEN}✓${NC} System dependencies satisfied"
fi

# Create virtual environment and install dependencies
echo ""
echo "Setting up Python environment..."
echo "This may take several minutes..."
echo ""

# Create poetry environment
poetry env use python3

# Install dependencies
echo "Installing Python dependencies..."
poetry install

echo ""
echo -e "${GREEN}========================================================================"
echo -e "✓ Environment setup completed successfully!"
echo -e "========================================================================${NC}"
echo ""
echo "Next steps:"
echo ""
echo "1. Activate the virtual environment:"
echo -e "   ${YELLOW}poetry shell${NC}"
echo ""
echo "2. Run a map conversion:"
echo -e "   ${YELLOW}poetry run python odr_to_ll2_with_postprocessing.py input/Town04_no_georef.xodr output.osm${NC}"
echo ""
