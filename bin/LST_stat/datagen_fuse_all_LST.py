import pandas as pd
import argparse

def merge_dataframes(file1, file2, output_file):
    # Load the first CSV file
    df1 = pd.read_csv(file1)

    # Load the second CSV file
    df2 = pd.read_csv(file2)

    # Merge the two dataframes on 'Subject_ID'
    merged_df = pd.merge(df2, df1, on='Subject_ID', how='left')

    # Define the columns to be moved
    columns_to_move = ['Lesion_volume_ml_LST', 'Number_of_lesions_LST']

    # Insert the columns at the desired positions
    for col in columns_to_move:
        merged_df.insert(2, col, merged_df.pop(col))

    # Save the merged DataFrame to a CSV file
    merged_df.to_csv(output_file, index=False)

    print(f"Merged data saved successfully as {output_file}.")

def main():
    parser = argparse.ArgumentParser(description='Merge two CSV files on Subject_ID and save the merged file.')
    parser.add_argument('file1', type=str, help='Path to the first CSV file')
    parser.add_argument('file2', type=str, help='Path to the second CSV file')
    parser.add_argument('output_file', type=str, help='Path to save the merged CSV file')

    args = parser.parse_args()

    merge_dataframes(args.file1, args.file2, args.output_file)

if __name__ == "__main__":
    main()


