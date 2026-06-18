# Get notifications by email when certain machines hit a predetermined threshold

import tkinter as tk
from tkinter import ttk

def launch_gui():
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




if __name__ == "__main__":
    launch_gui()