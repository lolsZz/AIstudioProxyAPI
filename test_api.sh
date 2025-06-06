#!/bin/bash

# AIstudioProxyAPI Test Script
# Quick test script to verify the API is working correctly

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SERVER_PORT=${1:-2048}
BASE_URL="http://127.0.0.1:$SERVER_PORT"

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  AI Studio Proxy API Tests${NC}"
    echo -e "${BLUE}================================${NC}"
    echo "Testing API at: $BASE_URL"
    echo ""
}

print_test() {
    echo -e "${YELLOW}[TEST]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✅ PASS]${NC} $1"
}

print_error() {
    echo -e "${RED}[❌ FAIL]${NC} $1"
}

# Test function
test_endpoint() {
    local endpoint="$1"
    local description="$2"
    local expected_status="${3:-200}"
    
    print_test "Testing $description..."
    
    local response=$(curl -s -w "%{http_code}" "$BASE_URL$endpoint" -o /tmp/api_response.json)
    local status_code="${response: -3}"
    
    if [ "$status_code" = "$expected_status" ]; then
        print_success "$description (Status: $status_code)"
        return 0
    else
        print_error "$description (Expected: $expected_status, Got: $status_code)"
        return 1
    fi
}

# Test chat completion
test_chat_completion() {
    print_test "Testing chat completion (non-streaming)..."
    
    local response=$(curl -s -w "%{http_code}" -X POST "$BASE_URL/v1/chat/completions" \
        -H 'Content-Type: application/json' \
        -d '{
            "model": "gemini-2.5-pro-preview-06-05",
            "messages": [{"role": "user", "content": "Say hello in one word"}],
            "stream": false,
            "max_output_tokens": 10
        }' \
        -o /tmp/chat_response.json \
        --max-time 30)
    
    local status_code="${response: -3}"
    
    if [ "$status_code" = "200" ]; then
        # Check if response contains expected fields
        if jq -e '.choices[0].message.content' /tmp/chat_response.json > /dev/null 2>&1; then
            local content=$(jq -r '.choices[0].message.content' /tmp/chat_response.json)
            print_success "Chat completion (Response: \"$content\")"
            return 0
        else
            print_error "Chat completion (Invalid response format)"
            return 1
        fi
    else
        print_error "Chat completion (Status: $status_code)"
        return 1
    fi
}

# Main test suite
main() {
    print_header
    
    local failed_tests=0
    local total_tests=0
    
    # Test 1: Health check
    ((total_tests++))
    if ! test_endpoint "/health" "Health check"; then
        ((failed_tests++))
    fi
    
    # Test 2: API info
    ((total_tests++))
    if ! test_endpoint "/api/info" "API info"; then
        ((failed_tests++))
    fi
    
    # Test 3: Models list
    ((total_tests++))
    if ! test_endpoint "/v1/models" "Models list"; then
        ((failed_tests++))
    fi
    
    # Test 4: Chat completion
    ((total_tests++))
    if ! test_chat_completion; then
        ((failed_tests++))
    fi
    
    # Summary
    echo ""
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  Test Results Summary${NC}"
    echo -e "${BLUE}================================${NC}"
    
    local passed_tests=$((total_tests - failed_tests))
    echo "Total tests: $total_tests"
    echo -e "Passed: ${GREEN}$passed_tests${NC}"
    echo -e "Failed: ${RED}$failed_tests${NC}"
    
    if [ $failed_tests -eq 0 ]; then
        echo ""
        print_success "All tests passed! 🎉"
        echo ""
        echo "API is ready for use:"
        echo "  Base URL: $BASE_URL/v1"
        echo "  Health:   $BASE_URL/health"
        echo "  Models:   $BASE_URL/v1/models"
        return 0
    else
        echo ""
        print_error "Some tests failed. Check the server logs."
        return 1
    fi
}

# Cleanup function
cleanup() {
    rm -f /tmp/api_response.json /tmp/chat_response.json
}

# Set trap for cleanup
trap cleanup EXIT

# Run main function
main "$@"
