#!/bin/bash
# Check CMS connectivity and health
# Usage: ./check-connectivity.sh [cms-url]

CMS_URL="${1:-http://localhost:3030}"
WWW_URL="${2:-http://localhost:3000}"

echo "=========================================="
echo "CMS Connectivity Check"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_pass() {
    echo -e "${GREEN}✓ PASS${NC}: $1"
}

check_fail() {
    echo -e "${RED}✗ FAIL${NC}: $1"
}

check_warn() {
    echo -e "${YELLOW}⚠ WARN${NC}: $1"
}

# 1. Check CMS is running
echo "1. Checking CMS at $CMS_URL..."
CMS_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$CMS_URL/admin" 2>/dev/null)
if [ "$CMS_RESPONSE" == "200" ] || [ "$CMS_RESPONSE" == "302" ]; then
    check_pass "CMS admin is accessible (HTTP $CMS_RESPONSE)"
else
    check_fail "CMS admin not accessible (HTTP $CMS_RESPONSE)"
    echo "  → Start CMS with: pnpm dev --filter cms"
fi

# 2. Check CMS API
echo ""
echo "2. Checking CMS API..."
API_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$CMS_URL/api/pages" 2>/dev/null)
if [ "$API_RESPONSE" == "200" ]; then
    check_pass "CMS API is responding (HTTP $API_RESPONSE)"

    # Count pages
    PAGE_COUNT=$(curl -s "$CMS_URL/api/pages" 2>/dev/null | grep -o '"totalDocs":[0-9]*' | cut -d':' -f2)
    echo "  → Found $PAGE_COUNT pages in CMS"
else
    check_fail "CMS API not responding (HTTP $API_RESPONSE)"
fi

# 3. Check WWW is running
echo ""
echo "3. Checking WWW at $WWW_URL..."
WWW_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$WWW_URL" 2>/dev/null)
if [ "$WWW_RESPONSE" == "200" ]; then
    check_pass "WWW is accessible (HTTP $WWW_RESPONSE)"
else
    check_fail "WWW not accessible (HTTP $WWW_RESPONSE)"
    echo "  → Start WWW with: pnpm dev --filter www"
fi

# 4. Check WWW can fetch from CMS
echo ""
echo "4. Checking WWW → CMS connection..."
# Try to fetch home page from CMS via WWW's perspective
HOME_PAGE=$(curl -s "$CMS_URL/api/pages?where[slug][equals]=home" 2>/dev/null)
if echo "$HOME_PAGE" | grep -q '"totalDocs":1'; then
    check_pass "Home page exists in CMS"
else
    check_warn "Home page not found in CMS"
    echo "  → Create a page with slug 'home' in CMS admin"
fi

# 5. Check environment variables
echo ""
echo "5. Checking environment files..."

CMS_ENV="apps/cms/.env"
WWW_ENV="apps/www/.env.local"

if [ -f "$CMS_ENV" ]; then
    check_pass "CMS .env exists"

    if grep -q "DATABASE_URI" "$CMS_ENV"; then
        check_pass "DATABASE_URI is set"
    else
        check_fail "DATABASE_URI not found"
    fi

    if grep -q "PAYLOAD_SECRET" "$CMS_ENV"; then
        check_pass "PAYLOAD_SECRET is set"
    else
        check_fail "PAYLOAD_SECRET not found"
    fi

    if grep -q "PREVIEW_SECRET" "$CMS_ENV"; then
        check_pass "PREVIEW_SECRET is set"
    else
        check_warn "PREVIEW_SECRET not set (preview won't work)"
    fi
else
    check_fail "CMS .env not found"
fi

if [ -f "$WWW_ENV" ]; then
    check_pass "WWW .env.local exists"

    if grep -q "CMS_PREVIEW_SECRET" "$WWW_ENV"; then
        check_pass "CMS_PREVIEW_SECRET is set"
    else
        check_warn "CMS_PREVIEW_SECRET not set (preview won't work)"
    fi
else
    check_warn "WWW .env.local not found"
fi

# 6. Check port availability
echo ""
echo "6. Checking ports..."
if lsof -i :3030 > /dev/null 2>&1; then
    check_pass "Port 3030 is in use (CMS)"
else
    check_warn "Port 3030 is free (CMS not running)"
fi

if lsof -i :3000 > /dev/null 2>&1; then
    check_pass "Port 3000 is in use (WWW)"
else
    check_warn "Port 3000 is free (WWW not running)"
fi

echo ""
echo "=========================================="
echo "Check complete!"
echo "=========================================="
