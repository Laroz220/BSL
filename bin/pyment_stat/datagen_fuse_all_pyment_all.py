import pandas as pd
import argparse

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Merge and process CSV files.')
    parser.add_argument('file1', type=str, help='Path to the first CSV file')
    parser.add_argument('file2', type=str, help='Path to the second CSV file')
    parser.add_argument('output', type=str, help='Path to the output CSV file')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Load the first CSV file
    df1 = pd.read_csv(args.file1)
    
    # Load the second CSV file
    df2 = pd.read_csv(args.file2)
    
    # Merge the two dataframes on 'Subject_ID'
    merged_df = pd.merge(df2, df1, on='Subject_ID', how='left')
    
    # Define the variables to be moved
    variables_to_move = ['prediction']
    
    # Insert the columns at the desired positions (start from index 2)
    for i, var in enumerate(variables_to_move, start=2):
        if var in merged_df.columns:
            merged_df.insert(2, var, merged_df.pop(var))
    
    # Save the merged DataFrame to the specified output CSV file
    merged_df.to_csv(args.output, index=False)
    
    print(f"Merged data saved successfully as {args.output}.")

if __name__ == "__main__":
    main()
