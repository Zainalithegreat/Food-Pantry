# ----------------------------------------------------------------------------
# Name: main.py
# Owner: Chip Weatherly
# Date Created: 10/10/2024
# Description: main file for running the connected program, currently unused
# ----------------------------------------------------------------------------
# Changes:
# 10/10/24 Initial creation -Chip W.

from ui.LoginUI import LoginUI
from ui.WebUI import WebUI

if __name__ == '__main__':
    app = WebUI()
    app.run()
    # app = LoginUI()
    # app.run()
