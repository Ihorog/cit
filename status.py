import sys
import os
import subprocess
from pathlib import Path
from datetime import datetime

# Add parent directory to path for utils imports
sys.path.insert(0, str(Path(__file__).parent))
from utils.json_handler import read_json_file

def get_node_status(port=5000):
    # Перевірка чи живий сервер
    try:
        result = subprocess.check_output(["lsof", f"-i:{port}"], stderr=subprocess.STDOUT)
        return "ONLINE", "Active"
    except subprocess.CalledProcessError:
        return "OFFLINE", "Inactive"

def check_registry():
    path = "docs/wiki/registry/matrix.json"
    return "VALID" if os.path.exists(path) else "MISSING"

def display_dashboard():
    matrix = read_json_file("docs/wiki/registry/matrix.json")
    
    if not matrix:
        print("Error: Could not load matrix.json")
        return
    
    print(f"\n{'='*75}")
    print(f"  CIMEIKA GLOBAL MONITOR | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*75}")
    print(f"{'NODE_ID':<20} | {'ROLE':<15} | {'STATUS':<10} | {'LHC POLICY'}")
    print(f"{'-'*75}")
    
    for node_id, info in matrix['nodes'].items():
        # Для локального вузла перевіряємо реально, для інших - статус зв'язку
        current_status, msg = ("ONLINE", "Ready") if node_id == "NODE-TMX-ADMIN" else ("REMOTE", "Monitoring")
        if node_id == "NODE-TMX-ADMIN":
            real_status, _ = get_node_status()
            current_status = real_status

        print(f"{node_id:<20} | {info['role']:<15} | {current_status:<10} | {info['lhc_policy']}")
    
    print(f"{'='*75}")
    print(f"Registry: {check_registry()} | Mode: {matrix['policies']['GEC-2']}")
    print(f"{'='*75}\n")

if __name__ == "__main__":
    display_dashboard()
