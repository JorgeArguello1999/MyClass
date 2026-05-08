from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from flask import request

main_bp = Blueprint('main', __name__)

from app.models.course import Course
from app.models.session import Session
from app.models.summary_topic import SummaryTopic
from app.models.key_moment import KeyMoment
from app.models.homework import Homework
from app.models.study_note import StudyNote
from app.models.user import User
from app import db
import random
from datetime import timedelta
@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main_bp.route('/dashboard')
@login_required # Ruta protegida con auth
def dashboard():
    courses = Course.query.filter_by(user_id=current_user.id).order_by(Course.created_at.desc()).all()
    return render_template('main/dashboard.html', active_page='dashboard', courses=courses, show_back_button=False)

@main_bp.route('/course/new')
@login_required
def add_course():
    return render_template('main/add_course.html', show_back_button=True)

@main_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        
        if full_name:
            current_user.full_name = full_name
            
        if email:
            existing_user = User.query.filter_by(email=email).first()
            if existing_user and existing_user.id != current_user.id:
                from flask import flash
                flash('Email is already taken.', 'error')
            else:
                current_user.email = email
                
        profile_pic = request.files.get('profile_picture')
        if profile_pic and profile_pic.filename != '':
            from werkzeug.utils import secure_filename
            from flask import current_app
            import os
            import uuid
            
            ext = profile_pic.filename.rsplit('.', 1)[1].lower() if '.' in profile_pic.filename else ''
            if ext in {'png', 'jpg', 'jpeg'}:
                filename = f"{uuid.uuid4().hex}_{secure_filename(profile_pic.filename)}"
                os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
                save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                profile_pic.save(save_path)
                current_user.profile_picture = filename
                
        db.session.commit()
        from flask import flash
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('main.settings'))
        
    return render_template('main/settings.html', active_page='settings', show_back_button=True)

@main_bp.route('/records')
@login_required
def records():
    # Fetch all courses for the user
    courses = Course.query.filter_by(user_id=current_user.id).all()
    course_ids = [c.id for c in courses]
    
    # Fetch all sessions for these courses
    all_sessions = Session.query.filter(Session.course_id.in_(course_ids)).order_by(Session.recorded_date.desc()).all()
    
    total_seconds = sum(s.duration_seconds for s in all_sessions if s.duration_seconds)
    total_hours = round(total_seconds / 3600, 1)
    
    key_topics_count = SummaryTopic.query.join(Session).filter(Session.course_id.in_(course_ids)).count()
    
    return render_template('main/records.html', active_page='records', show_back_button=True,
                           all_sessions=all_sessions, total_hours=total_hours, key_topics_count=key_topics_count)
@main_bp.route('/live/<int:course_id>')
@login_required
def live_session(course_id):
    from app.models.course import Course
    course = Course.query.get_or_404(course_id)
    return render_template('main/live_session.html', show_back_button=True, back_url=url_for('course.detail', course_id=course.id), course=course)

@main_bp.route('/course/<int:course_id>/end_session')
@login_required
def end_session(course_id):
    course = Course.query.get_or_404(course_id)
    if course.user_id != current_user.id:
        from flask import abort
        abort(403)
        
    # Generate random dummy data to see differences
    session_titles = ["Introduction to Concepts", "Advanced Theories", "Midterm Review", "Lab Session", "Guest Lecture"]
    durations = [1800, 3600, 5400, 7200, 2400]
    
    new_session = Session(
        course_id=course.id,
        title=f"{random.choice(session_titles)} - {course.name}",
        duration_seconds=random.choice(durations),
        status='ready'
    )
    db.session.add(new_session)
    db.session.commit()
    
    # Dummy Summary Topic
    topic = SummaryTopic(
        session_id=new_session.id,
        main_topic=f"Exploration of {course.name} fundamentals.",
        description="Detailed breakdown of the core methodologies and practical applications discussed during the class.",
        tags="Core, Review, Essential"
    )
    db.session.add(topic)
    
    # Dummy Key Moments
    for i in range(3):
        km = KeyMoment(
            session_id=new_session.id,
            timestamp_seconds=random.randint(100, new_session.duration_seconds - 100),
            title=f"Important Concept {i+1}",
            description="The professor emphasized this point significantly."
        )
        db.session.add(km)
        
    # Dummy Homework
    for i in range(2):
        hw = Homework(
            session_id=new_session.id,
            task_description=f"Read chapter {random.randint(1, 10)} and summarize.",
            due_date_extracted=f"In {random.randint(2, 7)} days"
        )
        db.session.add(hw)
        
    # Dummy Study Notes
    for i in range(2):
        is_tip = random.choice([True, False])
        note = StudyNote(
            session_id=new_session.id,
            note_text="Make sure to review the provided slides before the next exam." if is_tip else "Group study session scheduled for tomorrow.",
            is_professor_tip=is_tip
        )
        db.session.add(note)
        
    db.session.commit()
    
    return redirect(url_for('main.session_summary', session_id=new_session.id))

@main_bp.route('/session/<int:session_id>')
@login_required
def session_summary(session_id):
    session_obj = Session.query.get_or_404(session_id)
    course = Course.query.get(session_obj.course_id)
    
    if course.user_id != current_user.id:
        from flask import abort
        abort(403)
        
    back_url = url_for('course.detail', course_id=course.id)
    return render_template('main/session_summary.html', active_page='dashboard', show_back_button=True, back_url=back_url, session=session_obj, course=course)
