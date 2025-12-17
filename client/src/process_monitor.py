import psutil
import time
from collections import defaultdict

class ProcessMonitor:
    def __init__(self):
        self.process_history = defaultdict(list)
        self.suspicion_score = 0.0
        
    def get_running_processes(self):
        """Get list of all running processes with details"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
            try:
                pinfo = proc.info
                processes.append({
                    'pid': pinfo['pid'],
                    'name': pinfo['name'].lower() if pinfo['name'] else '',
                    'exe': pinfo['exe'].lower() if pinfo['exe'] else '',
                    'cmdline': ' '.join(pinfo['cmdline']).lower() if pinfo['cmdline'] else ''
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return processes
    
    def detect_suspicious_processes(self, processes, keywords):
        """Detect processes matching suspicious keywords"""
        suspicious = []
        
        for proc in processes:
            for keyword in keywords:
                if (keyword in proc['name'] or 
                    keyword in proc['exe'] or 
                    keyword in proc['cmdline']):
                    suspicious.append(proc['name'])
                    break
        
        # Update suspicion score
        if suspicious:
            self.suspicion_score = min(1.0, self.suspicion_score + 0.2)
        else:
            self.suspicion_score = max(0.0, self.suspicion_score - 0.05)
        
        return suspicious
    
    def detect_hidden_browsers(self):
        """Detect browsers running in background"""
        browsers = ['chrome', 'firefox', 'edge', 'safari', 'brave', 'opera']
        hidden_browsers = []
        
        for proc in psutil.process_iter(['name', 'status']):
            try:
                name = proc.info['name'].lower()
                if any(browser in name for browser in browsers):
                    # Check if process has visible window
                    if proc.info['status'] != psutil.STATUS_RUNNING:
                        continue
                    hidden_browsers.append(name)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        return hidden_browsers
    
    def monitor_network_activity(self):
        """Monitor suspicious network connections"""
        connections = []
        suspicious_domains = [
            'openai.com', 'anthropic.com', 'chat.openai.com',
            'claude.ai', 'gemini.google.com', 'copilot.microsoft.com'
        ]
        
        try:
            for conn in psutil.net_connections(kind='inet'):
                if conn.raddr:
                    connections.append({
                        'pid': conn.pid,
                        'remote_addr': conn.raddr.ip,
                        'remote_port': conn.raddr.port,
                        'status': conn.status
                    })
        except (psutil.AccessDenied, PermissionError):
            # May need admin privileges
            pass
        
        return connections
    
    def get_suspicion_score(self):
        """Get current suspicion score (0-1)"""
        return self.suspicion_score
    
    def check_screen_sharing_tools(self):
        """Check if screen sharing or remote desktop tools are running"""
        screen_share_keywords = [
            'zoom', 'teams', 'meet', 'webex', 'skype',
            'teamviewer', 'anydesk', 'vnc'
        ]
        
        processes = self.get_running_processes()
        active_tools = []
        
        for proc in processes:
            for keyword in screen_share_keywords:
                if keyword in proc['name']:
                    active_tools.append(proc['name'])
                    break
        
        return active_tools
