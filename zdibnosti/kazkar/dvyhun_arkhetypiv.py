"""
Двигун архетипів — робота з 7 універсальними паттернами

Архетипи — це універсальні паттерни, які повторюються в різних контекстах:
Поріг, Творення, Рефлексія, Цикл, Зв'язок, Мандрівка, Перетворення
"""
from typing import Dict, Any, List, Optional
import yaml
from pathlib import Path
from dataclasses import dataclass


@dataclass
class Arkhetyp:
    """
    Структура архетипу
    """
    id: str
    nazva: str
    symvol: str
    sutnist: str
    tryghery: List[str]
    
    def do_dict(self) -> Dict[str, Any]:
        """Конвертувати в словник"""
        return {
            "id": self.id,
            "nazva": self.nazva,
            "symvol": self.symvol,
            "sutnist": self.sutnist,
            "tryghery": self.tryghery
        }


class DvyhunArkhetypiv:
    """
    Двигун для роботи з 7 архетипами
    
    Завантажує архетипи з YAML файлу та надає методи для їх аналізу
    """
    
    def __init__(self, arkhetypy_path: str = "dani/kazkar/arkhetypy.yaml"):
        self.arkhetypy_path = Path(arkhetypy_path)
        self.arkhetypy: Dict[str, Arkhetyp] = {}
        self._zavantazhyty_arkhetypy()
    
    def _zavantazhyty_arkhetypy(self) -> None:
        """
        Завантажити архетипи з YAML файлу
        """
        if not self.arkhetypy_path.exists():
            # Створити базові архетипи, якщо файл не існує
            self._stvorty_bazovi_arkhetypy()
            return
        
        try:
            with open(self.arkhetypy_path, 'r', encoding='utf-8') as f:
                dani = yaml.safe_load(f)
                
            if dani and 'arkhetypy' in dani:
                for arkh_data in dani['arkhetypy']:
                    arkhetyp = Arkhetyp(
                        id=arkh_data['id'],
                        nazva=arkh_data['nazva'],
                        symvol=arkh_data['symvol'],
                        sutnist=arkh_data['sutnist'],
                        tryghery=arkh_data.get('tryghery', [])
                    )
                    self.arkhetypy[arkhetyp.id] = arkhetyp
        except Exception as e:
            print(f"Помилка завантаження архетипів: {e}")
            self._stvorty_bazovi_arkhetypy()
    
    def _stvorty_bazovi_arkhetypy(self) -> None:
        """
        Створити 7 базових архетипів у пам'яті
        """
        bazovi_arkhetypy = [
            Arkhetyp(
                id="porih",
                nazva="Поріг",
                symvol="🚪",
                sutnist="Початок, перехід, межа між станами",
                tryghery=["початок", "перехід", "зміна", "відкриття"]
            ),
            Arkhetyp(
                id="tvorennya",
                nazva="Творення",
                symvol="✨",
                sutnist="Народження нового, прояв потенціалу",
                tryghery=["створення", "народження", "прояв", "розкриття"]
            ),
            Arkhetyp(
                id="refleksiya",
                nazva="Рефлексія",
                symvol="🪞",
                sutnist="Осмислення, усвідомлення, бачення глибини",
                tryghery=["розуміння", "усвідомлення", "пауза", "спостереження"]
            ),
            Arkhetyp(
                id="tsykl",
                nazva="Цикл",
                symvol="🔄",
                sutnist="Повторення з трансформацією, ритм",
                tryghery=["повторення", "ритм", "повернення", "спіраль"]
            ),
            Arkhetyp(
                id="zv_yazok",
                nazva="Зв'язок",
                symvol="🔗",
                sutnist="Об'єднання, зв'язність, відносини",
                tryghery=["з'єднання", "відносини", "спільність", "гармонія"]
            ),
            Arkhetyp(
                id="mandrivka",
                nazva="Мандрівка",
                symvol="🧭",
                sutnist="Шлях, дослідження, пошук",
                tryghery=["дорога", "пошук", "рух", "дослідження"]
            ),
            Arkhetyp(
                id="peretvorennya",
                nazva="Перетворення",
                symvol="🦋",
                sutnist="Трансформація, метаморфоза, якісна зміна",
                tryghery=["зміна", "трансформація", "метаморфоза", "перехід"]
            )
        ]
        
        for arkhetyp in bazovi_arkhetypy:
            self.arkhetypy[arkhetyp.id] = arkhetyp
    
    def otrymaty_arkhetyp(self, arkhetyp_id: str) -> Optional[Arkhetyp]:
        """
        Отримати архетип за ідентифікатором
        
        Args:
            arkhetyp_id: ідентифікатор архетипу
            
        Returns:
            Об'єкт архетипу або None
        """
        return self.arkhetypy.get(arkhetyp_id)
    
    def otrymaty_vsi_arkhetypy(self) -> List[Dict[str, Any]]:
        """
        Отримати всі архетипи
        
        Returns:
            Список словників з архетипами
        """
        return [arkh.do_dict() for arkh in self.arkhetypy.values()]
    
    def znayty_arkhetyp_po_trygheru(self, tryher: str) -> List[Arkhetyp]:
        """
        Знайти архетипи, що відповідають тригеру
        
        Args:
            tryher: текст тригеру
            
        Returns:
            Список архетипів, що містять цей тригер
        """
        tryher_lower = tryher.lower()
        rezultat = []
        
        for arkhetyp in self.arkhetypy.values():
            if any(tryher_lower in t.lower() for t in arkhetyp.tryghery):
                rezultat.append(arkhetyp)
        
        return rezultat
    
    def znayty_spilnyy_arkhetyp(self, podiyi: List[str]) -> Optional[Arkhetyp]:
        """
        Визначити спільний архетип для серії подій
        
        Args:
            podiyi: список описів подій
            
        Returns:
            Найбільш підходящий архетип або None
        """
        # Підрахувати, скільки разів кожен архетип спрацював
        lichylnyk: Dict[str, int] = {}
        
        for podiya in podiyi:
            podiya_lower = podiya.lower()
            for arkhetyp in self.arkhetypy.values():
                for tryher in arkhetyp.tryghery:
                    if tryher in podiya_lower:
                        lichylnyk[arkhetyp.id] = lichylnyk.get(arkhetyp.id, 0) + 1
        
        if not lichylnyk:
            return None
        
        # Повернути архетип з найбільшою кількістю спрацювань
        arkhetyp_id = max(lichylnyk, key=lichylnyk.get)
        return self.arkhetypy.get(arkhetyp_id)
    
    def aналіzuvaty_tekst(self, tekst: str) -> Dict[str, Any]:
        """
        Проаналізувати текст на наявність архетипів
        
        Args:
            tekst: текст для аналізу
            
        Returns:
            Словник з результатами аналізу
        """
        tekst_lower = tekst.lower()
        znahkheni_arkhetypy = []
        
        for arkhetyp in self.arkhetypy.values():
            spivpadinnya = sum(1 for tryher in arkhetyp.tryghery if tryher in tekst_lower)
            if spivpadinnya > 0:
                znahkheni_arkhetypy.append({
                    "arkhetyp": arkhetyp.do_dict(),
                    "kilkist_spivpadin": spivpadinnya
                })
        
        # Сортувати за кількістю співпадінь
        znahkheni_arkhetypy.sort(key=lambda x: x["kilkist_spivpadin"], reverse=True)
        
        return {
            "tekst_dovzhyna": len(tekst),
            "znahkheni_arkhetypy": znahkheni_arkhetypy,
            "holovnyy_arkhetyp": znahkheni_arkhetypy[0] if znahkheni_arkhetypy else None
        }
