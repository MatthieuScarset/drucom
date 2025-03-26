#!/bin/bash

# Merge data files feched from Drupal API
# Usage: ./merge_drupal_data.sh <type>

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_FOLDER="$SCRIPT_DIR/../data/json"

merge_data() {
    FILENAME="$1"
    PAGES_FOLDER="$OUTPUT_FOLDER/pages_$FILENAME"
    MERGED_FILE="$OUTPUT_FOLDER/merged_$FILENAME.json"

    echo "Merging files in $PAGES_FOLDER..."
    find "$PAGES_FOLDER" -type f -name '*.json' -print0 | xargs -0 jq -s -c '.' > "$MERGED_FILE"

    if [ $? -eq 0 ]; then
        echo "✅ Data merged into $MERGED_FILE"
    else
        echo "❌ Failed to merge data"
    fi
}

case "$1" in
    user)
        merge_data "user"
        ;;
    organization)
        merge_data "organization"
        ;;
    event)
        merge_data "event"
        ;;
    *)
        echo "Usage: $0 {user|organization|event}"  exit 1
        exit 1
        ;;
esac