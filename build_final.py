"""
Final Complete Build Script
"""
import subprocess
import sys
import os
import shutil

print("""
╔════════════════════════════════════════════════════════════╗
║   🏗️  FINAL BUILD - Both Executables                      ║
╚════════════════════════════════════════════════════════════╝
""")

# Clean
print("🧹 Cleaning...")
for folder in ["build", "dist"]:
    if os.path.exists(folder):
        shutil.rmtree(folder)

for spec in ["Recruiter.spec", "Candidate.spec"]:
    if os.path.exists(spec):
        os.remove(spec)

# Build Recruiter
print("\n🔨 Building Recruiter (2-3 min)...")
subprocess.run([
    sys.executable, "-m", "PyInstaller",
    "--onefile", "--console",
    "--name=Recruiter",
    "--add-data=server/templates;templates",
    "--collect-all=flask",
    "--collect-all=flask_socketio",
    "--collect-all=werkzeug",
    "server/detection_server.py", "-y"
], check=True)

print("✅ Recruiter done!")

# Build Candidate
print("\n🔨 Building Candidate (3-5 min)...")
subprocess.run([
    sys.executable, "-m", "PyInstaller",
    "--onefile", "--console",
    "--name=Candidate",
    "--add-data=src;src",
    "--hidden-import=process_monitor",
    "--hidden-import=behavioral_monitor", 
    "--hidden-import=ml_classifier",
    "--hidden-import=audio_analyzer_stub",
    "--collect-all=psutil",
    "--collect-all=pynput",
    "--collect-all=pyperclip",
    "--collect-all=sklearn",
    "--collect-all=numpy",
    "client/candidate_detector.py", "-y"
], check=True)

print("✅ Candidate done!")

# Summary
print("""
╔════════════════════════════════════════════════════════════╗
║   ✅ BUILD COMPLETE!                                       ║
╚════════════════════════════════════════════════════════════╝
""")

if os.path.exists("dist/Recruiter.exe"):
    size = os.path.getsize("dist/Recruiter.exe") / (1024*1024)
    print(f"✅ Recruiter.exe: {size:.1f} MB")

if os.path.exists("dist/Candidate.exe"):
    size = os.path.getsize("dist/Candidate.exe") / (1024*1024)
    print(f"✅ Candidate.exe: {size:.1f} MB")

print("\n📦 Ready to distribute!")
print("\nTest:")
print("  cd dist")
print("  Recruiter.exe")
print("  Candidate.exe")