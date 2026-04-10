from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

main_bp = Blueprint('main', __name__)

from app.models.course import Course

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main_bp.route('/dashboard')
@login_required # Ruta protegida con auth
def dashboard():
    courses = Course.query.filter_by(user_id=current_user.id).order_by(Course.created_at.desc()).all()
    return render_template('main/dashboard.html', active_page='dashboard', courses=courses)

@main_bp.route('/course/new')
@login_required
def add_course():
    return render_template('main/add_course.html')

@main_bp.route('/settings')
@login_required
def settings():
    return render_template('main/settings.html', active_page='settings')

@main_bp.route('/records')
@login_required
def records():
    return render_template('main/records.html', active_page='records')

@main_bp.route('/live')
@login_required
def live_session():
    return render_template('main/live_session.html')

@main_bp.route('/course/session')
@login_required
def session_summary():
    return render_template('main/session_summary.html', active_page='dashboard')
