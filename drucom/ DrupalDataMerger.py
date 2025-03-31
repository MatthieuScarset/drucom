import os
import pandas as pd


class DrupalDataMerger:
    """
    A class to handle merging and processing of Drupal JSON data files.
    """

    def __init__(self, input_dir, output_file):
        """
        Initialize the DrupalDataMerger with input and output paths.

        :param input_dir: Directory containing the input JSON files.
        :param output_file: Path to the output merged JSON file.
        """
        self.input_dir = input_dir
        self.output_file = output_file

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

    def main(dataset_name: str):
        """
        Main function to merge Drupal pages.
        """
        # Make base_dir relative to the script directory
        data_base_dir = os.path.join(os.path.dirname(__file__), "../data")

        # Check if the dataset name is valid
        allowed_datasets = []
        for folder in os.listdir(f"{data_base_dir}/json"):
            if os.path.isdir(os.path.join(f"{data_base_dir}/json", folder)):
                allowed_datasets.append(folder)
        allowed_datasets.sort()
        if not dataset_name:
            raise ValueError(
                "Please provide a dataset name using --name argument.")
        if dataset_name not in allowed_datasets:
            raise ValueError(
                f"Invalid dataset name. Allowed names are: {allowed_datasets}")

        # Check if the dataset folder exists and is not empty.
        dataset_folder = f"{data_base_dir}/json/{dataset_name}"
        if not os.path.exists(dataset_folder):
            raise FileNotFoundError(
                f"The dataset folder {dataset_folder} does not exist.")
        if not os.listdir(dataset_folder):
            raise FileNotFoundError(
                f"The dataset folder {dataset_folder} is empty.")

        # Warning for large datasets.
        if dataset_name == "user":
            print(f"⚠️ Warning: merging 'user' is a long process (~8.5 minutes)")

        # Merge fetched pages into one DataFrame.
        print(f"Building {dataset_name} from folder: {dataset_folder}")
        output_file = f"{data_base_dir}/{dataset_name}.parquet"
        merged_df = merge_drupal_pages(f"{data_base_dir}/json/{dataset_name}")
        merged_df.to_parquet(output_file, index=False)
        print(f"Data successfully merged and saved to {output_file}")
        print(f"Reading the parquet file...")
        df = pd.read_parquet(output_file)
        print(f"Shape: {df.shape}")
        print(f"Columns: {df.columns.tolist()}")
