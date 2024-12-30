# ----------------------------------------------------------------------------
# Name: SettingsRoutes.py
# Owner: Chip Weatherly
# Date Created: 11/18/2024
# Description: Holds the flask routes associated with changing subscriber
#              settings
# ----------------------------------------------------------------------------
# Changes:
# 11/19/2024 Initial creation -CW
#
import random
from ui.WebUI import WebUI
from flask import render_template, request, session, redirect, url_for
from logic.User import User


class SettingsRoutes:
    __app = WebUI.get_app()

    @staticmethod
    @__app.route('/user_settings')
    def user_settings():
        if session['role'] == 'Manager':
            return redirect(url_for("manager"))
        return render_template("settings/user_settings.html", options=WebUI.MENU)

    # index -> /unsubscribe confirmation page
    @staticmethod
    @__app.route('/unsubscribe_emails')
    def unsubscribe_emails():
        return render_template('settings/unsubscribe_emails.html')

    # /unsubscribe -> user confirms ->?do_unsubscribe
    @staticmethod
    @__app.route('/do_unsubscribe_emails', methods=["GET", "POST"])
    def do_unsubscribe_emails():
        user_id = session["user"].getUserID()
        print(user_id)
        User.unsubscribe_user(user_id)
        return render_template("settings/confirm_unsubscribe.html")

    @staticmethod
    @__app.route('/subscribe_emails')
    def subscribe_emails():
        return render_template('settings/subscribe_emails.html')

    @staticmethod
    @__app.route('/do_subscribe_emails', methods=["GET", "POST"])
    def do_subscribe_emails():
        user_id = session["user"].getUserID()
        print(user_id)
        User.subscribe_user(user_id)
        return render_template("settings/confirm_subscribe.html")

    @staticmethod
    @__app.route('/change_password', methods=["GET", "POST"])
    def change_password():
        return render_template("settings/change_password.html")

    @staticmethod
    @__app.route('/confirm_change_password', methods=["GET", "POST"])
    def confirm_change_password():
        from logic.Email import Email
        # generate a random code
        user_code = random.randint(10000, 99999)
        print(user_code)

        # store the code in the session
        session['confirmation_code'] = user_code

        # get data in preparation of sending confirmation
        user_id = session["user"].getUserID()
        email_instance = Email(user_id)
        recipient = session["user"].getEmail()
        employee_email = "cis234atesting@gmail.com"
        subject = "Confirmation Code"
        message = (f"This is a password change confirmation code for PCC food pantry. "
                   f"Please don't share this code with anyone: {user_code}")
        server = email_instance.server_creation(employee_email)

        # Send confirmation email
        email_instance.send_email(subject, message, recipient, employee_email)
        server.quit()

        return render_template("settings/confirm_change_password.html")

    @staticmethod
    @__app.route('/do_confirm_change_password', methods=["GET", "POST"])
    def do_confirm_change_password():
        user_code = request.form.get("confirmation_code")

        # check to ensure entered code matches the session's code
        if user_code and int(user_code) == session.get('confirmation_code'):
            # change the password
            print("Confirmation Success!")
            return render_template("settings/enter_password.html")
        else:
            # If the code is incorrect, show an error
            return render_template("error.html", message_header="Invalid Code",
                                   message_body="The code you entered is incorrect. Please try again.")

    @staticmethod
    @__app.route('/do_enter_password', methods=["GET", "POST"])
    def enter_password():
        # take the two fields user has entered, make sure they are the same
        new_password = request.form.get("password")
        new_password_confirm = request.form.get("password_confirm")
        # ensure password meets requirements
        validity = User.pass_validation(new_password)
        # validity=true, valid password
        if validity:
            # ensure passwords match
            if new_password == new_password_confirm:
                user_id = session["user"].getUserID()
                hashed_password = User.hash_password(new_password)
                User.update_password(hashed_password, user_id)
                return render_template("settings/confirm_enter_password.html")
            else:
                return render_template("error.html", message_header="Error", message_body="Passwords do not match.")
        # validity=false, invalid password
        else:
            return render_template("error.html", message_header="Invalid password.",
                                   message_body="Must be 5+ characters, contain 1 number and 1 special character."
                                                " Re-enter password.",)

