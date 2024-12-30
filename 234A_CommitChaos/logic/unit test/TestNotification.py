# ----------------------------------------------------------------------------
# Name: TestNotification.py
# Owner: Chip Weatherly
# Date Created: 11/13/2024
# Description: test case for Notification class logic
# ----------------------------------------------------------------------------
# Changes:
# 11/12/2024  Initial creation - Chip Weatherly
import unittest
from datetime import datetime
from logic.Notification import Notification


class TestNotification(unittest.TestCase):

    def setUp(self):
        """
        Defines default values for the unit test
        """
        self.__notification_id = 555
        self.__username = "Chip"
        self.__subject = "The Subject Line"
        self.__datetime = datetime(2024, 11, 12)
        self.__message = "The body of the message in text."
        self.__subscriber_count = 42
        print("TestNotification setup called")

    def test_constructor(self):
        """
        Test creation of a new notification object
        """
        print("Testing Notification constructors")
        # create a new object
        test_notification = Notification(555, "Chip", "The Subject Line",
                                         datetime(2024, 11, 12),
                                         "The body of the message in text.", 42)
        # if all fields match, object is created successfully
        self.assertEqual(test_notification.get_notification_id(), self.__notification_id)
        self.assertEqual(test_notification.get_username(), self.__username)
        self.assertEqual(test_notification.get_subject(), self.__subject)
        self.assertEqual(test_notification.get_datetime(), self.__datetime)
        self.assertEqual(test_notification.get_message(), self.__message)
        self.assertEqual(test_notification.get_recipients(), self.__subscriber_count)

    def test_notification_build(self):
        """
        tests Notification.build() method which assembles notification objects from a dictionary
        """
        print("Testing Notifications.build()")
        # dummy notification dictionary to test, populated with SetUp values
        notification_dict = {
            "NotificationID": self.__notification_id,
            "Username": self.__username,
            "Subject": self.__subject,
            "DateTime": self.__datetime,
            "Message": self.__message,
            "SubscriberCount": self.__subscriber_count
        }
        # create a list of dictionaries to test
        notification_dicts = [notification_dict]
        # create the list of objects from the list of dictionaries
        notifications_log = [Notification.build(notification_dict) for notification_dict in notification_dicts]
        print("List of notification objects: ", notifications_log)
        self.assertEqual(notifications_log[0].get_notification_id(), self.__notification_id)
        self.assertEqual(notifications_log[0].get_username(), self.__username)
        self.assertEqual(notifications_log[0].get_subject(), self.__subject)
        self.assertEqual(notifications_log[0].get_datetime(), self.__datetime)
        self.assertEqual(notifications_log[0].get_message(), self.__message)
        self.assertEqual(notifications_log[0].get_recipients(), self.__subscriber_count)
