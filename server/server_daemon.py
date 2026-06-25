# Get notifications by email when certain machines hit a predetermined threshold
import argparse
import os
import configparser
import smtplib
import socket
import tkinter as tk
from tkinter import ttk, messagebox
from email_validator import validate_email, EmailNotValidError

from utils import *

#Input validation functions
#Just verify that an email address appears valid (without SMTP credentials)
def valid_email(email_address: str):
    try:
        #Check syntax and deliverability with a DNS lookup
        email_info = validate_email(email_address, check_deliverability=True)

        #Normalize
        normalized_email = email_info.email
        return True, normalized_email

    except EmailNotValidError as e:
        return False, str(e)

#Verify valid SMTP credentials (necessary to perform)
def verify_smtp_server(smtp_server: str, port: int, username: str, password: str, use_tls=True):
    print(f"Server: {smtp_server}\nPort: {port}\nUsername: {username}\nPassword: {password}")
    try:
        #Establish an initial connection with a 10 sec timeout
        server = smtplib.SMTP(smtp_server, port, timeout=10)

        #Send an EHLO greeting with TLS
        server.starttls()
        server.ehlo()

        #Attempt a server login
        server.login(username, password)

        #Cleanly disconnect
        server.quit()

        return (True, "Successful SMTP connection")

    except socket.timeout:
        return(False, "Error: socket timeout.")

    except (socket.gaierror, ConnectionRefusedError):
        return(False, "Error: could not connect to server, please check server address.")

    except smtplib.SMTPAuthenticationError:
        return(False, "Error: authentication failed, incorrect username or password.")

    except smtplib.SMTPException as e:
        return(False, f"SMTP error occurred: {e}")

    except Exception as e:
        return(False, f"An unexpected error occurred: {e}")

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
            temp_smtp_dict = {"smtp_server": "",
                              "smtp_port": "",
                              "sender_email": "",
                              "sender_password": ""} #Used in SMTP validation below

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

                #Days only needs to be a positive integer
                elif str(varname) == "days":
                    if not user_input.isdigit():
                        messagebox.showerror("Bad Entry", f"Unusable day count: {user_input}.")
                        return 1
                    
                #Smtp server settings populate the dictionary
                if str(varname) in temp_smtp_dict:
                    temp_smtp_dict[str(varname)] = user_input

                #Add to the config variable for future write
                config['settings'][f'{str(varname)}'] = user_input

            #Check if all SMTP fields are populated after the loop through entry fields
            if all(temp_smtp_dict.values()): #Returns True if no falsy values
                messagebox.showinfo("Performing SMTP check.", "Now checking SMTP credentials...")      
                response = verify_smtp_server(temp_smtp_dict["smtp_server"], temp_smtp_dict["smtp_port"], temp_smtp_dict["sender_email"], temp_smtp_dict["sender_password"])

                if response[0] == False:
                    messagebox.showerror("Huh?", response[1])
                    clear_txt(entry_boxes)
                    return 1
                else:
                    messagebox.showinfo("Successful SMTP config", response[1])

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
    root.geometry("1000x600")
    root.resizable(False, False)

    #Inner box title
    inner_title = ttk.Label(root, text="Please fill out the following...")
    inner_title.pack(pady=10)  

    #Section delimit
    label1 = ttk.Label(root, text="Email Notification Settings")
    label1.pack(pady=10)

    #Set up entry boxes
    email = ttk.Entry(root, width=50)
    email.pack(pady=10)
    email.insert(0, "Enter desired destination email...")

    days = ttk.Entry(root, width=50)
    days.pack(pady=10)
    days.insert(0, "Notify for all machines with less than this many days left in eval...")


    #Section delimit
    label2 = ttk.Label(root, text="SMTP Server Settings")
    label2.pack(pady=10)

    smtp_server = ttk.Entry(root, width=50)
    smtp_server.pack(pady=10)
    smtp_server.insert(0, "Enter SMTP server address...")

    smtp_port = ttk.Entry(root, width=50)
    smtp_port.pack(pady=10)
    smtp_port.insert(0, "Enter SMTP server port...")
   
    sender_email = ttk.Entry(root, width=50)
    sender_email.pack(pady=10)
    sender_email.insert(0, "Enter sender email...")

    sender_password = ttk.Entry(root, width=50)
    sender_password.pack(pady=10)
    sender_password.insert(0, "Enter sender password...")

    entry_boxes = {"email": email, 
                   "days": days, 
                   "smtp_server": smtp_server,
                   "smtp_port": smtp_port,
                   "sender_email": sender_email,
                   "sender_password": sender_password
    }

    #Set up control buttons
    submit = ttk.Button(root, text="Submit", command=lambda:submit_txt(entry_boxes))
    submit.pack(pady=10)

    clear = ttk.Button(root, text="Clear All", command=lambda:clear_txt(entry_boxes))
    clear.pack(pady=10)

    quit = ttk.Button(root, text="Quit", command=root.destroy)
    quit.pack(pady=10)

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
        smtp_server = config["settings"]["smtp_server"]
        smtp_port = config.getint("settings", "smtp_port")
        sender_email = config["settings"]["sender_email"]
        sender_password = config["settings"]["sender_password"]

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
    email_notification = EMAIL_NOTIFICATION(email, applicable_machines, smtp_server, smtp_port, sender_email, sender_password)
    msg = email_notification.email_setup()
    email_notification.send_email(msg)

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
