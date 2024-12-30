# ********************************************************************
# Name: TemplateCreationUI.
# Owner: Jiraschaya Freeburn
# Date Created: 11/12/2024
# Description: Unit testing
# ********************************************************************
import unittest
from logic.Template import Template

class TestTemplate(unittest.TestCase):
    # Test the constructor of the Template class
    def test_constructor(self):
        test_template = Template("Test Template", "Template Subject",
                                 "Template Message", user_id= "123")
        self.assertEqual(test_template.name, "Test Template")
        self.assertEqual(test_template.subject, "Template Subject")
        self.assertEqual(test_template.message, "Template Message")
        self.assertEqual(test_template.user_id, "123")

    # Test to check if the Template class can detect duplicate templates name
    def test_check_duplicate(self):
        duplicate_template = Template.check_duplicate("Demo")
        self.assertEqual(True, duplicate_template)

    # Test the save function to ensure it correctly saves a valid template
    def test_save_template(self):
        test_template = Template("Test Template", "Template Subject",
                                 "Template Message", user_id="41")
        saved_template = test_template.save()
        self.assertEqual(True, saved_template)

    # Test the save function with incomplete fields if it raised exception
    def test_incomplete_template_fields(self):
        test_incomplete_template = Template("", "Template Subject",
                                 "Template Message", user_id="41")
        with self.assertRaises(Exception) as context:
            test_incomplete_template.save()
        self.assertEqual(str(context.exception), "All values are required.")

    # Test the get_name method
    def test_get_name(self):
        test_template = Template("Test Template", "Template Subject","Template Message",)
        self.assertEqual(test_template.get_name(), "Test Template")







