import os
import sys
import shutil
import subprocess
from dotenv import load_dotenv

# Ensure we are in the root directory of the project to allow imports from app
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Load environment variables from the root .env file
load_dotenv(os.path.join(project_root, '.env'))

print("==============================================")
print("   SYSTEM ENVIRONMENT & INTEGRITY TEST      ")
print("==============================================")

def test_directories():
    print("\n[1/4] Checking required directories...")
    dirs = {
        "Audio Uploads": os.path.join(project_root, "app", "static", "uploads", "audio"),
        "Profile Uploads": os.path.join(project_root, "app", "static", "uploads", "profiles"),
    }
    
    all_ok = True
    for name, path in dirs.items():
        if os.path.exists(path):
            print(f"✅ {name}: Exists at '{path}'")
        else:
            print(f"⚠️ {name}: Missing at '{path}' (Attempting to create...)")
            try:
                os.makedirs(path, exist_ok=True)
                print(f"   ✅ Successfully created '{path}'")
            except Exception as e:
                print(f"   ❌ Failed to create '{path}': {e}")
                all_ok = False
    return all_ok

def test_database():
    print("\n[2/4] Checking database connection...")
    try:
        from app import create_app, db
        app = create_app(os.getenv('FLASK_CONFIG') or 'default')
        with app.app_context():
            with db.engine.connect() as conn:
                pass
        print("✅ Database: Connection successful!")
        return True
    except Exception as e:
        print(f"❌ Database: Connection failed! Error: {e}")
        return False

def test_ffmpeg():
    print("\n[3/4] Checking ffmpeg installation...")
    ffmpeg_path = shutil.which("ffmpeg")
    ffprobe_path = shutil.which("ffprobe")
    
    all_ok = True
    if ffmpeg_path:
        print(f"✅ ffmpeg: Found at '{ffmpeg_path}'")
        try:
            # Check version
            res = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, timeout=5)
            version_line = res.stdout.split("\n")[0]
            print(f"   Version details: {version_line}")
        except Exception as e:
            print(f"   ⚠️ Could not run 'ffmpeg -version': {e}")
    else:
        print("❌ ffmpeg: NOT found in system PATH.")
        print("   Required to convert webm recording chunks to wav for speech recognition.")
        all_ok = False
        
    if ffprobe_path:
        print(f"✅ ffprobe: Found at '{ffprobe_path}'")
    else:
        print("❌ ffprobe: NOT found in system PATH.")
        print("   Highly recommended to process audio streams correctly.")
        all_ok = False
        
    return all_ok

def test_llm():
    print("\n[4/4] Checking local LLM connection...")
    provider = os.getenv("LLM_PROVIDER", "mock").lower()
    model_name = os.getenv("LLM_MODEL")
    base_url = os.getenv("LLM_BASE_URL")
    
    if provider == "mock":
        print("ℹ️ LLM Provider is set to 'mock'. Connectivity test bypassed.")
        return True
        
    print(f"Configured Provider: {provider.upper()}")
    print(f"Configured Model: {model_name}")
    print(f"Configured URL: {base_url}")
    
    try:
        if provider == "ollama":
            from langchain_ollama import ChatOllama
            llm = ChatOllama(model=model_name, base_url=base_url, temperature=0.3)
        elif provider == "lmstudio":
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(
                model=model_name,
                openai_api_key="lm-studio",
                openai_api_base=base_url,
                temperature=0.3
            )
        elif provider == "openai":
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(
                model=model_name or "gpt-4o-mini",
                openai_api_key=os.getenv("OPENAI_API_KEY"),
                temperature=0.3
            )
        elif provider == "deepseek":
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(
                model=model_name or "deepseek-chat",
                openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
                openai_api_base=base_url or "https://api.deepseek.com",
                temperature=0.3
            )
        elif provider in ("claude", "anthropic"):
            from langchain_anthropic import ChatAnthropic
            llm = ChatAnthropic(
                model=model_name or "claude-3-5-sonnet-latest",
                api_key=os.getenv("ANTHROPIC_API_KEY"),
                temperature=0.3
            )
        else:
            print(f"❌ LLM: Unsupported provider '{provider}'")
            return False
            
        print("Sending test prompt: 'Please reply with OK'...")
        response = llm.invoke("Please reply with: OK")
        print(f"✅ LLM Response: {response.content.strip()}")
        return True
    except ImportError as ie:
        print(f"❌ LLM: Missing package dependencies. {ie}")
        print(f"   Please run: uv add langchain-{ 'ollama' if provider == 'ollama' else 'openai' }")
        return False
    except Exception as e:
        print(f"❌ LLM: Connection failed. Error: {e}")
        print("   Verify your local LLM server is running and the model is downloaded.")
        return False

if __name__ == "__main__":
    dir_ok = test_directories()
    db_ok = test_database()
    ffmpeg_ok = test_ffmpeg()
    llm_ok = test_llm()
    
    print("\n==============================================")
    print("                SUMMARY                       ")
    print("==============================================")
    print(f"Directories: {'✅ PASS' if dir_ok else '❌ FAIL'}")
    print(f"Database:    {'✅ PASS' if db_ok else '❌ FAIL'}")
    print(f"ffmpeg:      {'✅ PASS' if ffmpeg_ok else '❌ FAIL'}")
    print(f"Local LLM:   {'✅ PASS' if llm_ok else '❌ FAIL'}")
    print("==============================================")
    
    if all([dir_ok, db_ok, ffmpeg_ok, llm_ok]):
        print("🎉 All systems are ready and correctly configured!")
        sys.exit(0)
    else:
        print("⚠️ Some checks failed. Please review the output details above.")
        sys.exit(1)
