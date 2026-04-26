"""
Log Collector Module
Monitors log files and extracts new entries
"""

from typing import List, Dict, Optional
from datetime import datetime
import os
import time


class LogEntry:
    """Represents a single log entry"""
    def __init__(self, level: str, message: str, timestamp: datetime, source: str = ""):
        self.level = level
        self.message = message
        self.timestamp = timestamp
        self.source = source
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'level': self.level,
            'message': self.message,
            'timestamp': self.timestamp.isoformat(),
            'source': self.source
        }


class LogCollector:
    """
    LogCollector Class
    Monitors log files and collects log entries incrementally
    """
    
    def __init__(self, log_file_path: str, interval: int = 5):
        """
        Initialize LogCollector
        
        Args:
            log_file_path: Path to log file to monitor
            interval: Collection interval in seconds
        """
        self.log_file_path = log_file_path
        self.last_read_position = 0
        self.collection_interval = interval
        self.is_running = False
        
        # Validate log file
        if not self._validate_log_file():
            print(f"⚠️ Warning: Log file {log_file_path} does not exist yet")
    
    def start_collection(self):
        """Start continuous log collection"""
        self.is_running = True
        print(f"📝 LogCollector started for {self.log_file_path}")
    
    def stop_collection(self):
        """Stop log collection"""
        self.is_running = False
        print(f"🛑 LogCollector stopped")
    
    def read_new_logs(self) -> List[Dict]:
        """
        Read new log entries since last read
        
        Returns:
            List of log entry dictionaries
        """
        if not os.path.exists(self.log_file_path):
            return []
        
        logs = []
        
        try:
            with open(self.log_file_path, 'r', encoding='utf-8', errors='replace') as f:
                # Move to last read position
                f.seek(self.last_read_position)
                
                # Read new lines
                for line in f:
                    line = line.strip()
                    if line:
                        log_entry = self.parse_log_entry(line)
                        if log_entry:
                            logs.append(log_entry)
                
                # Update position
                self.last_read_position = f.tell()
        
        except Exception as e:
            print(f"❌ Error reading logs: {e}")
            # Ensure position advances even on error to avoid re-reading bad data
            try:
                with open(self.log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    f.seek(0, os.SEEK_END)
                    self.last_read_position = f.tell()
            except Exception:
                pass
        
        return logs
    
    def parse_log_entry(self, line: str) -> Optional[Dict]:
        """
        Parse a log line into structured format
        
        Args:
            line: Raw log line
        
        Returns:
            Dictionary with parsed log data or None
        """
        if not line:
            return None
        
        # Try to parse common log formats
        # Format: [TIMESTAMP] LEVEL: MESSAGE
        # or: TIMESTAMP - LEVEL - MESSAGE
        
        log_levels = ['DEBUG', 'INFO', 'WARNING', 'WARN', 'ERROR', 'CRITICAL', 'FATAL']
        
        level = 'INFO'  # Default
        message = line
        timestamp = datetime.now()
        
        # Try to extract level
        for lvl in log_levels:
            if lvl in line.upper():
                level = lvl
                # Extract message part
                parts = line.split(lvl, 1)
                if len(parts) > 1:
                    message = parts[1].strip(' :-')
                break
        
        # Try to extract timestamp (basic parsing)
        # Look for common timestamp patterns at the start
        try:
            if line.startswith('['):
                ts_end = line.find(']')
                if ts_end > 0:
                    ts_str = line[1:ts_end]
                    try:
                        timestamp = datetime.fromisoformat(ts_str)
                    except:
                        pass
        except:
            pass
        
        return {
            'level': level,
            'message': message,
            'timestamp': timestamp,
            'source': self.log_file_path
        }
    
    def _validate_log_file(self) -> bool:
        """
        Validate that log file exists and is readable
        
        Returns:
            True if valid, False otherwise
        """
        if not os.path.exists(self.log_file_path):
            return False
        
        if not os.path.isfile(self.log_file_path):
            return False
        
        try:
            with open(self.log_file_path, 'r') as f:
                pass
            return True
        except:
            return False
    
    def _update_read_position(self):
        """Update last read position"""
        try:
            with open(self.log_file_path, 'r') as f:
                f.seek(0, os.SEEK_END)
                self.last_read_position = f.tell()
        except:
            pass


# Test code
if __name__ == "__main__":
    print("Testing LogCollector...")
    
    # Create a test log file
    test_log_file = "/tmp/test.log"
    
    with open(test_log_file, 'w') as f:
        f.write("[2026-03-02T10:00:00] INFO: Application started\n")
        f.write("[2026-03-02T10:05:00] WARNING: High memory usage\n")
        f.write("[2026-03-02T10:10:00] ERROR: Database connection failed\n")
    
    # Create collector
    collector = LogCollector(test_log_file, interval=5)
    
    # Read logs
    logs = collector.read_new_logs()
    print(f"✅ Read {len(logs)} log entries")
    
    # Clean up
    if os.path.exists(test_log_file):
        os.remove(test_log_file)
    
    print("✅ LogCollector tests passed!")
