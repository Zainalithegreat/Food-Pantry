import unittest
import bcrypt
from logic.User import User as u


class TestUser(unittest.TestCase):
    def test_constructor(self):
        """
        Test that the User constructor correctly initializes Username and Password
        """
        user = u("testuser", "testpassword")

        self.assertEqual(user.getUsername(), "testuser")
        self.assertEqual(user.getPassword(), "testpassword")

    def test_email_validation_valid(self):
        """
        Test the email_validation method and returns True for valid email addresses
        """
        self.assertTrue(u.email_validation("test@example.com"))
        self.assertTrue(u.email_validation("user.name+tag@ex.com"))

    def test_email_validation_invalid(self):
        """
        Test that email_validation method returns False for invalid email addresses
        """
        self.assertFalse(u.email_validation("invalid-email"))
        self.assertFalse(u.email_validation("user@@test.co"))
        self.assertFalse(u.email_validation("user@.com"))

    def test_pass_validation_valid(self):
        """
        Test the pass_validation method and returns True for valid passwords
        """
        self.assertTrue(u.pass_validation("StrongP@ssw0rd"))
        self.assertTrue(u.pass_validation("Valid1!"))

    def test_pass_validation_invalid(self):
        """
        Tests the pass_validation method and returns False for invalid passwords
        """
        self.assertFalse(u.pass_validation("thisisaweakpassword"))
        self.assertFalse(u.pass_validation("NoNumber!"))
        self.assertFalse(u.pass_validation("12345"))

    def test_hash_password(self):
        """
        Tests the hash_password method
        """
        password = "SecureP@ss123"
        hashed_password = u.hash_password(password)
        self.assertTrue(bcrypt.checkpw(password.encode('utf-8'), hashed_password))


if __name__ == "__main__":
    unittest.main()