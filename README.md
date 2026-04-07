<div align="center">
  <img src="app/static/images/logo.png" alt="LuminaAcademic Logo" width="120" />
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

Follow these specific instructions to initialize the project environment correctly on your machine.

### 1. Prerequisites

Ensure you have the following installed:
- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (Extremely fast Python package installer and resolver)

### 2. Clone the Repository

```bash
git clone <your-repository-url>
cd MyClass
```
*(Note: If the inner folder is named `MyClass`, rename it or navigate into it accordingly).*

### 3. Create the Environment & Install Dependencies

Using `uv`, you can quickly synchronize the environment to match the exact `uv.lock`:

```bash
# This will automatically create a `.venv` and install the locked dependencies
uv sync
```

Alternatively, if you prefer standard pip:
```bash
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# .\venv\Scripts\activate  # On Windows
pip install -r requirements.txt
```

### 4. Setup Environment Variables

Copy the example environment configuration into a working `.env` file:
```bash
touch .env
```
*(Optionally define `SECRET_KEY`, `FLASK_APP=main.py`, `FLASK_DEBUG=1`, and `DATABASE_URI` inside this `.env` file).*

### 5. Initialize the Database

Use the built-in Flask commands to apply the database migrations or initiate it.

```bash
# If you are using Flask-Migrate:
uv run flask db upgrade
```

### 6. Run the Application

Start the local development server. The project features a startup script that automatically validates the environment integrity (Database connection and `.env` presence) before initializing Flask.

```bash
uv run python main.py
```
*(Or if your environment is activated conventionally, just `python main.py`)*

You should see output similar to this:
```
Verifying environment integrity...
✅ .env file verified.
✅ Database connection verified.
🚀 Verification completed successfully.

 * Running on http://127.0.0.1:5000
```

## 📱 Responsiveness

The application is fully responsive. It functions symmetrically as a rich mobile web app and scales up seamlessly using CSS Advanced Grids to provide a native-like experience on Desktop and Tablet devices.
