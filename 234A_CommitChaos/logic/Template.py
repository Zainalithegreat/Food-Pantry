# ********************************************************************
# Name: Template.py
# Owner: Jiraschaya Freeburn
# Date Created: 10/23/2024
# Description: Template class provide methods to check duplicate
#              template names, and save templates to database.
# *******************************************************************
from data.Database import Database
from datetime import datetime


class Template:
    """
    Defines a template with functions to check for duplicates
    and save entries to the database.
    """
    def __init__(self, name, subject, message, user_id=None):
        # initialize template properties with received values.
        self.name = name
        self.user_id = user_id
        self.subject = subject
        self.message = message
        self.date_time = datetime.now()

    @classmethod
    def check_duplicate(cls, name):
        """
        Checks if a template name already exists in the database.
        :param name: template name to check.
        :return: whether template name already exists.
        """
        return Database.check_duplicate_template(name)

    def save(self):
        """
        Saves the template to the database after validated
        :return: Confirmation of whether the template was saved
                 successfully in the database.
        :raises ValueError: if the values are missing.
        """
        if not self.name or self.user_id is None or not self.subject or not self.message:
            raise ValueError("All values are required.")
        return Database.save_template(self.name, self.user_id,
                                      self.subject, self.message, self.date_time)

    def get_name(self):
        """This function returns the name of the templates"""
        return self.name

    @staticmethod
    def fetch_templates():
        """This function adds templates names to templates
        and then returns templates"""
        templates = []
        rows = Database.fetch_templates()

        for row in rows:
            name, subject, message = row
            template = Template(name, subject, message)
            templates.append(template)

        return templates