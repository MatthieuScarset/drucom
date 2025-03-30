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
    local PAGES_FOLDER="$OUTPUT_FOLDER/$FILENAME"

    mkdir -p "$PAGES_FOLDER"

    # Get the total number of pages from the `.last` parameter
    local LAST_PAGE_URL=$(curl -s "${BASE_URL}/${RESOURCE}?${PARAMETERS}&page=0" | jq -r '.last')
    local TOTAL_PAGES=$(echo "$LAST_PAGE_URL" | grep -oP 'page=\K\d+')

    echo "Fetching data for $RESOURCE in parallel..."
    seq 0 $TOTAL_PAGES | parallel -j 100 --halt-on-error now,fail=1 \
        "if [ ! -f '$PAGES_FOLDER/page_{}.json' ]; then \
            curl -s '${BASE_URL}/${RESOURCE}?${PARAMETERS}&page={}' | \
            jq -c '.list[] | ${MAPPING}' > '$PAGES_FOLDER/page_{}.json'; \
        fi; \
        echo -ne \"Progress: \$(({} + 1))/$((TOTAL_PAGES + 1)) pages processed...\r\""
    echo "✅ Data saved in $PAGES_FOLDER"
}

# Define mappings for each type
user_mapping='{
    id: .uid,
    title: .name,
    fname: (.field_first_name // null),
    lname: (.field_last_name // null),
    created: .created,
    da_membership: (.field_da_ind_membership // null),
    slack: (.field_slack // null),
    mentors: (if (.field_mentors | type == "array") then .field_mentors | map(.id | tostring) else [] end),
    countries: (.field_country // null),
    language: (.field_user_primary_language // null),
    languages: (.field_languages // []),
    timezone: (.timezone // null),
    region: (if .timezone | length > 0 then (.timezone | tostring | split("/") | first) else null end),
    city: (if .timezone | length > 0 then (.timezone | tostring | split("/") | last) else null end),
    organizations: (if (.field_organizations | type == "array") then .field_organizations | map(.id | tostring) else [] end),
    industries: (.field_industries // null),
    contributions: (.field_contributed // null),
    events: (.field_events_attended // null)
}'

organization_mapping='{
    id: .nid,
    title: .title,
    created: .created,
    changed: .changed,
    author: (.author.id // null),
    url: (if (.field_link | type == "object") then .field_link.url else null end),
    budget: (.field_budget // null),
    headquarters: (.field_organization_headquarters // null)
}'

module_mapping='{
    id: .nid,
    title: .title,
    created: .created,
    changed: .changed,
    author: (.author.id // null),
    slug: .field_project_machine_name,
    stars: (.flag_project_star_user // [] | length // 0),
    security_status: .field_security_advisory_coverage,
    maintenance_status: (if (.taxonomy_vocabulary_44 | type == "object") then .taxonomy_vocabulary_44.id else null end),
    development_status: (if (.taxonomy_vocabulary_46 | type == "object") then .taxonomy_vocabulary_46.id else null end),
    categories: (if (.taxonomy_vocabulary_3 | type == "array") then .taxonomy_vocabulary_3 | map(.id | tostring) else [] end)
}'

event_mapping='{
    id: .nid,
    title: .title,
    from: (.field_date_of_event.value // null),
    to: (.field_date_of_event.value2 // null),
    duration: (.field_date_of_event.duration // null),
    event_type: (.field_event_type // [] | join("")),
    event_format: (.field_event_format // [] | join("")),
    author: (.author.id // null),
    speakers: (if (.field_event_speakers | type == "array") then .field_event_speakers | map(.id | tostring) else [] end),
    sponsors: (if (.field_event_sponsors | type == "array") then .field_event_sponsors | map(.id | tostring) else [] end),
    volunteers: (if (.field_event_volunteers | type == "array") then .field_event_volunteers | map(.id | tostring) else [] end),
    organizers: (if (.field_organizers | type == "array") then .field_organizers | map(.id | tostring) else [] end),
    city: (if (.field_event_address | type == "object") then .field_event_address.locality else null end),
    country: (if (.field_event_address | type == "object") then .field_event_address.country else null end)
}'

taxonomy_terms_mapping='{
    id: .tid,
    name: .name
}'

theme_mapping='{
    id: .nid,
    title: .title,
    created: .created,
    changed: .changed,
    author: (.author.id // null),
    slug: .field_project_machine_name,
    stars: (.flag_project_star_user // [] | length // 0),
}'

case "$1" in
    user)
        fetch_data "user" "user.json" "sort=uid&direction=ASC"  "$user_mapping"
        ;;
    organization)
        fetch_data "organization" "node.json" "type=organization&sort=nid&direction=ASC" "$organization_mapping"
        ;;
    module)
        fetch_data "module" "node.json" "type=project_module&sort=nid&direction=ASC" "$module_mapping"
        ;;
    module_terms)
        fetch_data "module_terms" "taxonomy_term.json" "vocabulary[]=3&vocabulary[]=44&vocabulary[]=46&sort=tid&direction=ASC" "$taxonomy_terms_mapping"
        ;;
    event)
        fetch_data "event" "node.json" "type=event&sort=nid&direction=ASC" "$event_mapping"
        ;;
    theme)
        fetch_data "theme" "node.json" "type=project_theme&sort=nid&direction=ASC" "$theme_mapping"
        ;;
    *)
        echo "Usage: $0 {user|organization|event|module|module_terms}"
        exit 1
        ;;
esac
