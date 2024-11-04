import sys
from bs4 import BeautifulSoup
import pandas as pd
import re

def extract_data(html_file_path):
    # Read the HTML file
    with open(html_file_path, 'r') as file:
        html_content = file.read()

    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the table containing the desired information
    results_table = soup.find('div', class_='column-02').find('table')

    # Initialize data dictionary with empty values
    data = {'Subject_ID': None, 'Lesion_volume_ml_LST': None, 'Number_of_lesions_LST': None}

    # Extract Subject ID from the Lesion map cell
    lesion_map_cell = soup.find('td', string='Lesion map').find_next('td')
    subject_id_match = re.search(r'sub-\d+_ses-\d+', lesion_map_cell.string)
    if subject_id_match:
        subject_id = subject_id_match.group()
    else:
        subject_id = None

    # Extract data for 'Lesion volume' and 'Number of lesions' if available
    for row in results_table.find_all('tr'):
        cells = row.find_all('td')
        if len(cells) == 2:
            key = cells[0].text.strip()
            if 'Lesion volume' in key:
                data['Lesion_volume_ml_LST'] = cells[1].text.strip().split()[0]
            elif 'Number of lesions' in key:
                data['Number_of_lesions_LST'] = cells[1].text.strip().split()[0]

    # Add Subject ID to the data dictionary
    data['Subject_ID'] = subject_id

    # Rearrange dictionary so that Subject_ID is the first key
    data = {'Subject_ID': data.pop('Subject_ID'), **data}

    # Create a DataFrame from the extracted data
    df = pd.DataFrame([data])

    # Save the DataFrame to a CSV file
    output_csv_path = html_file_path.replace('.html', '.csv')
    df.to_csv(output_csv_path, index=False)

    print("CSV file has been created successfully.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    extract_data(input_file)


