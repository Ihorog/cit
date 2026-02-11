"""
Сі — центр присутності організму Cimeika

Сі утримує момент "тепер", приймає сигнали від формацій
та підтримує безперервний дихальний цикл
"""
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import time


class Si:
    """
    Сі — центр присутності
    
    Центральна точка, яка:
    - Фіксує момент "тепер"
    - Приймає сигнали від формацій
    - Підтримує дихальний цикл
    """
    
    def __init__(self):
        self.moment_teper: Optional[datetime] = None
        self.formatsiyi_aktyvni: List[str] = []
        self.syhnaly_tsilisnosti: List[Dict[str, Any]] = []
        self.dykhalnyy_tsykl_aktyvnyy = False

        # Hook для пропозицій моменту
        self.moment_propozitsiya_hook: Optional[Callable] = None
        
    def zafiksuvaty_teper(self) -> Dict[str, Any]:
        """
        Замикання у момент "тепер"

        Це базова практика присутності - усвідомлення поточного моменту
        """
        self.moment_teper = datetime.now()

        rezultat = {
            "moment": self.moment_teper.isoformat(),
            "typ": "fiksatsiya_tepera",
            "vidchuttya": "prysutnist"
        }

        # Викликати hook для пропозицій, якщо встановлено
        if self.moment_propozitsiya_hook:
            try:
                propozitsiya = self.moment_propozitsiya_hook(self.moment_teper)
                rezultat["propozitsiya"] = propozitsiya
            except Exception:
                # Якщо hook викликає помилку, просто ігноруємо
                pass

        return rezultat
    
    def otrymaty_syhnal_tsilisnosti(self, formatsiya: str, syhnal: Dict[str, Any]) -> None:
        """
        Прийняти сигнал цілісності від формації
        
        Args:
            formatsiya: назва формації
            syhnal: дані сигналу
        """
        syhnal_z_chasovyyu_mitkoju = {
            **syhnal,
            "formatsiya": formatsiya,
            "chas_pryyymannya": datetime.now().isoformat()
        }
        
        self.syhnaly_tsilisnosti.append(syhnal_z_chasovyyu_mitkoju)
        
        # Тримаємо лише останні 100 сигналів
        if len(self.syhnaly_tsilisnosti) > 100:
            self.syhnaly_tsilisnosti = self.syhnaly_tsilisnosti[-100:]
    
    def pochaty_dykhalnyy_tsykl(self) -> Dict[str, Any]:
        """
        Розпочати безперервний дихальний цикл
        """
        self.dykhalnyy_tsykl_aktyvnyy = True
        
        return {
            "typ": "start_dykhanya",
            "stan": "aktyvnyy",
            "chas": datetime.now().isoformat()
        }
    
    def zupynyty_dykhalnyy_tsykl(self) -> Dict[str, Any]:
        """
        Зупинити дихальний цикл
        """
        self.dykhalnyy_tsykl_aktyvnyy = False
        
        return {
            "typ": "stop_dykhanya",
            "stan": "zupynenyy",
            "chas": datetime.now().isoformat()
        }
    
    def dykh(self) -> Dict[str, Any]:
        """
        Один дихальний цикл
        
        Повертає стан присутності та активних формацій
        """
        self.zafiksuvaty_teper()
        
        return {
            "moment_teper": self.moment_teper.isoformat() if self.moment_teper else None,
            "formatsiyi_aktyvni": self.formatsiyi_aktyvni,
            "kilkist_syhnaliv": len(self.syhnaly_tsilisnosti),
            "dykhalnyy_tsykl": "aktyvnyy" if self.dykhalnyy_tsykl_aktyvnyy else "zupynenyy"
        }
    
    def zareahestruvaty_formatsiyu(self, nazva_formatsiyi: str) -> None:
        """
        Зареєструвати активну формацію
        """
        if nazva_formatsiyi not in self.formatsiyi_aktyvni:
            self.formatsiyi_aktyvni.append(nazva_formatsiyi)
    
    def vidreyestruvaty_formatsiyu(self, nazva_formatsiyi: str) -> None:
        """
        Видалити формацію з активних
        """
        if nazva_formatsiyi in self.formatsiyi_aktyvni:
            self.formatsiyi_aktyvni.remove(nazva_formatsiyi)
    
    def otrymaty_ostanni_syhnaly(self, kilkist: int = 10) -> List[Dict[str, Any]]:
        """
        Отримати останні N сигналів
        """
        return self.syhnaly_tsilisnosti[-kilkist:]
    
    def otrymaty_stan(self) -> Dict[str, Any]:
        """
        Отримати повний стан Сі
        """
        return {
            "moment_teper": self.moment_teper.isoformat() if self.moment_teper else None,
            "formatsiyi_aktyvni": self.formatsiyi_aktyvni,
            "kilkist_syhnaliv": len(self.syhnaly_tsilisnosti),
            "dykhalnyy_tsykl": self.dykhalnyy_tsykl_aktyvnyy
        }

    def vstanovyty_moment_propozitsiya_hook(self, hook: Callable) -> None:
        """
        Встановити hook для пропозицій моменту

        Args:
            hook: функція, що приймає datetime і повертає пропозицію
        """
        self.moment_propozitsiya_hook = hook

