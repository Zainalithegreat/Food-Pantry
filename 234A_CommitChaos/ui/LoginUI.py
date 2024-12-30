# ----------------------------------------------------------------------------
# Name: LoginUI.py
# Owner: Björn Ingermann
# Date Created: 10/16/2024
# Description: class file for login ui
# ----------------------------------------------------------------------------
# Changes:
# 10/10/24  Initial creation - Björn Ingermann
# 10/19/24  Added register button functionality
#           Renamed class to match file name
# 10/23/24  Added login functionality, minor input validation and checks for existing users
# 10/28/24  Updated to accept email or username for login
#           Bound Enter key to log in button
#           Hid character entries in password entry with '*'

import pathlib
import random
import tkinter as tk
import pygubu
from tkinter import simpledialog, messagebox
import time

from tkinter import messagebox

from flask import session

from logic.User import User
from logic.Email import Email
from ui.RegisterUI import RegisterUI

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "templates\\pygubu_login_gui.ui"


class LoginUI:
    def __init__(self, platform="python", master=None):
        if platform == "python":

            self.builder = builder = pygubu.Builder()
            builder.add_resource_path(PROJECT_PATH)
            builder.add_from_file(PROJECT_UI)

            self.login: tk.Toplevel = builder.get_object("main", master)
            tk.Grid.columnconfigure(self.login, 0, weight=1)
            tk.Grid.rowconfigure(self.login, 0, weight=1)

            builder.connect_callbacks(self)

            self.user_entry = builder.get_object("user_entry")
            self.pass_entry = builder.get_object("pass_entry")

            # Set password entry to display as '*'
            self.pass_entry.config(show="*")

            # Bind the Return key to the user_login method
            self.login.bind('<Return>', self.return_key)
        else:
            self.builder = None
            self.register = None

    def return_key(self, event):
        self.user_login(platform="python", event=event)

    def user_login(self, platform="python", web_info=None, event=None):
        """
        Gets the user's credentials and matches them up with what is stored in the database
        :return: None
        """
        # Get username and password from GUI
        if platform == "python":
            user_or_email = self.user_entry.get()
            password = self.pass_entry.get()
        else:
            user_or_email, password = web_info

        # Checks that a username and password have been entered
        if not user_or_email or not password:
            if platform == "python":
                messagebox.showerror("Login Error", "Please enter both username and password.")
                self.user_entry.delete(0, tk.END)
                self.pass_entry.delete(0, tk.END)
            return self.handle_error(platform, "Please enter both username and password.")

        # Check if the user_entry input is an email or username
        email = User.email_validation(user_or_email)

        # Check the database for a given user and return it
        result = User.fetch_user(user_or_email, password, is_email=email)
        if not result:
            if platform == "python":
                messagebox.showerror("Login Error", "Invalid username/email or password.")
                self.user_entry.delete(0, tk.END)
                self.pass_entry.delete(0, tk.END)
            else:
                return self.handle_error(platform, "Invalid username or password.")
        else:
            time_limit = 600
            time_minutes = time_limit / 60
            messagebox.showinfo("Time", f"You have {int(time_minutes)} minutes remaining until the code is invalid")
            # Fetch the full user object
            user = User.fetch_user_object(result)

            # Use user information
            user_id = user.getUserID()
            user_email = user.getEmail()

            code = RegisterUI.send_confirmation_code(user_id, user_email, platform)
            start_time = time.time()

            # Store the code in the session for web users
            if platform == "web":
                session['confirmation_code'] = code
                session['user_id'] = user_id
                return

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

            if remaining_time <= 0:
                messagebox.showinfo("Time up", "Time is up please try again")

            elif remaining_time > 0:
                messagebox.showinfo("Successful Login", "Successful Login")
                print(user_id)
                if user.getRole() == "Manager":
                    try:
                        from ui.LandingUI import LandingUI

                        self.login.destroy()
                        landing_page = LandingUI(user_id=user_id)
                        landing_page.run()
                    except:
                        print("Error opening landing page")
                elif user.getRole() == "Subscriber":
                    from SubscriberSetting import SubscriberSettingsUI
                    self.login.destroy()
                    sub_settings = SubscriberSettingsUI(user_id=user_id)
                    sub_settings.run()
                else:
                    messagebox.showinfo("Failed Login", "Failed login, role not recognized")

    @staticmethod
    def handle_error(platform, message):
        """
        Function for handling error messages
        :param platform:
        :param message:
        :return: web error for web errors
        """
        if platform == "python":
            messagebox.showerror("Login Error", message)
        else:  # Web
            return message

    def user_register(self):
        """
        Close the login page and open the registration page
        """
        try:
            from ui.RegisterUI import RegisterUI

            self.login.destroy()
            register_page = RegisterUI()
            register_page.run()
        except:
            print("Error opening registration page")

    def forget_password(self, platform="python"):
        """
        Handles the forget password process by validating user input and sending a confirmation code.
        """
        from logic.Email import Email

        # Prompt user for username or email
        user_input = simpledialog.askstring("Input Required", "Enter your Username or Email:")
        if not user_input:
            return

        # Validate input as email or username
        email = User.email_validation(user_input)

        if email:  # Input is an email
            user_id = User.get_userid_email(user_input)
            if not user_id:
                messagebox.showerror("Invalid", "No user found with the provided email.")
                return
            user_email = user_input
            user_id = user_id[0][0]
        else:  # Input is assumed to be a username
            user_instance = User(user_input)
            user_id = user_instance.getUserID()
            user_email = user_instance.getEmail()

        # Handle case where no user is found
        if not user_id or not user_email:
            messagebox.showerror("Invalid", "No user found with the provided details.")
            return


        # Send confirmation code
        code = RegisterUI.send_confirmation_code(user_id, user_email, platform)

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

        if remaining_time <= 0:
            messagebox.showinfo("Time up", "Time is up please try again")
            return
        else:
            from PasswordReset import PasswordResetUI
            password_reset = PasswordResetUI(user_id=user_id)
            password_reset.run()


    # Run the class
    def run(self):
        self.login.mainloop()


if __name__ == "__main__":
    app = LoginUI()
    app.run()
