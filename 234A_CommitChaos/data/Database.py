# ----------------------------------------------------------------------------
# Name: Database.py
# Owner: Chip Weatherly, Bjorn Ingermann, Zain Ali, JJ Freeburn
# Date Created: 10/10/2024
# Description: holds Database class
# ----------------------------------------------------------------------------
# Changes:
# 10/10/24  Initial creation - Chip W.
# 10/15/24  Initial creation & population with placeholder data - CW
# 10/16/24  Added database connection - Björn I.
# 10/16/24  Altered get_notifications to return a list of dictionaries - CW
# 10/18/24  Reverted dictionaries change. Accessing the objects can be useful.
#           Will convert to dictionaries on case-by-case basis - CW
# 10/18/24  Added the class Database(connect function, fetch_emails) - Zain Ali.
# 10/22/24  Imported pymssql, added basic connection to database
# 10/23/24  Reorganized database class to match team design. Added error
#           exceptions in case of failed connections. Added get_cursor,
#           close_connection, and read_notifications functions - CW
# 10/23/24  Added user check method to see if a user exists - Björn I.
#           Close method added to close connection when not being used
#           Modified fetch function to check for pass hashes
# 10/29/24  Merged Database.py files to master - Everyone
# 11/01/24  Added fetch_templates, get_email, get_name, get_user_id, get_template_message, get_template_subject,
#           get_template_name, storing_notifications_info, get_email, fetch_templates
# 11/12/24  Moved SQL queries from RegisterUI.py to Database.py


import pymssql
import bcrypt

from tkinter import messagebox
from logic.Notification import Notification


class Database:
    __connection = None

    @classmethod
    def connect(cls):
        # the connection variables
        if cls.__connection is None:
            try:
                cls.__connection = pymssql.connect(
                    server="cisdbss.pcc.edu",
                    database="234A_CommitChaos",
                    user="234A_CommitChaos",
                    password="MyLuckyCodes7#",
                    charset="LATIN1"
                )
                print(cls.__connection)
            except pymssql.DatabaseError as e:
                print(f"Database connection failed: {e}")
                cls.__connection = None

    @classmethod
    def get_cursor(cls):
        """
        Class to create a cursor for executing queries
        :return: cursor
        """
        if cls.__connection is None:
            cls.connect()
        return cls.__connection.cursor()

    @classmethod
    def close_connection(cls):
        """
        Close the connection to the database
        """
        if cls.__connection:
            cls.__connection.close()
            cls.__connection = None

    @classmethod
    def add_user(cls, username, hashed_password, name, email, role='Subscriber'):
        """
        Adds a new user into the Users table
        :param username: str - Username for the new user
        :param hashed_password: bytes - Hashed and salted password
        :param name: str - Name of the user
        :param email: str - Email of the user
        :param role: str - Role of the user, default is 'Subscriber'
        :return: True if registration is successful, False otherwise
        """
        sql = """
        INSERT INTO Users (Username, Password, Name, Email, Role)
        VALUES (%s, %s, %s, %s, %s)
        """

        # Create a cursor and execute the insert query
        cursor = cls.get_cursor()

        try:
            # Execute the query
            cursor.execute(sql, (username, hashed_password, name, email, role))

            # Commit the changes to the database
            cls.__connection.commit()

            print("User created successfully.")

            # Close connection and existing cursor
            if cursor:
                cursor.close()
            cls.close_connection()
            return True
        except pymssql.DatabaseError as e:
            # Print error message
            messagebox.showerror("Database Insertion Error", f"Database insert failed: {e}")
            # Close connection and existing cursor
            if cursor:
                cursor.close()
            cls.close_connection()

            # Rollback any changes and return false
            cls.__connection.rollback()
            return False

    @classmethod
    def update_password(cls, hashed_password, user_id):
        """
        Updates the password of the user
        :param hashed_password: bytes - Hashed and salted password
        """
        sql = """
        UPDATE Users
        SET Password = %s
        WHERE UserID = %s
        """
        cursor = cls.get_cursor()

        cursor.execute(sql, (hashed_password, user_id))
        cls.__connection.commit()
        if cursor:
            cursor.close()
        cls.close_connection()
        print("Password updated")

    @classmethod
    def unsubscribe_user(cls, user_id):
        """
        Updates a user's unsubscribe value in the user table to 1. Located using userID.
        :param: user_id: int
        """
        sql = """
              UPDATE Users
              SET    Unsubscribed = 1
              WHERE  UserID = %s
              """
        cursor = cls.get_cursor()
        cursor.execute(sql, (user_id,))
        cls.__connection.commit()
        if cursor:
            cursor.close()
        cls.close_connection()
        print("Unsubscribe successful")

    @classmethod
    def subscribe_user(cls, user_id):
        """
        Updates a user's unsubscribe value in the user table to 0. Located using userID.
        :param: user_id: int
        """
        sql = """
                  UPDATE Users
                  SET    Unsubscribed = 0
                  WHERE  UserID = %s
                  """
        cursor = cls.get_cursor()
        cursor.execute(sql, (user_id,))
        cls.__connection.commit()
        print("Subscription successful")

    @classmethod
    def fetch_user(cls, user_or_email, password, is_email=False):
        """
        Method to fetch a user from the database.
        :param user_or_email: username or email used for login
        :param password: password provided by the user
        :param is_email: flag to check if login is via email
        :return: found user, if valid credentials
        """
        if is_email:
            sql = """
                  SELECT  UserID, 1, Email, Password, Role
                  FROM Users
                  WHERE Email = %s;
                  """
        else:
            sql = """
                  SELECT  UserID, Username, Email, Password, Role
                  FROM Users
                  WHERE Username = %s;
                  """

        cursor = cls.get_cursor()
        cursor.execute(sql, (user_or_email,))
        result = cursor.fetchone()

        if result and cls.check_password(result[3], password):
            return result[0]
        else:
            return None

    @classmethod
    def fetch_user_object(cls, user_id):
        """
        Method to fetch a user object from the database.
        :param user_id: user_id, str
        :return: user object, if valid credentials
        """
        from logic.User import User
        sql = """
                SELECT UserID, Username, Password, Name, Email, Role, Unsubscribed
                FROM Users
                WHERE UserID = %s;
              """

        cursor = cls.get_cursor()
        cursor.execute(sql, user_id)
        result = cursor.fetchone()

        if result:
            user = User(result[1], result[2])
            user.setUserID(result[0])
            user.setName(result[3])
            user.setEmail(result[4])
            user.setRole(result[5])
            user.setUnsubscribed(result[6])
            return user
        else:
            return None

    @classmethod
    def check_duplicate_template(cls, template_name):
        """
        Check for template name duplication.
        """
        cursor = cls.get_cursor()
        try:
            sql = """
                  SELECT COUNT(*) FROM Templates 
                  WHERE TempName=%s
                  """
            cursor.execute(sql,(template_name,))
            result = cursor.fetchone()
            return result[0] > 0
        except pymssql.DatabaseError as e:
            print(f"Database connection failed: {e}")
            return False

    @classmethod
    def save_template(cls,template_name, user_id, subject, message, date_time):
        """
        save template to database.
        """
        cursor = cls.get_cursor()
        try:
            sql = """
                  INSERT INTO Templates (TempName, UserID, Subject, Message, DateTime)
                  VALUES (%s, %s, %s, %s,%s)
                  """
            cursor.execute(sql, (template_name, user_id, subject, message, date_time))
            cls.__connection.commit()
            return True
        except pymssql.DatabaseError as e:
            print(f"Database connection failed: {e}")
            cls.__connection.rollback()
            return False

    @classmethod
    def check_password(cls, stored_password, provided_password):
        """
        Method to check the stored password against provided password, and ensure
        the stored password is in bytes
        :param stored_password:
        :param provided_password:
        :return:
        """
        # Ensure stored password is in bytes, not string
        if isinstance(stored_password, str):
            stored_password = stored_password.encode('utf-8')

        return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password)

    @classmethod
    def change_password(cls, user_id, new_password):
        """
        Method to change the stored password.
        :param user_id: int, used to locate the user
        """
        sql = """
        UPDATE Users
        SET Password = %s
        WHERE UserID = %s"""

        cursor = cls.get_cursor()
        cursor.execute(sql, (new_password, user_id))

    @classmethod
    def read_users(cls):
        """
        Read the database and create a list of users
        :return:
        """
        sql = """
              SELECT *
              FROM Users
              ORDER BY UserID ASC;
              """

        # Create cursor and execute query
        cursor = cls.get_cursor()
        cursor.execute(sql)

        users = []
        user = cursor.fetchone()
        while user is not None:
            users.append(user)
            user = cursor.fetchone()

        for i in users:
            print(i)

        return users

    @classmethod
    def check_users(cls, username = None, email = None):
        """
        Checks if a user already exists with the passed credentials
        :return: true if the user exists or false if they do not
        """

        sql = """
              SELECT COUNT(*)
              FROM Users
              WHERE Username = %s OR Email = %s;
              """

        cursor = cls.get_cursor()
        cursor.execute(sql, (username, email))
        count = cursor.fetchone()[0]
        return count > 0

    @classmethod
    def fetch_emails(cls):
        cls.connect()
        cursor = cls.get_cursor()

        sql = """
              SELECT Email
              FROM   Users
              WHERE  Unsubscribed = 0
              """
        cursor.execute(sql)
        rows = cursor.fetchall()

        user_emails = [row[0] for row in rows]
        return user_emails

    @classmethod
    def storing_notifications_info(cls, subject, message, date_time, sub_count, user_id):
        sql = """
            INSERT INTO Notifications (UserId, Subject, DateTime, Message, SubscriberCount)
            VALUES (%s, %s, %s, %s, %s)
            """
        cursor = cls.get_cursor()
        cursor.execute(sql, (user_id, subject, date_time, message, sub_count))
        cls.__connection.commit()

    @classmethod
    def get_template_name(cls):
        cls.connect()
        cursor = cls.get_cursor()
        sql = """
              SELECT TempName
              FROM Templates
              """
        cursor.execute(sql)
        rows = cursor.fetchall()

        temp_name = [row[0] for row in rows]
        return temp_name

    @classmethod
    def get_template_subject(cls):
        cls.connect()
        cursor = cls.get_cursor()
        sql = """
              SELECT Subject
              FROM Templates
              """
        cursor.execute(sql)
        rows = cursor.fetchall()

        temp_subject = [row[0] for row in rows]
        return temp_subject

    @classmethod
    def get_template_message(cls):
        cls.connect()
        cursor = cls.get_cursor()
        sql = """
              SELECT Message
              FROM Templates
              """
        cursor.execute(sql)
        rows = cursor.fetchall()

        temp_message = [row[0] for row in rows]
        return temp_message

    @classmethod
    def read_notifications(cls):
        """
        Retrieves the notifications objects from the database. Replaces UserID
        with Username from Users table, determined from UserID
        :returns: list of notifications dicts as notifications_log
        """
        cursor = cls.get_cursor()
        notifications_log = []
        try:
            sql = """
                  SELECT N.NotificationID, U.Username, N.Subject, N.DateTime, N.Message, N.SubscriberCount
                  FROM Notifications AS N
                  JOIN Users AS U ON U.UserID = N.UserID
                  ORDER BY N.DateTime
                  """
            cursor.execute(sql)
            desc = cursor.description
            column_names = [col[0] for col in desc]
            notification_dicts = [dict(zip(column_names, row)) for row in cursor.fetchall()]
            return notification_dicts
        except pymssql.DatabaseError as e:
            print(f"Database connection failed: {e}")
            cls.__connection = None
            return False

    @classmethod
    def dummy_data(cls):
        """
        Creates dummy notification objects and store them in a list
        Not used, but useful for troubleshooting
        :returns: notification_dicts, a list of dictionaries
        """
        # reusable message for dummy data
        message = ("Hello Subscribers, as of today we have some fresh food "
                   "available that will expire before tomorrow. Come and get it!")
        # notification_id, datetime, user_id(sender), recipients, subject, message
        notification_1 = Notification(1, '01-10-2024', 'Chip', 56,
                                      "Fresh Food In Stock", message)
        notification_2 = Notification(2, '10-12-2024', 'Bjorn', 32,
                                      "Expiration Warning!", message)
        # list of notification objects
        notifications_log = [notification_1, notification_2]
        return notifications_log

    @classmethod
    def get_user_id(cls, username):
        sql = """
                   SELECT UserID
                   FROM   Users
                   WHERE  Username = %s
                   """

        cursor = cls.get_cursor()
        cursor.execute(sql, (username,))
        result = cursor.fetchone()
        # print("result: ", result)
        return result

    @classmethod
    def get_name(cls, username):
        sql = """
                   SELECT Name
                   FROM   Users
                   WHERE  Username = %s
                   """

        cursor = cls.get_cursor()
        cursor.execute(sql, (username,))
        result = cursor.fetchone()
        print("result: ", result)
        return result

    @classmethod
    def get_email(cls, username):
        sql = """
                   SELECT Email
                   FROM   Users
                   WHERE  Username = %s
                   """

        cursor = cls.get_cursor()
        cursor.execute(sql, (username,))
        result = cursor.fetchone()
        print("result: ", result)
        return result

    @classmethod
    def fetch_templates(cls):
        sql = """
                   SELECT TempName, Subject, Message
                   FROM   Templates
                   """
        cursor = cls.get_cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        return result

    @classmethod
    def check_user(cls, username, email):
        sql = """
                   SELECT * 
                   FROM Users 
                   WHERE Username = %s OR Email = %s
               """
        cursor = cls.get_cursor()
        cursor.execute(sql, (username, email))
        if cursor.fetchone():  # If a record is found, return False
            print("Username or email already exists.")
            return False

        return True
    @classmethod
    def get_userid_email(cls, email):
        sql = """
                    SELECT UserID
                    FROM Users 
                    WHERE Email = %s
                """

        cursor = cls.get_cursor()
        cursor.execute(sql, (email,))
        result = cursor.fetchall()
        return result

    @classmethod
    def get_user(cls, user_id):
        sql = """
                    SELECT Username
                    FROM Users 
                    WHERE UserID = %s
                """
        cursor = cls.get_cursor()
        cursor.execute(sql, (user_id,))
        result = cursor.fetchone()
        return result

    @classmethod
    def change_username(cls, user_input, user_id):
        sql = """
               UPDATE Users
               SET Username = %s
               WHERE UserID = %s
               """
        cursor = cls.get_cursor()

        cursor.execute(sql, (user_input, user_id))
        cls.__connection.commit()
        if cursor:
            cursor.close()
        cls.close_connection()
        print("Username updated")

    @classmethod
    def change_email(cls, user_input, user_id):
        sql = """
               UPDATE Users
               SET Email = %s
               WHERE UserID = %s
               """
        cursor = cls.get_cursor()

        cursor.execute(sql, (user_input, user_id))
        cls.__connection.commit()
        if cursor:
            cursor.close()
        cls.close_connection()
        print("Email updated")

    @classmethod
    def check_username(cls, username):
        sql = """
                      SELECT * 
                      FROM Users 
                      WHERE Username = %s
                  """
        cursor = cls.get_cursor()
        cursor.execute(sql, (username,))
        if cursor.fetchone():  # If a record is found, return True
            print("Username already exists.")
            return True

        return False

    @classmethod
    def check_email(cls, email):
        sql = """
                      SELECT * 
                      FROM Users 
                      WHERE Email = %s
                  """
        cursor = cls.get_cursor()
        cursor.execute(sql, (email,))
        if cursor.fetchone():  # If a record is found, return True
            print("Username already exists.")
            return True

        return False

    @classmethod
    def delete_account(cls, user_id):
        sql = """
                          DELETE
                          FROM Users 
                          WHERE UserID = %s
                      """
        cursor = cls.get_cursor()
        cursor.execute(sql, (user_id,))
        cls.__connection.commit()
        if cursor:
            cursor.close()
        cls.close_connection()
        print("Account Deleted")

    @classmethod
    def get_email_from_userid(cls, user_id):
        sql = """
                             SELECT Email
                             FROM Users 
                             WHERE UserID = %s
                         """
        cursor = cls.get_cursor()
        cursor.execute(sql, (user_id,))
        result = cursor.fetchone()
        return result

    @classmethod
    def get_subbed(cls, user_id):
        sql = """
                                     SELECT Unsubscribed
                                     FROM Users 
                                     WHERE UserID = %s
                                 """
        cursor = cls.get_cursor()
        cursor.execute(sql, (user_id,))
        result = cursor.fetchone()
        return result




# if __name__ == "__main__":
#     Database.connect()
#     Database.read_users()
