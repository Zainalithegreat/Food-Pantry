#!/usr/bin/python3
import pathlib
import time
import tkinter as tk
import pygubu

from logic.User import User
from RegisterUI import RegisterUI
from tkinter import simpledialog, messagebox

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "templates//pygubu_user_settings.ui"
RESOURCE_PATHS = [PROJECT_PATH]


class SubscriberSettingsUI:
    def __init__(self, master=None, user_id=None):
        self.user_id = user_id
        self.builder = pygubu.Builder()
        self.builder.add_resource_paths(RESOURCE_PATHS)
        self.builder.add_from_file(PROJECT_UI)
        # Main widget
        self.mainwindow: tk.Toplevel = self.builder.get_object("main", master)
        self.builder.connect_callbacks(self)
        self.mainwindow.title("Subscriber Settings")
        username = User.get_user(user_id)
        self.username_label = self.builder.get_object("username")
        self.username_label.configure(text=f"Username: {username[0]}")
        self.check_button = self.builder.get_object("unsub_checkbutton")
        sub_status = User.get_subbed(user_id)
        self.check_var = tk.IntVar(value=0 if sub_status[0] == 1 else 1)
        self.check_button.config(variable=self.check_var, onvalue=1, offvalue=0)
        print("sub_status: ", sub_status)

        self.logout_button = self.builder.get_object("logout_button")
        self.user = User.fetch_user_object(self.user_id)

    def run(self):
        self.mainwindow.mainloop()

    def logout(self):
        if self.user.getRole() == "Manager":
            from ui.LandingUI import LandingUI
            self.mainwindow.destroy()
            LandingUI(user_id=self.user_id).run()
        else:
            self.mainwindow.destroy()
            from LoginUI import LoginUI
            login = LoginUI()
            login.run()

    def unsub_notifications(self):
        if self.check_var.get() == 0:
            User.unsubscribe_user(self.user_id)
            messagebox.showinfo("Unchecked", "You will no longer receive notifications")
        else:
            User.subscribe_user(self.user_id)
            messagebox.showinfo("Checked", "You will receive email notifications")

    def change_username(self):
        user_input = simpledialog.askstring("Input Required", "New Username:")
        if user_input is None:
            return
        user_email = User.get_email_from_userid(self.user_id)
        if self.confirmation_code(user_email) is True:
            if User.check_user(user_input) is False:
                User.change_username(user_input, self.user_id)
                self.username_label.configure(text=f"Username: {user_input}")
                messagebox.showinfo("Updated", "Username Updated")
            else:
                messagebox.showerror("Invalid", "Username already exists.")

    def change_email(self):
        user_input = simpledialog.askstring("Input Required", "New Email:")
        if user_input is None:
            return
        email = User.email_validation(user_input)
        if email and self.confirmation_code(user_input) is True:
            if User.check_email(user_input) is False:
                User.change_email(user_input, self.user_id)
                messagebox.showinfo("Updated", "Email Updated")
            else:
                messagebox.showerror("Invalid", "Email already exists.")
        elif not email:
            messagebox.showerror("Invalid", "Not an Email.")

    def change_password(self):
        user_email = User.get_email_from_userid(self.user_id)
        if self.confirmation_code(user_email) is True:
            from PasswordReset import PasswordResetUI
            password_reset = PasswordResetUI(user_id=self.user_id)
            password_reset.run()

    def delete_account(self):
        if self.user.getRole() == "Manager":
            messagebox.showerror("Invalid", "Managers can not delete accounts.")
            return
        user_email = User.get_email_from_userid(self.user_id)
        if self.confirmation_code(user_email) is True:
            response = messagebox.askyesno("Confirmation", "Are you sure you want to delete your account?")
            if response:
                User.delete_account(self.user_id)
                self.mainwindow.destroy()
                from LoginUI import LoginUI
                login = LoginUI()
                login.run()
            else:
                return

    def confirmation_code(self, email):
        platform = "python"
        time_limit = 600
        time_minutes = time_limit / 60
        messagebox.showinfo("Time", f"You have {int(time_minutes)} minutes remaining until the code is invalid")
        start_time = time.time()
        code = RegisterUI.send_confirmation_code(self.user_id, email, platform)
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
            return False
        else:
            return True


if __name__ == "__main__":
    app = SubscriberSettingsUI()
    app.run()
