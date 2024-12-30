# ----------------------------------------------------------------------------
# Name: LandingUI.py
# Owner: Björn Ingermann
# Date Created: 10/28/2024
# Description: class file for landing ui
# ----------------------------------------------------------------------------
# Changes:
# 10/28/24  Initial creation - Björn Ingermann
#           Added page launch methods for buttons

import pathlib
import tkinter as tk
import pygubu


PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "templates\\pygubu_landing_gui.ui"


class LandingUI:
    def __init__(self, master=None, user_id=None):
        self.user_id = user_id
        self.builder = builder = pygubu.Builder()
        builder.add_resource_path(PROJECT_PATH)
        builder.add_from_file(PROJECT_UI)
        # Main widget
        self.landing: tk.Toplevel = builder.get_object("toplevel1", master)
        builder.connect_callbacks(self)

    def notification_creation(self):
        """
        Close the landing page and open the notification creation page
        """
        try:
            from ui.SendNotificationSystem import SendNotificationSystemApp

            # Close the Notification page
            self.landing.destroy()

            notification_creation = SendNotificationSystemApp(user_id=self.user_id)
            notification_creation.run()
        except Exception as e:
            print("Error opening notification creation page:", e)

    def notification_review(self):
        """
        Close the landing page and open the notification review page
        """
        try:
            from ui.NotificationReviewUI import NotificationReviewUI

            self.landing.destroy()

            notification_review = NotificationReviewUI(user_id=self.user_id)
            notification_review.run()
        except Exception as e:
            print("Error opening notification review page:", e)

    def template_creation(self):
        """
        Close the landing page and open the template creation page
        """
        try:
            from ui.TemplateCreationUI import TemplateCreationUI

            self.landing.destroy()

            template_creation = TemplateCreationUI(user_id=self.user_id)
            template_creation.run()
        except Exception as e:
            print("Error opening template creation page:", e)


    def subscriber_page(self):
        """
                Close the landing page and open the subscriber setting page
                """
        try:
            from ui.SubscriberSetting import SubscriberSettingsUI

            self.landing.destroy()

            subscriber_page = SubscriberSettingsUI(user_id=self.user_id)
            subscriber_page.run()
        except Exception as e:
            print("Error opening template creation page:", e)

    def on_exit_button_clicked(self):
        """
        Method for closing the window
        :return: None
        """
        self.landing.destroy()

    def run(self):
        self.landing.mainloop()


if __name__ == "__main__":
    app = LandingUI()
    app.run()
