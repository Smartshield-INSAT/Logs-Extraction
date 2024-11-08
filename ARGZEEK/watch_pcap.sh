#!/bin/bash

# Directory to monitor for new .pcap files
WATCH_DIR="../received_files"
PROCESS_SCRIPT="./process_pcap.sh"

# Process existing .pcap files in the directory
for EXISTING_FILE in "$WATCH_DIR"/*.pcap; do
    # Only process if the file actually exists (handles empty directory case)
    if [[ -f "$EXISTING_FILE" ]]; then
        echo "Processing existing file: $EXISTING_FILE"
        "$PROCESS_SCRIPT" "$EXISTING_FILE"
    fi
done

# Monitor for new .pcap files
inotifywait -m -e close_write --format "%w%f" "$WATCH_DIR" | while read NEW_FILE
do
    if [[ "$NEW_FILE" == *.pcap ]]; then
        echo "New file detected: $NEW_FILE"
        "$PROCESS_SCRIPT" "$NEW_FILE"
    fi
done
