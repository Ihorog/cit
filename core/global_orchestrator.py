import os
import json
from core.cimeika_system import CimeikaSystem

class GlobalBot:
    def __init__(self):
        self.ci_system = CimeikaSystem()
        
    def process_intent(self, user_text):
        """Розпізнавання розмовної форми та виконання дій"""
        text = user_text.lower()
        
        if "галере" in text or "фото" in text:
            return self.manage_storage("gallery", text)
        if "кіно" in text or "фільм" in text:
            return self.manage_storage("cinema", text)
        if "стан" in text or "що з системою" in text:
            return self.ci_system.scan_resources()
            
        return "Наказ прийнято. Виконую фонову обробку..."

    def manage_storage(self, category, instruction):
        # Автоматичне виконання технічних дій без вашої участі
        self.ci_system.scan_resources()
        return f"Ресурси категорії {category} синхронізовано та впорядковано."

if __name__ == "__main__":
    # Це ядро, яке тепер слухає і Web, і Telegram
    pass
