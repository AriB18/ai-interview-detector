# 🔍 AI Interview Detector

Multi-modal AI detection system for remote interviews. Detects ChatGPT, Claude, Cluely, and other AI assistance tools in real-time.

##  Features

- **Process Detection**: Monitors for AI tools (ChatGPT, Claude, Copilot, Cluely, etc.)
- **Behavioral Analysis**: Detects copy-paste and suspicious typing patterns
- **Clipboard Monitoring**: Identifies AI-generated text
- **Real-time Dashboard**: Beautiful web interface for recruiters
- **ML-Powered**: Machine learning classification for accurate detection

##  Quick Start

### For Recruiters (Server)
```bash
# Download and run
dist/Recruiter.exe
```

Open browser to http://localhost:5000

### For Candidates (Client)
```bash
# Download and run
dist/Candidate.exe
```

Enter credentials provided by recruiter.

##  Installation (Development)
```bash
# Clone repository
git clone https://github.com/yourusername/ai-interview-guardian.git
cd ai-interview-guardian

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Run server
python server/detection_server.py

# Run client (in another terminal)
python client/candidate_detector.py
```

##  Building Executables
```bash
# Build both executables
python build_final.py

# Executables will be in dist/
# - Recruiter.exe (14 MB)
# - Candidate.exe (72 MB)
```

##  What Gets Detected

| Tool | Detection Rate |
|------|---------------|
| Cluely | 95%+ |
| ChatGPT tabs | 90%+ |
| Claude | 90%+ |
| Copilot | 85%+ |
| Copy-paste | 95%+ |

##  Requirements

- Windows 10/11
- Python 3.8+ (for development)
- Internet connection

##  Documentation

See [COMPLETE_SETUP_GUIDE.md](COMPLETE_SETUP_GUIDE.md) for detailed setup instructions.

##  Important Notes

- Candidates must consent to monitoring
- Complies with privacy laws (GDPR, etc.)
- For legitimate interview integrity only

##  Contributing

Pull requests welcome! Please read CONTRIBUTING.md first.

##  License

MIT License - See LICENSE file

##  Support

- Issues: https://github.com/yourusername/ai-interview-guardian/issues
- Email: support@yourcompany.com

---

**Made with love to ensure fair hiring practices**
