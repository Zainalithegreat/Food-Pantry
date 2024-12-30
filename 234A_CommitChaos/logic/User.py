# ----------------------------------------------------------------------------
# Name: User.py
# Owner: Björn Ingermann
# Date Created: 10/20/2024
# Description: holds User class to interact with the database class
# ----------------------------------------------------------------------------
# Changes:
# 10/20/2024    Björn Ingermann
#       Initial creation
#       Created User class with getters and setters
import re
import bcrypt

from data.Database import Database


class User:
    # __UserID = 0
    __Username = ""
    __Password = ""

    # __Name = ""
    # __Email = ""
    # __Role = ""

    def __init__(self, Username, Password=None):
        self.__Username = Username
        self.__Password = Password

    def getUserID(self):
        user_id = Database.get_user_id(self.__Username)
        return user_id

    def getUsername(self):
        return self.__Username

    def getPassword(self):
        return self.__Password

    def getName(self):
        name = Database.get_name(self.__Username)
        return name

    def getEmail(self):
        email = Database.get_email(self.__Username)
        return email

    def getRole(self):
        return self.__Role

    def getKey(self):
        return self.__Username.lower()

    def setUserID(self, UserID):
        self.__UserID = UserID

    def setUsername(self, Username):
        self.__Username = Username

    def setPassword(self, Password):
        self.__Password = Password

    def setName(self, Name):
        self.__Name = Name

    def setEmail(self, Email):
        self.__Email = Email

    def setRole(self, Role):
        self.__Role = Role

    def setUnsubscribed(self, Unsubscribed):
        self.__Unsubscribed = Unsubscribed

    @staticmethod
    def fetch_user(user_or_email, password, is_email):
        from data.Database import Database

        return Database.fetch_user(user_or_email, password, is_email)

    @staticmethod
    def fetch_user_object(user_id):
        from data.Database import Database

        return Database.fetch_user_object(user_id)

    @staticmethod
    def add_user(username, hashed_password, name, email):
        """
        Calls the Database method to register a new user
        :param username: str - Username for the new user
        :param hashed_password: bytes - Hashed password for the new user
        :param name: str - Name of the user
        :param email: str - Email of the user
        :return: True if registration is successful, False otherwise
        """
        return Database.add_user(username, hashed_password, name, email)

    @staticmethod
    def unsubscribe_user(user_id):
        """
        Updates a user's Unsubscribed column, located by name
        :param: username: str - Username
        """
        from data.Database import Database

        return Database.unsubscribe_user(user_id)

    @staticmethod
    def subscribe_user(user_id):
        """
        Updates a user's Unsubscribed column, located by name
        :param: username: str - Username
        """
        from data.Database import Database

        return Database.subscribe_user(user_id)

    @staticmethod
    def update_password(hashed_password, user_id):
        """
        Updates a user's password in the database. Only reached after login and confirmation code
        """
        print(user_id)
        from data.Database import Database

        return Database.update_password(hashed_password, user_id)

    @staticmethod
    def email_validation(email):
        """
        Checks if the email is valid, or validates that teh passed string is an email
        :param email: str
        :return: true for valid, false if not
        """

        # Pattern found at https://www.mailercheck.com/articles/email-validation-using-python
        pattern = r"^(?!\.)(?!.*\.\.)[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    @staticmethod
    def pass_validation(password):
        """
        Checks if the password is valid
        :param password: str
        :return: true if valid, false if not
        """
        length_check = len(password) >= 5
        number_check = re.search(r'\d', password)
        special_check = re.search(r'[!@#$%^&*(),.?":{}|<>]', password)
        return length_check and number_check and special_check

    @staticmethod
    def hash_password(password):
        # Create a salt and hash the password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

        return hashed_password

    @staticmethod
    def get_userid_email(email):
        from data.Database import Database

        return Database.get_userid_email(email)

    @staticmethod
    def get_user(user_id):
        from data.Database import Database

        return Database.get_user(user_id)

    @staticmethod
    def change_username(user_input, user_id):
        from data.Database import Database
        Database.change_username(user_input, user_id)

    @staticmethod
    def check_user(user_input):
        from data.Database import Database
        return Database.check_username(user_input)

    @staticmethod
    def change_email(user_input, user_id):
        from data.Database import Database
        Database.change_email(user_input, user_id)

    @staticmethod
    def check_email(user_input):
        from data.Database import Database
        return Database.check_email(user_input)

    @staticmethod
    def delete_account(user_id):
        from data.Database import Database
        return Database.delete_account(user_id)

    @staticmethod
    def check_user_email(username, email):
        from data.Database import Database
        return Database.check_user(username, email)

    @staticmethod
    def get_email_from_userid(user_id):
        from data.Database import Database
        return Database.get_email_from_userid(user_id)


    @staticmethod
    def get_subbed(user_id):
        from data.Database import Database
        return Database.get_subbed(user_id)


# if __name__ == '__main__':
#     user_instance = User("Zain", 12345)
#     user_instance.getName()
#     user_instance.getEmail()
