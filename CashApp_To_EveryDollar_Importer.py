import os
import csv
import json
import time
import shutil
import dateutil.tz
from datetime import datetime
from dateutil.parser import parse

# SELENIUM
from selenium import webdriver
import undetected_chromedriver  #as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


# VARIABLES ############################################################################################################
input_file_from_cashapp = "cash_app_report.csv"
transactions_file = 'import_spreadsheet_of_transactions.csv'
site_link = 'https://www.everydollar.com/app/budget'

headless = False
user_agent = None
selenium_temp_dir = os.path.join(os.getcwd(), 'temp')
proxy = None

# Functions ############################################################################################################
def show_logo():
    print('''
   ______           __       ___                   __           ______                      ____        ____          
  / ____/___ ______/ /_     /   |  ____  ____     / /_____     / ____/   _____  _______  __/ __ \____  / / /___ ______
 / /   / __ `/ ___/ __ \   / /| | / __ \/ __ \   / __/ __ \   / __/ | | / / _ \/ ___/ / / / / / / __ \/ / / __ `/ ___/
/ /___/ /_/ (__  ) / / /  / ___ |/ /_/ / /_/ /  / /_/ /_/ /  / /___ | |/ /  __/ /  / /_/ / /_/ / /_/ / / / /_/ / /    
\____/\__,_/____/_/ /_/  /_/  |_/ .___/ .___/   \__/\____/  /_____/_|___/\___/_/   \__, /_____/\____/_/_/\__,_/_/     
            ___________________/_/___/_/______________________   /  _/___ ___  ___/____/_  _____/ /____  _____        
           /____/____/____/____/____/____/____/____/____/____/   / // __ `__ \/ __ \/ __ \/ ___/ __/ _ \/ ___/        
          /____/____/____/____/____/____/____/____/____/____/  _/ // / / / / / /_/ / /_/ / /  / /_/  __/ /            
                                                              /___/_/ /_/ /_/ .___/\____/_/   \__/\___/_/             
                                                                           /_/                                        
     ===============================================================================================
                 A tool for automatically importing Cash App transactions to EveryDollar
    ''')

def write_to_csv(file_path, list):
    # Wrtie a list to a one-column csv file
    with open(file_path, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for row in list:
            writer.writerow([row])
    #print(f'Saved to {file_path}')


def cashapp_export_to_list_of_dict(input_file, start_date, end_date):
    # Timezone information dictionary for dateutil
    tzinfos = {
        "EDT": dateutil.tz.gettz('America/New_York'),
        "EST": dateutil.tz.gettz('America/New_York'),
        "CDT": dateutil.tz.gettz('America/Chicago'),
        "CST": dateutil.tz.gettz('America/Chicago'),
        "MDT": dateutil.tz.gettz('America/Denver'),
        "MST": dateutil.tz.gettz('America/Denver'),
        "PDT": dateutil.tz.gettz('America/Los_Angeles'),
        "PST": dateutil.tz.gettz('America/Los_Angeles'),
        "AKDT": dateutil.tz.gettz('America/Anchorage'),
        "AKST": dateutil.tz.gettz('America/Anchorage'),
        "HDT": dateutil.tz.gettz('Pacific/Honolulu'),
        "HST": dateutil.tz.gettz('Pacific/Honolulu'),
        "ADT": dateutil.tz.gettz('America/Puerto_Rico'),
        "AST": dateutil.tz.gettz('America/Puerto_Rico'),
        "SST": dateutil.tz.gettz('Pacific/Pago_Pago'),
        "ChST": dateutil.tz.gettz('Pacific/Guam')
    }

    timezone = dateutil.tz.gettz('America/New_York')

    start_date = parse(start_date, tzinfos=tzinfos).astimezone(timezone)
    end_date = parse(end_date, tzinfos=tzinfos).astimezone(timezone)

    results = []

    with open(input_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        for row in reader:
            date_str = row.get("Date")
            if not date_str:
                continue
            row_date = parse(date_str, tzinfos=tzinfos).astimezone(timezone)

            if start_date <= row_date <= end_date:
                direction = "In" if "PAYMENT DEPOSITED" in row.get("Status", "") or "CARD REFUNDED" in row.get("Status", "") else "Out"
                amount = row.get("Amount", "").replace("$", "").replace("-", "")
                note = f"{row.get('Status', '')} {row.get('Name of sender/receiver', '')} with note {row.get('Notes', '')}".strip()
                merchant = row.get('Notes', '')

                tx = {
                    "id": row.get("Transaction ID", ""),
                    "direction": direction,
                    "amount": amount,
                    "date": row_date.strftime("%m/%d/%y"),
                    "note": note,
                    "merchant": merchant
                }

                results.append(tx)

    return results


def set_chrome_options(user_agent=None, proxy=None):
    options = webdriver.ChromeOptions()
    # disable Chrome popups
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-save-password-bubble")
    options.add_argument(f"--user-data-dir={selenium_temp_dir}")  # Set custom user data directory
    if headless:
        options.add_argument("--headless=new")
    if user_agent:
        options.add_argument(f'user-agent={user_agent}')
    if proxy:
        options.add_argument(f'proxy-server={proxy}')
    return options


def setup_driver(user_agent=None, proxy=None):
    options = set_chrome_options(user_agent, proxy)
    driver = undetected_chromedriver.Chrome(options=options)
    driver.set_page_load_timeout(60)  # wait 60 second before error
    return driver


def quit_driver(driver):
    try:
        if driver is not None:
            driver.quit()
            shutil.rmtree(selenium_temp_dir, ignore_errors=True)  # Delete the temporary directory
    except:
        pass


def import_transactions(driver, auto=False):
    # The auto argument lets you set if you want to review each transaction before adding or not

    add_transaction_link = 'https://www.everydollar.com/app/budget/transaction/new'

    # XPaths
    expense_selection_xpath = '//input[@name="expense"]'
    income_selection_xpath = '//input[@name="income"]'
    amount_xpath = '//input[@name="amount"]'
    date_xpath = '//input[@name="date"]'
    merchant_xpath = '//input[@name="merchant"]'
    more_xpath = '//button[contains(text(), "More Options")]'
    id_xpath = '//input[@name="checkNumber"]'
    note_xpath = '//textarea[@name="note"]'
    submit_button_xpath = '//button[@type="submit"]'

    with open(file=transactions_file, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            data = json.loads(row[0])
            print(f'Importing Transaction: {data}')

            driver.get(add_transaction_link)

            # Wait until the page loads, or for 2min
            wait = WebDriverWait(driver, timeout=120)
            wait.until(EC.presence_of_element_located((By.XPATH, income_selection_xpath)))

            id = data["id"]
            direction = data["direction"]
            amount = data["amount"]
            date = data["date"]
            merchant = data["merchant"]
            note = data["note"]

            # Income or expense
            if direction == 'In':
                element = driver.find_element(By.XPATH, income_selection_xpath)
                ActionChains(driver).move_to_element(element).click().perform()
            else:
                element = driver.find_element(By.XPATH, expense_selection_xpath)
                ActionChains(driver).move_to_element(element).click().perform()

            # Amount
            element = driver.find_element(By.XPATH, amount_xpath)
            element.clear()
            element.send_keys(amount)

            # Date
            element = driver.find_element(By.XPATH, date_xpath)
            element.clear()
            element.send_keys(date)

            # Merchant
            driver.find_element(By.XPATH, merchant_xpath).send_keys(merchant)

            # Select More Options
            driver.find_element(By.XPATH, more_xpath).click()
            wait.until(EC.presence_of_element_located((By.XPATH, id_xpath)))  # (wait until it opens)

            # ID
            driver.find_element(By.XPATH, id_xpath).send_keys(id)

            # Note
            driver.find_element(By.XPATH, note_xpath).send_keys(note)

            input('To submit this transaction, press ENTER.') if not auto else None
            print('Submitting...')

            # Submit
            driver.find_element(By.XPATH, submit_button_xpath).click()
            time.sleep(5) if auto else time.sleep(3)


# PROGRAM STARTS #######################################################################################################
show_logo()

print('What would you like to do?\n')
print('( 1. ) - CREATE import spreadsheet of transactions from Cash App.')
print('( 2. ) - Manually review & add transactions to EveryDollar FROM import spreadsheet.')
print('( 3. ) - Automatically add transactions to EveryDollar FROM import spreadsheet.')
print('\n')

user_entered = ''
while True:
    try:
        user_entered = int(input('Type either 1, 2, or 3 and then press enter: '))
        if user_entered > 0 or user_entered < 4:
            break
    except:
        pass
    print('Invalid entry. Enter either 1, 2, or 3.')

print('\n')
if user_entered == 1:
    os.system('cls')
    print("Tip: Don't forget to delete the spreadsheets from the last time you ran this software.\n")
    print('Step 1. Sign into Cash App and click the download button to download a spreadsheet of all your transactions.\n')
    print(f'Step 2. Put this spreadsheet called "{input_file_from_cashapp}" in the same folder that this program was run from.\n')
    input('Step 3: After completing steps 1 and 2, press enter. You will be prompted to enter a start and end date.\n\n\n')
    start_date = input('Enter the START DATE in this format (year-month-day), for example: 2023-8-1\n').strip()
    end_date = input('Enter the END DATE in this format (year-month-day), for example: 2023-8-31\n').strip()
    print('Extracting transactions...')
    try:
        cleaned_data = cashapp_export_to_list_of_dict(input_file=input_file_from_cashapp, start_date=start_date, end_date=end_date)
        print(cleaned_data)
        for transaction in cleaned_data:
            write_to_csv(file_path=transactions_file, list=[json.dumps(transaction)])
        print('\n [ Import Spreadsheet Created! ] ')
        print('Now re-launch the program and run either 2 (for manual review), or 3 (for automatic import)')
        input('')
    except:
        os.system('cls')
        print('Input file from Cash App not found! Please relaunch the program and read the instructions more closely.')
        input('')

elif user_entered == 2:
    os.system('cls')
    print('Launching browser...\n')
    driver = setup_driver()
    driver.get(site_link)
    print('Sign into EveryDollar, then press ENTER in this window to continue.')
    print('Preparing to import transactions...')
    import_transactions(driver=driver, auto=False)
    quit_driver(driver=driver)
    print('\n [ All Transactions Imported! ] ')
    print("Don't forget to delete the spreadsheets we used, so they don't mess up your import next time.")
    input('')

elif user_entered == 3:
    os.system('cls')
    print('Launching browser...\n')
    driver = setup_driver()
    driver.get(site_link)
    print('Sign into EveryDollar, then press ENTER in this window to continue.')
    print('Preparing to import transactions...')
    import_transactions(driver=driver, auto=True)
    quit_driver(driver=driver)
    print('\n [ All Transactions Imported! ] ')
    print("Don't forget to delete the spreadsheets we used, so they don't mess up your import next time.")
    input('')
