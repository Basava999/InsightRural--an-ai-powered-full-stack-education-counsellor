#!/usr/bin/env python3
"""
InsightRural — Cross-Platform Setup & Launcher
================================================
Works on Windows, macOS, and Linux.
Run once to set up, then use to start the project.

Usage:
    python setup.py          # First-time setup
    python setup.py --start  # Start both backend + frontend
    python setup.py --check  # Health check only
"""

import os
import sys
import subprocess
import platform
import shutil
import time
import argparse
import webbrowser

ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT, "college", "backend")
FRONTEND_DIR = os.path.join(ROOT, "insightrural-frontend")
IS_WINDOWS = platform.system() == "Windows"

# ── Helpers ────────────────────────────────────────────────────────────────────

def run(cmd, cwd=None, check=True):
    print(f"  > {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    return subprocess.run(cmd, cwd=cwd, check=check, shell=IS_WINDOWS)

def venv_python():
    if IS_WINDOWS:
        return os.path.join(BACKEND_DIR, ".venv", "Scripts", "python.exe")
    return os.path.join(BACKEND_DIR, ".venv", "bin", "python")

def venv_pip():
    if IS_WINDOWS:
        return os.path.join(BACKEND_DIR, ".venv", "Scripts", "pip.exe")
    return os.path.join(BACKEND_DIR, ".venv", "bin", "pip")

def ok(msg):  print(f"  [OK] {msg}")
def err(msg): print(f"  [!!] {msg}")
def section(title): print(f"\n{'='*60}\n  {title}\n{'='*60}")

# ── Steps ──────────────────────────────────────────────────────────────────────

def check_python():
    section("Checking Python version")
    major, minor = sys.version_info[:2]
    if major < 3 or minor < 10:
        err(f"Python 3.10+ required. You have {major}.{minor}. Please upgrade.")
        sys.exit(1)
    ok(f"Python {major}.{minor} detected.")

def create_venv():
    section("Creating virtual environment")
    venv_path = os.path.join(BACKEND_DIR, ".venv")
    if os.path.isdir(venv_path):
        ok(".venv already exists — skipping creation.")
        return
    run([sys.executable, "-m", "venv", ".venv"], cwd=BACKEND_DIR)
    ok("Virtual environment created.")

def install_deps():
    section("Installing Python dependencies")
    req = os.path.join(BACKEND_DIR, "requirements.txt")
    run([venv_pip(), "install", "--upgrade", "pip", "--quiet"])
    run([venv_pip(), "install", "-r", req, "--quiet"])
    ok("All dependencies installed.")

def setup_env():
    section("Setting up .env file")
    env_file = os.path.join(BACKEND_DIR, ".env")
    env_example = os.path.join(BACKEND_DIR, ".env.example")
    if os.path.isfile(env_file):
        ok(".env already exists — skipping.")
        return
    if os.path.isfile(env_example):
        shutil.copy(env_example, env_file)
        ok(".env created from .env.example")
        print("  ⚠  Edit college/backend/.env and add your API keys (Groq, etc.) for AI features.")
    else:
        err(".env.example not found. Creating minimal .env...")
        with open(env_file, "w") as f:
            f.write("JWT_SECRET_KEY=insightrural_change_me_in_production\n")
            f.write("GROQ_API_KEY=\n")
            f.write("OLLAMA_HOST=http://localhost:11434\n")
            f.write("OLLAMA_MODEL=llama3\n")

def create_uploads_dir():
    section("Ensuring data directories exist")
    uploads = os.path.join(BACKEND_DIR, "data", "uploads")
    os.makedirs(uploads, exist_ok=True)
    gitkeep = os.path.join(uploads, ".gitkeep")
    if not os.path.exists(gitkeep):
        open(gitkeep, "w").close()
    ok(f"data/uploads/ ready")

def start_backend():
    section("Starting Backend (Flask) on port 5000")
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    kwargs = dict(cwd=BACKEND_DIR, env=env)
    cmd = [venv_python(), "-X", "utf8", "app.py"]
    if IS_WINDOWS:
        subprocess.Popen(
            ["cmd", "/k"] + cmd,
            creationflags=subprocess.CREATE_NEW_CONSOLE,
            **kwargs
        )
    else:
        subprocess.Popen(cmd, **kwargs)
    ok("Backend starting at http://127.0.0.1:5000")

def start_frontend():
    section("Starting Frontend (HTTP server) on port 8000")
    cmd = [sys.executable, "-m", "http.server", "8000"]
    kwargs = dict(cwd=FRONTEND_DIR)
    if IS_WINDOWS:
        subprocess.Popen(
            ["cmd", "/k"] + cmd,
            creationflags=subprocess.CREATE_NEW_CONSOLE,
            **kwargs
        )
    else:
        subprocess.Popen(cmd, **kwargs)
    ok("Frontend starting at http://localhost:8000")

def health_check():
    section("Running Health Check")
    try:
        import urllib.request
        time.sleep(3)
        with urllib.request.urlopen("http://127.0.0.1:5000/api/health", timeout=5) as r:
            ok(f"Backend /api/health → {r.status}")
    except Exception as e:
        err(f"Backend not reachable yet: {e}")
        print("  (This is normal if the backend just started — wait a few seconds and retry.)")

# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="InsightRural setup/launcher")
    parser.add_argument("--start",  action="store_true", help="Start backend + frontend")
    parser.add_argument("--check",  action="store_true", help="Health check only")
    parser.add_argument("--setup",  action="store_true", help="Run setup only (no start)")
    args = parser.parse_args()

    print("\n🎓  InsightRural — Cross-Platform Setup & Launcher")
    print(f"    OS: {platform.system()} | Python: {sys.version.split()[0]}\n")

    if args.check:
        health_check()
        return

    # Always run setup
    check_python()
    create_venv()
    install_deps()
    setup_env()
    create_uploads_dir()

    if args.setup:
        section("Setup Complete!")
        print("\n  ✅ Everything is ready.")
        print("  ▶  To start the app: python setup.py --start")
        return

    if args.start or not any(vars(args).values()):
        start_backend()
        time.sleep(5)
        start_frontend()
        time.sleep(2)
        webbrowser.open("http://localhost:8000")
        section("InsightRural is Running!")
        print("  Backend  → http://127.0.0.1:5000")
        print("  Frontend → http://localhost:8000")
        print("\n  Press Ctrl+C to stop.\n")
        health_check()


if __name__ == "__main__":
    main()
