import subprocess
import sys

def run_gabbar_ai():
    try:
        subprocess.run([sys.executable, "-m", "gabbar-ai"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running gabbar-ai: {e}")

if __name__ == "__main__":
    try:
        run_gabbar_ai()
    except KeyboardInterrupt:
        print("")
