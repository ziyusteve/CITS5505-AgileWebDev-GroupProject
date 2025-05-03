from flask import render_template, redirect, url_for, flash, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.auth import bp
from app.models.user import User
from app.extensions import db, login_manager
from app.auth.forms import LoginForm, RegisterForm
from flask_login import login_user, logout_user, login_required, current_user

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        
        # 表单验证器已经检查了用户名和邮箱是否重复
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        
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
        username = form.username.data
        password = form.password.data
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not check_password_hash(user.password, password):
            flash('请检查您的登录信息并重试。', 'danger')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember.data)
        
        next_page = request.args.get('next')
        if next_page:
            # 确保next参数是相对URL而非绝对URL（安全措施）
            if not next_page.startswith('/'):
                next_page = None
        
        flash('登录成功！', 'success')
        return redirect(next_page or url_for('dashboard.index'))
    
    return render_template('auth/login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已成功登出。', 'success')
    return redirect(url_for('main.index'))


@bp.route('/terms')
def terms():
    return render_template('auth/terms.html')

@bp.route('/privacy')
def privacy():
    return render_template('auth/privacy.html')