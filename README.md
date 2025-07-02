# GABBAR Ai powered by (Llama2 & CodeLlama)

## 🚀 Quick Start (Beginner Friendly)

1. **Make sure you have Python 3.8+ installed.**
2. **Open a terminal in this folder.**
3. **Run:**

   ```bash
   python -m gabbar-ai
   ```
   OR
   ```bash
   python start.py
   ```
   For windows use the **gabbarAI.bat** file to start the project

That's it! The script will:
- Install all required Python packages
- Check and install Ollama (if needed)
- Download the Llama2 and CodeLlama models (if needed)
- Start the web chat app

When you see the message:

> The web app is starting! Open http://localhost:5000 in your browser.

Go to that address in your browser and start chatting!

---

## 📁 Project Structure

- `__main__.py` — One-command setup and launch script
- `setup_ollama.py` — Installs Ollama and required models
- `app/` — Backend (Flask)
- `templates/` — Frontend HTML (Bootstrap)
- `static/` — CSS/JS for the frontend
- `requirements.txt` — Python dependencies

---

## ❓ Need Help?
If you get stuck, check the messages printed in the terminal—they'll tell you what's happening and what to do next. 

---

## ⚠️ Disclaimer
This project will take aprox **16gb of internet** and **20gb of storage** . It works on **CPU** but it will be better if you have a dedicated **GPU** in your PC.
