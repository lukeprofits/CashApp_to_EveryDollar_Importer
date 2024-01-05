import os
import threading
import tkcalendar as tkc
import customtkinter as ctk
from datetime import datetime, timedelta

import config as cfg
import CashApp_To_EveryDollar_Importer as imp


def create_import_spreadsheet():
    start, end = get_dates()
    imp.create_import_spreadsheet()
    #threading.Thread(target=imp.create_import_spreadsheet).start()
    cfg.tabview.set("Step 2")  # Move on to Step 2


def manual_import():
    cfg.tabview.set("Step 3")
    threading.Thread(target=imp.import_manually).start()


def automatic_import():
    cfg.tabview.set("Step 3")
    threading.Thread(target=imp.import_automatically).start()


def start_importing():
    cfg.start_importing = True
    if cfg.manual_mode:
        cfg.tabview.set("Step 4")


def get_first_last_day_of_last_month():
    today = datetime.today()
    first_day_of_current_month = datetime(today.year, today.month, 1)
    last_day_of_last_month = first_day_of_current_month - timedelta(days=1)
    first_day_of_last_month = datetime(last_day_of_last_month.year, last_day_of_last_month.month, 1)
    return first_day_of_last_month, last_day_of_last_month


def get_dates():
    start = start_date.get_date()
    end = end_date.get_date()
    print(f"Selected Start Date: {start}")
    print(f"Selected End Date: {end}")
    return start, end


def click_action():
    cfg.current_click_count += 1
    #print(cfg.current_click_count)


def delete_file(file):
    if os.path.exists(file):
        os.remove(file)
        print(f"File {file} has been deleted.")
    else:
        print(f"The file {file} does not exist.")


def delete_input_files():
    delete_file(cfg.transactions_file)
    delete_file(cfg.input_file_from_cashapp)


# INITIAL GUI SETUP ####################################################################################################
ctk.set_appearance_mode("dark")  # Modes: System, light, dark
ctk.set_default_color_theme("green")  # Themes: blue (default), dark-blue, green
app = ctk.CTk()
app.title("Cash App to EveryDollar Importer")  # Set title
app.iconbitmap('icon.ico')  # Set icon
app.geometry("720x240")  # Set window size
app.resizable(False, False)  # Make the window non-resizable
cfg.tabview = ctk.CTkTabview(master=app, anchor="W")  # Location of tabs
cfg.tabview.place(relx=0.5, rely=0.5, anchor=ctk.CENTER, relwidth=1, relheight=1)

# Create Tabs
cfg.tabview.add("Step 1")
cfg.tabview.add("Step 2")
cfg.tabview.add("Step 3")
cfg.tabview.add("Step 4")
cfg.tabview.add("Done")

# Set selected tab
cfg.tabview.set("Step 1")

# Get first and last day of the prior month
first_day, last_day = get_first_last_day_of_last_month()


# VISUAL ITEMS #########################################################################################################
# Step 1 Tab
label1_text = "Download your Cash App transaction history and put it in the same folder as this program.\n\nSelect the date range you want to import transactions from, then click the button below."
label1 = ctk.CTkLabel(master=cfg.tabview.tab("Step 1"), text=label1_text, fg_color="transparent")
start_date = tkc.DateEntry(master=cfg.tabview.tab("Step 1"), date_pattern='m/d/y', year=first_day.year, month=first_day.month, day=first_day.day)
date_label = ctk.CTkLabel(master=cfg.tabview.tab("Step 1"), text="-")
end_date = tkc.DateEntry(master=cfg.tabview.tab("Step 1"), date_pattern='m/d/y', year=last_day.year, month=last_day.month, day=last_day.day)
button1 = ctk.CTkButton(master=cfg.tabview.tab("Step 1"), text="     Prepare Transactions for Import     ", command=create_import_spreadsheet)

# Step2 Tab
label2_text = "Select an Import method.\n\nMake sure to update to the lastest version of Google Chrome before continuing.\n\n Open your browser and visit: chrome://settings/help"
label2 = ctk.CTkLabel(master=cfg.tabview.tab("Step 2"), text=label2_text, fg_color="transparent")
button2 = ctk.CTkButton(master=cfg.tabview.tab("Step 2"), text="     Import Manually (One At A Time)     ", fg_color="#505050", hover_color="#404040", command=manual_import)
button3 = ctk.CTkButton(master=cfg.tabview.tab("Step 2"), text="     Import Automatically (All at once)     ", command=automatic_import)

# Step 3 Tab
label3_text = 'Wait for Chrome to launch (<2 min), and sign in to Every Dollar.\n\nClose any initial pop-ups, then press "Start Importing".'
label3 = ctk.CTkLabel(master=cfg.tabview.tab("Step 3"), text=label3_text, fg_color="transparent")
button4 = ctk.CTkButton(master=cfg.tabview.tab("Step 3"), text="     Start Importing     ", command=start_importing)

# Step 4 Tab
label4_text = 'Manually review transactions one by one as they are imported.\n\nClick "Looks Correct" below to add the transaction shown and then move on to the next one.'
label4 = ctk.CTkLabel(master=cfg.tabview.tab("Step 4"), text=label4_text, fg_color="transparent")
button5 = ctk.CTkButton(master=cfg.tabview.tab("Step 4"), text="     Looks Correct     ", command=click_action)

# Done Tab
label5_text = "Thank you for using Luke Profits CashApp to Every Dollar importer.\n\nAll transactions have been imported."
label5 = ctk.CTkLabel(master=cfg.tabview.tab("Done"), text=label5_text, fg_color="transparent")
button6 = ctk.CTkButton(master=cfg.tabview.tab("Done"), text="     Delete Input Files     ", command=delete_input_files)


# PLACEMENT ############################################################################################################
# Step 1
label1.place(relx=0.5, rely=0.2475, anchor=ctk.CENTER)
start_date.place(relx=0.40, rely=0.495, anchor=ctk.CENTER)
date_label.place(relx=0.5, rely=0.495, anchor=ctk.CENTER)
end_date.place(relx=0.60, rely=0.495, anchor=ctk.CENTER)
button1.place(relx=0.5, rely=0.7425, anchor=ctk.CENTER)

# Step 2
label2.place(relx=0.5, rely=0.2475, anchor=ctk.CENTER)
button2.place(relx=0.33, rely=0.66, anchor=ctk.CENTER)
button3.place(relx=0.66, rely=0.66, anchor=ctk.CENTER)

# Step 3
label3.place(relx=0.5, rely=0.2475, anchor=ctk.CENTER)
button4.place(relx=0.5, rely=0.66, anchor=ctk.CENTER)

# Step 4
label4.place(relx=0.5, rely=0.2475, anchor=ctk.CENTER)
button5.place(relx=0.5, rely=0.66, anchor=ctk.CENTER)

# Done
label5.place(relx=0.5, rely=0.2475, anchor=ctk.CENTER)
button6.place(relx=0.5, rely=0.66, anchor=ctk.CENTER)


# RUN GUI ##############################################################################################################
app.mainloop()
