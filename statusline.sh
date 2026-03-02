#!/bin/bash
input=$(cat)

MODEL=$(echo "$input" | jq -r '.model.display_name // "unknown"')
PERCENT=$(echo "$input" | jq -r '.context_window.used_percentage // 0')
TOTAL=$(echo "$input" | jq -r '.context_window.context_window_size // 200000')

# Calculate actual tokens in context from percentage
TOTAL_K=$(echo "scale=0; $TOTAL / 1000" | bc)
USED_K=$(echo "scale=0; ($TOTAL * $PERCENT) / 100000" | bc)

echo "[$MODEL] ${PERCENT}% (~${USED_K}K/${TOTAL_K}K)"
