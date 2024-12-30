# ----------------------------------------------------------------------------
# Name: WebUI.py
# Owner: Chip Weatherly
# Date Created: 11/18/2024
# Description: Holds the WebUI class, containing Flask routes
# ----------------------------------------------------------------------------
# Changes:
# 11/18/2024 Initial creation -CW
from flask import Flask, render_template, request, session, redirect, url_for
from flask_session import Session
from sqlalchemy.orm.base import state_str

from logic.User import User
from logic.UserState import UserState
import ui.routes
import os
import bcrypt


class WebUI:
    # __app is what returns when the main flask constructor is called
    __app = Flask(__name__, template_folder='templates', static_folder='static')
    # this line forces flask to use the correct directory, otherwise it puts the folder in /ui
    __app.config["SESSION_FILE_DIR"] = "/flask_session"

    # these "paths" are the pages that will be allowed to the user BEFORE they log in
    ALLOWED_PATHS = [
        "/",
        "/login",
        "/do_login",
        "/static/web_ui.css",
        "/static/PCC_logo.png",
        "/reset_password",
        "/user_do_reset_password",
        "/do_reset_password",
        "/register",
        "/do_register",
        "/do_confirmation"
    ]
    # saving menu options as data in a constant
    # placeholder; illustrates correct syntax
    MENU = {
        "Notification Settings": {
            "unsubscribe_emails": "Unsubscribe from our email notifications.",
            "subscribe_emails": "Subscribe to Food Pantry notifications."
        },
        "Update Information": {
            "change_password": "Change the password associated with the account.",
        }
    }

    @classmethod
    def get_app(cls):
        return cls.__app

    # Determine if a user is logged in
    @classmethod
    def get_user(cls):
        if "user" in session:
            return session["user"]
        return None

    @classmethod
    def validate_field(cls, field_name):
        if field_name not in request.form:
            return None, render_template("error.html",
                                         message_header=
                                         f"{field_name.title()} cannot be empty!",
                                         message_body=
                                         f"No {field_name} was specified.")
        # .strip() removes leading & trailing whitespace from entries
        field_value = request.form[field_name].strip()
        if field_value == "":
            return None, render_template("error.html",
                                         message_header=
                                         f"{field_name.title()} cannot be empty!",
                                         message_body=
                                         f"No {field_name} was specified.")
        return field_value, None

    # if a user is not logged in, defaults to homepage
    @staticmethod
    @__app.before_request
    def before_request():
        """
        Called before each request to check if the user is logged in, if not it redirects to the homepage
        :return: homepage if not logged in
        """
        if "user" not in session:
            if request.path not in WebUI.ALLOWED_PATHS:
                return redirect(url_for('homepage'))
            return
        # Get user state
        user_state = UserState.lookup(WebUI.get_user_key())
        # Create new user state is user_state is none
        if user_state is None:
            UserState(WebUI.get_user())

    @classmethod
    def get_user_key(cls):
        """
        Returns the user key for the current user, if no user it returns none
        """
        user = session["user"]
        if user is None:
            return None
        else:
            try:
                return user.getKey()
            except AttributeError:
                return None

    @classmethod
    def login(cls, user):
        """
        logs in the passed-in user
        """
        session["user"] = user
        UserState(user)

    @classmethod
    def logout(cls):
        """
        Log out the user
        """
        UserState.logout(WebUI.get_user_key())

    @staticmethod
    @__app.route('/index')
    @__app.route('/index.html')
    @__app.route('/index.php')
    @__app.route('/')
    # render_template(file name): looks up a template in the templates folder
    # Example:
    def homepage():
        """
        Renders the subscriber settings page
        """
        from ui.routes.UserRoutes import UserRoutes
        redirect_response = UserRoutes.redirect_on_role()
        if redirect_response:
            return redirect_response
        return render_template("homepage.html",
                               options=WebUI.MENU)

    @classmethod
    def run(cls):
        # causes routes to be added to app object on run
        # pycharm says they are unused (greyed out), but it is incorrect, they are needed
        from ui.routes.UserRoutes import UserRoutes
        from ui.routes.SettingsRoutes import SettingsRoutes

        if "APPDATA" in os.environ:
            path = os.environ["APPDATA"]
        elif "HOME" in os.environ:
            path = os.environ["HOME"]
        else:
            raise Exception("Couldn't find config folder.")

        # identifies web server session
        cls.__app.secret_key = bcrypt.gensalt()
        # stores session in session files
        cls.__app.config["SESSION_TYPE"] = "filesystem"
        # constructs new session object which handles requests to the flask app
        Session(cls.__app)
        # paths may need to be adjusted, currently placeholders
        cls.__app.run(host="0.0.0.0", port=8444, ssl_context=(path + "/234A_CommitChaos/cert.pem",
                                                              path + "/234A_CommitChaos/key.pem"))


if __name__ == '__main__':
    WebUI.run()
