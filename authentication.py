import re
import tkinter as tk
from tkinter import messagebox
import database 

def validate_signup(name, age, precinct_code, code, rank, badge_number):
    """Validate officer registration data"""
    if not re.match(r'^[A-Za-z ]+$', name):
        return False, "Name must contain only letters!"
    if not age.isdigit():
        return False, "Age must be numerical!"
    if not re.match(r'^01[A-Z]{2}$', precinct_code):
        return False, "Precinct Code must start with '01' followed by two uppercase letters!"
    if not code.isdigit() or len(code) != 6:
        return False, "6-digit code must be numerical!"
    if not rank:
        return False, "Rank is required!"
    if not badge_number.isdigit():
        return False, "Badge number must be numerical!"
    return True, "Validation successful"

def show_login_window(parent_callback):
    """Show the login/signup window"""
    root = tk.Tk()
    root.title("Officer Login / Sign Up")
    root.geometry("400x400")
    root.minsize(400, 400)
    root.maxsize(400, 400)
    
    def login():
        username = username_entry.get()
        code = code_entry.get()
        officer = database.verify_officer(username, code)
        if officer:
            messagebox.showinfo("Success", "Login Successful!")
            root.destroy()
            parent_callback(officer)
        else:
            messagebox.showerror("Error", "Invalid credentials, try again!")
    
    def sign_up():
        signup_window = tk.Toplevel()
        signup_window.title("Officer Sign Up")
        signup_window.geometry("400x500")
        
        tk.Label(signup_window, text="Name:").pack()
        name_entry = tk.Entry(signup_window)
        name_entry.pack()
        
        tk.Label(signup_window, text="Age:").pack()
        age_entry = tk.Entry(signup_window)
        age_entry.pack()
        
        tk.Label(signup_window, text="Precinct Code:").pack()
        precinct_code_entry = tk.Entry(signup_window)
        precinct_code_entry.pack()
        
        tk.Label(signup_window, text="6-digit Code:").pack()
        code_entry = tk.Entry(signup_window, show="*")
        code_entry.pack()
        
        tk.Label(signup_window, text="Rank:").pack()
        rank_entry = tk.Entry(signup_window)
        rank_entry.pack()
        
        tk.Label(signup_window, text="Badge Number:").pack()
        badge_entry = tk.Entry(signup_window)
        badge_entry.pack()
        
        def submit_registration():
            name = name_entry.get()
            age = age_entry.get()
            precinct_code = precinct_code_entry.get()
            code = code_entry.get()
            rank = rank_entry.get()
            badge_number = badge_entry.get()
            
            valid, message = validate_signup(name, age, precinct_code, code, rank, badge_number)
            if not valid:
                messagebox.showerror("Error", message)
                return
                
            username = database.add_officer(name, age, precinct_code, code, rank, badge_number)
            if username:
                messagebox.showinfo("Success", f"Your username: {username}. Log in with your 6-digit code.")
                signup_window.destroy()
            else:
                messagebox.showerror("Error", "Officer already exists or badge number in use!")
        
        tk.Button(signup_window, text="Submit", command=submit_registration).pack(pady=10)
    
    tk.Label(root, text="Username:").pack()
    username_entry = tk.Entry(root)
    username_entry.pack()
    
    tk.Label(root, text="6-digit Code:").pack()
    code_entry = tk.Entry(root, show="*")
    code_entry.pack()
    
    tk.Button(root, text="Login", command=login).pack(pady=10)
    tk.Button(root, text="Sign Up", command=sign_up).pack(pady=10)
    
    root.mainloop()