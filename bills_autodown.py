import os
import pandas as pd
import re
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

import requests
from bs4 import BeautifulSoup

from datetime import datetime

print("download started...")
appendix_url = "https://ebill.dei.gr/"
provider_url =  "https://mydei.dei.gr/el/login/"
df = pd.read_excel("./data.xlsx")

# Set the desired download directory path
download_file_path = "C:/Users/admin/Documents/bills"

# Create the download directory if it doesn't exist
if not os.path.exists(download_file_path):
    os.makedirs(download_file_path)

# Set the Chrome options to specify the download directory
chrome_options = Options()
chrome_options.add_argument(f"--download.default_directory={download_file_path}")

# Launch Chrome WebDriver with the specified options
driver = webdriver.Chrome(options=chrome_options)

headers = {
    "User-Agent": "Chrome/51.0.2704.103",
}

raw_from_date = str(df['FROMDATE'][0])

logincodes = df['LOGINCODE'].to_dict()
addresses = df['ADDRESS'].to_dict()


def download_pdf(url, file_name, headers):

    # Send GET request
    response = requests.get(url, headers=headers)

    # Save the PDF
    if response.status_code == 200:
        with open(file_name, "wb") as f:
            f.write(response.content)
            print("\ndownload success!")
    else:
        print(response.status_code)
        

def workflow(raw_from_date, login_code, address):   #workflow(raw_from_date, ele_login_code, ele_address)
    
    # Create a WebDriver instance with the configured options
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(provider_url)
    print("downloding for LOGINCODE="+ str(login_code) +"... ")
    
    #date format process
    raw_from_date_object = datetime.strptime(raw_from_date, "%Y-%m-%d %H:%M:%S")
    date_format = "%d.%m.%Y"
    from_date = raw_from_date_object.strftime(r"%d.%m.%Y")
    
    # input field for contract account
    # driver.implicitly_wait(1)
    contract_account = driver.find_element(By.ID, 'communalLoginModel_ContractAccount')
    contract_account.send_keys(login_code)

    time.sleep(1)    
    
    accept_all_cookies = driver.find_element(By.ID, "onetrust-accept-btn-handler")
    if accept_all_cookies:
        accept_all_cookies.click()
        
    # View Button
    view_button = driver.find_element(By.XPATH, "//button[@class='b-login-shared__btn']")
    view_button.click()
    
    # 2nd Accept All Cookies button
    # driver.implicitly_wait(1)
    time.sleep(1)    

    second_accept_all_cookies = driver.find_element(By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll")
    if second_accept_all_cookies:
        second_accept_all_cookies.click()
        
    soup = BeautifulSoup(driver.page_source, "html.parser")
    elements = soup.find_all(attrs={'class': "BillItem"})
    i = 0

    for item in elements:

        item_title = item.find('a').get('title')
        item_original_url = appendix_url + item.find('a').get('href')
        # print("href", item_original_url)
        # xpath_expression = "//a[contains(@title, '{}')]".format(item_title)
        # pdf_link = driver.find_element(By.XPATH, xpath_expression)
        pattern = r"\d{2}.\d{2}.\d{4}"
        match = re.search(pattern, item_title)
        if match:
            raw_date = match.group()
            date_object = datetime.strptime(raw_date, r"%d.%m.%Y")
            date = date_object.strftime(r"%d.%m.%Y")

            if date_object >= raw_from_date_object:
                print("\nThe date of this file is '"+ str(date_object)+"'")
                print("The reference date is '"+ str(raw_from_date_object) +"'")
                print("The file name is '" + str(item_title) + "'")
                # response = requests.get(item_original_url, stream=True)

                # Set the desired file name for the downloaded PDF
                desired_file_name = "ΡΕΥΜΑ_"+ address +"_"+ str(i) +"_" + str(from_date) + ".pdf"
                print("The address for this LOGINCODE is '" + address + "'")
                i += 1
                download_pdf(item_original_url, desired_file_name, headers)
            
        else:
            print("No date found.")

    # driver.close()

    driver.implicitly_wait(1)
    
if __name__ == "__main__":

    for i in range(len(logincodes)):
        ele_logincode = logincodes[i]
        ele_address = addresses[i]
        workflow(raw_from_date, ele_logincode, ele_address)    

    driver.quit()
    print("download compledted!")
    # driver.close()