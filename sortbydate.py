import csv
from datetime import datetime



def sort_csv_by_dates(input_filename, output_filename, header_names):
    # Read data from CSV file
    with open(input_filename, 'r') as file:
        csv_reader = csv.reader(file)
        header = next(csv_reader)
        rows = [row for row in csv_reader]

    # Sort the rows by date (assuming the date is in the first column, index 0)
    sorted_rows = sorted(rows, key=lambda x: datetime.strptime(x[0], "%m/%d/%Y"))

    # Write sorted data to a new CSV file
    with open(output_filename, 'w', newline= '' ) as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(header_names)
        csv_writer.writerows(sorted_rows)

# Example usage
input_filename = 'progress.csv'  # Replace with your actual input file name
output_filename = 'sorted_output_file.csv'  # Replace with your desired output file name
header_names = ['Date', 'Total Records', 'Status', 'Verification', 'High', 'Low', 'Close','Next High', 'Next Low', 'Next Close']
selected_rows = []
sort_csv_by_dates(input_filename, output_filename,header_names)