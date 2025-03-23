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
    seq 0 $TOTAL_PAGES | xargs -P 100 -I {} bash -c \
        "if [ ! -f '$TEMP_FOLDER/page_{}.json' ]; then \
            curl -s '${BASE_URL}/${RESOURCE}?${PARAMETERS}&page={}' | \
            jq -c '.list[] | ${MAPPING}' > '$TEMP_FOLDER/page_{}.json'; \
        fi; \
        if (( {} % 50 == 0 )); then \
            echo -ne \"Progress: \$(ls -l $TEMP_FOLDER/*.json 2>/dev/null | wc -l)/$((TOTAL_PAGES + 1)) pages fetched...\r\"; \
        fi"

    echo -e "\nFetching complete."

    echo "Merging data..."
    echo "[" > "$OUTPUT_FILE"
    find "$TEMP_FOLDER" -type f -name "page_*.json" -exec cat {} + | sed '$!s/$/,/' >> "$OUTPUT_FILE"
    echo "]" >> "$OUTPUT_FILE"

    # Clean up temporary files
    # rm -rf "$TEMP_FOLDER"

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
            fname: .field_first_name,
            lname: .field_last_name,
            created: .created,
            da_membership: .field_da_ind_membership,
            slack: (if .field_slack == [] then null else .field_slack end),
            mentors: ([.field_mentors[].id | tostring] | join(",") | split(",")),
            countries: (if .field_country == [] then null else .field_country end),
            language: .field_user_primary_language,
            languages: (if .field_languages == [] then null else .field_languages end),
            timezone: .timezone,
            region: (if .timezone | length > 0 then (.timezone | tostring | split("/") | first) else null end),
            city: (if .timezone | length > 0 then (.timezone | tostring | split("/") | last) else null end),
            organizations: ([.field_organizations[].id | tostring] | join(",") | split(",")),
            industries: .field_industries,
            contributions: .field_contributed,
            events: .field_events_attended
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