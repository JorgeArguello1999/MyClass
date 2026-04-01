import os
import sys

from app import create_app, db

# Inicializa la app con el entorno definido en FLASK_CONFIG (por defecto "development")
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

def check_integrity():
    print("Verificando integridad del entorno...")
    
    # 1. Comprobar que existe .env
    base_dir = os.path.abspath(os.path.dirname(__file__))
    env_path = os.path.join(base_dir, '.env')
    if not os.path.exists(env_path):
        print("⚠️ No se encontró el archivo .env. Asegúrate de configurarlo correctamente.")
    else:
        print("✅ Archivo .env verificado.")
        
    # 2. Comprobar conexión a la BD
    try:
        with app.app_context():
            # Prueba iniciar una conexión básica
            with db.engine.connect() as conn:
                pass
        print("✅ Conexión a la Base de Datos verificada.")
    except Exception as e:
        print(f"❌ Error al conectar con la Base de Datos: {e}")
        print("ℹ️ Es posible que no hayas ejecutado las migraciones.")
        print("ℹ️ Ejecuta: 'flask db upgrade'")
        sys.exit(1)
        
    print("🚀 Verificación completada exitosamente.\n")

if __name__ == "__main__":
    check_integrity()
    # Inicia el servidor de desarrollo nativo de Flask
    app.run(host="127.0.0.1", port=5000, debug=True)
