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
import threading
from flask import current_app

def process_audio_background(app, session_id):
    with app.app_context():
        from app.models.session import Session
        from app.models.summary_topic import SummaryTopic
        from app.models.key_moment import KeyMoment
        from app.models.homework import Homework
        from app.models.study_note import StudyNote
        import re
        import os
        from deep_translator import GoogleTranslator
        
        session = Session.query.get(session_id)
        if not session:
            return
            
        text = session.raw_transcript
        
        # 1. Transcribe if missing
        if not text and session.audio_file_path:
            file_path = os.path.join(app.root_path, 'static', 'uploads', 'audio', session.audio_file_path)
            if os.path.exists(file_path):
                try:
                    from pydub import AudioSegment
                    import speech_recognition as sr
                    
                    wav_path = file_path.rsplit('.', 1)[0] + '.wav'
                    audio = AudioSegment.from_file(file_path, format="webm")
                    audio.export(wav_path, format="wav")
                    
                    recognizer = sr.Recognizer()
                    with sr.AudioFile(wav_path) as source:
                        audio_data = recognizer.record(source)
                    
                    text = recognizer.recognize_google(audio_data, language="ko-KR")
                    session.raw_transcript = text
                    
                    if os.path.exists(wav_path):
                        os.remove(wav_path)
                except Exception as e:
                    print("Transcription failed:", e)
                    text = "(Automated transcription failed)"
                    session.raw_transcript = text
        
        # 2. Translate
        if text and text != "(Automated transcription failed)":
            try:
                translated = GoogleTranslator(source='auto', target='en').translate(text)
                session.translated_transcript = translated
            except Exception as e:
                session.translated_transcript = "(Translation failed)"
                
        # 3. Generate AI insights
        llm_provider = os.getenv("LLM_PROVIDER", "mock").lower()
        success = False
        
        if llm_provider in ("ollama", "lmstudio", "openai", "deepseek", "claude", "anthropic"):
            try:
                import json
                model_name = os.getenv("LLM_MODEL")
                base_url = os.getenv("LLM_BASE_URL")
                
                print(f"[LLM] Initializing provider: {llm_provider.upper()} (Model: {model_name})")
                
                if llm_provider == "ollama":
                    from langchain_ollama import ChatOllama
                    llm = ChatOllama(model=model_name, base_url=base_url, temperature=0.3)
                elif llm_provider == "lmstudio":
                    from langchain_openai import ChatOpenAI
                    llm = ChatOpenAI(
                        model=model_name,
                        openai_api_key="lm-studio",
                        openai_api_base=base_url,
                        temperature=0.3
                    )
                elif llm_provider == "openai":
                    from langchain_openai import ChatOpenAI
                    llm = ChatOpenAI(
                        model=model_name or "gpt-4o-mini",
                        openai_api_key=os.getenv("OPENAI_API_KEY"),
                        temperature=0.3
                    )
                elif llm_provider == "deepseek":
                    from langchain_openai import ChatOpenAI
                    llm = ChatOpenAI(
                        model=model_name or "deepseek-chat",
                        openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
                        openai_api_base=base_url or "https://api.deepseek.com",
                        temperature=0.3
                    )
                elif llm_provider in ("claude", "anthropic"):
                    from langchain_anthropic import ChatAnthropic
                    llm = ChatAnthropic(
                        model=model_name or "claude-3-5-sonnet-latest",
                        api_key=os.getenv("ANTHROPIC_API_KEY"),
                        temperature=0.3
                    )
                
                translated_text = session.translated_transcript or ""
                original_text = text or ""
                recorded_date_str = session.recorded_date.strftime('%Y-%m-%d') if session.recorded_date else 'Today'
                
                prompt = f"""
                You are an academic assistant. Analyze the following class lecture transcripts and extract structured insights.
                You will receive BOTH the original Korean transcript and its automated English translation. Use both to ensure accuracy, but write all your extracted results in English.
                
                Session Recorded Date: {recorded_date_str}
                
                Original Korean Transcript:
                \"\"\"
                {original_text}
                \"\"\"
                
                English Translation:
                \"\"\"
                {translated_text}
                \"\"\"
                
                You MUST return ONLY a valid, parsable JSON object matching the schema below. Do not wrap the JSON in markdown code blocks (e.g. ```json ... ```). Output ONLY the JSON block.
                
                Guidelines for extraction:
                1. "main_topic": Concise main topic title of the class session.
                2. "class_summary": A comprehensive, detailed summary of what was taught in the class lecture, explaining the key ideas and content in detail (1-2 paragraphs).
                3. "description": A short summary of what was taught in the class (2-3 sentences).
                4. "tags": Comma-separated tag strings (e.g., "tag1, tag2, tag3").
                5. "key_moments": Key points timeline.
                6. "homework": Recommended tasks. For the "due_date" key: if a timeline or relative deadline is mentioned (e.g. "next Wednesday", "in 2 weeks"), calculate the absolute date based on the Session Recorded Date ({recorded_date_str}) and output it in YYYY-MM-DD format (e.g., "2026-05-27"). If no specific deadline can be calculated, output "TBD".
                7. "study_notes": Takeaways or concept notes. For each note, set "is_professor_tip" to true if the note was explicitly emphasized, suggested as an exam tip, or warned as an important recommendation by the professor (e.g., exam warnings, specific study focus). Set it to false for normal core definitions, concepts, or general facts.
                
                JSON Schema:
                {{
                  "main_topic": "Topic Title",
                  "class_summary": "1-2 paragraphs detailed summary...",
                  "description": "2-3 sentences summary",
                  "tags": "tag1, tag2, tag3",
                  "key_moments": [
                    {{
                      "title": "Concise title for key moment 1",
                      "description": "Short explanation of this point"
                    }}
                  ],
                  "homework": [
                    {{
                      "task_description": "Description of homework",
                      "due_date": "YYYY-MM-DD or TBD"
                    }}
                  ],
                  "study_notes": [
                    {{
                      "note_text": "An important concept, formula, or takeaway from the lecture",
                      "is_professor_tip": true
                    }},
                    {{
                      "note_text": "Another core fact or definition mentioned in class",
                      "is_professor_tip": false
                    }}
                  ]
                }}
                """
                
                print("[LLM] Invoking local model...")
                response = llm.invoke(prompt)
                response_text = response.content.strip()
                
                if response_text.startswith("```"):
                    first_line = response_text.find("\n")
                    if first_line != -1:
                        response_text = response_text[first_line:].strip()
                    if response_text.endswith("```"):
                        response_text = response_text[:-3].strip()
                        
                data = json.loads(response_text)
                
                # Create SummaryTopic
                main_topic = data.get("main_topic", f"Summary of {session.course.name}")
                description = data.get("description", "No summary generated.")
                tags = data.get("tags", "Core, Lecture")
                
                topic = SummaryTopic(
                    session_id=session.id,
                    main_topic=main_topic,
                    description=description,
                    tags=tags
                )
                db.session.add(topic)
                
                # Set class summary in Session
                session.class_summary = data.get("class_summary", "No detailed summary generated.")
                
                # Update session title with AI-generated topic title
                session.title = main_topic
                
                # Create KeyMoments (evenly spaced timestamp)
                key_moments = data.get("key_moments", [])
                duration = session.duration_seconds or 1800
                for idx, km_data in enumerate(key_moments):
                    ts = int(((idx + 1) / (len(key_moments) + 1)) * duration)
                    km = KeyMoment(
                        session_id=session.id,
                        timestamp_seconds=ts,
                        title=km_data.get("title", f"Key Point {idx+1}"),
                        description=km_data.get("description", "")
                    )
                    db.session.add(km)
                    
                # Create Homework
                homework_items = data.get("homework", [])
                for hw_data in homework_items:
                    hw = Homework(
                        session_id=session.id,
                        task_description=hw_data.get("task_description", "Study lecture notes"),
                        due_date_extracted=hw_data.get("due_date", "TBD")
                    )
                    db.session.add(hw)
                    
                # Create Study Notes
                notes = data.get("study_notes", [])
                for note_data in notes:
                    note = StudyNote(
                        session_id=session.id,
                        note_text=note_data.get("note_text", ""),
                        is_professor_tip=note_data.get("is_professor_tip", False)
                    )
                    db.session.add(note)
                
                success = True
                print("[LLM] Structured insights extracted successfully.")
            except Exception as e:
                print(f"[LLM] Error extracting insights with local LLM: {e}")
        
        if not success:
            print("[LLM] Falling back to mock random data generation.")
            sentences = [s.strip() for s in re.split(r'[.?!]+', text or "") if len(s.strip()) > 10]
            fallback_sentences = [
                "We will explore the fundamental properties discussed today.",
                "Remember to review the notes before the final exam.",
                "The core methodology relies on practical application.",
                "Read chapter 3 and write a short summary.",
                "Group study is highly recommended for this topic."
            ]
            
            def get_random_sentence():
                if sentences:
                    return random.choice(sentences)
                return random.choice(fallback_sentences)
            
            topic = SummaryTopic(
                session_id=session.id,
                main_topic=f"Summary of {session.course.name}",
                description=get_random_sentence(),
                tags="Core, Review, Essential"
            )
            db.session.add(topic)
            
            # Set a fallback class_summary
            session.class_summary = "This lecture covers the key topics discussed in class today. Please review key moments, notes, and homework guidelines."
            
            # Set a clean fallback title if LLM processing fails
            date_str = session.recorded_date.strftime('%b %d') if session.recorded_date else "Today"
            session.title = f"Lecture: {session.course.name} - {date_str}"
            
            for i in range(3):
                km = KeyMoment(
                    session_id=session.id,
                    timestamp_seconds=random.randint(10, max(session.duration_seconds - 10, 11)),
                    title=f"Key Point {i+1}",
                    description=get_random_sentence()
                )
                db.session.add(km)
                
            for i in range(2):
                hw = Homework(
                    session_id=session.id,
                    task_description=f"Task: {get_random_sentence()}",
                    due_date_extracted=f"In {random.randint(2, 7)} days"
                )
                db.session.add(hw)
                
            for i in range(2):
                is_tip = random.choice([True, False])
                note = StudyNote(
                    session_id=session.id,
                    note_text=get_random_sentence(),
                    is_professor_tip=is_tip
                )
                db.session.add(note)
            
        session.status = 'ready'
        db.session.commit()

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
    
    status = 'processing' # We will always process translation or transcription
    
    new_session = Session(
        course_id=course.id,
        title=f"{random.choice(session_titles)} - {course.name}",
        duration_seconds=duration,
        raw_transcript=raw_transcript,
        audio_file_path=audio_filename,
        status=status
    )
    db.session.add(new_session)
    db.session.commit()
    
    # Start background thread
    app = current_app._get_current_object()
    thread = threading.Thread(target=process_audio_background, args=(app, new_session.id))
    thread.start()
    
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

@main_bp.route('/session/<int:session_id>/transcript_data')
@login_required
def transcript_data(session_id):
    session = Session.query.get_or_404(session_id)
    if session.course.user_id != current_user.id:
        from flask import abort
        abort(403)
        
    from flask import jsonify
    
    if session.status == 'processing':
        return jsonify({
            'status': 'processing'
        })
        
    original_text = session.raw_transcript or "No transcript available."
    translated_text = session.translated_transcript or "(Translation unavailable)"
        
    return jsonify({
        'status': 'ready',
        'original': original_text,
        'translated': translated_text
    })

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

@main_bp.route('/session/<int:session_id>/update', methods=['POST'])
@login_required
def update_session_fields(session_id):
    session = Session.query.get_or_404(session_id)
    if session.course.user_id != current_user.id:
        from flask import abort
        abort(403)
        
    from flask import jsonify
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided'}), 400
        
    section = data.get('section')
    if not section:
        return jsonify({'status': 'error', 'message': 'No section specified'}), 400
        
    try:
        if section == 'title':
            title = data.get('title')
            if title is not None:
                session.title = title.strip()
                
        elif section == 'topic':
            topic_description = data.get('topic_description')
            topic_tags = data.get('topic_tags')
            topic = session.summary_topics.first()
            if not topic:
                topic = SummaryTopic(session_id=session.id)
                db.session.add(topic)
            if topic_description is not None:
                topic.description = topic_description.strip()
            if topic_tags is not None:
                topic.tags = topic_tags.strip()
                
        elif section == 'class_summary':
            class_summary = data.get('class_summary')
            if class_summary is not None:
                session.class_summary = class_summary.strip()
                
        elif section == 'study_group':
            study_group_note = data.get('study_group_note')
            if study_group_note is not None:
                session.study_group_note = study_group_note.strip() if study_group_note.strip() else None
                
        elif section == 'key_moments':
            key_moments_data = data.get('key_moments', [])
            incoming_ids = []
            for km_data in key_moments_data:
                km_id = km_data.get('id')
                if km_id is not None and not str(km_id).startswith('new-'):
                    incoming_ids.append(int(km_id))
            
            KeyMoment.query.filter(KeyMoment.session_id == session.id, ~KeyMoment.id.in_(incoming_ids)).delete(synchronize_session=False)
            
            for km_data in key_moments_data:
                km_id = km_data.get('id')
                title = km_data.get('title', '').strip()
                description = km_data.get('description', '').strip()
                ts_val = km_data.get('timestamp')
                
                ts_seconds = 0
                if ts_val is not None:
                    if isinstance(ts_val, int):
                        ts_seconds = ts_val
                    else:
                        ts_str = str(ts_val).strip()
                        if ':' in ts_str:
                            parts = ts_str.split(':')
                            try:
                                ts_seconds = int(parts[0]) * 60 + int(parts[1])
                            except:
                                ts_seconds = 0
                        else:
                            try:
                                ts_seconds = int(ts_str)
                            except:
                                ts_seconds = 0
                
                if km_id is not None and not str(km_id).startswith('new-'):
                    km = KeyMoment.query.filter_by(id=int(km_id), session_id=session.id).first()
                    if km:
                        km.title = title
                        km.description = description
                        km.timestamp_seconds = ts_seconds
                else:
                    new_km = KeyMoment(
                        session_id=session.id,
                        title=title,
                        description=description,
                        timestamp_seconds=ts_seconds
                    )
                    db.session.add(new_km)
                        
        elif section == 'notes':
            notes_data = data.get('notes', [])
            incoming_ids = []
            for note_data in notes_data:
                note_id = note_data.get('id')
                if note_id is not None and not str(note_id).startswith('new-'):
                    incoming_ids.append(int(note_id))
                    
            StudyNote.query.filter(StudyNote.session_id == session.id, ~StudyNote.id.in_(incoming_ids)).delete(synchronize_session=False)
            
            for note_data in notes_data:
                note_id = note_data.get('id')
                note_text = note_data.get('note_text', '').strip()
                is_professor_tip = note_data.get('is_professor_tip', False)
                
                if note_id is not None and not str(note_id).startswith('new-'):
                    note = StudyNote.query.filter_by(id=int(note_id), session_id=session.id).first()
                    if note:
                        note.note_text = note_text
                else:
                    new_note = StudyNote(
                        session_id=session.id,
                        note_text=note_text,
                        is_professor_tip=is_professor_tip
                    )
                    db.session.add(new_note)
                        
        elif section == 'homeworks':
            homeworks_data = data.get('homeworks', [])
            incoming_ids = []
            for hw_data in homeworks_data:
                hw_id = hw_data.get('id')
                if hw_id is not None and not str(hw_id).startswith('new-'):
                    incoming_ids.append(int(hw_id))
                    
            Homework.query.filter(Homework.session_id == session.id, ~Homework.id.in_(incoming_ids)).delete(synchronize_session=False)
            
            for hw_data in homeworks_data:
                hw_id = hw_data.get('id')
                task_description = hw_data.get('task_description', '').strip()
                due_date_extracted = hw_data.get('due_date_extracted', '').strip()
                
                if hw_id is not None and not str(hw_id).startswith('new-'):
                    hw = Homework.query.filter_by(id=int(hw_id), session_id=session.id).first()
                    if hw:
                        hw.task_description = task_description
                        hw.due_date_extracted = due_date_extracted
                else:
                    new_hw = Homework(
                        session_id=session.id,
                        task_description=task_description,
                        due_date_extracted=due_date_extracted,
                        is_completed=False
                    )
                    db.session.add(new_hw)
                        
        elif section == 'transcript':
            raw_transcript = data.get('raw_transcript')
            translated_transcript = data.get('translated_transcript')
            if raw_transcript is not None:
                session.raw_transcript = raw_transcript
            if translated_transcript is not None:
                session.translated_transcript = translated_transcript
                
        else:
            return jsonify({'status': 'error', 'message': f'Unknown section: {section}'}), 400
            
        db.session.commit()
        
        # When returning success, query the updated list and return all details for items
        # so the frontend can replace the view DOM elements dynamically
        new_items = []
        if section == 'notes':
            new_items = [{
                'id': n.id,
                'note_text': n.note_text,
                'is_professor_tip': n.is_professor_tip
            } for n in session.study_notes.all()]
        elif section == 'homeworks':
            new_items = [{
                'id': hw.id,
                'task_description': hw.task_description,
                'due_date_extracted': hw.due_date_extracted,
                'is_completed': hw.is_completed
            } for hw in session.homeworks.all()]
        elif section == 'key_moments':
            new_items = [{
                'id': km.id,
                'title': km.title,
                'description': km.description,
                'timestamp_seconds': km.timestamp_seconds
            } for km in session.key_moments.order_by(KeyMoment.timestamp_seconds.asc()).all()]
            
        return jsonify({'status': 'success', 'items': new_items})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@main_bp.route('/homework/<int:hw_id>/toggle', methods=['POST'])
@login_required
def toggle_homework(hw_id):
    hw = Homework.query.get_or_404(hw_id)
    if hw.session.course.user_id != current_user.id:
        from flask import abort
        abort(403)
        
    from flask import jsonify
    data = request.get_json() or {}
    
    is_completed = data.get('is_completed')
    if is_completed is not None:
        hw.is_completed = bool(is_completed)
        db.session.commit()
        return jsonify({'status': 'success', 'is_completed': hw.is_completed})
        
    return jsonify({'status': 'error', 'message': 'is_completed field required'}), 400

@main_bp.route('/session/<int:session_id>/download_audio')
@login_required
def download_audio(session_id):
    session = Session.query.get_or_404(session_id)
    if session.course.user_id != current_user.id:
        from flask import abort
        abort(403)
        
    if not session.audio_file_path:
        flash("No audio file available for this session.", "error")
        return redirect(url_for('main.session_summary', session_id=session.id))
        
    import os
    from flask import send_from_directory, current_app
    directory = os.path.join(current_app.root_path, 'static', 'uploads', 'audio')
    safe_title = "".join([c if c.isalnum() else "_" for c in (session.title or "audio")])
    download_name = f"{safe_title}.webm"
    return send_from_directory(directory, session.audio_file_path, as_attachment=True, download_name=download_name)

@main_bp.route('/session/<int:session_id>/retranslate', methods=['POST'])
@login_required
def retranslate_session(session_id):
    session = Session.query.get_or_404(session_id)
    if session.course.user_id != current_user.id:
        from flask import abort
        abort(403)
        
    data = request.get_json() or {}
    source = data.get('source', 'text')
    
    if source == 'audio':
        if not session.audio_file_path:
            return jsonify({'status': 'error', 'message': 'No audio file available for this session.'}), 400
            
        import os
        from flask import current_app
        file_path = os.path.join(current_app.root_path, 'static', 'uploads', 'audio', session.audio_file_path)
        if not os.path.exists(file_path):
            return jsonify({'status': 'error', 'message': 'Audio file not found on disk.'}), 404
            
        try:
            from pydub import AudioSegment
            import speech_recognition as sr
            
            wav_path = file_path.rsplit('.', 1)[0] + '.wav'
            audio = AudioSegment.from_file(file_path, format="webm")
            audio.export(wav_path, format="wav")
            
            recognizer = sr.Recognizer()
            with sr.AudioFile(wav_path) as source_file:
                audio_data = recognizer.record(source_file)
            
            transcribed_text = recognizer.recognize_google(audio_data, language="ko-KR")
            session.raw_transcript = transcribed_text
            
            if os.path.exists(wav_path):
                os.remove(wav_path)
        except Exception as e:
            return jsonify({'status': 'error', 'message': f'Audio transcription failed: {str(e)}'}), 500
            
    if not session.raw_transcript:
        return jsonify({'status': 'error', 'message': 'No original transcript available to translate.'}), 400
        
    try:
        from deep_translator import GoogleTranslator
        translated = GoogleTranslator(source='auto', target='en').translate(session.raw_transcript)
        session.translated_transcript = translated
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Translation updated successfully!',
            'raw_transcript': session.raw_transcript,
            'translated_transcript': translated
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Translation failed: {str(e)}'}), 500

@main_bp.route('/session/<int:session_id>/regenerate', methods=['POST'])
@login_required
def regenerate_ai_content(session_id):
    session = Session.query.get_or_404(session_id)
    if session.course.user_id != current_user.id:
        from flask import abort
        abort(403)
        
    if not session.raw_transcript:
        return jsonify({'status': 'error', 'message': 'No transcript available to base the AI generation on.'}), 400
        
    try:
        from app.models.summary_topic import SummaryTopic
        from app.models.key_moment import KeyMoment
        from app.models.homework import Homework
        from app.models.study_note import StudyNote
        
        # Clear existing AI-generated content
        SummaryTopic.query.filter_by(session_id=session.id).delete()
        KeyMoment.query.filter_by(session_id=session.id).delete()
        Homework.query.filter_by(session_id=session.id).delete()
        StudyNote.query.filter_by(session_id=session.id).delete()
        
        session.status = 'processing'
        db.session.commit()
        
        import threading
        from flask import current_app
        app = current_app._get_current_object()
        
        # Run background transcription & insights extraction
        thread = threading.Thread(target=process_audio_background, args=(app, session.id))
        thread.start()
        
        return jsonify({
            'status': 'success',
            'message': 'AI re-generation started in the background.'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Failed to start AI generation: {str(e)}'}), 500

