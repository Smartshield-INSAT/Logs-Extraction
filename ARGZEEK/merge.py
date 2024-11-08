import pandas as pd
from ARGZEEK.utils import *

def merge_dataframes(argus_path, zeek_path, output_path):
    """
    This function merges data from Argus and Zeek log files, cleans the data, 
    and outputs the merged data to a CSV file.

    Args:
        argus_path (str): The file path to the Argus CSV file
        zeek_path (str): The file path to the Zeek log file, which will be converted to a CSV using `log_to_csv`.
        output_path (str): The file path for the output CSV file containing the merged and processed data.

    Returns:
        None: This function writes the merged data directly to a CSV file at `output_path`.
    
    Workflow:
    1. Reads the Zeek log file, converts it to a CSV format, and loads both Zeek and Argus data as DataFrames.
    2. Drops duplicate entries in each DataFrame.
    3. Renames columns in the Argus DataFrame to match the Zeek DataFrame.
    4. Replaces service names in the 'dsport' column with corresponding port numbers (e.g., 'http' to 80).
    5. Converts 'sport' and 'dsport' columns to numeric values and drops rows with NaN values to ensure compatibility.
    6. Merges both DataFrames based on common fields: 'srcip', 'sport', 'dstip', 'proto', and 'dsport'.
    7. Preprocesses the merged DataFrame to drop specific unnecessary columns.
    8. Saves the final processed DataFrame to a CSV file.
    """
    # Reading the data
    log_to_csv(zeek_path)
    zeek = pd.read_csv(zeek_path.split(".")[0] + ".csv")
    argus = pd.read_csv(argus_path)

    # Drop duplicates
    zeek = zeek.drop_duplicates()
    argus = argus.drop_duplicates()

    # Rename columns to match
    argus = argus.rename(columns={'SrcAddr': 'srcip', 'Sport': 'sport', 'DstAddr': 'dstip', 'Proto' : 'proto', 'Dport' : 'dsport'})    

    # Replace 'http', 'http-alt', and 'https' with their respective port numbers
    argus['dsport'] = argus['dsport'].replace(to_replace='http', value='80')
    argus['dsport'] = argus['dsport'].replace(to_replace='http-alt', value='8080')
    argus['dsport'] = argus['dsport'].replace(to_replace='https', value='443')

    # Convert 'dsport' column to numeric, setting errors='coerce' to turn non-numeric values into NaN
    argus['dsport'] = pd.to_numeric(argus['dsport'], errors='coerce')
    zeek['dsport'] = pd.to_numeric(zeek['dsport'], errors='coerce')
    argus = argus.dropna(subset=['sport'])
    zeek = zeek.dropna(subset=['sport'])

    # Convert 'sport' column to numeric, setting errors='coerce' to turn non-numeric values into NaN
    argus['sport'] = pd.to_numeric(argus['sport'], errors='coerce')
    zeek['sport'] = pd.to_numeric(zeek['sport'], errors='coerce')
    argus = argus.dropna(subset=['sport'])
    zeek = zeek.dropna(subset=['sport'])

    # Convert 'sport' back to integer if needed
    argus['sport'] = argus['sport'].astype(int)
    zeek['sport'] = zeek['sport'].astype(int)

    # Convert 'sport' back to integer if needed
    argus['dsport'] = argus['dsport'].astype(int)
    zeek['dsport'] = zeek['dsport'].astype(int)

    # Merge the two dataframes
    result = pd.merge(argus, zeek, on=['srcip', 'sport', 'dstip','proto','dsport'], how='inner')

    # Preprocess the results
    result = preprocess_results(result)

    # Save the result to a CSV file
    result.to_csv(output_path, index=False)
