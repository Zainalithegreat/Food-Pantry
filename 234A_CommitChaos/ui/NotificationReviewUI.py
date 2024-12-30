# ----------------------------------------------------------------------------
# Name: NotificationReview.UI
# Owner: Chip Weatherly
# Date Created: 10/10/2024
# Description: class definition file for notification log ui
# ----------------------------------------------------------------------------
# Changes:
# 10/10/24 Initial creation -CW
# 10/15/24 refactored/renamed to fit standards, linked buttons to class -CW
# 10/16/24 Combobox functionality added. Boxes now populate with dates
#          from database entries. User selection event is recognized. - CW
# 10/18/24 endComboBox now populates data based on the selection from
#          startComboBox (only shows dates greater than/equal to start) - CW
# 10/18/24 Treeview data populates & removes to match combobox selections - CW
# 10/22/24 Replaced comboboxes with tk.DateEntry widgets. Removed combobox
#          related functions.
# 10/23/24 Added init_date_entries() function to prevent users from selecting
#          dates in the future. Resized UI. - CW
# 10/24/24 Altered init_log function, moved construction of notification
#          objects to logic tier - CW
#
import pathlib
import tkinter as tk
import pygubu
from datetime import datetime
from logic.NotificationsLog import NotificationsLog

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "templates\\pygubu_notification_gui.ui"
RESOURCE_PATHS = [PROJECT_PATH]


class NotificationReviewUI:
    def __init__(self, master=None, user_id=None):
        self.user_id = user_id
        self.builder = pygubu.Builder()
        self.builder.add_resource_paths(RESOURCE_PATHS)
        self.builder.add_from_file(PROJECT_UI)
        # Main widget
        self.__mainwindow: tk.Toplevel = self.builder.get_object(
            "NotificationReview", master)
        # Tk variables placeholder
        self.builder.connect_callbacks(self)
        # link pygubu code to class definition
        self.__start_date_entry = self.builder.get_object("startDateEntry", master)
        self.__end_date_entry = self.builder.get_object("endDateEntry", master)
        self.__selection_tree = self.builder.get_object("selectionTreeview",
                                                        master)
        self.__message_text_box = self.builder.get_object("notificationInfoText", master)

        # initialize treeview columns
        self.init_treeview()
        # sets max date value for both DateEntry widgets
        self.init_date_entries()

        # Selection handlers. Binds tkinter objects to their event handlers
        self.__start_date_entry.bind('<<DateEntrySelected>>', self.start_date_handler)
        self.__end_date_entry.bind('<<DateEntrySelected>>', self.end_date_handler)
        self.__selection_tree.bind('<ButtonRelease-1>', self.treeview_handler)

    @staticmethod
    def init_log():
        """
        Connects to the NotificationsLog class to retrieve the log from the database
        :return: log: a list of notification objects
        """
        notification_log = NotificationsLog.read_notifications()
        return notification_log

    def init_date_entries(self):
        """
        Limits the selectable dates to no later than today's date
        """
        start_box = self.__start_date_entry
        end_box = self.__end_date_entry
        today = datetime.today()
        start_box.config(maxdate=today)
        end_box.config(maxdate=today, mindate=start_box.get_date())
        start_box.set_date(today)
        end_box.set_date(today)

    def init_treeview(self):
        """
        Function to create treeview columns
        :return: none
        """
        tree = self.__selection_tree
        tree.configure(columns=(0, 1, 2, 3, 4))
        tree['show'] = 'headings'
        # Column names
        tree.heading(0, text="Date/Time")
        tree.heading(1, text="Subject")
        tree.heading(2, text="Message")
        tree.heading(3, text="Sent By")
        tree.heading(4, text="Recipient Count")
        # Column params
        tree.column(0, width=100)
        tree.column(1, width=150)
        tree.column(2, width=150)
        tree.column(3, width=100)
        tree.column(4, width=100)

    def start_date_handler(self, event):
        """
        Detects when the user makes a selection in StartDateEntry
        value is used to determine valid dates for EndComboBox
        :returns: the user's selection
        """
        selection = self.__start_date_entry.get_date()
        end_box = self.__end_date_entry
        if selection > end_box.get_date():
            print("Start date cannot be after end date.")
            return
        print("Start date:", selection)
        end_box.config(mindate=selection)
        self.add_data()

    def end_date_handler(self, event):
        """
        Detects when the user makes a selection in EndComboBox
        value is used to determine valid dates for StartComboBox
        :return: the user's selection
        """
        selection = self.__end_date_entry.get_date()
        start_box = self.__start_date_entry
        print("End date:", selection)
        start_box.config(maxdate=selection)
        self.add_data()

    def treeview_handler(self, event):
        """
        Treeview event handler, detects when an item in the treeview is clicked
        :param event: from tkinter, triggered by user clicking inside treeview
        :return: selection: the treeview node that was selected
        """
        selection = self.__selection_tree.identify('item', event.x, event.y)
        print("You clicked: ", selection)
        self.read_message(selection)

    def add_data(self):
        """
        Function to add data to treeview. Clears data, then populates treeview
        with data. Dates must be between the start and end date (inclusive)
        :return: none
        """
        start_box = self.__start_date_entry
        end_box = self.__end_date_entry
        data = self.init_log()
        print("Start: ", start_box.get_date())
        print("End: ", end_box.get_date())
        # start by clearing the current data
        self.clear_treeview()
        # Loop through data, looking for notifications that are between the selected dates (inclusive)
        for item in data:
            if (start_box.get_date() <= item.get_datetime().date()
                    <= end_box.get_date()):
                self.__selection_tree.insert('', 'end', iid=None, values=(
                    item.get_datetime(), item.get_subject(), item.get_message(), item.get_username(),
                    item.get_recipients()))

    def read_message(self, selection):
        """
        Function to read the contents of a notification selected in treeview
        :param selection: the user's highlighted treeview item, as a node
        :return: none
        """
        tree = self.__selection_tree
        textbox = self.__message_text_box
        # clear any previous data
        textbox.delete('1.0', 'end')
        # create a readable dict from selected row
        row_data = tree.set(selection)
        # check to see if row_data dict is empty before proceeding
        if row_data:
            textbox.insert(1.0, f'Subject: \n {row_data['1']} \n')
            textbox.insert(3.0, f'Message: \n {row_data["2"]}')

    def clear_treeview(self):
        self.__selection_tree.delete(*self.__selection_tree.get_children())

    def clear_text_box(self):
        textbox = self.__message_text_box
        textbox.delete('1.0', 'end')
        textbox.insert(1.0, f'Subject: \n \n')
        textbox.insert(3.0, f'Message: \n')

    def run(self):
        """
        Runs the main window's mainloop
        """
        self.__mainwindow.mainloop()

    def on_clear_button_clicked(self):
        """

        :return:
        """
        print("Clear button clicked")
        self.clear_treeview()
        self.clear_text_box()
        self.init_date_entries()

    # enables exit button to close the window
    def on_exit_button_clicked(self):
        """
        Method for bringing the user back to the login page from teh registration page
        :return: None
        """
        try:
            from ui.LandingUI import LandingUI

            # Close the registration page
            self.__mainwindow.destroy()

            # Run the LoginUI class
            landing_page = LandingUI(user_id=self.user_id)
            landing_page.run()
        except:
            print("Error opening landing page")


if __name__ == "__main__":
    app = NotificationReviewUI()
    app.run()
