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

@main_bp.route('/course/<int:course_id>/upload_audio_chunk/<session_uuid>', methods=['POST'])
@login_required
def upload_audio_chunk(course_id, session_uuid):
    course = Course.query.get_or_404(course_id)
    if course.user_id != current_user.id:
        from flask import abort
        abort(403)
        
    chunk = request.files.get('audio_chunk')
    if chunk:
        from werkzeug.utils import secure_filename
        from flask import current_app
        import os
        safe_uuid = secure_filename(session_uuid)
        if not safe_uuid:
            return 'Invalid UUID', 400
            
        filename = f"{safe_uuid}.webm"
        upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'audio')
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, filename)
        with open(file_path, 'ab') as f:
            f.write(chunk.read())
            
    return 'OK', 200

@main_bp.route('/course/<int:course_id>/end_session', methods=['GET', 'POST'])
@login_required
def end_session(course_id):
    course = Course.query.get_or_404(course_id)
    if course.user_id != current_user.id:
        from flask import abort
        abort(403)
        
    raw_transcript = ""
    duration = 1800
    session_uuid = None
    audio_filename = None
    
    if request.method == 'POST':
        raw_transcript = request.form.get('raw_transcript', '').strip()
        dur_str = request.form.get('duration', '1800')
        session_uuid = request.form.get('session_uuid')
        try:
            duration = int(dur_str)
            if duration < 60: duration = 60 # min 1 min for display
        except:
            duration = 1800
            
        if session_uuid:
            from werkzeug.utils import secure_filename
            safe_uuid = secure_filename(session_uuid)
            audio_filename = f"{safe_uuid}.webm"
    else:
        # Fallback to random if hit via GET directly
        duration = random.choice([1800, 3600, 5400, 7200, 2400])

    session_titles = ["Introduction to Concepts", "Advanced Theories", "Midterm Review", "Lab Session", "Guest Lecture"]
    
    new_session = Session(
        course_id=course.id,
        title=f"{random.choice(session_titles)} - {course.name}",
        duration_seconds=duration,
        raw_transcript=raw_transcript,
        audio_file_path=audio_filename,
        status='ready'
    )
    db.session.add(new_session)
    db.session.commit()
    
    import re
    # Split by common punctuation marks to extract sentences
    sentences = [s.strip() for s in re.split(r'[.?!]+', raw_transcript) if len(s.strip()) > 10]
    
    fallback_sentences = [
        "We will explore the fundamental properties discussed today.",
        "Remember to review the notes before the final exam.",
        "The core methodology relies on practical application.",
        "Read chapter 3 and write a short summary.",
        "Group study is highly recommended for this topic.",
        "The professor emphasized this concept multiple times.",
        "This is an essential insight into the subject matter."
    ]
    
    def get_random_sentence():
        if sentences:
            return random.choice(sentences)
        return random.choice(fallback_sentences)
    
    # Dummy Summary Topic
    topic = SummaryTopic(
        session_id=new_session.id,
        main_topic=f"Summary of {course.name}",
        description=get_random_sentence(),
        tags="Core, Review, Essential"
    )
    db.session.add(topic)
    
    # Dummy Key Moments
    for i in range(3):
        km = KeyMoment(
            session_id=new_session.id,
            timestamp_seconds=random.randint(10, max(duration - 10, 11)),
            title=f"Key Point {i+1}",
            description=get_random_sentence()
        )
        db.session.add(km)
        
    # Dummy Homework
    for i in range(2):
        hw = Homework(
            session_id=new_session.id,
            task_description=f"Task: {get_random_sentence()}",
            due_date_extracted=f"In {random.randint(2, 7)} days"
        )
        db.session.add(hw)
        
    # Dummy Study Notes
    for i in range(2):
        is_tip = random.choice([True, False])
        note = StudyNote(
            session_id=new_session.id,
            note_text=get_random_sentence(),
            is_professor_tip=is_tip
        )
        db.session.add(note)
        
    db.session.commit()
    
    return redirect(url_for('main.session_summary', session_id=new_session.id))

@main_bp.route('/session/<int:session_id>/delete', methods=['POST'])
@login_required
def delete_session(session_id):
    session = Session.query.get_or_404(session_id)
    course = session.course
    
    if course.user_id != current_user.id:
        from flask import abort
        abort(403)
        
    import os
    from flask import current_app
    
    # Delete the physical audio file if it exists to free up space
    if session.audio_file_path:
        file_path = os.path.join(current_app.root_path, 'static', 'uploads', 'audio', session.audio_file_path)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error deleting audio file: {e}")
                
    db.session.delete(session) # This cascades to SummaryTopic, KeyMoment, etc.
    db.session.commit()
    
    from flask import flash
    flash('Class session and all its resources have been successfully deleted.', 'success')
    return redirect(url_for('course.detail', course_id=course.id))

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
