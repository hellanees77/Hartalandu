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
import time
import sys


def main():
    import csv

    def get_unverified_rows(filename):
        unverified_rows = []

        with open(filename, 'r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip the header if present

            for row in csv_reader:
                date, value, status, verification = row
                if verification.lower() == 'unverified':
                    unverified_rows.append(row)

        return unverified_rows

    # Install the ChromeDriver executable and start a Chrome browser using Selenium
    driver = webdriver.Chrome()

    # Navigate to the webpage
    driver.get('https://merolagani.com/Floorsheet.aspx')
    filename = 'progress.csv'
    unverified_rows = get_unverified_rows(filename)
    for row in unverified_rows:
        # Find the input element by its ID
        input_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'ctl00_ContentPlaceHolder1_txtFloorsheetDateFilter')))
        input_element.clear()
        input_element.send_keys(row[0])

        input_element.send_keys(Keys.ENTER)

        search_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.ID, 'ctl00_ContentPlaceHolder1_lbtnSearchFloorsheet')))
        search_button.click()
        if not has_data_onDate(date_str, driver.page_source):
            continue
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
        if int(records_value) - int(row[1]) > 480:
            update_row(filename, row, "failed")

        else:
            update_row(filename, row, "passed")

    def update_row(filenames, row_value, status):
        updated_rows = []
        with open(filenames, 'r') as file:
            csv_reader = csv.reader(file)
            header = next(csv_reader)  # Save the header
            updated_rows.append(header)
            for row_value in csv_reader:
                if row_value == target_row:
                    # Update the verification status
                    row_value[3] = status
                    updated_rows.append(row_value)

            with open(filenames, 'w', newline='') as file:
                csv_writer = csv.writer(file)
                csv_writer.writerows(updated_rows)

    driver.quit()


if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            # Optionally, you can log the error to a file or another service
            time.sleep(5)  # Add a delay before restarting
            print(f"Restarting the program... {e}")
            continue
        except KeyboardInterrupt:
            print("Program terminated by user.")
            sys.exit()

# done
