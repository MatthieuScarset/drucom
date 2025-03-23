#!/bin/bash

# Simplified script to fetch and process data from Drupal API
# Usage: ./fetch_drupal_data.sh <type>
# Dependencies: jq, curl

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_FOLDER="$SCRIPT_DIR/../data/json"
BASE_URL="https://www.drupal.org/api-d7"

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
    seq 0 $TOTAL_PAGES | parallel -j 100 --halt-on-error now,fail=1 \
        "curl -s '${BASE_URL}/${RESOURCE}?${PARAMETERS}&page={}' | \
        jq -c '.list[] | ${MAPPING}' > '$TEMP_FOLDER/page_{}.json' && \
        echo -ne \"Progress: \$(ls -l $TEMP_FOLDER | wc -l)/$((TOTAL_PAGES + 1)) pages fetched...\r\""

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
            fname: (.field_first_name // null),
            lname: (.field_last_name // null),
            created: .created,
            da_membership: (.field_da_ind_membership // null),
            slack: (.field_slack // null),
            mentors: ([.field_mentors[]?.id | tostring] // [] | join(",") | split(",")),
            countries: (.field_country // null),
            language: (.field_user_primary_language // null),
            languages: (.field_languages // []),
            timezone: (.timezone // null),
            region: (if .timezone | length > 0 then (.timezone | tostring | split("/") | first) else null end),
            city: (if .timezone | length > 0 then (.timezone | tostring | split("/") | last) else null end),
            organizations: ([.field_organizations[]?.id | tostring] // [] | join(",") | split(",")),
            industries: (.field_industries // null),
            contributions: (.field_contributed // null),
            events: (.field_events_attended // null)
        }'
        ;;
    organization)
        fetch_data "organization" "node.json" "type=organization&sort=nid&direction=ASC" '{
            id: .nid,
            title: .title,
            created: .created,
            changed: .changed,
            author: (.author.id // null),
            url: (.field_link.url // null),
            budget: (.field_budget // null),
            headquarters: (.field_organization_headquarters // null)
        }'
        ;;
    event)
        fetch_data "event" "node.json" "type=event&sort=nid&direction=ASC" '{
            id: .nid,
            title: .title,
            from: (.field_date_of_event.value // null),
            to: (.field_date_of_event.value2 // null),
            duration: (.field_date_of_event.duration // null),
            event_type: (.field_event_type // [] | join("")),
            event_format: (.field_event_format // [] | join("")),
            author: (.author.id // null),
            speakers: (.field_event_speakers // [] | map(.id | tostring)),
            sponsors: (.field_event_sponsors // [] | map(.id | tostring)),
            volunteers: (.field_event_volunteers // [] | map(.id | tostring)),
            organizers: (.field_organizers // [] | map(.id | tostring)),
            city: (if (.field_event_address | type == "object") then .field_event_address.locality else null end),
            country: (if (.field_event_address | type == "object") then .field_event_address.country else null end)
        }'
        ;;
    *)
        echo "Usage: $0 {user|organization|event}"  exit 1
        exit 1
        ;;esac