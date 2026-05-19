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
- **Database Tables**: `Course` (Read), `Session` (Pending)
- **Current Status**: ⚠️ Partially Functional. Course data, editing, and deletion work. The historical list of classes is currently using hardcoded placeholders since the `Session` logic is not yet built.

---

## 5. Live Audio Recording (Live Session)
- **Templates**: `main/live_session.html`
- **Expected Behavior**: 
  - This is the active recording screen. It should capture microphone audio in real-time.
  - Displays animated waveforms or recording indicators to show active audio capture.
  - Should display live transcriptions (e.g., translated text) as the professor speaks.
  - Allows the user to tap a "Key Point" button to mark a specific timestamp during the live lecture.
  - Contains an "End Session" button that stops the recording, saves the audio, and navigates to the Session Summary for processing.
- **Database Tables**: `Session` (to store the raw audio file path, start time, and raw transcript text), `KeyPoint` (Pending)
- **Current Status**: 🎨 UI Ready (Mockup). Requires integration with JavaScript `Web Audio API` or `WebRTC` to capture audio, and a backend endpoint to receive and process the audio stream.

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
- **Database Tables**: `Session`, `SummaryTopic`, `KeyMoment`, `Homework` (All Pending)
- **Current Status**: 🎨 UI Ready (Mockup). This is the core AI feature. It requires backend integration with an LLM (like OpenAI GPT-4) and an audio transcription model (like Whisper) to generate these insights dynamically from the saved audio.

---

## 7. Lecture History (Global Records)
- **Templates**: `main/records.html`
- **Expected Behavior**: 
  - Displays aggregated metrics, such as total hours recorded and overall progress across the semester.
  - Shows a global historical feed of all recorded sessions across all courses.
  - Each item displays its processing status (e.g., "Summary Ready" or "Unprocessed").
- **Database Tables**: `Course`, `Session` (Pending)
- **Current Status**: 🎨 UI Ready (Mockup). Needs backend logic to sum durations and list actual `Session` records from the database.

---

## 8. User Settings & Profile
- **Templates**: `main/settings.html`
- **Expected Behavior**: 
  - Accessed via the profile avatar in the top navigation bar.
  - Allows the user to update their personal information (Name, Email), change their password, and toggle notification preferences.
  - Provides a secure "Log Out" button to terminate the session.
- **Database Tables**: `User` (Update operations)
- **Current Status**: ⚠️ Partially Functional. The layout is ready and the "Log Out" button works perfectly. The backend endpoints for updating user data and changing passwords are yet to be implemented.

---

## 🛠️ Missing Database Entities to Build Next

To fully activate the pending features (Live Recording, Summaries, and Histories), the following SQLAlchemy models need to be created:

1. **`Session` / `Lecture`**
   - **Foreign Key**: `course_id` (Links to `Course`)
   - **Fields**: `audio_file_path`, `duration_seconds`, `recorded_date`, `raw_transcript`, `status` (Enum: unprocessed, processing, ready).
2. **`KeyMoment` / `Timeline`**
   - **Foreign Key**: `session_id`
   - **Fields**: `timestamp_seconds`, `title`, `description`.
3. **`Homework` / `Task`**
   - **Foreign Key**: `session_id`
   - **Fields**: `task_description`, `due_date_extracted`, `is_completed`.
4. **`StudyNote` / `Highlight`**
   - **Foreign Key**: `session_id`
   - **Fields**: `note_text`, `is_professor_tip`.
