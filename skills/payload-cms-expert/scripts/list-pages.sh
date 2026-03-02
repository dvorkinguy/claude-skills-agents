#!/bin/bash
# List all CMS pages with their status
# Usage: ./list-pages.sh [cms-url]

CMS_URL="${1:-http://localhost:3030}"

echo "=========================================="
echo "CMS Pages List"
echo "=========================================="
echo ""

# Fetch all pages
PAGES=$(curl -s "$CMS_URL/api/pages?limit=100&sort=title" 2>/dev/null)

if [ -z "$PAGES" ]; then
    echo "Error: Could not fetch pages from CMS"
    echo "Make sure CMS is running at $CMS_URL"
    exit 1
fi

# Check for errors
if echo "$PAGES" | grep -q '"errors"'; then
    echo "Error fetching pages:"
    echo "$PAGES" | jq '.errors'
    exit 1
fi

# Get total count
TOTAL=$(echo "$PAGES" | grep -o '"totalDocs":[0-9]*' | cut -d':' -f2)
echo "Total pages: $TOTAL"
echo ""

# Parse and display pages
echo "Status | Template   | Slug                | Title"
echo "-------|------------|---------------------|----------------------------------"

# Use jq if available, otherwise use grep
if command -v jq &> /dev/null; then
    echo "$PAGES" | jq -r '.docs[] | "\(if ._status == "published" then "✓ Pub " else "○ Draft" end) | \(.template // "n/a" | .[0:10]) | \(.slug | .[0:19]) | \(.title | .[0:35])"' 2>/dev/null
else
    # Fallback without jq
    echo "$PAGES" | grep -oP '"title":"[^"]*"|"slug":"[^"]*"|"_status":"[^"]*"|"template":"[^"]*"' | \
    while read -r line; do
        echo "$line"
    done
fi

echo ""
echo "=========================================="

# Summary by status
PUBLISHED=$(echo "$PAGES" | grep -o '"_status":"published"' | wc -l)
DRAFT=$(echo "$PAGES" | grep -o '"_status":"draft"' | wc -l)

echo ""
echo "Summary:"
echo "  Published: $PUBLISHED"
echo "  Draft: $DRAFT"
echo ""

# List by template
echo "By template:"
echo "$PAGES" | grep -oP '"template":"[^"]*"' | sort | uniq -c | sed 's/"template":"//g' | sed 's/"//g' | \
while read -r count template; do
    echo "  $template: $count"
done
