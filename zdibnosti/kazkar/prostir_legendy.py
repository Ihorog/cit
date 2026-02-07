"""
✨ Легенда Сі — Інтерактивне поле знання

Легенда Сі — це семантичний граф, де користувач не читає текст,
а досліджує сенси через навігацію по вузлам значень.

Центральний вузол: "Присутність"
10 базових вузлів організовані у 3 рівні глибини
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SemantychnyyVuzol:
    """
    Вузол семантичного графа
    """
    id: str
    nazva: str
    opys: str
    hlybyna: int  # Рівень віддаленості від центру (0, 1, 2, 3)
    zv_yazani_vuzly: List[str] = field(default_factory=list)
    rezonansni_sensy: List[str] = field(default_factory=list)
    arkhetyp: Optional[str] = None
    
    def do_dict(self) -> Dict[str, Any]:
        """Конвертувати в словник"""
        return {
            "id": self.id,
            "nazva": self.nazva,
            "opys": self.opys,
            "hlybyna": self.hlybyna,
            "zv_yazani_vuzly": self.zv_yazani_vuzly,
            "rezonansni_sensy": self.rezonansni_sensy,
            "arkhetyp": self.arkhetyp
        }


class ProstirLegendy:
    """
    ✨ Легенда Сі — Інтерактивне поле знання
    
    Семантичний граф з 10 базовими вузлами, організованими
    навколо центрального концепту "Присутність"
    """
    
    def __init__(self):
        self.vuzly: Dict[str, SemantychnyyVuzol] = {}
        self.potochnyy_vuzol: Optional[str] = None
        self.istoriya_navihatsii: List[str] = []
        self._inicializuvaty_bazovi_vuzly()
        
    def _inicializuvaty_bazovi_vuzly(self):
        """
        Ініціалізувати 10 базових вузлів Легенди Сі
        
        Структура:
        - prysutnist (центр, глибина 0)
        - tysha, dostatnist, moment (глибина 1)
        - spokiy, pryynyattya, chas (глибина 2)
        - balans, mudrist, tsykl (глибина 3)
        """
        
        # Глибина 0: Центр
        self.vuzly["prysutnist"] = SemantychnyyVuzol(
            id="prysutnist",
            nazva="Присутність",
            opys="Центральна точка всього. Здатність бути тут і зараз.",
            hlybyna=0,
            zv_yazani_vuzly=["tysha", "dostatnist", "moment"],
            rezonansni_sensy=["усвідомленість", "тепер", "буття"],
            arkhetyp="Поріг"
        )
        
        # Глибина 1: Перший шар
        self.vuzly["tysha"] = SemantychnyyVuzol(
            id="tysha",
            nazva="Тиша",
            opys="Простір без шуму. Місце, де можна почути себе.",
            hlybyna=1,
            zv_yazani_vuzly=["prysutnist", "spokiy"],
            rezonansni_sensy=["спокій", "порожнеча", "глибина"],
            arkhetyp="Рефлексія"
        )
        
        self.vuzly["dostatnist"] = SemantychnyyVuzol(
            id="dostatnist",
            nazva="Достатність",
            opys="Відчуття повноти. Відсутність браку.",
            hlybyna=1,
            zv_yazani_vuzly=["prysutnist", "pryynyattya"],
            rezonansni_sensy=["повнота", "гармонія", "задоволення"],
            arkhetyp="Творення"
        )
        
        self.vuzly["moment"] = SemantychnyyVuzol(
            id="moment",
            nazva="Момент",
            opys="Точка в часі. Миттєвість, що містить вічність.",
            hlybyna=1,
            zv_yazani_vuzly=["prysutnist", "chas"],
            rezonansni_sensy=["зараз", "миттєвість", "вічність"],
            arkhetyp="Цикл"
        )
        
        # Глибина 2: Другий шар
        self.vuzly["spokiy"] = SemantychnyyVuzol(
            id="spokiy",
            nazva="Спокій",
            opys="Стан без тривоги. Внутрішня рівновага.",
            hlybyna=2,
            zv_yazani_vuzly=["tysha", "balans"],
            rezonansni_sensy=["рівновага", "мир", "стабільність"],
            arkhetyp="Рефлексія"
        )
        
        self.vuzly["pryynyattya"] = SemantychnyyVuzol(
            id="pryynyattya",
            nazva="Прийняття",
            opys="Здатність приймати те, що є. Без опору.",
            hlybyna=2,
            zv_yazani_vuzly=["dostatnist", "mudrist"],
            rezonansni_sensy=["відпускання", "дозвіл", "потік"],
            arkhetyp="Перетворення"
        )
        
        self.vuzly["chas"] = SemantychnyyVuzol(
            id="chas",
            nazva="Час",
            opys="Потік подій. Ритм існування.",
            hlybyna=2,
            zv_yazani_vuzly=["moment", "tsykl"],
            rezonansni_sensy=["ритм", "плин", "тривалість"],
            arkhetyp="Цикл"
        )
        
        # Глибина 3: Третій шар
        self.vuzly["balans"] = SemantychnyyVuzol(
            id="balans",
            nazva="Баланс",
            opys="Динамічна рівновага. Гармонія протилежностей.",
            hlybyna=3,
            zv_yazani_vuzly=["spokiy"],
            rezonansni_sensy=["гармонія", "центрованість", "рівновага"],
            arkhetyp="Зв'язок"
        )
        
        self.vuzly["mudrist"] = SemantychnyyVuzol(
            id="mudrist",
            nazva="Мудрість",
            opys="Глибоке розуміння. Знання через досвід.",
            hlybyna=3,
            zv_yazani_vuzly=["pryynyattya"],
            rezonansni_sensy=["розуміння", "досвід", "інсайт"],
            arkhetyp="Мандрівка"
        )
        
        self.vuzly["tsykl"] = SemantychnyyVuzol(
            id="tsykl",
            nazva="Цикл",
            opys="Повторення з трансформацією. Спіраль розвитку.",
            hlybyna=3,
            zv_yazani_vuzly=["chas"],
            rezonansni_sensy=["повторення", "ріст", "спіраль"],
            arkhetyp="Цикл"
        )
    
    def aktyvuvaty(self) -> Dict[str, Any]:
        """
        Активувати Легенду Сі з центру "Присутність"
        
        Returns:
            Словник з даними активації
        """
        self.potochnyy_vuzol = "prysutnist"
        self.istoriya_navihatsii = ["prysutnist"]
        
        return {
            "typ": "aktyvatsiya_legendy",
            "potochnyy_vuzol": self.otrymaty_vuzol("prysutnist").do_dict() if "prysutnist" in self.vuzly else None,
            "chas": datetime.now().isoformat()
        }
    
    def navihuvaty_do(self, vuzol_id: str) -> Dict[str, Any]:
        """
        Навігація до вказаного вузла
        
        Args:
            vuzol_id: ідентифікатор вузла
            
        Returns:
            Дані вузла та доступні шляхи
        """
        if vuzol_id not in self.vuzly:
            return {
                "pomylka": f"Вузол {vuzol_id} не знайдено",
                "dostupni_vuzly": list(self.vuzly.keys())
            }
        
        self.potochnyy_vuzol = vuzol_id
        self.istoriya_navihatsii.append(vuzol_id)
        
        vuzol = self.vuzly[vuzol_id]
        
        # Отримати інформацію про зв'язані вузли
        zv_yazani_vuzly_info = [
            {
                "id": zv_id,
                "nazva": self.vuzly[zv_id].nazva,
                "hlybyna": self.vuzly[zv_id].hlybyna
            }
            for zv_id in vuzol.zv_yazani_vuzly
            if zv_id in self.vuzly
        ]
        
        return {
            "potochnyy_vuzol": vuzol.do_dict(),
            "zv_yazani_vuzly": zv_yazani_vuzly_info,
            "istoriya": self.istoriya_navihatsii[-5:],  # Останні 5 кроків
            "chas": datetime.now().isoformat()
        }
    
    def poshuk_po_sensu(self, zapyt: str) -> List[Dict[str, Any]]:
        """
        Семантичний пошук по вузлах
        
        Args:
            zapyt: текст для пошуку
            
        Returns:
            Список вузлів, що відповідають запиту
        """
        zapyt_lower = zapyt.lower()
        rezultaty = []
        
        for vuzol in self.vuzly.values():
            # Пошук в назві, описі та резонансних сенсах
            if (zapyt_lower in vuzol.nazva.lower() or
                zapyt_lower in vuzol.opys.lower() or
                any(zapyt_lower in sens.lower() for sens in vuzol.rezonansni_sensy)):
                rezultaty.append(vuzol.do_dict())
        
        return rezultaty
    
    def eksportuvaty_graf(self) -> Dict[str, Any]:
        """
        Експортувати повний граф для візуалізації
        
        Returns:
            Повна структура графа
        """
        return {
            "vuzly": [vuzol.do_dict() for vuzol in self.vuzly.values()],
            "kilkist_vuzliv": len(self.vuzly),
            "potochnyy_vuzol": self.potochnyy_vuzol,
            "chas_eksportu": datetime.now().isoformat()
        }
    
    def otrymaty_vuzol(self, vuzol_id: str) -> Optional[SemantychnyyVuzol]:
        """
        Отримати вузол за ідентифікатором
        
        Args:
            vuzol_id: ідентифікатор вузла
            
        Returns:
            Об'єкт вузла або None
        """
        return self.vuzly.get(vuzol_id)
    
    def otrymaty_vuzly_po_hlybyny(self, hlybyna: int) -> List[Dict[str, Any]]:
        """
        Отримати всі вузли на певній глибині
        
        Args:
            hlybyna: рівень глибини (0, 1, 2, 3)
            
        Returns:
            Список вузлів на цій глибині
        """
        return [
            vuzol.do_dict()
            for vuzol in self.vuzly.values()
            if vuzol.hlybyna == hlybyna
        ]
