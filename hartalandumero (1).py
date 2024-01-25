#!/usr/bin/env python

from decimal import Decimal

import mysql.connector
import os
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from datetime import datetime, timedelta
import selenium.webdriver.common.keys
import pandas as pd
from bs4 import BeautifulSoup

import csv
from datetime import datetime
START_DATE = '01/19/2022'
END_DATE = "01/22/2022"

# Install the ChromeDriver executable and start a Chrome browser using Selenium
driver = webdriver.Chrome()

# Navigate to the webpage
driver.get('https://merolagani.com/Floorsheet.aspx')

file_name = "progress.csv"


class DuplicateDataException(Exception):
    def __init__(self, date_array=None, page_number=None, rows_value=None):
        self.date_array = date_array
        self.page_number = page_number
        self.rows_value = rows_value
        super().__init__()

def update_progress_csv(date, number, status):
    # Input validation: Check if the date is in the correct format
    try:
        datetime.strptime(date, "%m/%d/%Y")
    except ValueError:
        print("Invalid date format. Please use MM/DD/YYYY.")
        return

    # Validate the status
    if status not in ["started", "completed"]:
        print("Invalid status. Please provide 'started' or 'completed'.")
        return

    # Read the existing CSV file if it exists; otherwise, create a new file
    try:
        with open('progress.csv', 'r', newline='') as file:
            reader = csv.reader(file)
            rows = list(reader)

        # Check if a row with the given date exists
        existing_row_index = None
        for i, row in enumerate(rows):
            if row and row[0] == date:
                existing_row_index = i
                break

        # If a row with the given date exists, update it; otherwise, append a new row
        if existing_row_index is not None:
            rows[existing_row_index] = [date, str(number), status]
        else:
            rows.append([date, str(number), status])

        # Write the updated/added rows back to the CSV file
        with open('progress.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)

        print("CSV file updated successfully.")

    except FileNotFoundError:
        # If the file does not exist, create a new one and write the header and data
        with open('progress.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([date, str(number), status])

        print("CSV file created successfully.")


def extract_page_data(date, current_page_number, total_entries,total_pages ,target_value=0,):
    # Let's use BeautifulSoup to parse the page source
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Extract the data
    data = []
    rows = soup.select('.table-bordered tbody tr')
    # Find the index of the row with the target value

    target_index = None
    if target_value != 0:
        target_index = next((index for index, row in enumerate(rows) if
                             row.select_one('.text-center').get_text(strip=True) == str(target_value)), None)
        if target_index is not None:
            print(f"Target row with value {target_value} found at index {target_index}.")
            rows = rows[target_index + 1:]

    # Iterate through rows starting from the specified target_row or the next row
    for index, row in enumerate(rows, start=target_index + 1 if target_index is not None else 1):
        columns = row.find_all('td')
        row_data = [column.get_text(strip=True) for column in columns] + [date]
        print("trying to insert", row_data)
        insert_data(date, row_data, current_page_number, total_entries,total_pages)




start_date = datetime.strptime(START_DATE, '%m/%d/%Y')
end_date = datetime.strptime(END_DATE, '%m/%d/%Y')

date_array = []

# Get the current date


# Iterate through the date range
while start_date <= end_date:
    # Format the current date as MM/DD/YYYY and print
    current_date_str = start_date.strftime('%m/%d/%Y')
    #     date_input.clear()
    #     date_input.send.keys(current_date_str)
    date_array.append(current_date_str)

    # Move to the next date
    start_date += timedelta(days=1)
print(date_array)




def click_next_page(pages_num, number_of_pages):
    try:
        # Find the next page element and click it
        next_page = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//a[text()="Next"]'))
        )
        next_page.click()
        return True
    except Exception as e:
        print(f"Error clicking next page: {e}")
        if pages_num + 1 != number_of_pages:
            navigate_to_page(pages_num + 1)
            return True
        return False

def connect_to_database():
    try:
        # Connect to MySQL
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="hartalpittal"
        )

        print("Connected to the database!")
        return connection

    except mysql.connector.Error as err:
        print(f"Error connections: {err}")
        return None

def get_total_count(connection, date):
    cursor = connection.cursor()
    query = f"SELECT COUNT(*) AS total_entries FROM Hartalandu_table5 WHERE Date = '{date}'"
    print(query)
    try:
        cursor.execute(query)
        result = cursor.fetchone()
        max_value = result[0]
        print(f"count value is :{max_value}")
        return max_value

    except Exception as e:
        print(f"count value Exception: {e}")
        return 0;


def get_max_value(connection, date):

    cursor = connection.cursor()
    query = f"SELECT MAX(SerialNumber) AS MaxSerialNumber FROM Hartalandu_table5 WHERE Date = '{date}'"
    print(query)
    try:
        cursor.execute(query)
        result = cursor.fetchone()
        max_value = result[0]
        print(f"max valeu is :{max_value}")
        return max_value

    except Exception as e:
        print(f"Max value Exception: {e}")
        return 0;



def execute_query(connection, query, values=None):
    try:
        cursor = connection.cursor()

        if values is None:
            cursor.execute(query)
        else:
            cursor.execute(query, values)
            if cursor.description is not None:
                result = cursor.fetchone()
                if result:
                    print("Result:", result)
        connection.commit()

        print("Query executed successfully!")

    except mysql.connector.Error as err:
        print(f"Error in insertion: {err.msg}")
        if err.msg.__contains__("Duplicate entry"):
            raise DuplicateDataException

    finally:
        if cursor:
            cursor.close()


def scrape_data_for_date_range(date_array_toscrap, page_number=0, target_value=0):

    for date_str in date_array_toscrap:
        try:
            print(f"Getting data from {date_str}")
            print(f"getting data from {date_str}")
            # Find the input element by its ID
            input_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'ctl00_ContentPlaceHolder1_txtFloorsheetDateFilter')))
            input_element.clear()
            input_element.send_keys(date_str)


            input_element.send_keys(Keys.ENTER)

            search_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'ctl00_ContentPlaceHolder1_lbtnSearchFloorsheet')))
            search_button.click()
            if not  has_data_onDate(date_str,driver.page_source):
                date_array.remove(date_str)

            span_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'ctl00_ContentPlaceHolder1_PagerControl1_litRecords'))
            )

            # Extract the total pages value from the content
            total_pages_text = span_element.text
            start_index = total_pages_text.find("[Total pages:") + len("[Total pages:")
            end_index = total_pages_text.find("]", start_index)

            total_pages_value = total_pages_text[start_index:end_index]
            num_pages_to_scrape = int(total_pages_value)
            print(f"Total pages: {num_pages_to_scrape} Check This!!")

            # Extract the text content of the span
            records_text = span_element.text

            # Extract the value of records using string manipulation
            start_index = records_text.find("of ") + len("of ")
            end_index = records_text.find(" records", start_index)

            records_value = records_text[start_index:end_index]
            print(f"Total Records: {records_value} Check This!!!")
            date_span = driver.find_element(By.ID, 'ctl00_ContentPlaceHolder1_marketDate')
            date_value = date_span.text

            page_num = page_number
            if (page_num != 0):
                navigate_to_page(page_num + 1)
            for page in range(page_num, num_pages_to_scrape):
                print(f"Scraping data from page {page_num + 1}")
                extract_page_data(date_str, page, records_value, num_pages_to_scrape, target_value)


                # Click the next page
                if not click_next_page(page, num_pages_to_scrape):
                    print("No more pages to scrape.")
                    break
        except DuplicateDataException as duplicate:
            print("Man its duplicate entries")
            print(f"came at this place {duplicate.page_number}, {duplicate.rows_value}")
            scrape_data_for_date_range(date_array, duplicate.page_number, duplicate.rows_value)
        except Exception as e:
            print(f"Error: printing the page , date_str {date_str}: {e}")


def navigate_to_page(desired_page):
    # Execute the JavaScript function to change the page index to the desired page
    script = f"changePageIndex('{desired_page}', 'ctl00_ContentPlaceHolder1_PagerControl2_hdnCurrentPage', 'ctl00_ContentPlaceHolder1_PagerControl2_btnPaging')"
    driver.execute_script(script)

    # Wait for the page to load
    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element((By.CLASS_NAME, 'current_page'), str(desired_page))
    )


def has_data_onDate(expected_date,page_source):
    soup = BeautifulSoup(page_source, 'html.parser')
    input_element = soup.find('input', {'id': 'ctl00_ContentPlaceHolder1_txtFloorsheetDateFilter'})
    selected_date = input_element.get('value')
    if selected_date == expected_date:
        table = soup.find('table')
        if table:
            return True
        else:
            return False

    else:
        return False



def insert_data(date, data, page_number, total_entries,total_pages):
    preformatted_date = data[8]
    # Convert the date string to the appropriate format (YYYY-MM-DD)
    data[8] = datetime.strptime(data[8], '%m/%d/%Y').strftime('%Y-%m-%d')

    data[6] = float(data[6].replace(",", ""))

    data[7] = Decimal(data[7].replace(",", ""))

    data[5] = int(data[5].replace(",", ""))
    # Connect to the database
    db_connection = connect_to_database()

    if db_connection:
        # Example query with placeholders
        insert_query = "INSERT INTO Hartalandu_table5(SerialNumber, TransactionNumber, Symbol, Buyer, Seller, Quantity, Rate, Amount, Date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"

        try:
            execute_query(db_connection, insert_query, data)
            if (data[0] == 1):
                update_progress_csv(date, 1,"started")
            elif data[0] == total_entries:
                date_array.remove(preformatted_date)
                error_value_per_page = 5
                total_counts =  get_total_count()
                differences = int(total_entries) - total_counts
                if(differences<=error_value_per_page*total_pages):
                    update_progress_csv(date,total_counts,"completed")
                else:
                    update_progress_csv(date,total_counts,"incomplete")

        except DuplicateDataException as duplicate:
            max_values = get_max_value(db_connection, data[8])
            print(f"max_values{max_values}")
            if max_values != int(total_entries):
                page_number = max_values // 500
                rows_value = max_values
                print(f"came at not case page : {page_number} rows value :{rows_value}")
                duplicate = DuplicateDataException(date_array, page_number, rows_value)
                raise duplicate
            else:
                error_value_per_page = 5
                total_counts = get_total_count(db_connection,data[8])
                differences = int(total_entries) - total_counts
                if differences <= error_value_per_page * total_pages:
                    update_progress_csv(date, total_counts, "completed")
                else:
                    update_progress_csv(date, total_counts, "incomplete")
                date_array.remove(preformatted_date)
                duplicate = DuplicateDataException(date_array, 0, 0)
                raise duplicate

        db_connection.close()



scrape_data_for_date_range(date_array)

driver.quit()
