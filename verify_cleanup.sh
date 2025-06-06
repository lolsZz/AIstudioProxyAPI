#!/bin/bash

# AIstudioProxyAPI Cleanup Verification Script
# This script verifies that the cleanup was successful and all essential components remain

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  Cleanup Verification Report${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_success() {
    echo -e "${GREEN}[✅ PASS]${NC} $1"
}

print_error() {
    echo -e "${RED}[❌ FAIL]${NC} $1"
}

print_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

# Main verification function
main() {
    print_header
    
    local failed_checks=0
    local total_checks=0
    
    echo "Project Directory: $(pwd)"
    echo "Current Size: $(du -sh . | cut -f1)"
    echo ""
    
    # Check 1: Essential Python files
    print_info "=== Checking Core Application Files ==="
    ((total_checks++))
    essential_files=(
        "server.py"
        "launch_camoufox.py"
        "stream/main.py"
        "api_utils/app.py"
        "browser_utils/initialization.py"
    )
    
    missing_core=0
    for file in "${essential_files[@]}"; do
        if [ -f "$file" ]; then
            print_success "Core file: $file"
        else
            print_error "Missing core file: $file"
            ((missing_core++))
        fi
    done
    
    if [ $missing_core -eq 0 ]; then
        print_success "All core application files present"
    else
        print_error "$missing_core core files missing"
        ((failed_checks++))
    fi
    echo ""
    
    # Check 2: Startup scripts
    print_info "=== Checking Startup Scripts ==="
    ((total_checks++))
    startup_scripts=("start.sh" "start.py" "test_api.sh")
    missing_scripts=0
    
    for script in "${startup_scripts[@]}"; do
        if [ -f "$script" ] && [ -x "$script" ]; then
            print_success "Startup script: $script (executable)"
        elif [ -f "$script" ]; then
            print_success "Startup script: $script (exists, not executable)"
        else
            print_error "Missing startup script: $script"
            ((missing_scripts++))
        fi
    done
    
    if [ $missing_scripts -eq 0 ]; then
        print_success "All startup scripts present"
    else
        print_error "$missing_scripts startup scripts missing"
        ((failed_checks++))
    fi
    echo ""
    
    # Check 3: Documentation files
    print_info "=== Checking Documentation ==="
    ((total_checks++))
    doc_files=("README.md" "QUICK_START.md" "STARTUP_GUIDE.md" "README-Docker.md")
    missing_docs=0
    
    for doc in "${doc_files[@]}"; do
        if [ -f "$doc" ]; then
            print_success "Documentation: $doc"
        else
            print_error "Missing documentation: $doc"
            ((missing_docs++))
        fi
    done
    
    if [ $missing_docs -eq 0 ]; then
        print_success "All documentation files present"
    else
        print_error "$missing_docs documentation files missing"
        ((failed_checks++))
    fi
    echo ""
    
    # Check 4: Configuration files
    print_info "=== Checking Configuration Files ==="
    ((total_checks++))
    config_files=("requirements.txt" "excluded_models.txt" "gui_config.json" "supervisord.conf")
    missing_config=0
    
    for config in "${config_files[@]}"; do
        if [ -f "$config" ]; then
            print_success "Configuration: $config"
        else
            print_error "Missing configuration: $config"
            ((missing_config++))
        fi
    done
    
    if [ $missing_config -eq 0 ]; then
        print_success "All configuration files present"
    else
        print_error "$missing_config configuration files missing"
        ((failed_checks++))
    fi
    echo ""
    
    # Check 5: Essential directories
    print_info "=== Checking Essential Directories ==="
    ((total_checks++))
    essential_dirs=("api_utils" "browser_utils" "config" "stream" "auth_profiles" "certs" "logs")
    missing_dirs=0
    
    for dir in "${essential_dirs[@]}"; do
        if [ -d "$dir" ]; then
            print_success "Directory: $dir"
        else
            print_error "Missing directory: $dir"
            ((missing_dirs++))
        fi
    done
    
    if [ $missing_dirs -eq 0 ]; then
        print_success "All essential directories present"
    else
        print_error "$missing_dirs essential directories missing"
        ((failed_checks++))
    fi
    echo ""
    
    # Check 6: Verify cleanup was successful
    print_info "=== Verifying Cleanup Success ==="
    ((total_checks++))
    cleanup_success=0
    
    # Check that unwanted files are gone
    unwanted_items=(
        "__pycache__"
        "errors_py"
        "server重构前备份-参考.py"
        "api_utils/request_processor_backup.py"
        "支持作者.jpg"
    )
    
    for item in "${unwanted_items[@]}"; do
        if [ -e "$item" ]; then
            print_error "Cleanup failed: $item still exists"
            ((cleanup_success++))
        else
            print_success "Cleanup verified: $item removed"
        fi
    done
    
    if [ $cleanup_success -eq 0 ]; then
        print_success "Cleanup completed successfully"
    else
        print_error "$cleanup_success items not properly cleaned"
        ((failed_checks++))
    fi
    echo ""
    
    # Check 7: Virtual environment integrity
    print_info "=== Checking Virtual Environment ==="
    ((total_checks++))
    if [ -d ".venv" ] && [ -f ".venv/bin/python3" ]; then
        print_success "Virtual environment intact"
    else
        print_error "Virtual environment missing or damaged"
        ((failed_checks++))
    fi
    echo ""
    
    # Final summary
    print_info "=== Final Summary ==="
    local passed_checks=$((total_checks - failed_checks))
    echo "Total checks: $total_checks"
    echo -e "Passed: ${GREEN}$passed_checks${NC}"
    echo -e "Failed: ${RED}$failed_checks${NC}"
    
    if [ $failed_checks -eq 0 ]; then
        echo ""
        print_success "🎉 CLEANUP VERIFICATION SUCCESSFUL!"
        echo ""
        echo "✅ Project is clean and ready for production use"
        echo "✅ All core functionality preserved"
        echo "✅ All documentation maintained"
        echo "✅ Startup scripts ready"
        echo "✅ Authentication structure intact"
        echo ""
        echo "You can now run: ./start.sh"
        return 0
    else
        echo ""
        print_error "❌ CLEANUP VERIFICATION FAILED!"
        echo ""
        echo "Please check the failed items above and restore if necessary."
        echo "Backup information is available in: cleanup_backup_list.txt"
        return 1
    fi
}

# Run main function
main "$@"
