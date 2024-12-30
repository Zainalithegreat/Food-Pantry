# ----------------------------------------------------------------------------
# Name: SendNotificationSystem.UI
# Owner: Zain Ali
# Date Created: 10/14/2024
# Description: UI for sending notifications
# ----------------------------------------------------------------------------
# Changes:
# 10/14/24 Notification System -Zain Ali.


from debugpy.common.timestamp import current

from logic.Email import Email
# !/usr/bin/python3
import pathlib
import tkinter as tk
import pygubu
from logic.Template import Template
from datetime import datetime
from tkinter import simpledialog
from tkinter import filedialog
from PIL import Image, ImageTk
import smtplib

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "templates//send_notification_system.ui"


class SendNotificationSystemApp:
    """
        This is the UI class
    """

    def __init__(self, master=None, user_id=None):
        """
            This is the init function for the UI sendNotificationClass
        """
        self.user_id = user_id
        self.builder = builder = pygubu.Builder()
        builder.add_resource_path(PROJECT_PATH)
        builder.add_from_file(PROJECT_UI)
        self.templates = Template.fetch_templates()
        # Main widget
        self.mainwindow: tk.Toplevel = builder.get_object("main", master)
        builder.connect_callbacks(self)
        self.subject_entry = builder.get_object('subject_entry', master)
        self.message_entry = builder.get_object('message_entry', master)
        self.button_frame = builder.get_object('button_frame', master)
        self.print_message = builder.get_object('print', master)
        self.combo_box = builder.get_object('combo_box', master)
        self.combo_box.bind("<<ComboboxSelected>>", self.on_combobox_select)
        self.combo_options()
        self.progress_bar = builder.get_object('progress_bar', master)
        self.tag_replace_combobox = builder.get_object('tag_replace_combobox', master)
        self.tag_replace_combobox['values'] = ['{campus}',
                                               '{food item}',
                                               '{start time}',
                                               '{end time}', ]
        self.tag_replace_combobox.bind("<<ComboboxSelected>>", self.tag_selected)

        self.campus_popup = None

        self.image_refs = []

    def tag_selected(self, event):
        tag = self.tag_replace_combobox.get()
        if tag in ["{food item}", "{campus}", "{start time}", "{end time}"]:
            self.value_selector(tag)

    def value_selector(self, tag):
        if tag == "{campus}":
            self.open_campus_popup()
        elif tag == "{food item}":
            self.open_food_item_popup()
        elif tag in ["{start time}", "{end time}"]:
            self.open_time_popup(tag)

    def open_campus_popup(self):
        """
        Open the campus popup, creating it if it doesn't already exist.
        """
        if self.campus_popup is None or not self.campus_popup.winfo_exists():
            # Create the popup if it doesn't exist or was destroyed
            self.campus_popup = self.builder.get_object("campus_popup", self.mainwindow)

            # Configure the combobox
            campus_combobox = self.builder.get_object("campus_combobox")
            campus_combobox["values"] = ["Cascade Campus",
                                         "Rock Creek Campus",
                                         "Southeast Campus",
                                         "Sylvania Campus"]
            campus_combobox.current(0)

            tag_button = self.builder.get_object("tag_button")

            def set_campus():
                selected_value = campus_combobox.get()
                self.replace_tag_message("{campus}", selected_value)
                self.campus_popup.withdraw()

            tag_button.configure(command=set_campus)

        self.campus_popup.deiconify()
        self.campus_popup.lift()

    def open_food_item_popup(self):
        """
        Open a simple input dialog to replace the {food item} tag.
        """
        food_item = simpledialog.askstring("Food Item", "Enter Food Item:")
        if food_item:
            self.replace_tag_message("{food item}", food_item)

    def replace_tag_message(self, tag, value):
        current_subject = self.subject_entry.get()
        new_subject = current_subject.replace(tag, value, 1)
        self.subject_entry.delete(0, "end")
        self.subject_entry.insert(0, new_subject)

        current_text = self.message_entry.get("1.0", "end")
        new_text = current_text.replace(tag, value, 1)
        self.message_entry.delete("1.0", "end")
        self.message_entry.insert("1.0", new_text)

    def add_image(self):
        file_path = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")]
        )
        if file_path:
            img = Image.open(file_path)
            img = img.resize((100, 100))
            photo = ImageTk.PhotoImage(img)

            self.message_entry.image_create('end', image=photo)

            self.image_refs.append(photo)

            self.message_entry.insert("end", "\n")

    def combo_options(self):
        """
            This function 'combo_options' stores the names in template_names and then assigns the values to the combo box
        """
        template_names = [template.name for template in self.templates]
        self.combo_box["values"] = template_names

    def on_combobox_select(self, event):
        """
            This function if template name is the same as what is choosen in the combo box then based on that it will fill entry boxes
        """
        self.subject_entry.delete(0, "end")
        self.message_entry.delete("1.0", "end")

        for template in self.templates:
            if self.combo_box.get() == template.name:
                self.subject_entry.insert(0, template.subject)
                self.message_entry.insert("1.0", template.message)

    def send_email(self):
        """
            This function is callled when the send button is hit, this function sends subject, message, employee_email, and server to logic.Email.send_email
        """
        subject = None
        message = None
        employee_email = "cis234atesting@gmail.com"
        sub_count = 0
        client_email = Email.fetch_emails()
        date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ".000"
        self.progress_bar['maximum'] = len(client_email)
        if not self.subject_entry.get() or not self.message_entry.get("1.0", "end-1c"):
            self.progress_bar['value'] = 0
            self.button_frame.grid(row=4, column=0)
            self.print_message.config(text="Fields are empty")
        else:
            self.progress_bar['value'] = 0
            self.button_frame.grid(row=3, column=0)
            self.print_message.config(text="")
            email_instance = Email(self.user_id)
            print("user_id", self.user_id)
            subject, message, sub_count = email_instance.send_email(self.subject_entry.get(),
                                                             self.message_entry.get("1.0", "end-1c"), client_email,
                                                             employee_email, sub_count)
            self.progress_bar['value'] = sub_count
            self.progress_bar.update_idletasks()

            email_instance.storing_information(subject, message, date_time, sub_count)
            self.clear_entry()
            self.button_frame.grid(row=4, column=0)
            self.print_message.config(text="Email has been sent")

    def clear_entry(self):
        """
            This function clears the entries
        """
        self.subject_entry.delete(0, 'end')
        self.message_entry.delete("1.0", 'end')
        self.combo_box.set('')

    def landing_ui(self):
        """This function runs the Landing Ui"""
        from ui.LandingUI import LandingUI
        self.mainwindow.destroy()
        LandingUI(user_id=self.user_id).run()

    def run(self):
        self.mainwindow.mainloop()


if __name__ == "__main__":
    app = SendNotificationSystemApp()
    app.run()