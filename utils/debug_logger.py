import os
import datetime

class XMLDebugLogger:
    def __init__(self, filepath="debug_xml.log"):
        self.filepath = filepath
        with open(self.filepath, 'w', encoding='utf-8') as f:
            f.write(f"=== INÍCIO DO PROCESSAMENTO DE XML ===\n")
            
    def log(self, section, message):
        with open(self.filepath, 'a', encoding='utf-8') as f:
            f.write(f"\n[{section}]\n{message}\n")
            
    def log_raw(self, message):
        with open(self.filepath, 'a', encoding='utf-8') as f:
            f.write(f"{message}\n")
