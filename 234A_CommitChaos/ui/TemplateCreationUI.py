# ********************************************************************
# Name: TemplateCreationUI.
# Owner: Jiraschaya Freeburn
# Date Created: 10/15/2024
# Description: TemplateCreationUI provides a graphical interface
# for creating and managing templates.Users can input template details,
# insert predefined tags, and save or clear entries.
# The interface validates user inputs, checks for duplicate template
# names, and confirms successful saves.
# *******************************************************************

import pathlib
import tkinter as tk
from tkinter import ttk, messagebox
import pygubu
from logic.Template import Template

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH /"templates"/"pygubu_template_gui.ui"


class TemplateCreationUI:
    """
    UI for creating templates, handling user inputs, and
    saving/clearing templates.
    """
    # hard code exist user ID in the database

    def __init__(self, master=None, user_id=None):
        """
        Initializes the UI, loads UI components, and sets up
        event handlers.
        :param master: The window that display the UI
        """
        # Create the Pygubu builder object and load UI from file.
        self.user_id = user_id
        self.__builder = builder = pygubu.Builder()
        builder.add_from_file(PROJECT_UI)

        # Initialize UI elements from .ui file
        self.main_window = builder.get_object("main_window", master)
        self.template_name_entry = builder.get_object("template_name_entry")
        self.subject_entry = builder.get_object("subject_entry")
        self.text = builder.get_object("template_text")
        self.save_button = builder.get_object("btn_save_template")
        self.clear_button = builder.get_object("btn_clear")
        self.tag_combobox = builder.get_object("tag_combobox")
        # Set up template tags in combobox
        self.tag_combobox['values'] = ['{campus}',
                                       '{food item}',
                                       '{start time}',
                                       '{end time}',]
        # Enable insertion on selection
        self.tag_combobox.bind("<<ComboboxSelected>>", self.insert_tag)

        builder.connect_callbacks(self)

    def run(self):
        """
        Starts the main event loop to display the application window
        """
        self.main_window.mainloop()

    def insert_tag(self, event):
        """
        Inserts the selected tag from the combobox into the text area.
        :param event: event object associated with combo selection.
        :return: None
        """
        select_tag = self.tag_combobox.get()
        self.text.insert(tk.INSERT, select_tag)

    def save_template(self):
        """
        Handles the save template button click event.
        Validates inputs, checks for duplicates, and
        saves the template if valid.
        Displays success or error messages
        :return: None
        """
        template_name = self.template_name_entry.get()
        subject = self.subject_entry.get()
        message = self.text.get(1.0, tk.END).strip()

        # Create template instance with input data and user ID
        template = Template(template_name, subject, message, user_id=self.user_id)

        # Validate all fields entered
        if not template.name or not template.subject or not template.message:
            messagebox.showinfo("Attention!","All fields are required!")
            return

        # Check for duplicate template name
        if template.check_duplicate(template.name):
            messagebox.showinfo("Attention!", f"The template name '{template_name}' already exists!")
            return

        # Save template
        if template.save():
            self.clear_template()
            messagebox.showinfo("Success", "Template saved successfully")
        else:
            messagebox.showinfo("Error", "Template not saved")

    def clear_template(self):
        """
        Clears all input fields in the template creation form.
        :return: None
        """
        self.template_name_entry.delete(0, tk.END)
        self.subject_entry.delete(0, tk.END)
        self.text.delete(1.0, tk.END)
        self.tag_combobox.delete(0, tk.END)

    def back_to_landing(self):
        """
        Navigate back to landing page and close the window.
        :return: None
        """
        from ui.LandingUI import LandingUI
        self.main_window.destroy()
        landing_page = LandingUI(user_id=self.user_id)
        landing_page.run()

if __name__ == "__main__":
    app = TemplateCreationUI()
    app.run()



