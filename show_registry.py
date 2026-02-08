import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for config imports
sys.path.insert(0, str(Path(__file__).parent))
from config.paths import CIT_CORE_REGISTRY
from utils.json_handler import read_json_file

REGISTRY_PATH = str(CIT_CORE_REGISTRY)

def display_registry():
    data = read_json_file(REGISTRY_PATH)
    if not data:
        print("--- [Ciт] РЕЄСТР ПОРОЖНІЙ АБО НЕ СТВОРЕНИЙ ---")
        return

    subscribers = data.get("active_subscribers", {})
    
    print(f"\n{'='*75}")
    print(f" СТАН РЕЄСТРУ Ciт | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*75}")
    print(f"{'IP АБОНЕНТА':<18} | {'ТИП КЛІЄНТА':<12} | {'ОСТАННІЙ ВІЗИТ':<20} | {'СТАТУС'}")
    print(f"{'-'*75}")
    
    for ip, info in subscribers.items():
        c_type = info.get('client_type', 'UNKNOWN')
        last_s = info.get('last_seen', 'N/A')
        status = info.get('provisioning_status', 'N/A')
        print(f"{ip:<18} | {c_type:<12} | {last_s:<20} | {status}")
    
    print(f"{'='*75}")
    print(f"Усього активних систем у шлюзі: {len(subscribers)}")

if __name__ == "__main__":
    display_registry()
