#!/bin/bash

# Ensure a .pcap file is passed as an argument
if [ -z "$1" ]; then
    echo "Usage: $0 <pcap_file>"
    exit 1
fi

# Assign the provided .pcap file path to a variable
PCAP_FILE="$1"
# Extract the base name of the pcap file without the .pcap extension
PCAP_NAME=$(basename "$PCAP_FILE" .pcap)

# Directory paths (update these as needed)
ZEEK_OUTPUT_DIR="ZeekFiles"
ARGUS_OUTPUT_DIR="ArgusFiles"
FINAL_OUTPUT_DIR="FinalOutput"
ZEEK_SCRIPT="script.zeek"

# Create output directories if they don't exist
mkdir -p "$ZEEK_OUTPUT_DIR" "$ARGUS_OUTPUT_DIR" "$FINAL_OUTPUT_DIR"

# Run Zeek with the specified log directory and script, storing output with PCAP name
zeek -r "$PCAP_FILE" "ExtractFeatures::log_dir=$ZEEK_OUTPUT_DIR/ZEEK_${PCAP_NAME}" "$ZEEK_SCRIPT"

# Remove all .log files from the Zeek output directory
rm *.log

# Run Argus to generate ARGUS file
argus -r "$PCAP_FILE" -w "$ARGUS_OUTPUT_DIR/ARGUS_${PCAP_NAME}.argus"

# Run ra on the ARGUS file to generate CSV
ra -r "$ARGUS_OUTPUT_DIR/ARGUS_${PCAP_NAME}.argus" \
   -s sport,saddr,dport,daddr,stime,dur,proto,state,spkts,dpkts,sbytes,dbytes,rate,sload,dload,sloss,dloss,sintpkt,dintpkt,sjit,djit,tcprtt,smeansz \
   -u -c ',' > "$ARGUS_OUTPUT_DIR/RA_${PCAP_NAME}.csv"

# Call to python script with proper arguments
python3 ./merge.py \
    "$ARGUS_OUTPUT_DIR/RA_${PCAP_NAME}.csv" \
    "$ZEEK_OUTPUT_DIR/ZEEK_${PCAP_NAME}.log" \
    "$FINAL_OUTPUT_DIR/MERGED_${PCAP_NAME}.csv"