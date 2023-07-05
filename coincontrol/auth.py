from flask import Blueprint, session
from flask import request, render_template, redirect, url_for, flash
from coincontrol.forms import RegistrationForm, LoginForm
from coincontrol.extensions import bcrypt
from coincontrol.models import Users
from coincontrol.extensions import db
from flask_login import login_required, login_user, logout_user, current_user
from coincontrol.token import generate_confirmation_token, check_confirm_token
from datetime import datetime
from coincontrol.email import send_email
from itsdangerous import SignatureExpired ,BadSignature

auth = Blueprint("auth", __name__, template_folder='templates', static_folder='static')



@auth.route('/register', methods=["GET", "POST"])
def register():

    form = RegistrationForm()

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        user = Users(username=username, email=email, password=password)
        user.generate_password_hash(password)
      
        db.session.add(user)
        db.session.commit()
        
        token = generate_confirmation_token(user.email)
        confirm_url = url_for('auth.confirm_token', token=token, _external=True)
        send_email(email, confirm_url)
        
        login_user(user)
        flash("A confirmation email has been sent to your email address.")
        return redirect(url_for("main.home"))

    return render_template("auth/register.html", form=form)



# Token confirmation route
@auth.route('/confirm/<token>', methods=["GET"])
@login_required
def confirm_token(token):
    try:
        email = check_confirm_token(token)
       
    except SignatureExpired:
        flash('The confirmation link is invalid or has expired.')
        return redirect(url_for('main.home'))
    user = Users.query.filter_by(email=email).first()
    if user.verified:
        flash('Account already verified. Please login.')
    else:
        user.verified = True
        user.date_verified = datetime.now()
        db.session.add(user)
        db.session.commit()
        flash('You have verified your account. Thanks!')
    return redirect(url_for('main.home'))

@auth.route('/login', methods=["GET", "POST"])
def login():
    
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        remember = form.remember.data
       
        user = Users.query.filter_by(email=email).first()
        user_password = user.password
        password_check = bcrypt.check_password_hash(user_password, password)
            
        if user is not None and password_check:
            login_user(user, remember=remember)
            flash('logged in successfully')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for("main.dashboard"))
        else:
            flash("Login Unsuccessful. Please check username and password")

    return render_template("auth/login.html", form=form)



@auth.route('/logout', methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return  redirect(url_for("auth.login"))





@auth.route('/admin', methods=["GET"])
@login_required
def admin():
    if current_user.is_admin != True:
        flash('You need to be an admin to access this page')
        return redirect(url_for('auth.login'))
    return render_template('auth/admin_dashboard.html')

