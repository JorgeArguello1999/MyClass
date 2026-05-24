import os
import sys

from app import create_app, db

# Initialize the app with the environment defined in FLASK_CONFIG (default is "development")
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

def check_integrity():
    print("Verifying environment integrity...")
    
    # 1. Check if .env exists
    base_dir = os.path.abspath(os.path.dirname(__file__))
    env_path = os.path.join(base_dir, '.env')
    if not os.path.exists(env_path):
        print("⚠️ .env file not found. Make sure to configure it correctly.")
    else:
        print("✅ .env file verified.")
        
    # 2. Run Database Migrations Automatically
    try:
        from flask_migrate import upgrade, migrate
        with app.app_context():
            print("🔄 Running database migrations (migrate & upgrade)...")
            migrate()
            upgrade()
            print("✅ Database migrations applied successfully.")
    except Exception as e:
        print(f"❌ Error running migrations: {e}")
        sys.exit(1)

    # 3. Check Database connection
    try:
        with app.app_context():
            # Try to start a basic connection
            with db.engine.connect() as conn:
                pass
        print("✅ Database connection verified.")
    except Exception as e:
        print(f"❌ Error connecting to Database: {e}")
        sys.exit(1)
        
    # 4. Check LLM connection if configured
    provider = os.getenv("LLM_PROVIDER", "mock").lower()
    if provider == "mock":
        print("ℹ️ LLM Provider is set to 'mock'. Local LLM connectivity check bypassed.")
    elif provider in ("ollama", "lmstudio"):
        model_name = os.getenv("LLM_MODEL")
        base_url = os.getenv("LLM_BASE_URL")
        print(f"🔄 Checking local LLM connection ({provider.upper()} - {model_name} at {base_url})...")
        try:
            if provider == "ollama":
                try:
                    from langchain_ollama import ChatOllama
                except ImportError:
                    print("❌ Missing dependency: 'langchain-ollama'. Please run: uv add langchain-ollama")
                    sys.exit(1)
                llm = ChatOllama(model=model_name, base_url=base_url, temperature=0.3)
            else:  # lmstudio
                try:
                    from langchain_openai import ChatOpenAI
                except ImportError:
                    print("❌ Missing dependency: 'langchain-openai'. Please run: uv add langchain-openai")
                    sys.exit(1)
                llm = ChatOpenAI(
                    model=model_name,
                    openai_api_key="lm-studio",
                    openai_api_base=base_url,
                    temperature=0.3
                )
            
            # Simple test call
            llm.invoke("test connection")
            print("✅ Local LLM connection verified.")
        except Exception as e:
            print(f"❌ Error connecting to Local LLM ({provider.upper()}): {e}")
            print("⚠️ Please ensure the local LLM server is running and the model is downloaded.")
            sys.exit(1)
        
    print("🚀 Verification completed successfully.\n")


if __name__ == "__main__":
    check_integrity()
    # Start Flask's native development server
    app.run(host="0.0.0.0", port=10000, debug=True)
