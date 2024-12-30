import unittest
from Email import Email
from unittest.mock import patch, Mock, MagicMock
from data.Database import Database


class TestEmail(unittest.TestCase):
    def test_constructor(self):
        test_email = Email(41)
        self.assertEqual(41, test_email.get_user_id())

    @patch('Email.Database')  # Mock the Database class in the Email module
    def test_storing_information(self, mock_database):
        user_id = 41
        test_email = Email(user_id)

        subject = "Test Subject"
        message = "Test Message"
        date_time = "2024-11-16 10:00:00"
        sub_count = 5

        test_email.storing_information(subject, message, date_time, sub_count)

        mock_database.storing_notifications_info.assert_called_once_with(
            subject, message, date_time, sub_count, user_id
        )

    @patch("builtins.print")
    @patch("smtplib.SMTP")
    def test_send_email(self, mock_smtp, mock_print):
        # Arrange
        subject = "Test Subject"
        message = "This is a test message."
        recipient = "recipient@example.com"
        employee_email = "sender@example.com"

        mock_server_instance = MagicMock()
        mock_smtp.return_value = mock_server_instance

        Email._Email__server = None

        result = Email.send_email(subject, message, recipient, employee_email)

        mock_smtp.assert_called_once_with("smtp.gmail.com", 587)
        mock_server_instance.starttls.assert_called_once()
        mock_server_instance.login.assert_called_once_with(employee_email, "euwl cyyu oari ewvx")
        mock_server_instance.sendmail.assert_called_once_with(
            employee_email,
            recipient,
            f"Subject: {subject}\n\n {message}"
        )

        self.assertEqual(result, (subject, message))

        mock_print.assert_any_call("email: ", recipient)
        mock_print.assert_any_call("Message: ", message)
        mock_print.assert_any_call("Subject: ", subject)
        Email.send_email(subject, message, recipient, employee_email)

        mock_smtp.assert_called_once()
        mock_server_instance.sendmail.assert_called_with(
            employee_email,
            recipient,
            f"Subject: {subject}\n\n {message}"
        )
    @patch("smtplib.SMTP")
    def test_server_creation(self, mock_smtp):

        employee_email = "sender@example.com"
        mock_server_instance = Mock()
        mock_smtp.return_value = mock_server_instance

        server = Email.server_creation(employee_email)
        mock_smtp.assert_called_once_with("smtp.gmail.com", 587)
        mock_server_instance.starttls.assert_called_once()
        mock_server_instance.login.assert_called_once_with(employee_email, "euwl cyyu oari ewvx")

        self.assertEqual(server, mock_server_instance)

    @patch("Email.Database.fetch_emails")
    def test_fetch_emails(self, mock_fetch_emails):
        mock_fetch_emails.return_value = [
            {"id": 1, "email": "user1@example.com"},
            {"id": 2, "email": "user2@example.com"},
        ]
        result = Email.fetch_emails()
        mock_fetch_emails.assert_called_once()

        self.assertEqual(result, [
            {"id": 1, "email": "user1@example.com"},
            {"id": 2, "email": "user2@example.com"},
        ])

