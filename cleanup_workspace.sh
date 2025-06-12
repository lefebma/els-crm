#!/bin/bash

# ELS CRM Workspace Cleanup Script
# This script removes redundant development and testing files

echo "🧹 Starting ELS CRM workspace cleanup..."

# Create a backup directory for deleted files (just in case)
BACKUP_DIR="deleted_files_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "📦 Creating backup in: $BACKUP_DIR"

# Function to safely remove files
safe_remove() {
    local file="$1"
    if [ -e "$file" ]; then
        echo "🗑️  Moving $file to backup..."
        mv "$file" "$BACKUP_DIR/"
    else
        echo "⚠️  File not found: $file"
    fi
}

# Remove backup/alternative app files
echo "🔧 Cleaning up app file variants..."
safe_remove "app_backup.py"
safe_remove "app_debug.py"
safe_remove "app_minimal.py"
safe_remove "app_no_csrf.py"
safe_remove "app_simple.py"
safe_remove "app_simple_working.py"
safe_remove "app_test.py"
safe_remove "app_working.py"
safe_remove "debug_app.py"

# Remove test deployment directories
echo "📁 Cleaning up deployment directories..."
safe_remove "clean_deploy"
safe_remove "full_deploy"
safe_remove "minimal_deploy"

# Remove alternative requirements files
echo "📋 Cleaning up requirements variants..."
safe_remove "requirements_debug.txt"
safe_remove "requirements_full.txt"
safe_remove "requirements_local.txt"
safe_remove "requirements_minimal.txt"
safe_remove "requirements_simple.txt"

# Remove temporary test scripts
echo "🧪 Cleaning up temporary test files..."
safe_remove "test_account_edit.py"
safe_remove "simple_test.py"

# Remove backup documentation
echo "📚 Cleaning up documentation backups..."
safe_remove "README_backup.md"
safe_remove "README_new.md"
safe_remove "README_old.md"

# Remove miscellaneous development files
echo "🔧 Cleaning up miscellaneous files..."
safe_remove "compare_deployments.py"
safe_remove "cookies.txt"
safe_remove "latest_logs.zip"
safe_remove "newest-logs.zip"
safe_remove "startup_simple.sh"

# Optional: Remove test files (uncomment if you don't need testing infrastructure)
echo "🧪 Test files (keeping them for now - uncomment lines in script to remove):"
echo "   - test_app.py"
echo "   - test_auth.py"
echo "   - test_db_connection.py"
echo "   - test_db_connection_fixed.py"
echo "   - test_db_simple.py"
echo "   - test_full_deployment.py"
echo "   - test_full_functionality.py"
echo "   - test_local.py"
echo "   - test_navigation.py"
echo "   - test_password_reset.py"

# Uncomment these lines if you want to remove test files too:
# safe_remove "test_app.py"
# safe_remove "test_auth.py"
# safe_remove "test_db_connection.py"
# safe_remove "test_db_connection_fixed.py"
# safe_remove "test_db_simple.py"
# safe_remove "test_full_deployment.py"
# safe_remove "test_full_functionality.py"
# safe_remove "test_local.py"
# safe_remove "test_navigation.py"
# safe_remove "test_password_reset.py"

echo ""
echo "✅ Cleanup completed!"
echo "📦 Backup created at: $BACKUP_DIR"
echo ""
echo "🗂️  REMAINING CORE FILES:"
echo "   - app.py (main application)"
echo "   - requirements.txt (production dependencies)"
echo "   - README.md (main documentation)"
echo "   - azure.yaml (deployment configuration)"
echo "   - routes/, templates/, infra/ (core application)"
echo ""
echo "💡 You can safely delete the backup directory once you confirm everything works."
echo ""
echo "🚀 Your workspace is now clean and production-ready!"
