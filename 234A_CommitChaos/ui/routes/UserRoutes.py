# ----------------------------------------------------------------------------
# Name: UserRoutes.py
# Owner: Chip Weatherly
# Date Created: 11/18/2024
# Description: holds logic for managing user logins in WebUI
# ----------------------------------------------------------------------------
# Changes:
# 11/18/2024 Initial creation -CW
import random
import time

from logic.Email import Email
from ui.LoginUI import LoginUI
from ui.WebUI import WebUI
from flask import render_template, request, session, redirect, url_for, flash
from logic.User import User
from data.Database import Database


class UserRoutes:
    # Retrieve the app instance from WebUI
    __app = WebUI.get_app()

    @staticmethod
    @__app.route("/set_user")
    def set_user():
        """
        Used to set the user manually through the browser, not used in finished product
        syntax example: 'set_user?username=sub' logs in as user 'sub'
        """
        if "user_id" in request.args:
            user = User.fetch_user_object(request.args["user_id"])
            session["user"] = user
            return "User set."
        if "username" in session:
            del session["username"]
        return "User cleared."

    @staticmethod
    @__app.route("/login")
    def login():
        # render the login html
        redirect_response = UserRoutes.redirect_on_role()
        if redirect_response:
            return redirect_response
        return render_template("user/login.html")

    # login.html points here to "do_login", successful login leads to homepage
    @staticmethod
    @__app.route("/do_login", methods=["GET", "POST"])
    def do_login():
        """
        Validates user credentials, matches them with database records,
        and redirects based on user role.
        """
        redirect_response = UserRoutes.redirect_on_role()
        if redirect_response:
            return redirect_response

        session['action'] = 'login'

        user_or_email = request.form.get("username")
        password = request.form.get("password")

        login_creds = (user_or_email, password)

        login_ui = LoginUI(platform='web')
        error = login_ui.user_login(platform='web', web_info=login_creds)

        if error:
            error_message = error
            return render_template(
                "user/login.html",
                error_message=error_message
            )

        return render_template("user/confirmation.html")

    @staticmethod
    @__app.route("/register")
    def register():
        redirect_response = UserRoutes.redirect_on_role()
        if redirect_response:
            return redirect_response
        return render_template("user/register.html")

    @staticmethod
    @__app.route("/do_register", methods=["POST"])
    def do_register():
        from ui.RegisterUI import RegisterUI

        redirect_response = UserRoutes.redirect_on_role()
        if redirect_response:
            return redirect_response

        session['action'] = 'register'

        name = request.form.get("name")
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        password_confirm = request.form.get("password_confirm")

        registration_creds = (name, username, email, password, password_confirm)

        register_ui = RegisterUI(platform='web')
        error = register_ui.confirm_registration(platform='web', web_info=registration_creds)

        if error:
            error_message, error_field = error
            return render_template(
                "user/register.html",
                error_message=error_message,
                error_field=error_field,
                name=name,
                username=username,
                email=email,
            )

        # After sending the email and generating the code, render the confirmation page
        return render_template("user/confirmation.html")

    @staticmethod
    @__app.route("/reset_password")
    def reset_password():
        redirect_response = UserRoutes.redirect_on_role()
        if redirect_response:
            return redirect_response
        return render_template("user/username.html")

    @staticmethod
    @__app.route("/user_do_reset_password", methods=["POST"])
    def user_do_reset_password():
        from ui.RegisterUI import RegisterUI
        redirect_response = UserRoutes.redirect_on_role()
        if redirect_response:
            return redirect_response

        session["action"] = "reset"

        user_input = request.form.get("username")
        email = User.email_validation(user_input)
        if email:  # Input is an email
            user_id = User.get_userid_email(user_input)
            if not user_id:
                flash("No user found with the provided email.", "error")
                return
            user_email = user_input
            session["reset_email"] = user_email
            user_id = user_id[0][0]
            session["user_id"] = user_id
        else:
            user_instance = User(user_input)
            user_id = user_instance.getUserID()
            user_email = user_instance.getEmail()
            session["reset_email"] = user_email
            session["user_id"] = user_id

        if not user_id or not user_email:
            flash("No user found with the provided details.", "error")
            return

        register_instance = RegisterUI(platform="web")
        register_instance.send_confirmation_code(user_id, user_email, platform="web")

        return render_template("user/confirmation.html")

    @staticmethod
    @__app.route("/do_reset_password", methods=["POST"])
    def do_reset_password():
        from ui.PasswordReset import PasswordResetUI

        redirect_response = UserRoutes.redirect_on_role()
        if redirect_response:
            return redirect_response

        # Get form data
        password = request.form.get("password")
        confirm_password = request.form.get("password_confirm")

        # Check for missing fields
        if not password or not confirm_password:
            flash("Both password fields are required.", "error")
            return redirect(url_for('do_reset_password'))

        # Password validation
        if not User.pass_validation(password):
            flash(
                "Password must be at least 5 characters long, contain a number, and a special character.",
                "error"
            )
            return redirect(url_for('do_reset_password'))

        # Check if passwords match
        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for('reset_password'))

        # Get user ID from session
        user_id = session.get("user_id")
        if not user_id:
            flash("Session expired or invalid user ID. Please try again.", "error")
            return redirect(url_for('reset_password'))

        # Hash the password and update it
        hashed_password = User.hash_password(password)
        User.update_password(hashed_password, user_id)
        flash("Password has been reset successfully!", "success")

        return redirect(url_for('login'))

    @staticmethod
    @__app.route("/do_confirmation", methods=["POST"])
    def do_confirmation():
        redirect_response = UserRoutes.redirect_on_role()
        if redirect_response:
            return redirect_response

        user_code = request.form.get("confirmation_code")

        # Check if the entered code matches the one in the session
        if user_code and int(user_code) == session.get('confirmation_code'):
            if session.get('action') == 'register':
                # Proceed with final registration
                name = session.get('name')
                username = session.get('username')
                email = session.get('email')
                password = session.get('password')

                # Check if the user already exists in the database
                if Database.check_user(username, email):
                    # Add the user to the database
                    User.add_user(username, password, name, email)

                    # Clear the session after successful registration
                    session.clear()

                    session['role'] = 'subscriber'

                    # Redirect to login page after successful registration
                    return redirect(url_for('login'))
                else:
                    return render_template("error.html", message_header="Registration Error",
                                           message_body="Username or Email already exists.")
            elif session.get("action") == "reset":
                return render_template("user/reset_password.html")
            else:
                session.pop('confirmation_code', None)
                session.pop('action', None)

                # Store the user information in the session
                user = User.fetch_user_object(session.get('user_id'))
                session['user'] = user  # Store user_id in the session
                session['role'] = user.getRole()
                if session['role'] == "Manager":
                    return redirect(url_for("manager"))
                elif session['role'] == "Subscriber":
                    return redirect(url_for("user_settings"))
        else:
            # If the code is incorrect, show an error
            return render_template("error.html", message_header="Invalid Code",
                                   message_body="The code you entered is incorrect. Please try again.")

    @staticmethod
    @__app.route("/manager")
    def manager():
        """
        Placeholder for possible future manager WebUI page
        :return: manager html
        """
        if session['role'] == 'Manager':
            return render_template("manager.html",
                                   options=WebUI.MENU)
        elif session['role'] == 'Subscriber':
            return render_template("settings/user_settings.html",
                                   options=WebUI.MENU)
        else:
            return render_template("error.html",
                                   message_header="Error",
                                   message_body="Role does not exist")

    @staticmethod
    @__app.route("/logout")
    def logout():
        """
        Log out the user
        :return: redirection to homepage
        """
        if "user" in session:
            WebUI.logout()
            del session["user"]
        return redirect(url_for("login"))

    @staticmethod
    def redirect_on_role():
        """
        Redirect the user based on their role
        """
        if "user" in session:
            role = session.get("role")
            if role == "Manager":
                return redirect(url_for("manager"))
            elif role == "Subscriber":
                return redirect(url_for("user_settings"))
        return None
