# 🗺️ LuminaAcademic Functional Mapping (Roadmap)

This document provides a comprehensive mapping of all the features and templates available in **LuminaAcademic**. It details the expected behavior of every view, its underlying data connections, and the pending work required for full backend integration.

---

## 1. Authentication & Security
- **Templates**: `auth/login.html`, `auth/register.html`
- **Expected Behavior**: 
  - Allows new users to create an account by providing a username, email, and password. 
  - Allows existing users to securely log in to access their personalized academic dashboard. 
  - Protects all internal routes (requires a logged-in session).
- **Database Tables**: `User`
- **Current Status**: ✅ Fully Functional. Powered by `Flask-Login` and `werkzeug.security` for password hashing.

---

## 2. Main Dashboard
- **Templates**: `main/dashboard.html`
- **Expected Behavior**: 
  - Acts as the central hub after login. 
  - Displays a personalized welcome message.
  - Lists all active courses created by the user in a grid layout. 
  - Tapping a course card acts as an iOS-style navigation link, taking the user directly to the Course Detail view.
  - If no courses exist, displays an empty state prompting the user to create their first course.
- **Database Tables**: `Course` (filtered by `user_id`)
- **Current Status**: ✅ Fully Functional. Dynamically lists courses fetched from the SQLite database.

---

## 3. Course Management (Create & Edit)
- **Templates**: `main/add_course.html`, `main/edit_course.html`
- **Expected Behavior**: 
  - Provides a clean form to input or modify course metadata. 
  - Fields include: Course Name, Professor, Schedule, Location, and an Icon/Subject Group selector (e.g., Math, Science, Computing).
  - The icon selection gives visual context to the dashboard.
- **Database Tables**: `Course` (Insert / Update operations)
- **Current Status**: ✅ Fully Functional. Data is correctly persisted and updated in the database.

---

## 4. Course Details
- **Templates**: `main/course_detail.html`
- **Expected Behavior**: 
  - Shows specific information about the selected course.
  - Contains actions to **Edit** or **Delete** (with confirmation) the current course.
  - Features a prominent, primary action button to **"Record New Class"** which transitions the user to the live recording interface.
  - Displays a historical list of recorded classes specifically tied to this course.
- **Database Tables**: `Course` (Read), `Session` (Read)
- **Current Status**: ✅ Fully Functional. Course data, editing, deletion, and historical sessions list are fully connected and displayed dynamically from the database.

---

## 5. Live Audio Recording (Live Session)
- **Templates**: `main/live_session.html`
- **Expected Behavior**: 
  - This is the active recording screen. It captures microphone audio in real-time.
  - Displays animated waveforms or recording indicators to show active audio capture.
  - Displays live transcriptions (via Web Speech API / Google Speech Recognition) as the professor speaks.
  - Allows the user to tap a "Key Point" button to mark a specific timestamp during the live lecture.
  - Contains an "End Session" button that stops the recording, saves the audio chunks, and navigates to the Session Summary for processing.
- **Database Tables**: `Session` (stores the raw audio file path, duration, and raw transcript text)
- **Current Status**: ✅ Fully Functional. JavaScript Web Audio API chunking records and uploads audio in real-time WebM streams to a dedicated Flask endpoint.

---

## 6. Session Summary & AI Extraction
- **Templates**: `main/session_summary.html`
- **Expected Behavior**: 
  - The post-processing view shown after a lecture concludes or when reviewing an old class.
  - Features an audio player with a timeline scrubber to replay the lecture.
  - **Main Topic**: Displays the overarching theme detected from the transcript.
  - **Key Moments (Timeline)**: A chronological list of timestamps and descriptions mapping out the structure of the lecture.
  - **Important Notes**: Curated list of high-value insights, definitions, or professor tips.
  - **Homework/Tasks**: Automatically detected assignments, readings, or deadlines mentioned during the class.
- **Database Tables**: `Session`, `SummaryTopic`, `KeyMoment`, `Homework`, `StudyNote`
- **Current Status**: ✅ Fully Functional. Core AI engine processes WebM-to-WAV conversion using FFmpeg, auto-translates Korean speech to English via deep-translator, and uses LangChain (`lang`) with Ollama or LM Studio to extract structured JSON metadata.

---

## 7. Lecture History (Global Records)
- **Templates**: `main/records.html`
- **Expected Behavior**: 
  - Displays aggregated metrics, such as total hours recorded and overall progress across the semester.
  - Shows a global historical feed of all recorded sessions across all courses.
  - Each item displays its processing status (e.g., "Ready" or "Processing").
- **Database Tables**: `Course`, `Session`
- **Current Status**: ✅ Fully Functional. Dynamically aggregates total lecture hours, total extracted topics count, and lists historical session entries.

---

## 8. User Settings & Profile
- **Templates**: `main/settings.html`
- **Expected Behavior**: 
  - Accessed via the profile avatar in the top navigation bar.
  - Allows the user to update their personal information (Name, Email) and upload a profile picture.
  - Provides a secure "Log Out" button to terminate the session.
- **Database Tables**: `User` (Update operations)
- **Current Status**: ✅ Fully Functional. Profile details updates, profile picture uploads, and user logout are fully integrated with the database.

---

## 💾 Database Entities & Models (Completed)

All database schemas are built as SQLAlchemy models and fully integrated:

1. **`User`**
   - Main user table supporting flask-login sessions, securely hashing passwords, and storing user details.
2. **`Course`**
   - **Foreign Key**: `user_id` (Links to `User`)
   - **Fields**: `name`, `professor`, `schedule`, `location`, `icon`, `cover_image`.
3. **`Session`**
   - **Foreign Key**: `course_id` (Links to `Course`)
   - **Fields**: `title`, `audio_file_path`, `duration_seconds`, `recorded_date`, `raw_transcript`, `translated_transcript`, `status` (processing, ready).
4. **`KeyMoment`**
   - **Foreign Key**: `session_id` (Links to `Session`)
   - **Fields**: `timestamp_seconds`, `title`, `description`.
5. **`Homework`**
   - **Foreign Key**: `session_id` (Links to `Session`)
   - **Fields**: `task_description`, `due_date_extracted`, `is_completed`.
6. **`StudyNote`**
   - **Foreign Key**: `session_id` (Links to `Session`)
   - **Fields**: `note_text`, `is_professor_tip`.
