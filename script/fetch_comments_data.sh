#!/bin/bash

# Script to fetch and process data from Drupal API
# Usage: ./fetch_comments_data.sh
# Dependencies: jq, curl, parallel

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_FOLDER="$SCRIPT_DIR/../data/json/batches_comment"
BASE_URL="https://www.drupal.org/api-d7"
RESOURCE="comment.json"

fetch_comments_data() {
    local USER_ID=$1
    local PARAMETERS="limit=1&sort=cid&direction=ASC&author=$USER_ID"
    local RESULTS=$(curl -s "${BASE_URL}/${RESOURCE}?${PARAMETERS}")
    local LAST_PAGE_URL=$(echo "$RESULTS" | jq -r '.last // "null"')
    local TOTAL_PAGES=$(echo "$LAST_PAGE_URL" | grep -oP 'page=\K\d+' || echo "1")
    
    # Convert total page to integer
    TOTAL_PAGES=$(echo "$TOTAL_PAGES" | sed 's/[^0-9]//g')

    # Skip if no result.
    if [ "$TOTAL_PAGES" -eq 0 ]; then
        return
    fi

    local FIRST_TIMESTAMP=$(echo "$RESULTS" | jq -r '.list[0].created // "null"')
    local LAST_TIMESTAMP=$FIRST_TIMESTAMP

    # Curl another time only if total page is more than 1
    if [ "$TOTAL_PAGES" -gt 1 ]; then
        local LAST_PAGE=$((TOTAL_PAGES -1))
        local LAST_RESULTS=$(curl -s "${BASE_URL}/${RESOURCE}?${PARAMETERS}&page=${LAST_PAGE}")
        local LAST_TIMESTAMP=$(echo "$LAST_RESULTS" | jq -r '.list[0].created // "null"')
    fi

    jq -n --arg user "$USER_ID" \
          --argjson count "$TOTAL_PAGES" \
          --arg first "$FIRST_TIMESTAMP" \
          --arg last "$LAST_TIMESTAMP" \
          '{($user): {count: $count, first: $first, last: $last}}'
}

run() {
    export -f fetch_comments_data
    export BASE_URL RESOURCE OUTPUT_FOLDER

    local USER_IDS_FILE="$SCRIPT_DIR/../data/json/user_uids.json"
    mapfile -t USER_IDS < <(jq -r '.[]' "$USER_IDS_FILE")

    # Total number of users
    local TOTAL_USERS=${#USER_IDS[@]}
    echo "Fetching comments data for $TOTAL_USERS users in parallel..."

    # Create output folder if it doesn't exist
    mkdir -p "$OUTPUT_FOLDER"

    # Process users in batches of 1000
    local BATCH_SIZE=1000
    local BATCH_NUMBER=1
    for ((i = 0; i < TOTAL_USERS; i += BATCH_SIZE)); do
        local BATCH_USERS=("${USER_IDS[@]:i:BATCH_SIZE}")
        local OUTPUT_FILE="$OUTPUT_FOLDER/batch_${BATCH_NUMBER}.json"

        echo "Processing batch $BATCH_NUMBER with ${#BATCH_USERS[@]} users..." >&2
        echo "================================================================" >&2

        # Process each user in the batch in parallel
        printf "%s\n" "${BATCH_USERS[@]}" | parallel -j 100 --halt-on-error now,fail=1 \
            "fetch_comments_data {}" | jq -s 'add' > $OUTPUT_FILE

        echo "✅ Data saved to $OUTPUT_FILE"

        ((BATCH_NUMBER++))
    done
}

run