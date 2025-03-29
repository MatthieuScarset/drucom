#!/bin/bash

# Script to fetch and process data from Drupal API
# Usage: ./fetch_comments_data.sh
# Dependencies: jq, curl

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_FOLDER="$SCRIPT_DIR/../data/json"
OUTPUT_FILE="$OUTPUT_FOLDER/comments.json"
BASE_URL="https://www.drupal.org/api-d7"
RESOURCE="comment.json"

fetch_comments_data() {
    local PARAMETERS="limit=1&sort=cid&direction=ASC&author=$USER_ID"
    local RESULTS=$(curl -s "${BASE_URL}/${RESOURCE}?${PARAMETERS}")
    local LAST_PAGE_URL=$(echo "$RESULTS" | jq -r '.last // "null"')
    local TOTAL_PAGES=$(echo "$LAST_PAGE_URL" | grep -oP 'page=\K\d+' || echo "1")
    TOTAL_PAGES=$((TOTAL_PAGES - 1))
    local FIRST_TIMESTAMP=$(echo "$RESULTS" | jq -r '.list[0].created // "null"')
    local LAST_RESULTS=$(curl -s "${BASE_URL}/${RESOURCE}?${PARAMETERS}&page=$TOTAL_PAGES")
    local LAST_TIMESTAMP=$(echo "$LAST_RESULTS" | jq -r '.list[0].created // "null"')

    # Output the JSON object instead of using return
    jq -n --arg user "$USER_ID" \
          --argjson count "$TOTAL_PAGES" \
          --arg first "$FIRST_TIMESTAMP" \
          --arg last "$LAST_TIMESTAMP" \
          '{($user): {count: $count, first: $first, last: $last}}'
}

run() {
    # Read ./data/user_uids.json into an array
    local USER_IDS_FILE="$SCRIPT_DIR/../data/json/user_uids.json"
    if [ ! -f "$USER_IDS_FILE" ]; then
        echo "Error: $USER_IDS_FILE does not exist."
        exit 1
    fi

    # Parse user IDs into an array
    mapfile -t USER_IDS < <(jq -r '.[]' "$USER_IDS_FILE")
    local TOTAL_USER_IDS=${#USER_IDS[@]}

    # Initialize the output JSON file
    mkdir -p "$OUTPUT_FOLDER"
    if [ ! -f "$OUTPUT_FILE" ]; then
        echo "[]" > "$OUTPUT_FILE"  # Start with an empty JSON array
    fi

    local COUNTER=0
    for USER_ID in "${USER_IDS[@]}"; do
        COUNTER=$((COUNTER + 1))

        # Fetch data for the current user
        RESULTS=$(fetch_comments_data)
        echo "Fetched data for user $USER_ID: $RESULTS"

        # Append the result to the JSON file
        jq ". + [$RESULTS]" "$OUTPUT_FILE" > "$OUTPUT_FILE.tmp" && mv "$OUTPUT_FILE.tmp" "$OUTPUT_FILE"

        echo "Progress: $COUNTER/$TOTAL_USER_IDS users processed..."
    done
}

run