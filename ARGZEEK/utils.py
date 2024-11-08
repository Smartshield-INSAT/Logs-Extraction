import pandas as pd
from parsezeeklogs import ParseZeekLogs

def ct_src_dport_ltm(result_df):
    """
    This function calculates the count of occurrences of the same source IP ('srcip') 
    and destination port ('dsport') in the last 100 connections before each row in 
    the given DataFrame, and stores the result as a new column.

    Args:
        result_df (pd.DataFrame): The DataFrame containing the connection data. 

    Returns:
        pd.DataFrame: The input DataFrame with an additional column 'ct_src_dport_ltm', 
    """
    # Sort by StartTime to ensure we process in chronological order
    result_df = result_df.sort_values(by='StartTime').reset_index(drop=True)
    
    # Initialize a list to hold the count values
    ct_src_dport_values = []
    for i in range(len(result_df)):
        # Look at the last 100 connections
        start_index = max(0, i - 100)
        subset_df = result_df.iloc[start_index:i]
        
        # Count occurrences of matching srcip and dsport
        srcip = result_df.at[i, 'srcip']
        dsport = result_df.at[i, 'dsport']
        count = subset_df[(subset_df['srcip'] == srcip) & (subset_df['dsport'] == dsport)].shape[0]
        
        ct_src_dport_values.append(count)
    
    # Add the list as a new column in result_df
    result_df['ct_src_dport_ltm'] = ct_src_dport_values
    return result_df


def ct_dst_sport_ltm(result_df):
    """
    This function calculates the count of occurrences of the same destination IP ('dstip') 
    and source port ('sport') in the last 100 connections before each row in the given 
    DataFrame, and stores the result as a new column.

    Args:
        result_df (pd.DataFrame): The DataFrame containing the connection data. 

    Returns:
        pd.DataFrame: The input DataFrame with an additional column 'ct_dst_sport_ltm', 
    """
    # Sort by StartTime to ensure we process in chronological order
    result_df = result_df.sort_values(by='StartTime').reset_index(drop=True)
    
    # Initialize a list to hold the count values
    ct_dst_sport_values = []
    for i in range(len(result_df)):
        # Look at the last 100 connections
        start_index = max(0, i - 100)
        subset_df = result_df.iloc[start_index:i]
        
        # Count occurrences of matching dstip and sport
        dstip = result_df.at[i, 'dstip']
        sport = result_df.at[i, 'sport']
        count = subset_df[(subset_df['dstip'] == dstip) & (subset_df['sport'] == sport)].shape[0]
        
        ct_dst_sport_values.append(count)
    
    # Add the list as a new column in result_df
    result_df['ct_dst_sport_ltm'] = ct_dst_sport_values
    return result_df

def log_to_csv(log_path):
    """
    This function reads a Zeek log file, parses the log records using the `ParseZeekLogs` 
    function, and writes selected fields to a CSV file.

    Args:
        log_path (str): The file path of the Zeek log to be processed. The function will generate
                        a corresponding CSV file by replacing the log file's extension with `.csv`.

    Returns:
        None: This function writes the parsed log data directly to a CSV file at the generated path.
    """
    LIST = ['ts', 'uid', 'srcip', 'sport', 'dstip', 'dsport', 'service', 'proto', 
            'trans_depth', 'is_sm_ips_ports', 'ct_flw_http_mthd', 'is_ftp_login']
    save_path = log_path.split(".")[0] + ".csv"
    with open(save_path, "w") as outfile:
        outfile.write(",".join(LIST) + "\n")
        for log_record in ParseZeekLogs(log_path, output_format="csv", fields=LIST):
            if log_record is not None:
                outfile.write(log_record + "\n")

def preprocess_results(result_df):
    """
    This function preprocesses the given DataFrame by removing specific features 
    that are not needed for further analysis.

    Args:
        result_df (pd.DataFrame): The input DataFrame containing the raw log data. 
                                  It must have columns such as 'ts', 'uid', 'srcip', etc.

    Returns:
        pd.DataFrame: A new DataFrame with specific columns dropped, which simplifies 
                      the data for further analysis.
    """
    result_df = ct_src_dport_ltm(result_df)
    result_df = ct_dst_sport_ltm(result_df)
    result_df = result_df.sort_values(by='StartTime').reset_index(drop=True)
    features_to_drop = ['ts', 'uid', 'srcip', 'dsport', 'dstip', 'StartTime', 'sport']
    result_df.drop(columns=features_to_drop, inplace=True)
    return result_df