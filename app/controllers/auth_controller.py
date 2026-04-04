from flask import Blueprint, render_template, redirect, flash, url_for, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if user exists by email
        user = User.query.filter_by(email=email).first()
        if user is not None and user.check_password(password):
            login_user(user)
            # Redirect to the page the user originally requested
            next_page = request.args.get('next')
            if next_page is None or not next_page.startswith('/'):
                next_page = url_for('main.dashboard')
            return redirect(next_page)
        flash('Invalid email or password.', 'error')
        
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        username = email.split('@')[0] if email else ''  # Derive basic username from email
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('auth.register'))
        
        # Very basic validation
        if User.query.filter_by(email=email).first():
            flash('That email is already registered.', 'error')
            return redirect(url_for('auth.register'))
            
        if User.query.filter_by(username=username).first():
            flash('That username is already taken.', 'error')
            return redirect(url_for('auth.register'))
            
        # Create user
        user = User(email=email, username=username, full_name=full_name)
        user.password = password
        db.session.add(user)
        db.session.commit()
        
        flash('You can now log in.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))
