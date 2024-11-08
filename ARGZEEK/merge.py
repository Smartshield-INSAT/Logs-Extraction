import pandas as pd
import argparse
from utils import *

def clean_string_values(value):
    """Helper function to clean string values by replacing \x2d with -"""
    if isinstance(value, str):
        return value.replace('\x2d', '-')
    return value

def merge_dataframes(argus_path, zeek_path, output_path):
    """
    This function merges data from Argus and Zeek log files, cleans the data, 
    and outputs the merged data to a CSV file with specific column names and order.
    """
    # Reading the data
    log_to_csv(zeek_path)
    zeek = pd.read_csv(zeek_path.split(".")[0] + ".csv")
    argus = pd.read_csv(argus_path)

    # Drop duplicates
    zeek = zeek.drop_duplicates()
    argus = argus.drop_duplicates()

    # Create mapping dictionary for Argus columns to final names
    argus_mapping = {
        'SrcAddr': 'srcip',
        'Sport': 'sport', 
        'DstAddr': 'dstip', 
        'Proto': 'proto', 
        'Dport': 'dsport',
        'Duration': 'dur',
        'State': 'state',
        'SrcPkts': 'spkts',
        'DstPkts': 'dpkts',
        'SrcBytes': 'sbytes',
        'DstBytes': 'dbytes',
        'Rate': 'rate',
        'SrcLoad': 'sload',
        'DstLoad': 'dload',
        'SrcLoss': 'sloss',
        'DstLoss': 'dloss',
        'SrcIntPkt': 'sinpkt',
        'DstIntPkt': 'dinpkt',
        'SrcJitter': 'sjit',
        'DstJitter': 'djit',
        'TCPRtt': 'tcprtt',
        'SrcMeanPktSize': 'smean'
    }

    # Rename columns in Argus DataFrame
    argus = argus.rename(columns=argus_mapping)

    # Replace service names with port numbers
    service_ports = {
        'http': '80', 'http-alt': '8080', 'https': '443', 
        'dns': '53', 'mdns': '5353', 'bootps': '67', 'bootpc': '68'
    }
    argus['dsport'] = argus['dsport'].replace(service_ports)
    argus['sport'] = argus['sport'].replace(service_ports)

    # Convert 'sport' and 'dsport' columns to numeric
    for col in ['sport', 'dsport']:
        argus[col] = pd.to_numeric(argus[col], errors='coerce')
        zeek[col] = pd.to_numeric(zeek[col], errors='coerce')

    # Drop rows with NaN values in 'sport' and 'dsport' columns
    argus = argus.dropna(subset=['sport', 'dsport'])
    zeek = zeek.dropna(subset=['sport', 'dsport'])

    # Convert columns to integers after cleaning NaNs
    argus['sport'] = argus['sport'].astype(int)
    argus['dsport'] = argus['dsport'].astype(int)
    zeek['sport'] = zeek['sport'].astype(int)
    zeek['dsport'] = zeek['dsport'].astype(int)

    # Merge the two dataframes
    result = pd.merge(argus, zeek, on=['srcip', 'sport', 'dstip', 'proto', 'dsport'], how='inner')

    # Preprocess the results to add ct_src_dport_ltm and ct_dst_sport_ltm
    result = preprocess_results(result)

    # Define the final column order and their types
    column_types = {
        'dur': 'float64',
        'proto': 'str',
        'service': 'str',
        'state': 'str',
        'spkts': 'int64',
        'dpkts': 'int64',
        'sbytes': 'int64',
        'dbytes': 'int64',
        'rate': 'float64',
        'sload': 'float64',
        'dload': 'float64',
        'sloss': 'int64',
        'dloss': 'int64',
        'sinpkt': 'float64',
        'dinpkt': 'float64',
        'sjit': 'float64',
        'djit': 'float64',
        'tcprtt': 'float64',
        'smean': 'float64',
        'trans_depth': 'int64',
        'ct_src_dport_ltm': 'int64',
        'ct_dst_sport_ltm': 'int64',
        'is_ftp_login': 'int64',
        'ct_flw_http_mthd': 'int64',
        'is_sm_ips_ports': 'int64'
    }

    # Clean service and protocol columns
    if 'service' in result.columns:
        result['service'] = result['service'].apply(clean_string_values)
    if 'proto' in result.columns:
        result['proto'] = result['proto'].apply(clean_string_values)

    # Ensure all required columns exist and handle empty/missing values
    for col, dtype in column_types.items():
        if col not in result.columns:
            # Add missing columns with appropriate type
            if dtype in ['int64', 'float64']:
                result[col] = 0
            else:
                result[col] = ''
        else:
            # Handle empty values based on column type
            if dtype in ['int64', 'float64']:
                result[col] = pd.to_numeric(result[col], errors='coerce').fillna(0)
                if dtype == 'int64':
                    result[col] = result[col].astype('int64')
                else:
                    result[col] = result[col].astype('float64')

    # Select and order only the required columns
    result = result[list(column_types.keys())]

    # Save the result to a CSV file
    result.to_csv(output_path, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge Argus and Zeek data files into a single CSV.")
    parser.add_argument("argus_path", type=str, help="Path to the Argus CSV file.")
    parser.add_argument("zeek_path", type=str, help="Path to the Zeek log file.")
    parser.add_argument("output_path", type=str, help="Path for the output CSV file.")
    args = parser.parse_args()
    merge_dataframes(args.argus_path, args.zeek_path, args.output_path)