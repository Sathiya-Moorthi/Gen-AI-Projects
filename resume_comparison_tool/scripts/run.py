# ============================================
# run.py (Optional - Run both servers with one command)
# ============================================

import subprocess
import sys
import time
import os

def run_servers():
    """Run both FastAPI and Streamlit servers"""
    print("🚀 Starting Resume Comparison Tool...")
    print("=" * 60)
    
    # Start FastAPI backend
    print("\n📡 Starting FastAPI backend on http://localhost:8000")
    backend_process = subprocess.Popen(
        [sys.executable, "app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for backend to start
    time.sleep(3)
    
    # Start Streamlit frontend
    print("🎨 Starting Streamlit frontend on http://localhost:8501")
    frontend_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "streamlit_app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    print("\n" + "=" * 60)
    print("✅ Both servers are running!")
    print("=" * 60)
    print("📡 FastAPI Backend: http://localhost:8000")
    print("📡 API Docs: http://localhost:8000/docs")
    print("🎨 Streamlit Frontend: http://localhost:8501")
    print("\n⚠️  Press Ctrl+C to stop both servers")
    print("=" * 60)
    
    try:
        # Keep script running
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down servers...")
        backend_process.terminate()
        frontend_process.terminate()
        print("✅ Servers stopped successfully!")

if __name__ == "__main__":
    run_servers()