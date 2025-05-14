from flask import render_template, redirect, url_for, flash, request, current_app
from app.auth import bp
from app.models.user import User
from app.extensions import db, mail
from app.auth.forms import LoginForm, RegisterForm
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from datetime import datetime, UTC


@bp.route("/register", methods=["GET", "POST"])
def register():
    """User registration route."""
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = RegisterForm()
    if form.validate_on_submit():
        # Form validators already check for duplicate username and email
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        # Send verification email
        token = user.generate_verification_token()
        msg = Message(
            'Verify Your Email',
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[user.email]
        )
        verification_url = f"{current_app.config['BASE_URL']}/auth/verify/{token}"
        msg.body = f'''To verify your email, visit the following link:
{verification_url}

If you did not make this request then simply ignore this email.
'''
        mail.send(msg)

        flash("Account created successfully! Please check your email to verify your account.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@bp.route("/verify/<token>")
def verify_email(token):
    """Email verification route."""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt='email-verification-salt',
            max_age=3600
        )
    except (BadSignature, SignatureExpired):
        flash("The verification link is invalid or has expired.", "danger")
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("auth.login"))

    if user.is_verified:
        flash("Your email is already verified.", "info")
        return redirect(url_for("dashboard.index"))

    user.is_verified = True
    db.session.commit()
    flash("Your email has been verified! You can now log in.", "success")
    return redirect(url_for("auth.login"))


@bp.route("/resend-verification")
@login_required
def resend_verification():
    """Resend verification email."""
    if current_user.is_verified:
        flash("Your email is already verified.", "info")
        return redirect(url_for("dashboard.index"))

    token = current_user.generate_verification_token()
    msg = Message(
        'Verify Your Email',
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[current_user.email]
    )
    verification_url = f"{current_app.config['BASE_URL']}/auth/verify/{token}"
    msg.body = f'''To verify your email, visit the following link:
{verification_url}

If you did not make this request then simply ignore this email.
'''
    mail.send(msg)

    flash("A new verification email has been sent to your email address.", "success")
    return redirect(url_for("dashboard.index"))


@bp.route("/login", methods=["GET", "POST"])
def login():
    """User login route."""
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash("Please check your login details and try again.", "danger")
            return redirect(url_for("auth.login"))

        if not user.is_verified:
            flash("Please verify your email before logging in.", "warning")
            return redirect(url_for("auth.login"))

        # Update last_login timestamp
        user.last_login = datetime.now(UTC)
        db.session.commit()

        login_user(user, remember=form.remember.data)
        next_page = request.args.get("next")

        # Ensure next parameter is a relative URL, not absolute (security measure)
        if next_page and urlparse(next_page).netloc != "":
            next_page = None

        flash("Login successful!", "success")
        return redirect(next_page or url_for("dashboard.index"))

    return render_template("auth/login.html", form=form)


@bp.route("/logout")
@login_required
def logout():
    """User logout route."""
    logout_user()
    flash("You have been successfully logged out.", "success")
    return redirect(url_for("auth.login"))


@bp.route("/terms")
def terms():
    return render_template("auth/terms.html")


@bp.route("/privacy")
def privacy():
    return render_template("auth/privacy.html")
