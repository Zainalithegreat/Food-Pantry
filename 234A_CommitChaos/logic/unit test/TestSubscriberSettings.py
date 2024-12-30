# ----------------------------------------------------------------------------
# Name: TestSubscriberSettings.py
# Owner: Chip Weatherly
# Date Created: 11/18/2024
# Description: test case for WebUI
# ----------------------------------------------------------------------------
# Changes:
# 11/18/2024  Initial creation - Chip Weatherly
import flask_unittest
from ui.WebUI import WebUI


class TestWebUI(flask_unittest.ClientTestCase):
    app = WebUI.get_app()

    def test_settings_page(self, client):
        client.get('/login')
