# Get notifications by email when certain machines hit a predetermined threshold
import argparse
import os
import tkinter as tk
from tkinter import ttk

#Update notification settings interactively
def launch_gui(config_path: str):
    #Config
    with open(config_path, "w") as conf:
        conf.write("Hello world")

    #Entry box functions
    def submit_txt(entry):
        user_input = entry.get()
        print(user_input)
        return
    
    def clear_txt(entry):
        #Delete text from index 0 to the end
        entry.delete(0, tk.END)
        print("Text cleared")
        return

    #Initialize the main window
    root = tk.Tk()
    root.title("Configure email notifications.")
    root.geometry("400x200")
    root.resizable(False, False)

    #Set up entry boxes
    email = ttk.Entry(root, width=25)
    email.pack(pady=10)
    email.insert(0, "Enter desired destination email...")

    #Set up control buttons
    submit = ttk.Button(root, text="Submit", command=lambda:submit_txt(email))
    submit.pack(pady=10)

    clear = ttk.Button(root, text="Clear All", command=lambda:clear_txt(email))
    clear.pack(pady=10)

    #Start main loop
    root.mainloop()

    return

#Check over SQL server for predetermined countdown threshold
def tempfunc():
    print("Tempfunc")
    return

if __name__ == "__main__":
    #Write configurations to APPDATA to prevent permissions issues
    app_data_path = os.environ.get("LOCALAPPDATA")
    config_directory = os.path.join(app_data_path, "ThresholdNotifications (ActiveStatus)", "Config")
    os.makedirs(config_directory, exist_ok=True) #Create config directory if nonexistent
    config_file = os.path.join(config_directory, "config.ini")

    #Use argparse to take in cmdline arguments
    parser = argparse.ArgumentParser(description="Threshold Notification")
    parser.add_argument("--db_check", action="store_true", help="Run automated SQL check for countdown threshold")
    args = parser.parse_args()

    #Argparse branches
    if args.db_check and os.path.exists(config_file):
        tempfunc()
    
    #This branch will launch if the config file is non-existent in APPDATA or if launched interactively (i.e., without cmd line args)
    else:
        launch_gui(config_file)