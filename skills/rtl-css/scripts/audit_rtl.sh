#!/bin/bash
# Audit codebase for RTL CSS violations

echo "🔍 Scanning for RTL violations..."
echo ""

# Find physical properties in TSX/JSX files
VIOLATIONS=$(grep -rn "pl-\|pr-\|ml-\|mr-\|left-\|right-\|text-left\|text-right" \
  --include="*.tsx" --include="*.jsx" \
  --exclude-dir=node_modules \
  --exclude-dir=.next \
  2>/dev/null)

if [ -z "$VIOLATIONS" ]; then
  echo "✅ No RTL violations found!"
  exit 0
else
  echo "❌ Found RTL violations:"
  echo ""
  echo "$VIOLATIONS" | while read line; do
    echo "  $line"
  done
  echo ""
  echo "Replace with logical properties:"
  echo "  pl-* → ps-*"
  echo "  pr-* → pe-*"
  echo "  ml-* → ms-*"
  echo "  mr-* → me-*"
  echo "  left-* → start-*"
  echo "  right-* → end-*"
  echo "  text-left → text-start"
  echo "  text-right → text-end"
  exit 1
fi
