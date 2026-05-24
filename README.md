<div align="center">
  <img src="app/static/images/logo.jpeg" alt="LuminaAcademic Logo" width="120" />
  <h1>LuminaAcademic</h1>
</div>

Welcome to the **LuminaAcademic** repository. LuminaAcademic is an intelligent academic tracking and recording system designed to organize your lecture transcripts, audio histories, study notes, and assignments—all wrapped in a clean, state-of-the-art UI.

## 🚀 Features

- **Modern Dashboard**: Clean, responsive grid layout for managing courses and getting high-level insights.
- **Lecture Recording Module**: Live translation visualization, animated audio waves, and dynamic transcription tracking.
- **Session Summaries**: Study-optimized, dual-column notes combining audio playback, timelines, main topics, and homework tracking.
- **MVC Architecture**: Engineered using standard Flask Model-View-Controller patterns via Blueprint separation.
- **Security Checkup**: Integrity validation running directly during the application startup via `main.py`.

## 🛠 Tech Stack

- **Backend Framework**: Python / Flask
- **Database**: SQLite / SQLAlchemy ORM
- **Package Manager**: `uv` (Fast Python package manager)
- **Frontend**: Jinja2 Templates, Bootstrap 5, Custom CSS (`dashboard.css`)
- **Icons**: Bootstrap Icons

## ⚙️ Installation & Setup

Follow these detailed instructions to initialize the project environment, configure database migrations, set up the artificial intelligence models, and run the system.

### 1. Prerequisites

Ensure you have the following installed on your host system:
- **Python 3.12+** (configured in `pyproject.toml`)
- **[uv](https://github.com/astral-sh/uv)** (Recommended - an extremely fast Python package manager and resolver)
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

Using `uv`, you can instantly synchronize your virtual environment to match the exact `uv.lock` file:

```bash
# This will automatically create a `.venv` and install the locked dependencies
uv sync
```

*Alternatively, if you prefer standard pip:*
```bash
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# .\venv\Scripts\activate  # On Windows
pip install -r requirements.txt
```

### 4. Setup Environment Variables

Copy the example environment configuration or create a `.env` file in the root directory:
```bash
touch .env
```
Populate the file with the following variables:
```ini
# Flask Configuration
SECRET_KEY=dev-secret-key-12345
FLASK_APP=main.py
FLASK_DEBUG=1
FLASK_CONFIG=development

# LLM Provider Configuration
# Set LLM_PROVIDER to "ollama", "lmstudio", or "mock" (default fallback)
LLM_PROVIDER=ollama
LLM_MODEL=llama3.1-16k
LLM_BASE_URL=http://localhost:11434
```

---

## 💾 Database Setup & Migrations

The project uses **SQLite** as its default development database, resulting in a self-contained local file (`data-dev.sqlite`).

1. **Auto-Migrations on Startup**: When you start the application, the system automatically checks the database connection and runs pending migrations via `Flask-Migrate`/`Alembic` before launching the Flask server.
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

The system is configured to support three different LLM providers through environment variables in your `.env` file:

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

Once your `.env` is configured and your environment verification passes, start the development server:

```bash
uv run python main.py
```

By default, the server will bind to `0.0.0.0` on port `10000`. You can access the interface in your browser at:
**[http://localhost:10000](http://localhost:10000)**

## 📱 Responsiveness

The application is fully responsive. It functions symmetrically as a rich mobile web app and scales up seamlessly using CSS Advanced Grids to provide a native-like experience on Desktop and Tablet devices.


