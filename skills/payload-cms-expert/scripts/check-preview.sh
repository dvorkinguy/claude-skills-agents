#!/bin/bash
# Check CMS preview configuration
# Usage: ./check-preview.sh [slug]

SLUG="${1:-home}"
CMS_URL="${CMS_URL:-http://localhost:3030}"
WWW_URL="${WWW_URL:-http://localhost:3000}"

echo "=========================================="
echo "Preview Configuration Check"
echo "=========================================="
echo ""
echo "Checking preview for slug: $SLUG"
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

# 1. Check CMS PREVIEW_SECRET
echo "1. Checking CMS PREVIEW_SECRET..."
CMS_ENV="apps/cms/.env"
if [ -f "$CMS_ENV" ]; then
    CMS_SECRET=$(grep "^PREVIEW_SECRET=" "$CMS_ENV" | cut -d'=' -f2)
    if [ -n "$CMS_SECRET" ]; then
        check_pass "CMS PREVIEW_SECRET is set (${#CMS_SECRET} chars)"
    else
        check_fail "CMS PREVIEW_SECRET is empty or not set"
    fi
else
    check_fail "CMS .env file not found"
    CMS_SECRET=""
fi

# 2. Check WWW CMS_PREVIEW_SECRET
echo ""
echo "2. Checking WWW CMS_PREVIEW_SECRET..."
WWW_ENV="apps/www/.env.local"
if [ -f "$WWW_ENV" ]; then
    WWW_SECRET=$(grep "^CMS_PREVIEW_SECRET=" "$WWW_ENV" | cut -d'=' -f2)
    if [ -n "$WWW_SECRET" ]; then
        check_pass "WWW CMS_PREVIEW_SECRET is set (${#WWW_SECRET} chars)"
    else
        check_fail "WWW CMS_PREVIEW_SECRET is empty or not set"
    fi
else
    check_warn "WWW .env.local not found"
    WWW_SECRET=""
fi

# 3. Check secrets match
echo ""
echo "3. Checking secrets match..."
if [ -n "$CMS_SECRET" ] && [ -n "$WWW_SECRET" ]; then
    if [ "$CMS_SECRET" == "$WWW_SECRET" ]; then
        check_pass "Secrets match!"
    else
        check_fail "Secrets DO NOT match!"
        echo "  CMS: $CMS_SECRET"
        echo "  WWW: $WWW_SECRET"
        echo ""
        echo "  → Set the same value in both files"
    fi
else
    check_warn "Cannot compare - one or both secrets missing"
fi

# 4. Check page exists in CMS
echo ""
echo "4. Checking page '$SLUG' exists..."
PAGE_DATA=$(curl -s "$CMS_URL/api/pages?where[slug][equals]=$SLUG" 2>/dev/null)
if echo "$PAGE_DATA" | grep -q '"totalDocs":1'; then
    check_pass "Page '$SLUG' exists in CMS"

    # Check publish status
    STATUS=$(echo "$PAGE_DATA" | grep -o '"_status":"[^"]*"' | head -1 | cut -d'"' -f4)
    if [ "$STATUS" == "published" ]; then
        check_pass "Page is published"
    else
        check_warn "Page status: $STATUS (may need preview to view)"
    fi
else
    check_fail "Page '$SLUG' not found in CMS"
fi

# 5. Check preview route exists
echo ""
echo "5. Checking preview route handler..."
PREVIEW_ROUTE="apps/www/app/api-v2/cms/preview/route.ts"
if [ -f "$PREVIEW_ROUTE" ]; then
    check_pass "Preview route exists"

    # Check it reads the right env var
    if grep -q "CMS_PREVIEW_SECRET" "$PREVIEW_ROUTE"; then
        check_pass "Route uses CMS_PREVIEW_SECRET"
    else
        check_warn "Route may use different secret variable"
    fi
else
    check_fail "Preview route not found at $PREVIEW_ROUTE"
fi

# 6. Generate test preview URL
echo ""
echo "6. Generating preview URL..."
if [ -n "$CMS_SECRET" ]; then
    PREVIEW_SLUG=$SLUG
    if [ "$SLUG" == "home" ]; then
        PREVIEW_SLUG=""
    fi
    PREVIEW_URL="$WWW_URL/api-v2/cms/preview?slug=$PREVIEW_SLUG&collection=pages&secret=$CMS_SECRET"
    echo ""
    echo "Test URL:"
    echo "$PREVIEW_URL"
    echo ""

    # 7. Test preview URL
    echo "7. Testing preview URL..."
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -L "$PREVIEW_URL" 2>/dev/null)
    if [ "$RESPONSE" == "200" ]; then
        check_pass "Preview URL works (HTTP 200)"
    elif [ "$RESPONSE" == "307" ] || [ "$RESPONSE" == "302" ]; then
        check_pass "Preview URL redirects (HTTP $RESPONSE)"
    elif [ "$RESPONSE" == "401" ]; then
        check_fail "Preview URL returns 401 - secret mismatch"
    else
        check_warn "Preview URL returns HTTP $RESPONSE"
    fi
else
    check_warn "Cannot generate preview URL - secret not found"
fi

echo ""
echo "=========================================="
echo "Preview check complete!"
echo "=========================================="
