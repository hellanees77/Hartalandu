#!/usr/bin/env python
# coding: utf-8
from decimal import Decimal

# In[19]:
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
#import datetime
#from datetime import timedelta
import selenium.webdriver.common.keys
import pandas as pd
from bs4 import BeautifulSoup


# In[20]:


# Install the ChromeDriver executable and start a Chrome browser using Selenium
driver = webdriver.Chrome()


# In[21]:


# Navigate to the webpage
driver.get('https://merolagani.com/Floorsheet.aspx')


# In[22]:


file_name = "progress.csv"

# Check if the file exists
if not os.path.isfile(file_name):
    # If the file doesn't exist, create a new CSV file with headers
    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write headers to the CSV file
    print(f"The file '{file_name}' has been created.")
else:
    print(f"The file '{file_name}' already exists.")


# In[29]:


def extract_page_data(date, page,total_pages,target_row=0 ):



     # Let's use BeautifulSoup to parse the page source
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Extract the data you
    data = []
    rows = soup.select('.table-bordered tbody tr')

    # Find the index of the row with the target value
    if target_row != 0:
        target_index = next((index for index, row in enumerate(rows) if row.find_all('td')[0].get_text(strip=True) == str(target_row)), None)
        if target_index is not None:
            # Start enumeration from the next row
            rows = rows[target_index + 1:]

    # Iterate through rows starting from the specified target_row or the next row
    for index, row in enumerate(rows, start=target_row):
        columns = row.find_all('td')
        row_data = [column.get_text(strip=True) for column in columns] + [date]
        data.append(row_data)
        insertdata(date,row_data,22,22)
        print(f"Adding data for row {index + 1}")

    return data


# Calculate the specific date (e.g., start from one week ago)
start_date_str = '01/19/2022'
start_date = datetime.strptime(start_date_str , '%m/%d/%Y')
date_array = []

# Get the current date
end_date = datetime.now()

# Iterate through the date range
while start_date <= end_date:
    # Format the current date as MM/DD/YYYY and print
    current_date_str = start_date.strftime('%m/%d/%Y')
#     date_input.clear()
#     date_input.send.keys(current_date_str)
    date_array.append(  current_date_str )

    # Move to the next date
    start_date += timedelta(days=1)
print(date_array)


# In[32]:


# Define a function to click the next page button
def click_next_page():
    try:
        # Find the next page element and click it
        next_page = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//a[text()="Next"]'))
        )
        next_page.click()
        return True
    except Exception as e:
        print(f"Error clicking next page: {e}")
        return False


# In[33]:


csv_data = []
all_data = []

def connect_to_database():
    try:
        # Connect to MySQL
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="hartalandu_db"
        )

        print("Connected to the database!")
        return connection

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None


def execute_query(connection, query, values=None):
    try:
        # Create a cursor object
        cursor = connection.cursor()

        # Execute the query with optional values
        if values is None:
            cursor.execute(query)
        else:
            cursor.execute(query, values)

        # Commit the changes
        connection.commit()

        print("Query executed successfully!")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        # Close the cursor (but keep the connection open for reuse)
        if cursor:
            cursor.close()


def scrape_data_for_date_range(date_array, page_number=0,target_row=0):

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    for date_str in date_array:
        try:
            print(f"Getting data from {date_str}")
            print(f"getting data from {date_str}")
            # Find the input element by its ID
            input_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'ctl00_ContentPlaceHolder1_txtFloorsheetDateFilter')))
            input_element.clear()
            input_element.send_keys(date_str)

            # Print the extracted value
            # print("Date Value:", date_value)
            # Press Enter to confirm the new date (optional, depends on the website's behavior)
            input_element.send_keys(Keys.ENTER)

            # Wait for the element to be clickable (you might need to adjust the timeout)
            search_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'ctl00_ContentPlaceHolder1_lbtnSearchFloorsheet')))
            # Click the "Search" button
            search_button.click()
            # Extract the total pages value from the content
            # total_pages_text = span_element.get_text(strip=True)
            # start_index = total_pages_text.find("[Total pages:") + len("[Total pages:")
            # end_index = total_pages_text.find("]", start_index)

            # total_pages_value = total_pages_text[start_index:end_index]
            # num_pages_to_scrape = int(total_pages_value)

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
            # Extract the text value from the span element
            date_value = date_span.text


            # Loop through pages
            for page_num in range(num_pages_to_scrape):
                print(f"Scraping data from page {page_num + 1}")

                # Extract data from the current page
                current_data  = extract_page_data(date_str, page_num, num_pages_to_scrape, target_row)

                all_data.extend(current_data)

                # Click the next page
                if not click_next_page():
                    print("No more pages to scrape.")
                    break

        except Exception as e:
            print(f"Error: printing the page {page_num + 1}, date_str {date_str}: {repr(e)}")


def insertdata(date, data, page_number, total_entries):
    # Convert the date string to the appropriate format (YYYY-MM-DD)
     data[8]= datetime.strptime(data[8], '%m/%d/%Y').strftime('%Y-%m-%d')
     #print(f"this is type Rate:{type(data[6])} amount:{type(data[7])}")
     #data[6] = '{:,.2f}'.format(data[6]) # Format as a float with 2 decimal places and commas


     data[6] = float(data[6].replace(",", ""))

      #data[7] = '{:,.2f}'.format(data[7])  # Format as a float with 2 decimal places and commas


     data[7] = Decimal(data[7].replace(",", ""))


     data[5]= int(data[5].replace(",", ""))
     # Connect to the database
     db_connection = connect_to_database()

     if db_connection:
        # Example query with placeholders
        insert_query = "INSERT INTO Hartalandu_table5 (SerialNumber, TransactionNumber, Symbol, Buyer, Seller, Quantity, Rate, Amount, Date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"

        # Execute the query with the data list (excluding the last element and adding the formatted date)
        execute_query(db_connection, insert_query, data)

        # Close the database connection after query execution
        db_connection.close()


# if success ok
# check first or last
#  append to csv at end with loading status
# if last replace csv with completed status
# if duplicate unique key error
# check the query again get the maximum value of entries and try to navigate to the certain page and insert the data after that
       #if (total_entries!= maximum_entries_from_db):
            #page = maximum_entries_from_db//500
            # rows = maximum_entries_from_db%500
            #scrape_data_for_date_range(date_array, page_number=page,target_row=data[0])
        #else:
            #scrape_data_for_date_range(date_array.remove(date))


# if last page last entry than update csv to done
# if first page entry than update csc to started
#             # Read the existing CSV file into a list of lists
#     with open(file, 'r', newline='') as file:
#         data = list(csv.reader(file))

#     # Check if the last row has the target value in the first column
#     if data and data[-1][0] == date:
#         # Replace the last row with the new row
#         data[-1] = new_row
#     else:
#         # If the target value is not found in the last row, append a new row
#         data.append(new_row)

#     # Write the modified data back to the CSV file
#     with open(file, 'w', newline='') as file:
#         csv.writer(file).writerows(data)
#         print(data)
#         writer.writerow(date,data[0],"pending")



# In[34]:


scrape_data_for_date_range(date_array)


# In[17]:



# In[18]:


# Close the browser
driver.quit()


# In[ ]:


# Print the collected data
print("Collected Data:")
for row in all_data:
    print(row)




