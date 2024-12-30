# ----------------------------------------------------------------------------
# Name: SendNotificationSystem.UI
# Owner: Zain Ali
# Date Created: 10/14/2024
# Description: Logic for sending emails
# ----------------------------------------------------------------------------
# Changes:
# 10/14/24 Notification System -Zain Ali.

import smtplib
from data.Database import Database


class Email:
    __user_id = 0
    __server = None

    def __init__(self, user_id):
        """Init function which assigns self.__user_id to user_id"""
        self.__user_id = user_id

    @staticmethod
    def send_email(subject, message, recipient, employee_email, sub_count=None):
        """This function sends the email using 'server' which is an SMTP(Simple Mail Transfer Protocol)"""
        full_message = f"Subject: {subject}\n\n {message}"

        if Email.__server is None:
            Email.__server = Email.server_creation(employee_email)

        try:
            Email.__server.sendmail(employee_email, recipient, full_message)
            if sub_count is not None:
                sub_count += len(recipient)
            print("email: ", recipient)
        except Exception as e:
            print(f"An error occurred: {e}")

        print("Message: ", message)
        print("Subject: ", subject)

        return subject, message, sub_count

    def storing_information(self, subject, message, date_time, sub_count):
        """This function stores the subject, message, date_time, sub_count, and self.__user_id into the database """
        Database.storing_notifications_info(subject, message, date_time, sub_count, self.__user_id)

    @staticmethod
    def server_creation(employee_email):
        """This fucntion creates the smtp server"""
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(employee_email, "euwl cyyu oari ewvx")

        return server

    @staticmethod
    def fetch_emails():
        """ This funciton fetches the emails from the database"""
        from data.Database import Database
        return Database.fetch_emails()

    def get_user_id(self):
        return self.__user_id