#!/bin/bash

# Simplified script to fetch and process data from Drupal API
# Usage: ./fetch_drupal_data.sh <type>
# Dependencies: jq, curl

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_FOLDER="$SCRIPT_DIR/../data/json"
BASE_URL="https://www.drupal.org/api-d7"
COLUMNS_TO_KEEP='.title, .nid, .url, .field_budget, .field_organization_headquarters'

mkdir -p "$OUTPUT_FOLDER"

fetch_data() {
    local FILENAME=$1
    local RESOURCE=$2
    local PARAMETERS=$3
    local OUTPUT_FILE="$OUTPUT_FOLDER/$FILENAME.json"

    # Get the total number of pages from the `.last` parameter
    local LAST_PAGE_URL=$(curl -s "${BASE_URL}/${RESOURCE}?${PARAMETERS}&page=0" | jq -r '.last')
    local TOTAL_PAGES=$(echo "$LAST_PAGE_URL" | grep -oP 'page=\K\d+')

    echo "Fetching data for $RESOURCE..."
    for page in $(seq 0 $TOTAL_PAGES); do
        curl -s "${BASE_URL}/${RESOURCE}?${PARAMETERS}&page=${page}" | \
        jq -c ".list[] | {nid: .nid, title: .title, created: .created, changed: .changed, author: .author.id, url: .field_link.url, field_budget: .field_budget, field_organization_headquarters: .field_organization_headquarters}" >> "$OUTPUT_FILE"
        # Display progress
        echo -ne "Progress: $((page + 1))/$((TOTAL_PAGES + 1)) pages\r"
    done
    echo -ne "\n"

    # Add a comma at the end of each line except the first and the last one
    sed -i '$!s/$/,/' "$OUTPUT_FILE"
    # Add opening and closing brackets
    sed -i '1s/^/[/' "$OUTPUT_FILE"
    # Add closing right at the end of the last line.
    sed -i '$s/$/]/' "$OUTPUT_FILE"

    # Validate JSON
    if ! jq -e . "$OUTPUT_FILE" > /dev/null 2>&1; then
        echo "❌ Error: Invalid JSON in $OUTPUT_FILE"
        exit 1
    fi

    echo "✅ Data saved in $OUTPUT_FILE"
}

case "$1" in
    user)
        fetch_data "user" "user.json" "sort=uid&direction=ASC"
        ;;
    organization)
        fetch_data "organization" "node.json" "type=organization&sort=nid&direction=ASC"
        ;;
    *)
        echo "Usage: $0 {user|organization}"
        exit 1
        ;;
esac