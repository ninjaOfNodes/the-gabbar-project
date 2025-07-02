import os
import sys
import time
import shutil
import urllib.request
import subprocess
import tempfile
import platform

# Windows Registry for PATH update
if platform.system() == "Windows":
    import winreg

# URL to Ollama Setup for Windows
OLLAMA_WINDOWS_URL = "https://ollama.com/download/OllamaSetup.exe"

# Styling
BLUE = "\033[94m"
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"
TICK = f"{GREEN}✅{RESET}"
CROSS = f"{RED}❌{RESET}"

def print_status(msg):
    print(f"\n{BOLD}=== {msg} ==={RESET}\n")

# --- Download with resume support and progress bar ---
def download_with_resume(url, dest_path):
    resume_byte_pos = 0
    headers = {}
    mode = 'wb'

    if os.path.exists(dest_path):
        resume_byte_pos = os.path.getsize(dest_path)
        headers['Range'] = f'bytes={resume_byte_pos}-'
        mode = 'ab'

    req = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(req)
    total_size = int(response.headers.get('Content-Length', 0)) + resume_byte_pos

    print_status("Downloading Ollama with resume support")
    start = time.time()

    with open(dest_path, mode) as f:
        downloaded = resume_byte_pos
        while True:
            chunk = response.read(8192)
            if not chunk:
                break
            f.write(chunk)
            downloaded += len(chunk)
            percent = downloaded / total_size * 100
            elapsed = time.time() - start
            speed = downloaded / 1024 / 1024 / elapsed if elapsed > 0 else 0
            eta = (total_size - downloaded) / (downloaded / elapsed) if downloaded > 0 else 0
            eta_str = time.strftime("%M:%S", time.gmtime(eta))
            print(f"\rProgress: {percent:6.2f}% | {downloaded/1024/1024:6.2f}/{total_size/1024/1024:.2f} MB | "
                  f"{speed:.2f} MB/s | ETA: {eta_str}", end='', flush=True)
    print(f"\n{TICK} Download complete.")

# --- Ollama Installation ---
def install_ollama_windows():
    temp_dir = tempfile.mkdtemp()
    exe_path = os.path.join(temp_dir, 'OllamaSetup.exe')
    download_with_resume(OLLAMA_WINDOWS_URL, exe_path)
    print_status(f"Running installer: {exe_path}")
    try:
        subprocess.run([exe_path, '/S'], check=True)
        print(f"{TICK} Ollama installed successfully.")
    except subprocess.CalledProcessError:
        print(f"{CROSS} Ollama installation failed.")
        sys.exit(1)

def install_ollama_mac():
    print_status("Installing Ollama via Homebrew")
    try:
        subprocess.run(["brew", "install", "ollama"], check=True)
        print(f"{TICK} Ollama installed via Homebrew.")
    except subprocess.CalledProcessError:
        print(f"{CROSS} Homebrew install failed. Try manual install: https://ollama.com/download")
        sys.exit(1)

def install_ollama_linux():
    print_status("Installing Ollama via curl")
    try:
        subprocess.run("curl -fsSL https://ollama.com/install.sh | sh", shell=True, check=True)
        print(f"{TICK} Ollama installed via shell script.")
    except subprocess.CalledProcessError:
        print(f"{CROSS} curl install failed. Try manual install: https://ollama.com/download")
        sys.exit(1)

def install_ollama():
    system = platform.system()
    if system == "Windows":
        install_ollama_windows()
    elif system == "Darwin":
        install_ollama_mac()
    elif system == "Linux":
        install_ollama_linux()
    else:
        print(f"{CROSS} Unsupported OS. Please install Ollama manually.")
        sys.exit(1)

# --- Executable Detection ---
def find_ollama():
    path = shutil.which("ollama")
    if path:
        return path

    win_path = os.path.expandvars(r"%LocalAppData%\Programs\Ollama\ollama.exe")
    if os.path.isfile(win_path):
        return win_path

    print(f"{CROSS} Ollama executable not found.")
    sys.exit(1)

# --- Add to PATH (Windows only) ---
def add_ollama_to_path_windows(ollama_exe_path):
    ollama_dir = os.path.dirname(ollama_exe_path)
    print_status("Verifying Ollama installation path in system PATH (Windows)")

    # Normalize the path to match case, slashes, and trailing separators
    normalized_ollama_dir = os.path.normcase(os.path.normpath(ollama_dir.strip()))

    # Current session PATH
    current_env_paths = [
        os.path.normcase(os.path.normpath(p.strip()))
        for p in os.environ.get('PATH', '').split(';') if p.strip()
    ]

    # Registry PATH
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Environment', 0, winreg.KEY_ALL_ACCESS) as key:
            try:
                path_value, _ = winreg.QueryValueEx(key, 'Path')
            except FileNotFoundError:
                path_value = ""

            current_registry_paths = [
                os.path.normcase(os.path.normpath(p.strip()))
                for p in path_value.split(';') if p.strip()
            ]

            # If Ollama is already in registry or env PATH
            if normalized_ollama_dir in current_env_paths or normalized_ollama_dir in current_registry_paths:
                print(f"{TICK} Ollama path is already in PATH.")
                return

            # Append to registry PATH
            new_path = path_value + ";" + ollama_dir if path_value else ollama_dir
            winreg.SetValueEx(key, 'Path', 0, winreg.REG_EXPAND_SZ, new_path)

            # Append to current session PATH so script can find it immediately
            os.environ["PATH"] += ";" + ollama_dir

            print(f"{TICK} Ollama path added to PATH. Please restart your terminal to apply system-wide.")
    except Exception as e:
        print(f"{CROSS} Failed to update PATH: {e}")

# --- Optional Debug Function ---
def debug_env_path(ollama_path):
    ollama_dir = os.path.normcase(os.path.normpath(os.path.dirname(ollama_path)))

    for p in os.environ.get('PATH', '').split(';'):
        norm = os.path.normcase(os.path.normpath(p.strip()))

# --- Ollama Checks ---
def is_ollama_installed():
    return shutil.which("ollama") or os.path.isfile(
        os.path.expandvars(r"%LocalAppData%\Programs\Ollama\ollama.exe"))

def model_installed(ollama_path, model_name):
    try:
        result = subprocess.run([ollama_path, 'list'], capture_output=True, text=True)
        return model_name in result.stdout
    except Exception:
        return False

def pull_model(ollama_path, model_name):
    print_status(f"Pulling model: {model_name}")
    try:
        subprocess.run([ollama_path, 'pull', model_name], check=True)
        print(f"{TICK} Pulled model: {model_name}")
    except subprocess.CalledProcessError:
        print(f"{CROSS} Failed to pull model: {model_name}")

# --- Ensure Models ---
def ensure_models(ollama_path):
    models = ['llama2','codellama']

    for model in models:
        if model_installed(ollama_path, model):
            print(f"{TICK} Model '{model}' already installed.")
        else:
            if model=='codellama':
                choice = input(f"{BOLD}Do you want to install 'codellama'? (Y/n): {RESET}").strip().lower()
                if choice in ['', 'y', 'yes']:
                    pull_model(ollama_path, model)
            else:
                pull_model(ollama_path, model)

# --- Main Flow ---
if __name__ == "__main__":
    if not is_ollama_installed():
        print(f"{CROSS} Ollama not found. Installing now.")
        install_ollama()
    else:
        print(TICK + " Ollama is already installed.")

    ollama_path = find_ollama()
    # Add to PATH if on Windows and not already present
    if platform.system() == "Windows":
        add_ollama_to_path_windows(ollama_path)
        debug_env_path(ollama_path)

    ensure_models(ollama_path)

    print_status(f"{GREEN}✅ Ollama and models are ready to use!{RESET}")
