#!/bin/bash

# prepare-public-release.sh
# This script prepares the AI Rails repository for public release
# by ensuring all personal/sensitive information is removed

set -e

echo "=== AI Rails Public Release Preparation ==="
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check for hardcoded IPs
check_hardcoded_ips() {
    echo "Checking for hardcoded IP addresses..."
    
    # Pattern to match common private IP formats
    IP_PATTERN='(10\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}|192\.168\.[0-9]{1,3}\.[0-9]{1,3}|172\.(1[6-9]|2[0-9]|3[0-1])\.[0-9]{1,3}\.[0-9]{1,3})'
    
    # Find files with potential IPs (excluding .git and node_modules)
    FILES=$(find . -type f \( -name "*.py" -o -name "*.sh" -o -name "*.md" -o -name "*.json" -o -name "*.yml" -o -name "*.yaml" \) \
            -not -path "./.git/*" -not -path "./node_modules/*" -not -path "./venv/*" | head -50)
    
    FOUND_IPS=false
    for file in $FILES; do
        if grep -E "$IP_PATTERN" "$file" > /dev/null 2>&1; then
            echo -e "${RED}Found IP in: $file${NC}"
            grep -n -E "$IP_PATTERN" "$file" | head -3
            FOUND_IPS=true
        fi
    done
    
    if [ "$FOUND_IPS" = true ]; then
        echo -e "${YELLOW}Warning: Found hardcoded IPs. These should be replaced with localhost or environment variables.${NC}"
    else
        echo -e "${GREEN}No hardcoded IPs found!${NC}"
    fi
}

# Function to check for sensitive files
check_sensitive_files() {
    echo
    echo "Checking for sensitive files..."
    
    SENSITIVE_FILES=(
        ".env"
        ".env.local"
        ".env.personal"
        ".env.colin"
        "personal-config"
        "*_test.py"
        "test_*.py"
    )
    
    FOUND_SENSITIVE=false
    for pattern in "${SENSITIVE_FILES[@]}"; do
        if find . -name "$pattern" -not -path "./.git/*" | grep -q .; then
            echo -e "${RED}Found sensitive file(s): $pattern${NC}"
            find . -name "$pattern" -not -path "./.git/*" | head -5
            FOUND_SENSITIVE=true
        fi
    done
    
    if [ "$FOUND_SENSITIVE" = true ]; then
        echo -e "${YELLOW}Warning: Found sensitive files. Ensure these are in .gitignore.${NC}"
    else
        echo -e "${GREEN}No sensitive files found in repository!${NC}"
    fi
}

# Function to verify .gitignore
verify_gitignore() {
    echo
    echo "Verifying .gitignore completeness..."
    
    REQUIRED_IGNORES=(
        ".env"
        ".env.personal"
        "*.colin.*"
        "test_*.py"
        "personal-config/"
    )
    
    MISSING_IGNORES=()
    for pattern in "${REQUIRED_IGNORES[@]}"; do
        if ! grep -q "^$pattern" .gitignore 2>/dev/null; then
            MISSING_IGNORES+=("$pattern")
        fi
    done
    
    if [ ${#MISSING_IGNORES[@]} -gt 0 ]; then
        echo -e "${YELLOW}Missing from .gitignore:${NC}"
        printf '%s\n' "${MISSING_IGNORES[@]}"
    else
        echo -e "${GREEN}.gitignore looks complete!${NC}"
    fi
}

# Function to create release checklist
create_release_checklist() {
    echo
    echo "Creating release checklist..."
    
    cat > RELEASE_CHECKLIST.md << 'EOF'
# AI Rails Release Checklist

## Pre-Release Checks

- [ ] All hardcoded IPs replaced with localhost or env variables
- [ ] Personal configuration files removed
- [ ] Test files removed or gitignored
- [ ] .gitignore is complete
- [ ] Documentation updated with generic examples
- [ ] Docker compose files use generic configurations
- [ ] README.md has correct repository URLs
- [ ] All MCP URLs point to localhost in .example.env

## Documentation Checks

- [ ] CUSTOM_MCP_SETUP.md has placeholder repository URLs
- [ ] MCP_DEVELOPMENT_GUIDE.md examples are generic
- [ ] No personal network topology mentioned
- [ ] Installation instructions work with Docker

## Testing

- [ ] Fresh clone and setup works
- [ ] Docker mock services start correctly
- [ ] Basic workflow runs with mock MCPs
- [ ] Documentation is clear for new users

## Final Steps

- [ ] Create GitHub release
- [ ] Tag version appropriately
- [ ] Update any external documentation
EOF
    
    echo -e "${GREEN}Created RELEASE_CHECKLIST.md${NC}"
}

# Function to create backup
create_backup() {
    echo
    echo "Creating backup of current configuration..."
    
    BACKUP_DIR="ai-rails-backup-$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Backup current env if it exists
    if [ -f ".env" ]; then
        cp .env "$BACKUP_DIR/.env.backup"
        echo "Backed up .env to $BACKUP_DIR/"
    fi
    
    # Create a summary of current config
    cat > "$BACKUP_DIR/config-summary.txt" << EOF
AI Rails Configuration Backup
Date: $(date)
Git Branch: $(git branch --show-current)
Git Commit: $(git rev-parse HEAD)

Environment Variables:
$(env | grep -E '^(OLLAMA_|MCP_|AI_RAILS_)' | sed 's/=.*$/=<value>/')
EOF
    
    echo -e "${GREEN}Backup created in: $BACKUP_DIR/${NC}"
}

# Main execution
echo "This script will help prepare AI Rails for public release."
echo "It will check for sensitive information and create necessary files."
echo

read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# Run all checks
check_hardcoded_ips
check_sensitive_files
verify_gitignore
create_release_checklist
create_backup

echo
echo "=== Summary ==="
echo
echo "1. Review and fix any issues found above"
echo "2. Check RELEASE_CHECKLIST.md and complete all items"
echo "3. Your configuration is backed up (see backup directory)"
echo "4. When ready, create a new branch for the public release"
echo
echo -e "${YELLOW}Remember: Never commit personal configuration files!${NC}"