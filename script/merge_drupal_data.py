import os
import pandas as pd


def merge_drupal_pages(input_folder: str) -> pd.DataFrame:
    """
    Merge a list of dataframes into a single dataframe.

    Parameters
    ----------
    input_folder : str
        The path to the folder containing the JSON files.

    Returns
    -------
    pandas.DataFrame
        Merged dataframe.
    """

    # Initialize an empty list to store dataframes
    dataframes = []

    # Dynamically set max_pages to the total number of JSON files in the directory
    max_pages = len([f for f in os.listdir(
        input_folder) if f.endswith(".json")])

    # For testing purposes, limit the number of pages to process.
    # max_pages = 1000

    # Get a sorted list of JSON files
    json_files = sorted(
        [f for f in os.listdir(input_folder) if f.endswith(".json")],
        # Sort by page number
        key=lambda x: int(x.split("_")[-1].split(".")[0])
    )[:max_pages]  # Limit to max_pages files

    # Iterate over the selected JSON files
    for filename in json_files:
        file_path = os.path.join(input_folder, filename)
        # Read the JSON file into a dataframe
        df = pd.read_json(file_path, lines=True)
        # Append the dataframe to the list
        dataframes.append(df)

    # Concatenate all dataframes
    merged_df = pd.concat(dataframes, ignore_index=True)
    print("Data concatenated and ready to be merged!")
    return merged_df


# Merge fetched pages into one DataFrame.
# ⚠️ Warning: can take a long time to run (user takes ~8.5 minutes).
for name in ['organization', 'event', 'user', 'module', 'module_terms']:
    output_file = f"../data/{name}.parquet"
    merged_df = merge_drupal_pages(f"../data/json/pages_{name}")
    merged_df.to_parquet(output_file, index=False)
    print(f"Data successfully merged and saved to {output_file}")
    print(f"Reading the parquet file: {output_file}")
    df = pd.read_parquet(output_file)
    df.shape
