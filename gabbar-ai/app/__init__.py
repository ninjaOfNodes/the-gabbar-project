from flask import Flask
import os
import subprocess
import signal
import psutil  # pip install psutil

def create_app():
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    template_dir = os.path.join(base_dir, 'templates')
    static_dir = os.path.join(base_dir, 'assets')
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir, static_url_path='/assets')

    from .routes import main_bp
    app.register_blueprint(main_bp)

    return app

def stop_ollama():
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if 'ollama' in proc.info['name'].lower() or 'ollama' in ' '.join(proc.info['cmdline']).lower():
                print(f"Stopping ollama process (PID {proc.pid})...")
                proc.terminate()
                proc.wait(timeout=5)
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return False

def start_ollama():
    print("Starting ollama...")
    subprocess.Popen(['ollama', 'serve'])

# For running with 'python -m app'
if __name__ == '__main__':
    # Stop if already running
    stop_ollama()

    # Start fresh
    start_ollama()

    # Start Flask app
    app = create_app()
    app.run(debug=True, host='0.0.0.0')
