"""
Базовий клас для всіх 7 формацій цілісності організму Cimeika
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime


class Formatsiya(ABC):
    """
    Базовий клас формації цілісності
    
    Кожна з 7 формацій наслідує цей клас та реалізує свої унікальні здібності
    """
    
    def __init__(self, nazva: str):
        self.nazva = nazva
        self.aktyvna = False
        self.stan = "neaktyvna"
        self.ostannya_aktyvatsiya: Optional[datetime] = None
        self.tsilisnist_riven = 0.0  # від 0.0 до 1.0
        
    @abstractmethod
    def aktyvuvaty(self) -> Dict[str, Any]:
        """
        Активувати формацію
        Повертає словник зі станом активації
        """
        pass
    
    @abstractmethod
    def vidchuttya_tsilisnosti(self) -> float:
        """
        Повернути поточне відчуття цілісності (0.0 - 1.0)
        """
        pass
    
    @abstractmethod
    def proyav_v_ui(self) -> Dict[str, Any]:
        """
        Повернути дані для відображення в UI
        """
        pass
    
    def dykhaty(self) -> Dict[str, Any]:
        """
        Дихальний цикл формації
        Метод викликається періодично для підтримання зв'язку з Сі
        """
        if not self.aktyvna:
            return {
                "formatsiya": self.nazva,
                "dykhannya": "pryzupynene",
                "tsilisnist": self.tsilisnist_riven
            }
        
        # Оновлення рівня цілісності
        self.tsilisnist_riven = self.vidchuttya_tsilisnosti()
        
        return {
            "formatsiya": self.nazva,
            "dykhannya": "aktyvne",
            "tsilisnist": self.tsilisnist_riven,
            "chas": datetime.now().isoformat()
        }
    
    def syhnalizuvaty_trishchynu(self, opys: str, riven_krytychnosti: float) -> Dict[str, Any]:
        """
        Сигналізувати про тріщину в цілісності
        
        Args:
            opys: опис тріщини
            riven_krytychnosti: від 0.0 (легка) до 1.0 (критична)
        """
        return {
            "formatsiya": self.nazva,
            "typ": "trishchyna",
            "opys": opys,
            "krytychnist": riven_krytychnosti,
            "chas": datetime.now().isoformat()
        }
    
    def otrymaty_stan(self) -> Dict[str, Any]:
        """
        Повернути повний стан формації
        """
        return {
            "nazva": self.nazva,
            "aktyvna": self.aktyvna,
            "stan": self.stan,
            "tsilisnist": self.tsilisnist_riven,
            "ostannya_aktyvatsiya": self.ostannya_aktyvatsiya.isoformat() if self.ostannya_aktyvatsiya else None
        }
