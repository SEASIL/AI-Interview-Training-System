"""
launch_colab.py  –  AI Interview Training System
Free tunnels only – no pyngrok, no paid service, no signup needed.
Uses Cloudflare Tunnel (best) → localtunnel → serveo as fallbacks.

Usage in Google Colab:
    !python launch_colab.py
"""

import subprocess
import threading
import time
import sys
import os
import re


# ─────────────────────────────────────────────────────────────
# Step 1 – install dependencies  (Gemini, no Anthropic/pyngrok)
# ─────────────────────────────────────────────────────────────
def install_deps():
    packages = [
        "streamlit",
        "google-generativeai",
        "textblob",
        "nltk",
        "mediapipe",
        "opencv-python-headless",
        
        "SpeechRecognition",
        "pandas",
        "Pillow",
    ]
    print("📦 Installing dependencies...")
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "-q"] + packages
    )
    print("✅ All packages installed.")


# ─────────────────────────────────────────────────────────────
# Step 2 – NLTK data
# ─────────────────────────────────────────────────────────────
def setup_nltk():
    import nltk
    for pkg in ["punkt", "stopwords", "averaged_perceptron_tagger", "punkt_tab"]:
        nltk.download(pkg, quiet=True)
    print("✅ NLTK data ready.")


# ─────────────────────────────────────────────────────────────
# Step 3 – start Streamlit in background
# ─────────────────────────────────────────────────────────────
def start_streamlit(port: int = 8501):
    def run():
        subprocess.run([
            "streamlit", "run", "app.py",
            "--server.port", str(port),
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false",
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false",
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    threading.Thread(target=run, daemon=True).start()
    print(f"⏳ Starting Streamlit on port {port}...")
    time.sleep(6)
    print("✅ Streamlit is running.")


# ─────────────────────────────────────────────────────────────
# Tunnel 1: Cloudflare (FREE – best option, no account needed)
# ─────────────────────────────────────────────────────────────
def try_cloudflared(port: int) -> str | None:
    try:
        binary = "/usr/local/bin/cloudflared"
        if not os.path.exists(binary):
            print("   Downloading cloudflared binary...")
            subprocess.check_call([
                "wget", "-q",
                "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64",
                "-O", binary
            ])
            subprocess.check_call(["chmod", "+x", binary])

        proc = subprocess.Popen(
            [binary, "tunnel", "--url", f"http://localhost:{port}"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )

        for _ in range(25):
            line = proc.stderr.readline()
            if "trycloudflare.com" in line or ("https://" in line and "INF" in line):
                urls = re.findall(r'https://[^\s]+', line)
                if urls:
                    return urls[0].rstrip("|")
            time.sleep(1)
    except Exception as e:
        print(f"   cloudflared error: {e}")
    return None


# ─────────────────────────────────────────────────────────────
# Tunnel 2: localtunnel (FREE – no account, uses Node.js)
# ─────────────────────────────────────────────────────────────
def try_localtunnel(port: int) -> str | None:
    try:
        subprocess.check_call(
            ["npm", "install", "-g", "localtunnel"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        proc = subprocess.Popen(
            ["lt", "--port", str(port)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        for _ in range(15):
            line = proc.stdout.readline()
            if "https://" in line:
                urls = re.findall(r'https://[^\s]+', line)
                if urls:
                    return urls[0]
            time.sleep(1)
    except Exception as e:
        print(f"   localtunnel error: {e}")
    return None


# ─────────────────────────────────────────────────────────────
# Tunnel 3: serveo (FREE – SSH-based, zero install)
# ─────────────────────────────────────────────────────────────
def try_serveo(port: int) -> str | None:
    try:
        proc = subprocess.Popen(
            ["ssh", "-o", "StrictHostKeyChecking=no",
             "-R", f"80:localhost:{port}", "serveo.net"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        for _ in range(15):
            line = proc.stdout.readline() + proc.stderr.readline()
            if "serveo.net" in line and "https" in line:
                urls = re.findall(r'https://[^\s]+', line)
                if urls:
                    return urls[0]
            time.sleep(1)
    except Exception as e:
        print(f"   serveo error: {e}")
    return None


# ─────────────────────────────────────────────────────────────
# Tunnel 4: Colab built-in (always works as last resort)
# ─────────────────────────────────────────────────────────────
def try_colab_builtin(port: int) -> str | None:
    try:
        from google.colab.output import eval_js
        url = eval_js(f"google.colab.kernel.proxyPort({port})")
        return url
    except Exception:
        return None


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    PORT = 8501

    install_deps()
    setup_nltk()
    start_streamlit(PORT)

    print("\n🔗 Finding a free public tunnel...")

    url = None

    print("\n[1/4] Trying Cloudflare tunnel (free, no account)...")
    url = try_cloudflared(PORT)

    if not url:
        print("\n[2/4] Trying localtunnel (free, no account)...")
        url = try_localtunnel(PORT)

    if not url:
        print("\n[3/4] Trying serveo (free SSH tunnel)...")
        url = try_serveo(PORT)

    if not url:
        print("\n[4/4] Trying Colab built-in proxy...")
        url = try_colab_builtin(PORT)

    print("\n" + "=" * 60)
    if url:
        print("🚀  AI INTERVIEW TRAINER IS LIVE!")
        print("=" * 60)
        print(f"🌐  Open this link in a new tab:\n    {url}")
        print("=" * 60)
        print("\n✅ 100% free – no signup, no payment required.")
        print("📌 Paste your FREE Gemini API key in the app sidebar.")
        print("   Get it at: https://aistudio.google.com/app/apikey")
        print("\nKeep this cell running to keep the app alive.\n")
    else:
        print("⚠️  All tunnels failed. Try this in a new Colab cell:")
        print("=" * 60)
        print("   from google.colab.output import eval_js")
        print(f"   print(eval_js('google.colab.kernel.proxyPort({PORT})'))")
        print("=" * 60)

    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("\nShutting down...")
