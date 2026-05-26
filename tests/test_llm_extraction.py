import os
import sys
from dotenv import load_dotenv

# Add project root to python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Load env variables
load_dotenv(os.path.join(project_root, '.env'))

print("==============================================")
print("     LOCAL LLM EXTRACTION DRY-RUN TEST        ")
print("==============================================")

try:
    from app import create_app, db
    from app.models.course import Course
    from app.models.session import Session
    from app.models.summary_topic import SummaryTopic
    from app.models.key_moment import KeyMoment
    from app.models.homework import Homework
    from app.models.study_note import StudyNote
    from app.controllers.main_controller import process_audio_background
except Exception as e:
    print(f"❌ Failed to import modules: {e}")
    sys.exit(1)

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

with app.app_context():
    # 1. Check if we have at least one course
    course = Course.query.first()
    if not course:
        print("⚠️ No courses found in database to attach a test session to.")
        print("Creating a temporary course for this test...")
        course = Course(
            name="Temporary Test Course",
            icon="bi-flask",
            professor="Professor Test",
            schedule="Monday",
            location="Room 101",
            user_id=1  # Assumes user 1 exists, or we will check if any user exists
        )
        # Check if user 1 exists
        from app.models.user import User
        if not User.query.get(1):
            temp_user = User(username="temp_test_user", email="temp_test@lumina.com")
            temp_user.set_password("password123")
            db.session.add(temp_user)
            db.session.commit()
            course.user_id = temp_user.id
        db.session.add(course)
        db.session.commit()

    print(f"Using Course: {course.name} (ID: {course.id})")

    # 2. Create a dummy session with sample Korean and English transcripts
    print("Creating a dummy session with sample transcripts...")
    dummy_session = Session(
        course_id=course.id,
        title="Test Lecture on Neural Networks",
        duration_seconds=600,
        raw_transcript="오늘 우리는 인공신경망에 대해 배웠습니다. 역전파 알고리즘은 가중치를 최적화하기 위해 손실 함수의 기울기를 계산하는 매우 중요한 개념입니다. 다음 주 수요일까지 이에 대한 요약본을 제출하는 과제가 있습니다. 팁으로, 활성화 함수인 ReLU와 Sigmoid의 차이점을 잘 파악해 두는 것이 시험에 도움이 됩니다.",
        translated_transcript="Today we learned about artificial neural networks. The backpropagation algorithm is a very important concept that calculates the gradient of the loss function to optimize weights. There is an assignment to submit a summary of this by next Wednesday. As a tip, understanding the difference between the activation functions ReLU and Sigmoid well will help with the exam.",
        status="processing"
    )
    db.session.add(dummy_session)
    db.session.commit()
    print(f"Created Session: {dummy_session.title} (ID: {dummy_session.id})")

    # 3. Execute process_audio_background synchronously
    print("\nRunning process_audio_background synchronously...")
    try:
        process_audio_background(app, dummy_session.id)
        
        # Reload session from db
        db.session.refresh(dummy_session)
        print(f"Session status after processing: {dummy_session.status}")
        print(f"Session title after processing: {dummy_session.title}")
        
        # 4. Fetch and display the extracted insights
        print("\n=== Extracted Insights ===")
        topic = SummaryTopic.query.filter_by(session_id=dummy_session.id).first()
        if topic:
            print(f"Main Topic: {topic.main_topic}")
            print(f"Description: {topic.description}")
            print(f"Tags: {topic.tags}")
        else:
            print("❌ SummaryTopic not found!")

        print("\n--- Key Moments ---")
        moments = KeyMoment.query.filter_by(session_id=dummy_session.id).all()
        for km in moments:
            print(f"[{km.timestamp_seconds}s] {km.title}: {km.description}")

        print("\n--- Homework ---")
        homeworks = Homework.query.filter_by(session_id=dummy_session.id).all()
        for hw in homeworks:
            print(f"Task: {hw.task_description} (Due: {hw.due_date_extracted})")

        print("\n--- Study Notes ---")
        notes = StudyNote.query.filter_by(session_id=dummy_session.id).all()
        for note in notes:
            tip_str = " [PROFESSOR TIP]" if note.is_professor_tip else ""
            print(f"- {note.note_text}{tip_str}")

        print("==========================")
        
        # If LLM failed, check print log
        provider = os.getenv("LLM_PROVIDER", "mock")
        if provider == "mock":
            print("\nℹ️ LLM_PROVIDER is set to 'mock'. Insights were generated randomly.")
        else:
            print("\n✅ Insights extracted successfully using local LLM!")

    except Exception as e:
        print(f"❌ Error during dry-run execution: {e}")
    finally:
        # Clean up the dummy session to keep database clean
        print("\nCleaning up database...")
        try:
            db.session.delete(dummy_session)
            db.session.commit()
            print("✅ Database clean up completed.")
        except Exception as e:
            print(f"⚠️ Clean up failed: {e}")
