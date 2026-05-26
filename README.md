<div align="center">
  <img src="app/static/images/logo.jpeg" alt="LuminaAcademic Logo" width="120" />
  <h1>LuminaAcademic</h1>
</div>

Welcome to the **LuminaAcademic** repository. LuminaAcademic is an intelligent academic tracking and recording system designed to organize your lecture transcripts, audio histories, study notes, and assignments—all wrapped in a clean, state-of-the-art UI.

## 🚀 Features

- **Modern Dashboard**: Clean, responsive grid layout for managing courses and getting high-level insights.
- **Lecture Recording & Dictation Module**:
  - **Cross-Browser Compatibility**: Fully supported across Chrome, Brave, Firefox, Edge, and Safari (macOS/iOS).
  - **Spoken Language Selector**: Real-time choice of recording language (Korean `ko-KR`, Spanish `es-ES`, English `en-US`), mapped directly to backend STT.
  - **Real-Time Translation**: Asynchronous segment-by-segment live English translation displayed on-screen as the lecture is recorded.
  - **Dictation Status Banner**: A responsive status banner featuring active, initializing, unsupported (Firefox), privacy-blocked (Brave shields), and blocked microphone states.
  - **Auto-Recovery**: SpeechRecognition automatically restarts on transient silence or non-fatal network interruptions.
- **Fully Editable Session Summaries**:
  - **Pencil-Locked Inline Editing**: Visual fields remain read-only with sleek toggle inputs unlocked via pencil icons. Supports inline title edits, main topic & tags, key moments, important notes, class summaries, and study group notes.
  - **Dynamic Item Lists**: Append new entries or delete old ones dynamically on-the-fly inside key moments, notes, and homework sections.
  - **Homework Checklist & Date Pickers**: Toggle completed tasks directly with fading strikethroughs, utilizing native date picker calendars (`<input type="date">`) for absolute deadline dates.
  - **Conditional Study Group Notes**: Hides the card layout entirely if empty, rendering a dashed placeholder button to initialize study group notes on demand.
- **Advanced Actionable Operations**:
  - **Download Audio**: Downloads the original class recording utilizing correct format extensions dynamically (`.mp4` on Safari/iOS vs `.webm` on Chrome/Brave).
  - **Selective Re-translation**: Choose between re-transcribing from raw audio container headers or translating from edited text.
  - **Safe Re-generation**: Re-trigger LLM extraction from current transcripts, locked behind a safety warning modal to prevent accidental data loss.
  - **Universal Audio Playback**: Direct source binding on HTML5 audio tags to guarantee cross-browser audio playback regardless of local codecs.
- **MVC Architecture**: Engineered using standard Flask Model-View-Controller patterns via Blueprint separation.
- **Security Checkup**: Integrity validation running directly during the application startup via `main.py`.

## 🛠 Tech Stack

- **Backend Framework**: Python / Flask
- **Database**: SQLite / SQLAlchemy ORM
- **Environment & Package Manager**: `uv` (Fast Python package, environment, and tool manager)
- **Frontend**: Jinja2 Templates, Bootstrap 5, Custom CSS (`dashboard.css`)
- **Icons**: Bootstrap Icons

## ⚙️ Installation & Setup

Follow these detailed instructions using `uv` to initialize the project environment, configure database migrations, set up the artificial intelligence models, and run the system.

### 1. Prerequisites

Ensure you have the following installed on your host system:
- **[uv](https://github.com/astral-sh/uv)** (We use `uv` exclusively to manage Python versions, virtual environments, dependencies, and execution commands).
- **Python 3.12+** (Automatically managed and downloaded by `uv` using the settings in `pyproject.toml`).
- **FFmpeg & FFprobe**: Required to convert live WebM audio recording chunks into WAV format for speech recognition.
  - **macOS**: `brew install ffmpeg`
  - **Linux (Ubuntu/Debian)**: `sudo apt update && sudo apt install ffmpeg`
  - **Windows**: Download the static binaries from the official site and add them to your system's environment `PATH`.

### 2. Clone the Repository

```bash
git clone <your-repository-url>
cd MyClass
```

### 3. Create the Environment & Install Dependencies

We use `uv` to manage the virtual environment. To create the `.venv` and install the exact locked dependencies from `uv.lock`, run:

```bash
# This will automatically download the correct Python version (if missing), create the .venv, and sync dependencies
uv sync
```

### 4. Setup Environment Variables

Copy the example environment configuration or create a `.env` file in the root directory:
```bash
touch .env
```
Populate the file with the following variables:
```ini
# Flask & Server Configuration
SECRET_KEY=dev-secret-key-12345
FLASK_APP=main.py
FLASK_DEBUG=1
FLASK_CONFIG=development
PORT=10000

# Verification Pre-flight Configuration
# Set to 1 to bypass the local LLM connectivity check during startup checks
SKIP_LLM_CHECK=1

# LLM Provider Configuration
# Set LLM_PROVIDER to "ollama", "lmstudio", or "mock" (default fallback)
LLM_PROVIDER=ollama
LLM_MODEL=llama3.1-16k
LLM_BASE_URL=http://localhost:11434
```

---

## 💾 Database Setup & Migrations

The project uses **SQLite** as its default development database, resulting in a self-contained local file (`data-dev.sqlite`).

1. **Auto-Migrations on Startup**: When you launch the application (`python main.py`), the system automatically runs a robust 3-stage migration check:
   - **Stage 1 (Upgrade)**: Syncs the database table schema to match all existing migrations on disk first, avoiding target mismatches.
   - **Stage 2 (Migrate)**: Checks for new schema changes in the python models and auto-generates dynamic version scripts in the versions folder.
   - **Stage 3 (Upgrade)**: Applies any newly generated migration versions to the SQLite database.
2. **Manual Migrations**: If you need to manually apply migrations or initialize a clean database from scratch, use the following commands:
   ```bash
   # Apply pending migrations to the database file
   uv run flask db upgrade

   # (Optional) Generate a new migration script if you modified SQLAlchemy models
   uv run flask db migrate -m "Description of changes"
   ```

---

## 🤖 AI Models Configuration (via LangChain / `lang`)

We use **LangChain** (often referred to in the codebase as `lang` or `langchain`) to manage, configure, and orchestrate the AI models. This allows the system to easily swap providers, parse structured JSON outputs, and connect to local open-source LLMs.

### Supported LLM Providers

The system is configured to support multiple LLM providers through environment variables in your `.env` file:

1. **Mock (`mock`)**
   - **How it works**: Bypasses any external network request or local LLM server. It generates randomized, highly structured mock academic insights (summary topics, key moments, homework, and study notes) directly from the text.
   - **Configuration**:
     ```ini
     LLM_PROVIDER=mock
     ```

2. **Ollama (`ollama`)**
   - **How it works**: Connects to a local instance of Ollama running on your machine.
   - **Configuration**:
     ```ini
     LLM_PROVIDER=ollama
     LLM_MODEL=llama3.1-16k      # Replace with your downloaded model name
     LLM_BASE_URL=http://localhost:11434
     ```
   - **Prerequisites**: Make sure the Ollama server is running locally and you have downloaded the target model:
     ```bash
     ollama run llama3.1-16k
     ```

3. **LM Studio (`lmstudio`)**
   - **How it works**: Connects to LM Studio's OpenAI-compatible local server.
   - **Configuration**:
     ```ini
     LLM_PROVIDER=lmstudio
     LLM_MODEL=lmstudio         # Or the specific model loaded in LM Studio
     LLM_BASE_URL=http://localhost:1234/v1
     ```
   - **Prerequisites**: Open LM Studio, load your desired model, and start the Local Inference Server on port `1234`.

4. **OpenAI (`openai`)**
   - **How it works**: Connects to the official OpenAI API using `langchain-openai`.
   - **Configuration**:
     ```ini
     LLM_PROVIDER=openai
     LLM_MODEL=gpt-4o-mini      # Or any OpenAI model (e.g. gpt-4o, gpt-3.5-turbo)
     OPENAI_API_KEY=your-openai-api-key-here
     ```
   - **Prerequisites**: A valid OpenAI API key.

5. **DeepSeek (`deepseek`)**
   - **How it works**: Connects to the DeepSeek API utilizing OpenAI-compatible protocols.
   - **Configuration**:
     ```ini
     LLM_PROVIDER=deepseek
     LLM_MODEL=deepseek-chat    # Default DeepSeek chat model
     DEEPSEEK_API_KEY=your-deepseek-api-key-here
     LLM_BASE_URL=https://api.deepseek.com
     ```
   - **Prerequisites**: A valid DeepSeek API key.

6. **Claude / Anthropic (`claude` or `anthropic`)**
   - **How it works**: Connects to the Anthropic Claude API using `langchain-anthropic`.
   - **Configuration**:
     ```ini
     LLM_PROVIDER=claude        # Or LLM_PROVIDER=anthropic
     LLM_MODEL=claude-3-5-sonnet-latest  # Or any Anthropic model (e.g. claude-3-5-haiku-latest)
     ANTHROPIC_API_KEY=your-anthropic-api-key-here
     ```
   - **Prerequisites**: A valid Anthropic API key.

---

## 🔍 Verifying your Environment

To verify that your workspace is fully set up (including directories, database connection, `ffmpeg` path, and LLM server connectivity), run the built-in environment and integrity check script:

```bash
uv run python tests/test_environment.py
```

A successful output will look like this:
```
==============================================
   SYSTEM ENVIRONMENT & INTEGRITY TEST      
==============================================

[1/4] Checking required directories...
✅ Audio Uploads: Exists at '.../MyClass/app/static/uploads/audio'
✅ Profile Uploads: Exists at '.../MyClass/app/static/uploads/profiles'

[2/4] Checking database connection...
✅ Database: Connection successful!

[3/4] Checking ffmpeg installation...
✅ ffmpeg: Found at '/usr/local/bin/ffmpeg'
✅ ffprobe: Found at '/usr/local/bin/ffprobe'

[4/4] Checking local LLM connection...
Configured Provider: OLLAMA
Configured Model: llama3.1-16k
Configured URL: http://localhost:11434
Sending test prompt: 'Please reply with OK'...
✅ LLM Response: OK

==============================================
                SUMMARY                       
==============================================
Directories: ✅ PASS
Database:    ✅ PASS
ffmpeg:      ✅ PASS
Local LLM:   ✅ PASS
==============================================
🎉 All systems are ready and correctly configured!
```

---

## 🚀 Running the Application

Once your `.env` is configured, start the server:

```bash
uv run python main.py
```

By default, the server will bind to `0.0.0.0` on port `10000` (or the custom port set via the `PORT` env variable). You can access the interface at:
**[http://localhost:10000](http://localhost:10000)**

### ⚙️ Startup Behavior & Pre-flight Checks

Upon startup, `main.py` automatically initiates the following pre-flight verification sequence before binding to the web port:

1. **Auto-Migrations & Integrity Check**: Sube la base de datos local SQLite al día mediante el flujo de 3 fases (`upgrade` -> `migrate` -> `upgrade`).
2. **Environment Verification**: Runs the required unit validation checks from `tests/test_environment.py`:
   - Checks/creates media upload directories.
   - Verifies SQLite read/write transaction capabilities.
   - Validates that `ffmpeg` and `ffprobe` binaries are accessible.
   - **Local LLM Verification**: Skip this connectivity test by setting the environment variable `SKIP_LLM_CHECK=1` or launching the script with the `--skip-llm` argument.

If any required verification check fails, the application prints a pre-flight summary and immediately halts startup with a non-zero exit code to prevent running in a misconfigured environment.

---

## 🐳 Docker Deployment

For easy containerized deployment, the repository includes a `Dockerfile`. The container includes:
- Automated installation of **FFmpeg**, **FFprobe**, and **FLAC** inside the container (required for audio parsing and speech-to-text transcription).
- Support for persistent volumes for the SQLite database and uploaded audio files.
- Support for dynamic network routing (`host.docker.internal`) to connect to LLM servers (like Ollama) running on your host machine.

### Build the Image

```bash
docker build -t lumina-academic .
```

### Run the Container

Start the container and map the required ports, environment variables, and persistent data volumes:

```bash
docker run -d \
  -p 10000:10000 \
  -e SECRET_KEY=dev-secret-key-12345 \
  -e FLASK_APP=main.py \
  -e FLASK_DEBUG=1 \
  -e FLASK_CONFIG=development \
  -e SKIP_LLM_CHECK=1 \
  -e LLM_PROVIDER=mock \
  -e DEV_DATABASE_URL=sqlite:////app/data/data-dev.sqlite \
  -e DATABASE_URL=sqlite:////app/data/data.sqlite \
  -e LLM_BASE_URL=http://host.docker.internal:11434 \
  -v lumina_db_data:/app/data \
  -v lumina_upload_data:/app/app/static/uploads \
  --add-host=host.docker.internal:host-gateway \
  --name lumina-academic-app \
  lumina-academic
```

### Manage the Container

- **Check logs**:
  ```bash
  docker logs -f lumina-academic-app
  ```
- **Stop the container**:
  ```bash
  docker stop lumina-academic-app
  ```
- **Start the container again**:
  ```bash
  docker start lumina-academic-app
  ```
- **Remove the container**:
  ```bash
  docker rm lumina-academic-app
  ```

### Volumes & Persistence

- `lumina_db_data`: Mounts to `/app/data` to persist the SQLite database.
- `lumina_upload_data`: Mounts to `/app/app/static/uploads` to persist recorded class audio and profile files.

---

## 📱 Responsiveness

The application is fully responsive. It functions symmetrically as a rich mobile web app and scales up seamlessly using CSS Advanced Grids to provide a native-like experience on Desktop and Tablet devices.
