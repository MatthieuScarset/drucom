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
    local MAPPING=$4
    local OUTPUT_FILE="$OUTPUT_FOLDER/$FILENAME.json"
    local TEMP_FOLDER="$OUTPUT_FOLDER/temp_$FILENAME"

    mkdir -p "$TEMP_FOLDER"

    # Get the total number of pages from the `.last` parameter
    local LAST_PAGE_URL=$(curl -s "${BASE_URL}/${RESOURCE}?${PARAMETERS}&page=0" | jq -r '.last')
    local TOTAL_PAGES=$(echo "$LAST_PAGE_URL" | grep -oP 'page=\K\d+')

    echo "Fetching data for $RESOURCE in parallel..."
    local PROGRESS=0
    export MAPPING # Export the mapping so it can be accessed by the subshell
    seq 0 $TOTAL_PAGES | xargs -P 50 -I {} bash -c \
        "curl -s '${BASE_URL}/${RESOURCE}?${PARAMETERS}&page={}' | \
        jq -c '.list[] | ${MAPPING}' > '$TEMP_FOLDER/page_{}.json'; \
        echo -ne \"Progress: \$((++PROGRESS))/$((TOTAL_PAGES + 1)) pages fetched...\r\""

    echo -e "\nFetching complete."

    echo "Merging data..."
    echo "[" > "$OUTPUT_FILE"
    find "$TEMP_FOLDER" -type f -name "page_*.json" -exec cat {} + | sed '$!s/$/,/' >> "$OUTPUT_FILE"
    echo "]" >> "$OUTPUT_FILE"

    # Clean up temporary files
    rm -rf "$TEMP_FOLDER"

    # Validate JSON
    if ! jq -e . "$OUTPUT_FILE" > /dev/null 2>&1; then
        echo "❌ Error: Invalid JSON in $OUTPUT_FILE"
        exit 1
    fi

    echo "✅ Data saved in $OUTPUT_FILE"
}

case "$1" in
    user)
        fetch_data "user" "user.json" "sort=uid&direction=ASC" '{
            id: .uid,
            title: .name,
            created: .created,
            da_membership: (if .field_da_ind_membership == [] then null else .field_da_ind_membership end),
            timezone: (if .timezone == "" then null else .timezone end),
            slack: (if .field_slack == [] then null else .field_slack end),
            mentors: (if .field_mentors == [] then null else .field_mentors end),
            countries: (if .field_country == [] then null else .field_country end),
            languages: (if .field_languages == [] then null else .field_languages end),
            organizations: (if .field_organizations == [] then null else .field_organizations end)
        }'
        ;;
    organization)
        fetch_data "organization" "node.json" "type=organization&sort=nid&direction=ASC" '{
            id: .nid,
            title: .title,
            created: .created,
            changed: .changed,
            author: .author.id,
            url: (if (.field_link | type) == "array" then (.field_link[]?.url // null) elif (.field_link | type) == "object" then .field_link.url else null end),
            budget: (if .field_budget == [] then null else .field_budget end),
            headquarters: (if .field_organization_headquarters == [] then null else .field_organization_headquarters end)
        }'
        ;;
    *)
        echo "Usage: $0 {user|organization}"
        exit 1
        ;;
esac