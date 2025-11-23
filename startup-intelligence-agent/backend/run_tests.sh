#!/bin/bash
# Test runner script for Startup Intelligence Agent

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Startup Intelligence Agent Test Suite ===${NC}\n"

# Check if we're in the right directory
if [ ! -f "pytest.ini" ]; then
    echo -e "${YELLOW}Warning: pytest.ini not found. Running from backend directory?${NC}"
    echo "Expected location: startup-intelligence-agent/backend/"
    exit 1
fi

# Parse command line arguments
TEST_TYPE="${1:-all}"
COVERAGE="${2:-false}"

case "$TEST_TYPE" in
    unit)
        echo -e "${GREEN}Running unit tests...${NC}\n"
        if [ "$COVERAGE" = "true" ]; then
            pytest tests/unit/ -v -m unit --cov=src --cov-report=term-missing
        else
            pytest tests/unit/ -v -m unit
        fi
        ;;
    integration)
        echo -e "${GREEN}Running integration tests...${NC}\n"
        if [ "$COVERAGE" = "true" ]; then
            pytest tests/integration/ -v -m integration --cov=src --cov-report=term-missing
        else
            pytest tests/integration/ -v -m integration
        fi
        ;;
    e2e)
        echo -e "${GREEN}Running end-to-end tests...${NC}\n"
        echo -e "${YELLOW}Note: E2E tests require running services${NC}\n"
        pytest tests/e2e/ -v -m e2e
        ;;
    all)
        echo -e "${GREEN}Running all tests (unit + integration)...${NC}\n"
        if [ "$COVERAGE" = "true" ]; then
            pytest tests/unit/ tests/integration/ -v --cov=src --cov-report=term-missing --cov-report=html
            echo -e "\n${GREEN}Coverage report generated in htmlcov/index.html${NC}"
        else
            pytest tests/unit/ tests/integration/ -v
        fi
        ;;
    *)
        echo "Usage: $0 [unit|integration|e2e|all] [coverage]"
        echo ""
        echo "Examples:"
        echo "  $0 unit              # Run unit tests"
        echo "  $0 integration       # Run integration tests"
        echo "  $0 e2e               # Run E2E tests"
        echo "  $0 all               # Run all tests (unit + integration)"
        echo "  $0 all coverage      # Run all tests with coverage report"
        exit 1
        ;;
esac

echo -e "\n${GREEN}✅ Tests completed!${NC}"

