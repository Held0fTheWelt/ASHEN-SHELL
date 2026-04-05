#!/bin/bash
# Setup test environment - installs all required dependencies
#
# This script MUST be run before running any tests.
# It installs both production and test dependencies.
#
# Usage:
#   ./setup-test-environment.sh

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}World of Shadows: Test Environment Setup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Get repository root
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_ROOT"

# Check if python is available
if ! command -v python &> /dev/null; then
    echo -e "${RED}Error: Python not found${NC}" >&2
    echo "Please install Python 3.10+ and try again." >&2
    exit 1
fi

echo "Repository: $REPO_ROOT"
echo "Python: $(python --version)"
echo ""

# Install backend dependencies
echo -e "${YELLOW}Installing backend dependencies...${NC}"
cd backend

if [[ ! -f "requirements.txt" ]]; then
    echo -e "${RED}Error: backend/requirements.txt not found${NC}" >&2
    exit 1
fi

if [[ ! -f "requirements-test.txt" ]]; then
    echo -e "${RED}Error: backend/requirements-test.txt not found${NC}" >&2
    exit 1
fi

echo "Installing production dependencies..."
pip install -r requirements.txt -q

echo "Installing test dependencies..."
pip install -r requirements-test.txt -q

cd ..

# Verify critical dependencies
echo ""
echo -e "${YELLOW}Verifying critical dependencies...${NC}"

MISSING=()

packages=("flask" "sqlalchemy" "flask_sqlalchemy" "flask_migrate" "flask_limiter" "pytest" "pytest_asyncio")

for pkg in "${packages[@]}"; do
    if python -c "import ${pkg}" 2>/dev/null; then
        echo "  ✓ $pkg"
    else
        echo "  ✗ $pkg (MISSING)"
        MISSING+=("$pkg")
    fi
done

echo ""

if [[ ${#MISSING[@]} -gt 0 ]]; then
    echo -e "${RED}Error: Missing required packages:${NC}"
    for pkg in "${MISSING[@]}"; do
        echo "  - $pkg"
    done
    echo ""
    echo "Try running pip install again:"
    echo "  pip install -r backend/requirements.txt -r backend/requirements-test.txt"
    exit 1
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}All dependencies installed successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "You can now run tests:"
echo "  python -m pytest tests/smoke/ -v"
echo "  python -m pytest backend/tests/ -v"
echo ""
