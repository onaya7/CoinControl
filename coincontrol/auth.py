import os
import json
from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from coincontrol.forms import RegistrationForm, LoginForm, ResetPasswordForm, EmailForm
from coincontrol.extensions import bcrypt
from coincontrol.models import Users
from coincontrol.extensions import db
from flask_login import login_required, login_user, logout_user, current_user
from coincontrol.tokens import generate_confirmation_token, check_confirm_token
from datetime import datetime
from coincontrol.email import (
    send_confirm_email,
    resend_confirm_email,
    send_passwordreset_email,
)
from itsdangerous import SignatureExpired, BadSignature
from coincontrol.decorators import check_confirmed
from google_auth_oauthlib.flow import Flow
from google.auth.transport import requests
from google.oauth2 import id_token

auth_bp = Blueprint("auth_bp", __name__, template_folder="templates", static_folder="static")
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        user = Users(username=username, email=email, password=password)
        user.generate_password_hash(password)

        db.session.add(user)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while processing your request. Please try again later.')
            return redirect(url_for("auth_bp.register"))
        
        token = generate_confirmation_token(user.email)
        confirm_url = url_for("auth_bp.confirm_token", token=token, _external=True)

        send_confirm_email(
            email_receiver=email, user=user.username, confirm_url=confirm_url
        )

        login_user(user)
        flash("A confirmation email has been sent to your email address.")
        return redirect(url_for("auth_bp.unconfirmed"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/unconfirmed", methods=["GET"])
@login_required
def unconfirmed():
    try:
        if current_user.verified:
            flash("Your account has already been verified. Please login.")
            return redirect(url_for("main_bp.home"))
        flash("An error occurred while processing your request. Please try again later.")
        return render_template("auth/unconfirmed.html")
    except Exception as e:
        flash("An error occurred while processing your request. Please try again later.")
        return redirect(url_for("main_bp.home"))

# Token confirmation_bp route
@auth_bp.route("/confirm/<token>", methods=["GET"])
@login_required
def confirm_token(token):
    try:
        email = check_confirm_token(token)
    except SignatureExpired:
        flash("The confirmation link is invalid or has expired.")
        return redirect(url_for("main_bp.home"))
    user = Users.query.filter_by(email=email).first()
    if user.verified:
        flash("Account already verified. Please login.")
    else:
        user.verified = True
        user.date_verified = datetime.now()
        db.session.add(user)
        db.session.commit()
        flash(
            "You have verified your email, you can now login to your dashboard. Thanks!"
        )
    return redirect(url_for("main_bp.home"))


@auth_bp.route("/resend-token", methods=["GET"])
@login_required
def resend_confirmation():
    try:
        token = generate_confirmation_token(current_user.email)
    except:
        flash("Error generating confirmation token. Please try again later.")
        return redirect(url_for("auth_bp.unconfirmed"))
    confirm_url = url_for("auth_bp.confirm_token", token=token, _external=True)
    try:
        resend_confirm_email(
            email_receiver=current_user.email,
            user=current_user.username,
            confirm_url=confirm_url,
        )
    except:
        flash("Error sending confirmation email. Please try again later.")
        return redirect(url_for("auth_bp.unconfirmed"))
    flash("A new confirmation email has been sent.")
    return redirect(url_for("auth_bp.unconfirmed"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        remember = form.remember.data
        
        user = Users.query.filter_by(email=email).first()
        if user is not None:
            user_password = user.password
            password_check = bcrypt.check_password_hash(user_password, password)
            if password_check:
                login_user(user, remember=remember)
                flash('logged in successfully')
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('main_bp.dashboard'))
            else:
                flash('Login Unsuccessful. Please check username and password')
        else:
            flash('Login Unsuccessful. Please check username and password')

    return render_template("auth/login.html", form=form)


@auth_bp.route("/google/Oauth/login", methods=["GET"])
def google_oauth_login():
    client_secrets_json = os.environ.get("CLIENT_SECRETS_JSON")
    client_secrets = json.loads(client_secrets_json)
    flow = Flow.from_client_config(
        client_secrets,
        scopes=[
            "openid",
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/userinfo.email",
        ],
        redirect_uri=os.environ.get("GOOGLE_REDIRECT_URI"),
    )
    authorization_url, state = flow.authorization_url(
        access_type="offline", include_granted_scopes="true"
    )
    session["state"] = state
    return redirect(authorization_url)


@auth_bp.route("/google/Oauth/signup", methods=["GET"])
def google_oauth_signup():
    client_secrets_json = os.environ.get("CLIENT_SECRETS_JSON")
    client_secrets = json.loads(client_secrets_json)
    flow = Flow.from_client_config(
        client_secrets,
        scopes=[
            "openid",
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/userinfo.email",
        ],
        redirect_uri=os.environ.get("GOOGLE_REDIRECT_URI"),
    )
    authorization_url, state = flow.authorization_url(
        access_type="offline", include_granted_scopes="true"
    )
    session["state"] = state
    return redirect(authorization_url)


@auth_bp.route("/google/auth/authorized", methods=["GET"])
def google_auth_authorized():
    state = session["state"]
    client_secrets_json = os.environ.get("CLIENT_SECRETS_JSON")
    client_secrets = json.loads(client_secrets_json)
    flow = Flow.from_client_config(
        client_secrets,
        scopes=[
            "openid",
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/userinfo.email",
        ],
        redirect_uri=os.environ.get("GOOGLE_REDIRECT_URI"),
        state=state,
    )
    flow.fetch_token(authorization_response=request.url, code_verifier="")

    credentials = flow.credentials
    session["google_token"] = credentials.token
    id_token_info = id_token.verify_oauth2_token(
        credentials.id_token, requests.Request(), flow.client_config["client_id"]
    )
    session["user_email"] = id_token_info.get("email")
    session["user_name"] = id_token_info.get("name")

    username = session["user_name"]
    email = session["user_email"]

    existing_user = Users.query.filter_by(email=email).first()
    if existing_user:
        if existing_user.verified != True:
            token = generate_confirmation_token(existing_user.email)
            confirm_url = url_for("auth_bp.confirm_token", token=token, _external=True)
            send_confirm_email(
                email_receiver=email,
                user=existing_user.username,
                confirm_url=confirm_url,
            )
        login_user(existing_user)
        flash("logged in successfully")
        return redirect(url_for("main_bp.dashboard"))

    user = Users(email=email, username=username)
    user.generate_password_hash(os.environ.get("FAKE_USER_GOOGLE_PASSWORD"))
    db.session.add(user)
    db.session.commit()

    token = generate_confirmation_token(user.email)
    confirm_url = url_for("auth_bp.confirm_token", token=token, _external=True)

    send_confirm_email(
        email_receiver=email, user=user.username, confirm_url=confirm_url
    )

    login_user(user)
    flash("logges in successfully")
    return redirect(url_for("main_bp.dashboard"))


@auth_bp.route("/forgotpassword", methods=["GET", "POST"])
def forgotpassword():
    form = EmailForm()
    if form.validate_on_submit():
        # verify if user exists
        user = Users.query.filter_by(email=form.email.data).first()
        form_email = form.email.data

        token = generate_confirmation_token(form_email)
        confirm_url = url_for("auth_bp.confirmpassword", token=token, _external=True)

        send_passwordreset_email(
            email_receiver=form_email, user=user.username, confirm_url=confirm_url
        )
        flash(f"We just emailed {form_email} with instructions to reset your password")
        return redirect(url_for("auth_bp.login"))
    return render_template("auth/forgotpassword.html", form=form)


@auth_bp.route("/confirmpassword/<token>", methods=["GET", "POST"])
def confirmpassword(token):
    try:
        email = check_confirm_token(token)
    except SignatureExpired:
        flash("The password reset link has expired.")
        return redirect(url_for("auth_bp.login"))
    except BadSignature:
        flash("The password reset link is invalid ")
        return redirect(url_for("auth_bp.login"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        password = form.password.data
        user = Users.query.filter_by(email=email).first()
        user.generate_password_hash(password)
        db.session.commit()
        flash("Your password has been updated successfully")
        return redirect(url_for("auth_bp.login"))

    return render_template("auth/confirmpassword.html", form=form, token=token)


@auth_bp.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for("auth_bp.login"))


@auth_bp.route("/admin", methods=["GET"])
@login_required
@check_confirmed
def admin():
    # if current_user.is_admin != True:
    #     flash("You need to be an admin to access this page")
    #     return redirect(url_for("auth_bp.login"))
    return render_template("dashboard/admin_dashboard.html")
