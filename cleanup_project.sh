#!/bin/bash

# AIstudioProxyAPI Project Cleanup Script
# This script removes unnecessary files while preserving core functionality

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Backup list file
BACKUP_LIST="cleanup_backup_list.txt"

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  AIstudioProxyAPI Cleanup${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_status() {
    echo -e "${GREEN}[CLEANUP]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to log removed files for potential restoration
log_removed_file() {
    local file_path="$1"
    local reason="$2"
    echo "$(date '+%Y-%m-%d %H:%M:%S') | REMOVED | $file_path | $reason" >> "$BACKUP_LIST"
}

# Function to safely remove files/directories
safe_remove() {
    local target="$1"
    local reason="$2"
    
    if [ -e "$target" ]; then
        print_status "Removing: $target ($reason)"
        log_removed_file "$target" "$reason"
        rm -rf "$target"
        return 0
    else
        print_warning "Not found: $target (already clean)"
        return 1
    fi
}

# Function to get directory size
get_size() {
    if [ -e "$1" ]; then
        du -sh "$1" 2>/dev/null | cut -f1
    else
        echo "0B"
    fi
}

# Main cleanup function
main() {
    print_header
    
    # Initialize backup list
    echo "# AIstudioProxyAPI Cleanup Log - $(date)" > "$BACKUP_LIST"
    echo "# Format: TIMESTAMP | ACTION | PATH | REASON" >> "$BACKUP_LIST"
    echo "" >> "$BACKUP_LIST"
    
    print_status "Starting project cleanup..."
    print_status "Backup log will be saved to: $BACKUP_LIST"
    echo ""
    
    # Calculate initial size
    initial_size=$(get_size ".")
    print_status "Initial project size: $initial_size"
    echo ""
    
    # Category 1: Python Cache Files
    print_status "=== Removing Python Cache Files ==="
    safe_remove "__pycache__" "Python bytecode cache"
    safe_remove "api_utils/__pycache__" "Python bytecode cache"
    safe_remove "browser_utils/__pycache__" "Python bytecode cache" 
    safe_remove "config/__pycache__" "Python bytecode cache"
    safe_remove "logging_utils/__pycache__" "Python bytecode cache"
    safe_remove "models/__pycache__" "Python bytecode cache"
    safe_remove "stream/__pycache__" "Python bytecode cache"
    echo ""
    
    # Category 2: Error Debug Files
    print_status "=== Removing Error Debug Files ==="
    if [ -d "errors_py" ]; then
        error_count=$(find errors_py -name "*.html" -o -name "*.png" | wc -l)
        print_status "Found $error_count error debug files"
        safe_remove "errors_py" "Debug error snapshots (not needed for production)"
    fi
    echo ""
    
    # Category 3: Backup Files
    print_status "=== Removing Backup Files ==="
    safe_remove "server重构前备份-参考.py" "Development backup file"
    safe_remove "api_utils/request_processor_backup.py" "Development backup file"
    echo ""
    
    # Category 4: Support Image
    print_status "=== Removing Non-Essential Images ==="
    safe_remove "支持作者.jpg" "Support author image (not essential for functionality)"
    echo ""
    
    # Category 5: Log Files
    print_status "=== Removing Runtime Log Files ==="
    safe_remove "logs/app.log" "Runtime log file (will be regenerated)"
    echo ""
    
    # Category 6: Clean up empty auth directories
    print_status "=== Cleaning Authentication Directories ==="
    if [ -d "auth_profiles/saved" ] && [ -z "$(ls -A auth_profiles/saved)" ]; then
        print_status "auth_profiles/saved is empty - keeping directory structure"
    fi
    
    # Remove any .pyc files that might be scattered
    print_status "=== Removing Scattered .pyc Files ==="
    pyc_count=$(find . -name "*.pyc" -type f | wc -l)
    if [ "$pyc_count" -gt 0 ]; then
        print_status "Found $pyc_count .pyc files"
        find . -name "*.pyc" -type f -exec rm {} \;
        log_removed_file "*.pyc files" "Python compiled bytecode"
    else
        print_status "No scattered .pyc files found"
    fi
    echo ""
    
    # Calculate final size and savings
    final_size=$(get_size ".")
    print_status "Final project size: $final_size"
    
    echo ""
    print_status "=== Cleanup Summary ==="
    removed_count=$(grep -c "REMOVED" "$BACKUP_LIST" 2>/dev/null || echo "0")
    print_status "Total items removed: $removed_count"
    print_status "Backup log saved to: $BACKUP_LIST"
    
    echo ""
    print_status "=== Verification ==="
    print_status "Checking essential files are still present..."
    
    essential_files=(
        "server.py"
        "launch_camoufox.py" 
        "requirements.txt"
        "start.sh"
        "start.py"
        "README.md"
        "QUICK_START.md"
        "STARTUP_GUIDE.md"
    )
    
    missing_files=0
    for file in "${essential_files[@]}"; do
        if [ -f "$file" ]; then
            echo "  ✅ $file"
        else
            echo "  ❌ $file (MISSING!)"
            ((missing_files++))
        fi
    done
    
    essential_dirs=(
        "api_utils"
        "browser_utils"
        "config"
        "stream"
        "auth_profiles"
        "certs"
    )
    
    for dir in "${essential_dirs[@]}"; do
        if [ -d "$dir" ]; then
            echo "  ✅ $dir/"
        else
            echo "  ❌ $dir/ (MISSING!)"
            ((missing_files++))
        fi
    done
    
    echo ""
    if [ "$missing_files" -eq 0 ]; then
        print_status "✅ All essential files and directories are present!"
        print_status "🎉 Cleanup completed successfully!"
        echo ""
        echo "The project is now clean and ready for production use."
        echo "All core functionality has been preserved."
    else
        print_error "❌ $missing_files essential files/directories are missing!"
        print_error "Please check the backup log and restore if necessary."
        exit 1
    fi
}

# Function to show what would be removed (dry run)
dry_run() {
    print_header
    print_status "DRY RUN - Showing what would be removed:"
    echo ""
    
    targets=(
        "__pycache__:Python bytecode cache"
        "api_utils/__pycache__:Python bytecode cache"
        "browser_utils/__pycache__:Python bytecode cache"
        "config/__pycache__:Python bytecode cache"
        "logging_utils/__pycache__:Python bytecode cache"
        "models/__pycache__:Python bytecode cache"
        "stream/__pycache__:Python bytecode cache"
        "errors_py:Debug error snapshots"
        "server重构前备份-参考.py:Development backup file"
        "api_utils/request_processor_backup.py:Development backup file"
        "支持作者.jpg:Support author image"
        "logs/app.log:Runtime log file"
    )
    
    total_size=0
    found_count=0
    
    for target_info in "${targets[@]}"; do
        target="${target_info%%:*}"
        reason="${target_info##*:}"
        
        if [ -e "$target" ]; then
            size=$(get_size "$target")
            echo "  🗑️  $target ($size) - $reason"
            ((found_count++))
        fi
    done
    
    # Check for .pyc files
    pyc_count=$(find . -name "*.pyc" -type f | wc -l)
    if [ "$pyc_count" -gt 0 ]; then
        echo "  🗑️  $pyc_count scattered .pyc files - Python compiled bytecode"
        ((found_count++))
    fi
    
    echo ""
    print_status "Total items that would be removed: $found_count"
    echo ""
    echo "Run without --dry-run to perform the actual cleanup."
}

# Parse command line arguments
if [ "$1" = "--dry-run" ]; then
    dry_run
elif [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Usage: $0 [--dry-run] [--help]"
    echo ""
    echo "Options:"
    echo "  --dry-run    Show what would be removed without actually removing"
    echo "  --help       Show this help message"
    echo ""
    echo "This script removes unnecessary files from the AIstudioProxyAPI project"
    echo "while preserving all core functionality and documentation."
else
    main
fi
