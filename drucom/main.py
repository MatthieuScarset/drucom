# -*- coding: utf-8 -*-
"""
Drucom Package
====================
This package is designed to work with Drupal data.
It provides functionality to merge and process data from Drupal JSON files.
"""

def main():
    print(
        "💧 Welcome to the Drucom package 💧\n"
        "This package is designed to work with Drupal data.\n"
        "You can use it to merge and process data from Drupal JSON files.\n"
        "For more information, please refer to the documentation."
    )

def help():
    print(
        "# Example usage of DrupalDataFetcher\n"
        "from drucom import DrupalDataFetcher\n"
        "url = 'https://example.com/drupal-data.json'\n"
        "output_file = './data/drupal_data.json'\n"
        "fetcher = DrupalDataFetcher(url, output_file)\n"
        "fetcher.fetch_data()\n"
    )
    
    print(
        "# Example usage of DrupalDataMerger\n"
        "from drucom import DrupalDataMerger\n"
        "input_dir = './data/json'\n"
        "output_file = './data/merged_data.json'\n"
        "merger = DrupalDataMerger(input_dir, output_file)\n"
        "merger.merge_data()\n"
        "merger.process_data()\n"
    )

if __name__ == "__main__":
    main()
