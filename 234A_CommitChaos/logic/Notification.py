# ----------------------------------------------------------------------------
# Name: Notification.py
# Owner: Chip Weatherly
# Date Created: 10/15/2024
# Description: Class file to define the Notification class,
#              for individual notification log entries
# ----------------------------------------------------------------------------
# Changes:
# 10/15/24 Initial creation -CW
# 10/16/24 Refined naming conventions after creating database - CW
# 10/18/24 Added id and datetime getters, created to_dict method to convert
#          objects into readable dictionaries - CW
# 10/23/24 Reorganized class attributes to exactly match database, and
#          added build method to create Notification objects from database
#          rows - CW
import datetime as dt


class Notification:
    __notification_id = 0
    __username = ""
    __subject = ""
    __datetime = dt.datetime(1, 1, 1)
    __message = ""
    __subscriber_count = 0

    def __init__(self, notification_id, username, subject, datetime, message, subscriber_count):
        self.__notification_id = notification_id
        self.__username = username
        self.__subject = subject
        self.__datetime = datetime
        self.__message = message
        self.__subscriber_count = subscriber_count

    @classmethod
    def build(cls, notification_dict):
        return Notification(
            notification_dict["NotificationID"],
            notification_dict["Username"],
            notification_dict["Subject"],
            notification_dict["DateTime"],
            notification_dict["Message"],
            notification_dict["SubscriberCount"]
        )

    def get_notification_id(self):
        return self.__notification_id

    def get_username(self):
        return self.__username

    def get_subject(self):
        return self.__subject

    def get_datetime(self):
        return self.__datetime

    def get_message(self):
        return self.__message

    def get_recipients(self):
        return self.__subscriber_count
