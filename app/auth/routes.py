from flask import render_template, redirect, url_for, flash, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from app.auth import bp
from app.models.user import User
from app.extensions import db
from app.auth.forms import LoginForm, RegistrationForm

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(
            username=form.username.data, 
            email=form.email.data, 
            password=hashed_password
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('账户创建成功！您现在可以登录了。', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if not user or not check_password_hash(user.password, form.password.data):
            flash('请检查您的登录详情并重试。', 'danger')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember.data)
        
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        
        flash('登录成功！', 'success')
        return redirect(url_for('dashboard.index'))
    
    return render_template('auth/login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已退出登录。', 'success')
    return redirect(url_for('main.index'))

@bp.route('/terms')
def terms():
    return render_template('auth/terms.html')

@bp.route('/privacy')
def privacy():
    return render_template('auth/privacy.html')