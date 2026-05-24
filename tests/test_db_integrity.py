import os
import sys
from dotenv import load_dotenv

# Ensure the root directory of the project is in python path to allow imports from app
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

def check_env_file():
    print("\n[1/3] Checking .env file configuration...")
    env_path = os.path.join(project_root, '.env')
    if not os.path.exists(env_path):
        print("⚠️ .env file not found. Database configuration might fall back to defaults.")
        return False
    else:
        print("✅ .env file verified.")
        load_dotenv(env_path)
        return True

def run_db_migrations(app):
    print("\n[2/3] Checking & running database migrations...")
    try:
        from flask_migrate import upgrade, migrate
        with app.app_context():
            print("   Running migrations (migrate & upgrade)...")
            migrate()
            upgrade()
            print("✅ Database migrations applied successfully.")
        return True
    except Exception as e:
        print(f"❌ Error during database migrations: {e}")
        return False

def verify_db_connection(app, db):
    print("\n[3/3] Verifying database connection & query integrity...")
    try:
        with app.app_context():
            # Test basic connection
            with db.engine.connect() as conn:
                print("   Connection: Established successfully.")
            
            # Inspect active tables
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"   Database Tables found: {', '.join(tables) if tables else 'None (Empty database)'}")
            
            # Test querying the user table if it exists
            if 'user' in tables or 'users' in tables or any('user' in t.lower() for t in tables):
                try:
                    from app.models.user import User
                    user_count = User.query.count()
                    print(f"   Query test: Count of users in database = {user_count}")
                except Exception as qe:
                    print(f"   ⚠️ Could not query User model: {qe}")
            
        print("\n✅ Database connection and structure verified successfully.")
        return True
    except Exception as e:
        print(f"❌ Error connecting or querying Database: {e}")
        return False

def run_all_integrity_checks(app, db):
    print("==============================================")
    print("     DATABASE INTEGRITY & MIGRATION TEST      ")
    print("==============================================")
    
    check_env_file()
    
    if not run_db_migrations(app):
        sys.exit(1)
        
    if not verify_db_connection(app, db):
        sys.exit(1)
        
    print("\n🚀 Database verification completed successfully.\n")

if __name__ == "__main__":
    # Load environment variables first
    load_dotenv(os.path.join(project_root, '.env'))
    
    try:
        from app import create_app, db
        app = create_app(os.getenv('FLASK_CONFIG') or 'default')
    except Exception as e:
        print(f"❌ Failed to initialize Flask application context: {e}")
        sys.exit(1)
        
    run_all_integrity_checks(app, db)
    sys.exit(0)
