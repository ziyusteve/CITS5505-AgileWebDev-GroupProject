from flask import render_template, redirect, url_for, flash, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.auth import bp
from app.models.user import User
from app.extensions import db, login_manager
from app.auth.forms import LoginForm, RegisterForm
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse


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

        flash("Account created successfully! You can now log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


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

        # Update last_login timestamp
        from datetime import datetime

        user.last_login = datetime.utcnow()
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
