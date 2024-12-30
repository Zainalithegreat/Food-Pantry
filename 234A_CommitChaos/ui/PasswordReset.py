#!/usr/bin/python3
import pathlib
import tkinter as tk
import pygubu
from tkinter import messagebox
from logic.User import User

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "templates//pygubu_password_reset.ui"
RESOURCE_PATHS = [PROJECT_PATH]


class PasswordResetUI:
    def __init__(self, master=None, user_id=None):
        self.user_id = user_id
        self.builder = pygubu.Builder()
        self.builder.add_resource_paths(RESOURCE_PATHS)
        self.builder.add_from_file(PROJECT_UI)
        # Main widget
        self.mainwindow: tk.Toplevel = self.builder.get_object(
            "password_reset", master)
        self.builder.connect_callbacks(self)
        self.password_enter = self.builder.get_object("password_enter")
        self.confirm_enter = self.builder.get_object("confirm_enter")
        self.password_enter.config(show="*")
        self.confirm_enter.config(show="*")

    def run(self):
        self.mainwindow.mainloop()

    def forget_password_helper(self):
        """
        Validates and updates the password after a successful confirmation code verification.
        """

        # Ensure password fields are valid
        if not self.password_enter or not self.confirm_enter:
            messagebox.showerror("Error", "Password fields are not initialized.")
            return

        # Validate and update password
        new_password = self.password_enter.get()
        confirm_password = self.confirm_enter.get()

        # Password validation
        if not User.pass_validation(new_password):
            messagebox.showerror(
                "Password Error",
                "Password must be at least 5 characters long, contain a number, and a special character."
            )
            return

        # Password confirmation
        if new_password != confirm_password:
            messagebox.showerror("Password Error", "Passwords do not match.")
            return

        # Hash and update password
        hashed_password = User.hash_password(new_password)
        print(self.user_id)
        User.update_password(hashed_password, self.user_id)
        messagebox.showinfo("Success", "Password has been reset successfully!")
        self.mainwindow.destroy()

    def cancel(self):
        self.clear_entry()
        self.mainwindow.destroy()

    def clear_entry(self):
        self.password_enter.delete(0, 'end')
        self.confirm_enter.delete(0, 'end')

if __name__ == "__main__":
    app = PasswordResetUI()
    app.run()
