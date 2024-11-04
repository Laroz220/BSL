import pandas as pd
import argparse

def main():
    # Set up argparse to handle command-line arguments
    parser = argparse.ArgumentParser(description='Process and modify CSV files.')
    parser.add_argument('input_file', type=str, help='Path to the input CSV file')
    parser.add_argument('output_file', type=str, help='Path to the output CSV file')
    args = parser.parse_args()

    # Read the CSV file into a DataFrame
    df = pd.read_csv(args.input_file)

    # Remove everything after "sub-0234_ses-01" part of the 'Subject_ID' column using regex
    df['Subject_ID'] = df['Subject_ID'].str.replace(r'(sub-\d+_ses-\d+).*', r'\1', regex=True)

    # Save the modified DataFrame to a CSV file
    df.to_csv(args.output_file, index=False)

    # Display the modified DataFrame
    print("DataFrame after first modification:")
    print(df)

if __name__ == "__main__":
    main()
