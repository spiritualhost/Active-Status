# Get notifications by email when certain machines hit a predetermined threshold
import argparse
import os
import configparser
import tkinter as tk
from tkinter import ttk, messagebox
from email_validator import validate_email, EmailNotValidError

from utils import *

#Input validation
def valid_email(email_address: str):
    try:
        #Check syntax and deliverability with a DNS lookup
        email_info = validate_email(email_address, check_deliverability=True)

        #Normalize
        normalized_email = email_info.email
        return True, normalized_email

    except EmailNotValidError as e:
        return False, str(e)


#Update notification settings interactively
def launch_gui(config_path: str):

    #Config setup
    config = configparser.ConfigParser()
    config.read(config_path)
    if 'settings' not in config:
        config['settings'] = {}

    #Entry box functions
    def submit_txt(entry_boxes: dict):
        try:
            for varname, entry in entry_boxes.items():
                user_input = str(entry.get())

                #Input validation
                if str(varname) == "email":
                    email_result = valid_email(user_input)
                    if email_result[0]:
                        user_input = email_result[1]
                    else:
                        messagebox.showerror("Bad Entry", f"Email invalid: {email_result[1]}")
                        return 1
                else:
                    if not user_input.isdigit():
                        messagebox.showerror("Bad Entry", f"Unusable day count.")
                        return 1
                
                config['settings'][f'{str(varname)}'] = user_input
            
            #Write to config file
            with open(config_path, "w", encoding="utf-8") as configfile:
                config.write(configfile)
            messagebox.showinfo("Good Entry", "Successful write to config file!")
        
        except Exception as e:
            print(f"Exception: {e}")
    

    def clear_txt(entry_boxes: dict):
        try:
            for entry in entry_boxes.values():

                #Delete text from index 0 to the end
                entry.delete(0, tk.END)
                print("Text cleared")

            return 0
        
        except Exception as e:
            print(f"Exception: {e}")


    #Initialize the main window
    root = tk.Tk()
    root.title("Configure email notifications.")
    root.geometry("400x200")
    root.resizable(False, False)

    #Set up entry boxes
    email = ttk.Entry(root, width=50)
    email.pack(pady=10)
    email.insert(0, "Enter desired destination email...")

    days = ttk.Entry(root, width=50)
    days.pack(pady=10)
    days.insert(0, "Notify for all machines with less than this many days left in eval...")

    entry_boxes = {"email": email, "days": days}

    #Set up control buttons
    submit = ttk.Button(root, text="Submit", command=lambda:submit_txt(entry_boxes))
    submit.pack(pady=10)

    clear = ttk.Button(root, text="Clear All", command=lambda:clear_txt(entry_boxes))
    clear.pack(pady=10)

    #Start main loop
    root.mainloop()

    return 0

#Check over SQL server for predetermined countdown threshold, send email
def scan_and_report(config_path: str):    
    #Parse config for query details
    try:
        config = configparser.ConfigParser()
        config.read(config_path)
        
        email = config["settings"]["email"]
        days_left = config.getint("settings", "days")

        print("Successful config read.")

    except Exception as e:
        print(f"Exception: unreadable config: {e}")

    #Set up PostgreSQL server connection
    serv_connect = SQL_SCAN()
    conn = serv_connect.confirm_connection()
    if not conn:
        print("Bad connection.")
        return 1
    print("Good connection.")

    #Scan the SQL database using the query as detailed in the config, return dictionary
    applicable_machines = serv_connect.scan_query(conn, days_left)

    #Send an email notification
    email_notification = EMAIL_NOTIFICATION(email, applicable_machines)
    email_notification.email_setup()

    return 0




if __name__ == "__main__":
    #Write configurations to APPDATA to prevent permissions issues
    app_data_path = os.environ.get("LOCALAPPDATA")
    config_directory = os.path.join(app_data_path, "ThresholdNotifications (ActiveStatus)", "Config")
    os.makedirs(config_directory, exist_ok=True) #Create config directory if nonexistent
    config_file = os.path.join(config_directory, "config.ini")

    #Use argparse to take in cmdline arguments
    argparser = argparse.ArgumentParser(description="Threshold Notification")
    argparser.add_argument("--db_check", action="store_true", help="Run automated SQL check for countdown threshold")
    args = argparser.parse_args()

    #Argparse branches
    if args.db_check and os.path.exists(config_file):
        scan_and_report(config_file)
    
    #This branch will launch if the config file is non-existent in APPDATA or if launched interactively (i.e., without cmd line args)
    else:
        launch_gui(config_file)
