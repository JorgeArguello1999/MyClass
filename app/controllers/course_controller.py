from flask import Blueprint,render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.models.course import Course

course_bp = Blueprint('course', __name__)

@course_bp.route('/create', methods=['POST'])
@login_required
def create_course():
    name = request.form.get('name')
    icon = request.form.get('icon') or 'bi-book'
    professor = request.form.get('professor')
    schedule = request.form.get('schedule')
    location = request.form.get('location')
    
    if not name:
        flash('Course name is required.', 'error')
        return redirect(url_for('main.add_course'))
        
    course = Course(
        name=name,
        icon=icon,
        professor=professor,
        schedule=schedule,
        location=location,
        user_id=current_user.id
    )
    db.session.add(course)
    db.session.commit()
    flash('Course created successfully!', 'success')
    return redirect(url_for('main.dashboard'))

@course_bp.route('/<int:course_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    course = Course.query.get_or_404(course_id)
    if course.user_id != current_user.id:
        abort(403)
        
    if request.method == 'POST':
        course.name = request.form.get('name', course.name)
        course.icon = request.form.get('icon', course.icon)
        course.professor = request.form.get('professor', course.professor)
        course.schedule = request.form.get('schedule', course.schedule)
        course.location = request.form.get('location', course.location)
        
        db.session.commit()
        flash('Course updated successfully!', 'success')
        return redirect(url_for('main.dashboard'))
        
    return render_template('main/edit_course.html', course=course)

@course_bp.route('/<int:course_id>/delete', methods=['POST'])
@login_required
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    if course.user_id != current_user.id:
        abort(403)
        
    db.session.delete(course)
    db.session.commit()
    flash('Course deleted successfully!', 'success')
    return redirect(url_for('main.dashboard'))

@course_bp.route('/<int:course_id>')
@login_required
def detail(course_id):
    course = Course.query.get_or_404(course_id)
    if course.user_id != current_user.id:
        abort(403)
    
    # Since we are not updating DB models, we just render the detail template.
    # In a full integration, we would load `records = course.records`.
    # For now, we just pass the course.
    return render_template('main/course_detail.html', course=course, show_back_button=True)
