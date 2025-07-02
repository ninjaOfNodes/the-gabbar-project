import os
import subprocess
import sys
import time
import importlib.util
import webbrowser
import platform

# Colored output
BLUE = "\033[94m"
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"
TICK = f"{GREEN}✅{RESET}"
CROSS = f"{RED}❌{RESET}"

# Get absolute path to the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def clear_screen():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def print_status(msg):
    print(f"\n{BOLD}=== {msg} ==={RESET}\n")

def is_package_installed(package_name):
    spec = importlib.util.find_spec(package_name)
    return spec is not None

def install_package(package_name):
    print(f"🔄 Installing {package_name} ...", end=' ', flush=True)
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", package_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print(f"{TICK} {package_name}")
    except subprocess.CalledProcessError:
        print(f"{CROSS} Failed to install {package_name}")

def process_requirements():
    # Always resolve requirements.txt relative to this script's directory
    requirements_file = os.path.join(BASE_DIR, 'requirements.txt')
    print_status("Checking and installing Python dependencies")
    if not os.path.exists(requirements_file):
        print(f"{CROSS} {requirements_file} not found!")
        sys.exit(1)

    with open(requirements_file, 'r') as f:
        packages = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    for pkg in packages:
        pkg_name = pkg.split('==')[0] if '==' in pkg else pkg
        if is_package_installed(pkg_name):
            print(f"{TICK} {pkg_name} already installed")
        else:
            install_package(pkg)

# --- Main Execution ---
if __name__ == '__main__':
  try:
    clear_screen()
    print(fr"""{GREEN}
 ██████╗  █████╗ ██████╗ ██████╗  █████╗ ██████╗      █████╗ ██╗
██╔════╝ ██╔══██╗██╔══██╗██╔══██╗██╔══██╗██╔══██╗    ██╔══██╗██║
██║  ███╗███████║██████╔╝██████╔╝███████║██████╔╝    ███████║██║
██║   ██║██╔══██║██╔══██╗██╔══██╗██╔══██║██╔══██╗    ██╔══██║██║
╚██████╔╝██║  ██║██████╔╝██████╔╝██║  ██║██║  ██║    ██║  ██║██║
 ╚═════╝ ╚═╝  ╚═╝╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝    ╚═╝  ╚═╝╚═╝
{RESET}""")
    print ("Created with "+ f"{RED}❤️{RESET}"+"  from "+f"{GREEN}NinjaOfNodes{RESET}"+" ). \nRead the documents and README.md for further details on how to use it !\n\n\n")
    input("Press enter to Start !")

    process_requirements()

    print_status("Checking and installing Ollama and required models")
    setup_ollama_path = os.path.join(BASE_DIR, 'setup_ollama.py')
    subprocess.run([sys.executable, setup_ollama_path])

    print_status("Starting the web server (Flask)")
    subprocess.Popen([sys.executable, '-m', 'app'], cwd=BASE_DIR)

    print("\nThe web app is starting! Open http://localhost:5000 in your browser.\n")
    time.sleep(2)
    webbrowser.open("http://localhost:5000")
    print("(Leave this window open while you use the app.)")
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print(f"{RED}\n\n⛔ Exiting. You can close this window !{RESET}")
  except KeyboardInterrupt:
    print(f"{RED}\n\n⚠️Program stopped by user !{RESET}")
    exit(0)