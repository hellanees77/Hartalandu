import csv
from datetime import datetime

def parse_date(date_str, current_format, target_format):
    try:
        date_obj = datetime.strptime(date_str, current_format)
        return date_obj.strftime(target_format)
    except ValueError:
        return None

def append_data_by_dates(file1,file2,output_filename,date_format1, date_format2):
    with open(file1, 'r') as file1_reader:
        csv_reader1 = csv.reader(file1_reader)
        data1 = list(csv_reader1)
        header1 = data1[0]
        print(f"Data1:{data1}")

    with open(file2, 'r') as file2_reader:
        csv_reader2 = csv.reader(file2_reader)
        header2 = next(csv_reader2)
        indices_to_append = [header2.index(header_name) for header_name in ["High", "Low", "Close"]]
        data2 = list(csv_reader2)
        print(f"Data2:{data2}")

        data2_dict = {parse_date(row2[header2.index("Date")],date_format2, date_format1): row2 for row2 in data2}

        for row1 in data1[1:]:
            date_key = parse_date(row1[header1.index("Date")],date_format1,date_format1)
            if date_key in data2_dict:
                row2 =data2_dict[date_key]
                for index in indices_to_append:
                    row1.append(row2[index])
            else:
                for _ in indices_to_append:
                    row1.append("")

        # # Append "High," "Low," and "Close" columns from file2 to file1
        # for row1, row2 in zip(data1[1:], data2):
        #     for index in indices_to_append:
        #         row1.append(row2[index])

    with open(output_filename, 'w', newline='') as output_file:
        csv_writer = csv.writer(output_file)
        csv_writer.writerows(data1)
        print(f"Output combined:{data1}")


# Example usage
file1 = 'sorted_output_file.csv'  # Replace with the actual file1 name
file2 = 'nepseindices.csv'  # Replace with the actual file2 name
output_filename = 'combined_output.csv'  # Replace with your desired output file name
date_format1 = "%m/%d/%Y"
date_format2 = "%Y-%m-%d"
append_data_by_dates(file1, file2, output_filename,date_format1, date_format2)