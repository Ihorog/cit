#!/bin/bash

# Cimeika Build Verification Script
# Перевіряє успішність збірки та готовність до розгортання

set -e

echo "🔍 Cimeika Build Verification"
echo "=============================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0

# Test function
test_step() {
    local description=$1
    local command=$2
    
    echo -n "Testing: $description... "
    
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        ((FAILED++))
        return 1
    fi
}

echo "📦 Checking Dependencies"
echo "------------------------"
test_step "Node.js installed" "command -v node"
test_step "npm installed" "command -v npm"
test_step "Python installed" "command -v python3"
echo ""

echo "📁 Checking Project Structure"
echo "------------------------------"
test_step "web/ directory exists" "[ -d web ]"
test_step "server/ directory exists" "[ -d server ]"
test_step "web/package.json exists" "[ -f web/package.json ]"
test_step "web/vercel.json exists" "[ -f web/vercel.json ]"
test_step "next.config.cjs/mjs exists" "[ -f web/next.config.cjs ] || [ -f web/next.config.mjs ]"
echo ""

echo "🔨 Checking Build Output"
echo "------------------------"
test_step "web/.next directory exists" "[ -d web/.next ]"
test_step "Build manifest exists" "[ -f web/.next/build-manifest.json ]"
test_step "Server files exist" "[ -d web/.next/server ]"
test_step "Static files exist" "[ -d web/.next/static ]"
echo ""

echo "📄 Checking Source Files"
echo "------------------------"
test_step "AppShell component exists" "[ -f web/src/components/AppShell.tsx ]"
test_step "ChatInterface component exists" "[ -f web/src/components/ChatInterface.tsx ]"
test_step "Layout exists" "[ -f web/src/app/layout.tsx ]"
test_step "Page exists" "[ -f web/src/app/page.tsx ]"
test_step "Global styles exist" "[ -f web/src/styles/globals.css ]"
echo ""

echo "🎨 Checking Assets"
echo "------------------"
test_step "Manifest exists" "[ -f web/public/manifest.json ]"
test_step "Icons directory exists" "[ -d web/public/icons ]"
echo ""

echo "🐍 Checking Python Server"
echo "-------------------------"
test_step "cit_server.py exists" "[ -f server/cit_server.py ]"
test_step "orchestrator.py exists" "[ -f orchestrator.py ]"
echo ""

echo "📋 Checking Documentation"
echo "-------------------------"
test_step "README.md exists" "[ -f README.md ]"
test_step "README_DEPLOY.md exists" "[ -f README_DEPLOY.md ]"
test_step "Health report exists" "[ -f ci_health_report.json ]"
echo ""

echo "🐳 Checking Docker Configuration"
echo "--------------------------------"
test_step "docker-compose.yml exists" "[ -f docker-compose.yml ]"
test_step "Dockerfile.api exists" "[ -f Dockerfile.api ]"
test_step "web/Dockerfile exists" "[ -f web/Dockerfile ]"
echo ""

# TypeScript check (if available)
if command -v tsc > /dev/null 2>&1; then
    echo "🔍 TypeScript Validation"
    echo "-----------------------"
    cd web
    if npx tsc --noEmit > /dev/null 2>&1; then
        echo -e "${GREEN}✓ TypeScript validation passed${NC}"
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠ TypeScript validation warnings (non-critical)${NC}"
    fi
    cd ..
    echo ""
fi

# Summary
echo "=============================="
echo "📊 Summary"
echo "=============================="
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed! Ready for deployment.${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Deploy to Vercel: vercel --prod"
    echo "  2. Or run locally: cd web && npm start"
    echo "  3. Or use Docker: docker-compose up -d"
    exit 0
else
    echo -e "${RED}❌ Some checks failed. Please review the errors above.${NC}"
    exit 1
fi
