# ----------------------------------------------------------------------------
# Name: Notification.py
# Owner: Chip Weatherly
# Date Created: 10/15/2024
# Description: Class definition for the notifications log,
#              which holds an ordered collection of notifications
#              populated from the database
# ----------------------------------------------------------------------------
# 10/16/24 File created -CW
# 11/13/24 Created build_log function, moving one line of logic from database
#          to this class, improving N-tier architecture - CW
from logic.Notification import Notification


class NotificationsLog:
    __notifications = []

    def __init__(self, notifications):
        self.__notifications = notifications

    @staticmethod
    def read_notifications():
        """
        Accesses the database to return a list of dictionaries
        :returns: notification_dicts
        """
        from data.Database import Database

        notification_dicts = Database.read_notifications()
        notifications_log = NotificationsLog.build_log(notification_dicts)
        return notifications_log

    @staticmethod
    def build_log(notification_dicts):
        """
        Accepts a list of Notification dicts and converts them into a list of Notification objects
        :param: notification_dicts
        :returns: notifications_log
        """
        notifications_log = [Notification.build(notification_dict) for notification_dict in notification_dicts]
        return notifications_log
