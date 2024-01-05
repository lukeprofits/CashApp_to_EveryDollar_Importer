import os
import threading


def goto_done():
    def gtd():
        #time.sleep(2)
        tabview.set("Done")

    threading.Thread(target=gtd).start()


tabview = ''
start_importing = False
manual_mode = False

input_file_from_cashapp = "cash_app_report.csv"
transactions_file = 'import_spreadsheet_of_transactions.csv'
site_link = 'https://www.everydollar.com/app/budget'

headless = False
user_agent = None
selenium_temp_dir = os.path.join(os.getcwd(), 'temp')
proxy = None

last_click_count = 0
current_click_count = 0
