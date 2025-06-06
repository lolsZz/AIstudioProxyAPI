#!/bin/bash

# AIstudioProxyAPI Startup Script
# This script provides an easy way to start the AI Studio Proxy API
# with proper authentication handling and different launch modes.

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default configuration
DEFAULT_SERVER_PORT=2048
DEFAULT_STREAM_PORT=3120
DEFAULT_HELPER=""
DEFAULT_PROXY=""

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
AUTH_ACTIVE_DIR="$SCRIPT_DIR/auth_profiles/active"
AUTH_SAVED_DIR="$SCRIPT_DIR/auth_profiles/saved"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  AI Studio Proxy API Launcher${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Function to check if virtual environment exists and activate it
setup_environment() {
    print_status "Setting up environment..."

    if [ ! -d "$VENV_DIR" ]; then
        print_error "Virtual environment not found at $VENV_DIR"
        print_error "Please run: uv venv .venv && source .venv/bin/activate && uv install -r requirements.txt"
        exit 1
    fi

    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    print_status "Virtual environment activated"
}

# Function to cleanup ports if needed
cleanup_ports() {
    local server_port=${1:-$DEFAULT_SERVER_PORT}
    local stream_port=${2:-$DEFAULT_STREAM_PORT}
    local camoufox_port=9222

    print_status "Checking for port conflicts..."

    # Function to check if a port is in use
    check_port() {
        local port=$1
        local port_name=$2
        if lsof -ti :$port >/dev/null 2>&1; then
            local pids=$(lsof -ti :$port 2>/dev/null)
            print_warning "$port_name port $port is in use by PID(s): $pids"

            # In headless mode, automatically kill processes
            if [[ "$MODE" == "headless" || "$MODE" == "auto" ]]; then
                print_status "Automatically cleaning up $port_name port $port..."
                for pid in $pids; do
                    if kill -TERM $pid 2>/dev/null; then
                        print_status "Terminated process $pid using $port_name port $port"
                        sleep 1
                    fi
                done

                # Check if port is now free
                if ! lsof -ti :$port >/dev/null 2>&1; then
                    print_status "✅ $port_name port $port is now available"
                else
                    print_warning "⚠️ $port_name port $port may still be in use"
                fi
            else
                print_warning "⚠️ $port_name port $port conflict detected - may cause startup issues"
            fi
        else
            print_status "✅ $port_name port $port is available"
        fi
    }

    # Check all required ports
    check_port $server_port "FastAPI server"
    check_port $stream_port "Stream proxy"
    check_port $camoufox_port "Camoufox debug"
}

# Function to check authentication status
check_authentication() {
    print_status "Checking authentication status..."

    # Create auth directories if they don't exist
    mkdir -p "$AUTH_ACTIVE_DIR"
    mkdir -p "$AUTH_SAVED_DIR"

    # Check for active authentication files
    local active_files=$(find "$AUTH_ACTIVE_DIR" -name "*.json" 2>/dev/null | wc -l)
    local saved_files=$(find "$AUTH_SAVED_DIR" -name "*.json" 2>/dev/null | wc -l)

    if [ "$active_files" -gt 0 ]; then
        print_status "Active authentication found - can run in headless mode"
        return 0
    elif [ "$saved_files" -gt 0 ]; then
        print_warning "Saved authentication found but not active"
        echo "Moving saved authentication to active directory..."
        cp "$AUTH_SAVED_DIR"/*.json "$AUTH_ACTIVE_DIR"/ 2>/dev/null || true
        return 0
    else
        print_warning "No authentication found - will need to authenticate first"
        return 1
    fi
}

# Function to run initial authentication
run_authentication() {
    print_status "Starting authentication process..."
    print_status "A browser window will open for Google login"
    print_status "Complete the login and press Enter when prompted"

    python3 launch_camoufox.py --debug \
        --server-port "$DEFAULT_SERVER_PORT" \
        --stream-port "$DEFAULT_STREAM_PORT" \
        --helper "$DEFAULT_HELPER" \
        --internal-camoufox-proxy "$DEFAULT_PROXY"
}

# Function to run in headless mode
run_headless() {
    local server_port=${1:-$DEFAULT_SERVER_PORT}
    local stream_port=${2:-$DEFAULT_STREAM_PORT}

    print_status "Starting AI Studio Proxy API in headless mode..."
    print_status "Server will be available at: http://127.0.0.1:$server_port"
    print_status "Stream proxy running on port: $stream_port"
    print_status "Press Ctrl+C to stop the server"

    python3 launch_camoufox.py --headless \
        --server-port "$server_port" \
        --stream-port "$stream_port" \
        --helper "$DEFAULT_HELPER" \
        --internal-camoufox-proxy "$DEFAULT_PROXY"
}

# Function to run in debug mode
run_debug() {
    local server_port=${1:-$DEFAULT_SERVER_PORT}
    local stream_port=${2:-$DEFAULT_STREAM_PORT}

    print_status "Starting AI Studio Proxy API in debug mode..."
    print_status "Browser window will open for interaction"
    print_status "Server will be available at: http://127.0.0.1:$server_port"

    python3 launch_camoufox.py --debug \
        --server-port "$server_port" \
        --stream-port "$stream_port" \
        --helper "$DEFAULT_HELPER" \
        --internal-camoufox-proxy "$DEFAULT_PROXY"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [MODE] [OPTIONS]"
    echo ""
    echo "MODES:"
    echo "  auto      - Automatically choose best mode (default)"
    echo "  headless  - Run in headless mode (requires authentication)"
    echo "  debug     - Run in debug mode with browser window"
    echo "  auth      - Run authentication setup only"
    echo "  test      - Test API endpoints"
    echo ""
    echo "OPTIONS:"
    echo "  --server-port PORT   - FastAPI server port (default: $DEFAULT_SERVER_PORT)"
    echo "  --stream-port PORT   - Stream proxy port (default: $DEFAULT_STREAM_PORT)"
    echo "  --help               - Show this help message"
    echo ""
    echo "EXAMPLES:"
    echo "  $0                   - Auto mode (headless if auth available, else debug)"
    echo "  $0 headless          - Force headless mode"
    echo "  $0 debug             - Force debug mode"
    echo "  $0 auth              - Setup authentication only"
    echo "  $0 headless --server-port 8080"
}

# Function to test API endpoints
test_api() {
    local server_port=${1:-$DEFAULT_SERVER_PORT}
    local base_url="http://127.0.0.1:$server_port"

    print_status "Testing API endpoints..."

    # Test health endpoint
    echo "Testing health endpoint..."
    if curl -s "$base_url/health" > /dev/null; then
        print_status "✅ Health endpoint responding"
    else
        print_error "❌ Health endpoint not responding"
        return 1
    fi

    # Test models endpoint
    echo "Testing models endpoint..."
    if curl -s "$base_url/v1/models" > /dev/null; then
        print_status "✅ Models endpoint responding"
    else
        print_error "❌ Models endpoint not responding"
        return 1
    fi

    # Test API info
    echo "Testing API info endpoint..."
    if curl -s "$base_url/api/info" > /dev/null; then
        print_status "✅ API info endpoint responding"
    else
        print_error "❌ API info endpoint not responding"
        return 1
    fi

    print_status "All API endpoints are working!"
    echo ""
    echo "API Base URL: $base_url/v1"
    echo "Health Check: $base_url/health"
    echo "Models List:  $base_url/v1/models"
    echo "API Info:     $base_url/api/info"
}

# Main script logic
main() {
    print_header

    # Change to script directory
    cd "$SCRIPT_DIR"

    # Parse command line arguments
    MODE="auto"
    SERVER_PORT="$DEFAULT_SERVER_PORT"
    STREAM_PORT="$DEFAULT_STREAM_PORT"

    while [[ $# -gt 0 ]]; do
        case $1 in
            auto|headless|debug|auth|test)
                MODE="$1"
                shift
                ;;
            --server-port)
                SERVER_PORT="$2"
                shift 2
                ;;
            --stream-port)
                STREAM_PORT="$2"
                shift 2
                ;;
            --help|-h)
                show_usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done

    # Setup environment
    setup_environment

    # Cleanup ports if needed (except for test mode)
    if [[ "$MODE" != "test" ]]; then
        cleanup_ports "$SERVER_PORT" "$STREAM_PORT"
    fi

    # Handle different modes
    case "$MODE" in
        "auto")
            if check_authentication; then
                print_status "Auto mode: Running in headless mode"
                run_headless "$SERVER_PORT" "$STREAM_PORT"
            else
                print_status "Auto mode: No authentication found, running debug mode for setup"
                run_authentication
            fi
            ;;
        "headless")
            if check_authentication; then
                run_headless "$SERVER_PORT" "$STREAM_PORT"
            else
                print_error "No authentication found. Run '$0 auth' first or use debug mode."
                exit 1
            fi
            ;;
        "debug")
            run_debug "$SERVER_PORT" "$STREAM_PORT"
            ;;
        "auth")
            run_authentication
            ;;
        "test")
            test_api "$SERVER_PORT"
            ;;
        *)
            print_error "Invalid mode: $MODE"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
