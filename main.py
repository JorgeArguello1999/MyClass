import os
import sys

from app import create_app, db

# Initialize the app with the environment defined in FLASK_CONFIG (default is "development")
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

def check_integrity():
    from tests.test_db_integrity import run_all_integrity_checks
    run_all_integrity_checks(app, db)

def check_environment():
    print("==============================================")
    print("      RUNNING PRE-FLIGHT ENVIRONMENT CHECKS   ")
    print("==============================================")
    try:
        from tests.test_environment import test_directories, test_database, test_ffmpeg, test_llm
        dir_ok = test_directories()
        db_ok = test_database()
        ffmpeg_ok = test_ffmpeg()
        
        # Determine if LLM check should be bypassed
        skip_llm = os.getenv("SKIP_LLM_CHECK") == "1" or "--skip-llm" in sys.argv
        if skip_llm:
            print("\n[4/4] Local LLM connection check: Bypassed (requested).")
            llm_ok = True
        else:
            llm_ok = test_llm()
            
    except Exception as e:
        print(f"❌ Failed to run environment tests: {e}")
        sys.exit(1)
        
    print("\n==============================================")
    print("             PRE-FLIGHT SUMMARY               ")
    print("==============================================")
    print(f"Directories: {'✅ PASS' if dir_ok else '❌ FAIL'}")
    print(f"Database:    {'✅ PASS' if db_ok else '❌ FAIL'}")
    print(f"ffmpeg:      {'✅ PASS' if ffmpeg_ok else '❌ FAIL'}")
    print(f"Local LLM:   {'⚠️ Bypassed (skip requested)' if skip_llm else ('✅ PASS' if llm_ok else '❌ FAIL')}")
    print("==============================================")
    
    if not all([dir_ok, db_ok, ffmpeg_ok, llm_ok]):
        print("❌ Pre-flight checks failed! Flask server startup aborted.")
        sys.exit(1)
    print("🎉 All required checks passed! Starting Flask server...\n")

if __name__ == "__main__":
    check_integrity()
    check_environment()
    
    port = int(os.getenv('PORT', 10000))
    debug = os.getenv('FLASK_DEBUG', '0') == '1'
    
    # Start Flask server
    app.run(host="0.0.0.0", port=port, debug=debug)
