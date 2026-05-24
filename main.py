import os
import sys

from app import create_app, db

# Initialize the app with the environment defined in FLASK_CONFIG (default is "development")
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

def check_integrity():
    from tests.test_db_integrity import run_all_integrity_checks
    run_all_integrity_checks(app, db)



if __name__ == "__main__":
    check_integrity()
    # Start Flask's native development server
    app.run(host="0.0.0.0", port=10000, debug=True)
