import csv

def append_next_day_data(input_file, output_file):
    # Read data from the CSV file
    with open(input_file, 'r') as input_file_reader:
        csv_reader = csv.reader(input_file_reader)
        header = next(csv_reader)
        data = list(csv_reader)
        print(data[0])

    # Find the indices of the relevant columns
    high_index = header.index("High")
    low_index = header.index("Low")
    close_index = header.index("Close")
    next_high_index = header.index("Next High")
    next_low_index = header.index("Next Low")
    next_close_index = header.index("Next Close")

    # Iterate through rows and append data to the just previous row
    for i in range(0, len(data)-1):
        # Check if columns are missing before performing assignments
        if len(data[i]) >= next_high_index:
            data[i].extend(data[i + 1][high_index:high_index + 1])
        if len(data[i]) >= next_low_index:
            data[i].extend(data[i + 1][low_index:low_index + 1])
        if len(data[i]) >= next_close_index:
            data[i].extend(data[i + 1][close_index:close_index + 1])

    # Write the modified data to a new CSV file
    with open(output_file, 'w', newline='') as output_file_writer:
        csv_writer = csv.writer(output_file_writer)

        # Write the header to the new CSV file
        csv_writer.writerow(header)

        # Write the modified data to the new CSV file
        csv_writer.writerows(data)

# Example usage
input_file = 'combined_output.csv'  # Replace with the actual input file name
output_file = 'progres_done.csv'  # Replace with your desired output file name

append_next_day_data(input_file, output_file)
