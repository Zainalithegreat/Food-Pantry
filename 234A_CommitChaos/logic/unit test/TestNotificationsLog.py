# ----------------------------------------------------------------------------
# Name: TestNotification.py
# Owner: Chip Weatherly
# Date Created: 11/13/2024
# Description: test case for Notification class logic
# ----------------------------------------------------------------------------
# Changes:
# 11/13/2024  Initial creation - Chip Weatherly
import unittest
from datetime import datetime
from logic.Notification import Notification
from logic.NotificationsLog import NotificationsLog


class TestNotification(unittest.TestCase):
    def setUp(self):
        """
        Creates a list of Notification objects containing 1 Notification object for testing
        """
        self.__notifications = [Notification(555, "Chip", "The Subject Line",
                                             datetime(2024, 11, 12),
                                             "The body of the message in text.", 42)]
        print("TestNotificationsLog setup called")

    def test_build_log(self):
        """
        test NotificationsLog.build_log(); accepts a list of dicts and converts to a list of Notification objects
        """
        print("Testing NotificationsLog.build_log()")
        # create a notification dict matching setUp
        notification_dict = {
            "NotificationID": 555,
            "Username": "Chip",
            "Subject": "The Subject Line",
            "DateTime": datetime(2024, 11, 12),
            "Message": "The body of the message in text.",
            "SubscriberCount": 42
        }
        # hold the dict in a list of dicts
        notification_dicts = [notification_dict]
        # build the log from the list of dicts
        notifications_log = NotificationsLog.build_log(notification_dicts)
        self.assertEqual(notifications_log[0].get_notification_id(), 555)
        self.assertEqual(notifications_log[0].get_username(), "Chip")
        self.assertEqual(notifications_log[0].get_subject(), "The Subject Line")
        self.assertEqual(notifications_log[0].get_datetime(), datetime(2024, 11, 12))
        self.assertEqual(notifications_log[0].get_message(), "The body of the message in text.")
        self.assertEqual(notifications_log[0].get_recipients(), 42)

