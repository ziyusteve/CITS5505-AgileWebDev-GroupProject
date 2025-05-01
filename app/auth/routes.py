from flask import render_template, redirect, url_for, flash, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.auth import bp
from app.models.user import User
from app.extensions import db
from app.auth.forms import LoginForm, RegistrationForm

@bp.route('/register', methods=['GET', 'POST'])
def register():
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
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if not user or not check_password_hash(user.password, form.password.data):
            flash('请检查您的登录详情并重试。', 'danger')
            return redirect(url_for('auth.login'))
        
        session['user_id'] = user.id
        session['username'] = user.username
        
        flash('登录成功！', 'success')
        return redirect(url_for('dashboard.index'))
    
    return render_template('auth/login.html', form=form)

@bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.index'))


@bp.route('/terms')
def terms():
    return render_template('auth/terms.html')

@bp.route('/privacy')
def privacy():
    return render_template('auth/privacy.html')