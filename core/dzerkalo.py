"""
Дзеркало — синхронізація UI ↔ Dev

Дзеркало забезпечує двосторонню синхронізацію між:
- UI (стан, який бачить користувач)
- Dev (технічна реалізація)
через файл manifest.json
"""
import json
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime


class Dzerkalo:
    """
    Дзеркало для синхронізації стану організму
    
    Читає та записує manifest.json, забезпечуючи узгодженість
    між інтерфейсом користувача та внутрішньою реалізацією
    """
    
    def __init__(self, manifest_path: str = "manifest.json"):
        self.manifest_path = Path(manifest_path)
        self.stan_orhanizmu: Optional[Dict[str, Any]] = None
        
    def zavantazhyty_manifest(self) -> Dict[str, Any]:
        """
        Завантажити manifest.json
        
        Returns:
            Словник зі станом організму
        """
        if not self.manifest_path.exists():
            # Створити базовий маніфест, якщо не існує
            return self._stvorty_bazowyy_manifest()
        
        try:
            with open(self.manifest_path, 'r', encoding='utf-8') as f:
                self.stan_orhanizmu = json.load(f)
                return self.stan_orhanizmu
        except Exception as e:
            print(f"Помилка завантаження маніфесту: {e}")
            return self._stvorty_bazowyy_manifest()
    
    def zberihty_manifest(self, stan: Dict[str, Any]) -> bool:
        """
        Зберегти стан в manifest.json
        
        Args:
            stan: словник зі станом для збереження
            
        Returns:
            True, якщо успішно збережено
        """
        try:
            self.stan_orhanizmu = stan
            self.stan_orhanizmu['synkhronizatsiya']['ostannye_onovlennya'] = datetime.now().isoformat()
            
            with open(self.manifest_path, 'w', encoding='utf-8') as f:
                json.dump(self.stan_orhanizmu, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Помилка збереження маніфесту: {e}")
            return False
    
    def onovyty_stan_formatsiyi(self, nazva_formatsiyi: str, stan_formatsiyi: Dict[str, Any]) -> bool:
        """
        Оновити стан конкретної формації
        
        Args:
            nazva_formatsiyi: назва формації
            stan_formatsiyi: новий стан формації
            
        Returns:
            True, якщо успішно оновлено
        """
        if not self.stan_orhanizmu:
            self.zavantazhyty_manifest()
        
        if not self.stan_orhanizmu:
            return False
        
        # Оновити стан формації
        if 'formatsiyi' not in self.stan_orhanizmu:
            self.stan_orhanizmu['formatsiyi'] = {}
        
        self.stan_orhanizmu['formatsiyi'][nazva_formatsiyi] = stan_formatsiyi
        
        # Зберегти
        return self.zberihty_manifest(self.stan_orhanizmu)
    
    def otrymaty_stan_formatsiyi(self, nazva_formatsiyi: str) -> Optional[Dict[str, Any]]:
        """
        Отримати стан конкретної формації
        
        Args:
            nazva_formatsiyi: назва формації
            
        Returns:
            Стан формації або None
        """
        if not self.stan_orhanizmu:
            self.zavantazhyty_manifest()
        
        if not self.stan_orhanizmu or 'formatsiyi' not in self.stan_orhanizmu:
            return None
        
        return self.stan_orhanizmu['formatsiyi'].get(nazva_formatsiyi)
    
    def synkhronizuvaty_ui_do_dev(self) -> Dict[str, Any]:
        """
        Синхронізація UI → Dev
        
        Читає стан з UI та оновлює внутрішню реалізацію
        """
        manifest = self.zavantazhyty_manifest()
        
        return {
            "naprymok": "UI → Dev",
            "stan": manifest,
            "chas": datetime.now().isoformat()
        }
    
    def synkhronizuvaty_dev_do_ui(self, stan_dev: Dict[str, Any]) -> bool:
        """
        Синхронізація Dev → UI
        
        Оновлює manifest.json зі стану внутрішньої реалізації
        
        Args:
            stan_dev: стан з внутрішньої реалізації
            
        Returns:
            True, якщо успішно синхронізовано
        """
        return self.zberihty_manifest(stan_dev)
    
    def _stvorty_bazowyy_manifest(self) -> Dict[str, Any]:
        """
        Створити базову структуру маніфесту
        """
        bazovyy_manifest = {
            "orhanizm": {
                "nazva": "Cimeika",
                "versiya": "0.1.0",
                "stan": "inicializatsiya"
            },
            "formatsiyi": {
                "kazkar": {
                    "nazva": "Казкар",
                    "aktyvna": False,
                    "stan": "neaktyvna",
                    "tsilisnist": 0.0
                }
            },
            "synkhronizatsiya": {
                "ostannye_onovlennya": datetime.now().isoformat(),
                "dzerkalo_aktyvne": True
            }
        }
        
        # Зберегти базовий маніфест
        self.zberihty_manifest(bazovyy_manifest)
        
        return bazovyy_manifest
