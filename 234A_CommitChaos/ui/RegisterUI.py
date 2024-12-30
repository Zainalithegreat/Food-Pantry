# ----------------------------------------------------------------------------
# Name: RegisterUI.py
# Owner: Björn Ingermann
# Date Created: 10/19/2024
# Description: class file for registration ui
# ----------------------------------------------------------------------------
# Changes:
# 10/19/24  Initial creation - Björn Ingermann
# 10/19/24  Created RegisterUI file and class
#           Fixed issue where register page would not expand correctly
#           Added back button to return to login page
# 10/23/24  Added registration ability
#           Added registration validation
# 10/28/24  Added requirements for password and validation for email
#           Added password hashing and salting
# 11/12/24  Moved methods from register and login to this file
# 11/13/24          Added Confirmation - Zain A

import pathlib
import tkinter as tk
import pygubu
import random
from logic.Email import Email

from flask import session
from tkinter import simpledialog, messagebox
from logic.User import User
import time

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "templates\\pygubu_account_creation_gui.ui"


class RegisterUI:
    def __init__(self, platform="python", master=None):
        if platform == "python":
            self.builder = builder = pygubu.Builder()
            builder.add_resource_path(PROJECT_PATH)
            builder.add_from_file(PROJECT_UI)

            self.register: tk.Toplevel = builder.get_object("toplevel", master)
            tk.Grid.columnconfigure(self.register, 0, weight=1)
            tk.Grid.rowconfigure(self.register, 0, weight=1)

            builder.connect_callbacks(self)

            self.name_entry = builder.get_object("name_entry")
            self.user_entry = builder.get_object("user_entry")
            self.email_entry = builder.get_object("email_entry")
            self.pass_entry = builder.get_object("pass_entry")
            self.pass_confirm_entry = builder.get_object("pass_confirm_entry")

            # Set password entry to display as '*'
            self.pass_entry.config(show="*")
            self.pass_confirm_entry.config(show="*")
        else:
            self.builder = None
            self.register = None

    def confirm_registration(self, platform="python", web_info=None):
        """
        Method for collecting the information inserted into the registration gui
        and populating the local variables with these values
        :return:
        """
        from data.Database import Database
        from logic.User import User

        if platform == "python":
            # Get username and password from GUI
            name = self.name_entry.get()
            username = self.user_entry.get()
            email = self.email_entry.get()
            password = self.pass_entry.get()
            password_confirm = self.pass_confirm_entry.get()
        else:
            name, username, email, password, password_confirm = web_info

        if not name:
            return self.handle_error(platform, "Please enter your name.", "name")
        if not username:
            return self.handle_error(platform, "Please enter your username.", "username")
        if not email:
            return self.handle_error(platform, "Please enter your email.", "email")
        if not password:
            return self.handle_error(platform, "Please enter your password.", "password")
        if not password_confirm:
            return self.handle_error(platform, "Please confirm your password.", "password_confirm")

        # Additional validations
        if not User.email_validation(email):
            return self.handle_error(platform, "Please enter a valid email address.", "email")
        if not User.pass_validation(password):
            return self.handle_error(platform, "Password must be minimum 5 Characters, 1 Number, 1 Special character",
                                     "password")
        if password != password_confirm:
            return self.handle_error(platform, "Passwords do not match.", "password_confirm")

        user_instance = User(username, password)
        user_id = user_instance.getUserID()
        code = self.send_confirmation_code(user_id, email, platform)

        # Store the code in the session for web users
        if platform == "web":
            session['confirmation_code'] = code

        # Hash and salt the password
        hashed_password = User.hash_password(password)

        if platform == "web":
            session['name'] = name
            session['username'] = username
            session['email'] = email
            session['password'] = hashed_password
            return

        # Connect to the db and check if the user already exists
        time_limit = 600
        time_minutes = time_limit / 60
        messagebox.showinfo("Time", f"You have {int(time_minutes)} minutes remaining until the code is invalid")
        start_time = time.time()
        while True:
            time_left = time.time() - start_time
            remaining_time = time_limit - time_left
            if remaining_time <= 0:
                break
            else:
                try:
                    user_input = simpledialog.askstring("Input Required", "Confirmation Code:")
                    if user_input is None:
                        return
                    if int(user_input) != code:
                        messagebox.showerror("Invalid", "Please enter the correct confirmation code.")
                    else:
                        print(user_input)
                        break
                except ValueError:
                    messagebox.showerror("Invalid", "Invalid input. Please enter a valid integer.")

        time_left = time.time() - start_time
        remaining_time = time_limit - time_left

        hashed_password = User.hash_password(password)
        user = User.check_user_email(username, email)

        if user and remaining_time > 0:
            # Hash and salt the password
            User.add_user(username, hashed_password, name, email)
            messagebox.showinfo("Registration Successful", "Registration Successful")
            self.back_to_login()
        elif not user:
            messagebox.showerror("Registration Unsuccessful", "Username or Email already exists")

        elif remaining_time <= 0:
            messagebox.showinfo("Time up", "Time is up please try again")

    @staticmethod
    def send_confirmation_code(user_id, email, platform="python"):
        """
        Generates a confirmation code, sends it via email, and stores it in the session
        """
        code = random.randint(10000, 99999)
        email_instance = Email(user_id)
        employee_email = "cis234atesting@gmail.com"
        subject = "Confirmation Code"
        message = f"This is a confirmation code. Please don't share it with anyone: {code}"

        # Send email
        email_instance.send_email(subject, message, email, employee_email)

        # For web users, store the confirmation code in the session
        if platform == "web":
            session['confirmation_code'] = code

        return code

    @staticmethod
    def handle_error(platform, message, field=None):
        """
        Function for handling error messages
        :param field:
        :param platform:
        :param message:
        :return: web error for web errors
        """
        if platform == "python":
            messagebox.showerror("Registration Error", message)
        else:  # Web
            return message, field

    def back_to_login(self):
        """
        Method for bringing the user back to the login page from teh registration page
        :return: None
        """
        try:
            from ui.LoginUI import LoginUI

            # Close the registration page
            self.register.destroy()

            # Run the LoginUI class
            login_page = LoginUI()
            login_page.run()
        except:
            print("Error opening login page")

    # Run the class
    def run(self):
        self.register.mainloop()
