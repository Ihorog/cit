"""
Казкар — Форма Оповіді (Друга формація цілісності)

Казкар є формою оповіді, здатністю зберігати сенс та бачити зв'язок між подіями.
Всередині Казкара знаходиться ✨ Легенда Сі — інтерактивне поле знання.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime

from core.formatsiyi import Formatsiya
from zdibnosti.kazkar.prostir_legendy import ProstirLegendy
from zdibnosti.kazkar.semantychnyi_graf import SemantychnyyGraf
from zdibnosti.kazkar.dvyhun_arkhetypiv import DvyhunArkhetypiv
from zdibnosti.kazkar.opovidach import Opovidach


class Kazkar(Formatsiya):
    """
    Казкар — Форма Оповіді
    
    Друга формація цілісності організму Cimeika.
    Здатність зберігати сенс, бачити зв'язок між подіями,
    не загубитися в хаосі фактів.
    """
    
    def __init__(self):
        super().__init__("Казкар")
        
        # Ініціалізація компонентів
        self.prostir_legendy = ProstirLegendy()
        self.semantychnyi_graf = SemantychnyyGraf()
        self.dvyhun_arkhetypiv = DvyhunArkhetypiv()
        self.opovidach = Opovidach(self.dvyhun_arkhetypiv, self.prostir_legendy)
        
        # Ініціалізація семантичного графа з вузлів легенди
        self._inicializuvaty_semantychnyi_graf()
        
        # Стан Казкара
        self.v_legendi = False
        self.potochna_opovid: Optional[Dict[str, Any]] = None
    
    def _inicializuvaty_semantychnyi_graf(self):
        """
        Ініціалізувати семантичний граф з вузлів Легенди Сі
        """
        for vuzol in self.prostir_legendy.vuzly.values():
            self.semantychnyi_graf.dodaty_vuzol(vuzol.id)
            
            for zv_yazanyy_id in vuzol.zv_yazani_vuzly:
                self.semantychnyi_graf.dodaty_zv_yazok(vuzol.id, zv_yazanyy_id)
    
    def aktyvuvaty(self) -> Dict[str, Any]:
        """
        Активувати Казкар
        
        Returns:
            Словник зі станом активації
        """
        self.aktyvna = True
        self.stan = "aktyvna"
        self.ostannya_aktyvatsiya = datetime.now()
        self.tsilisnist_riven = 0.8
        
        return {
            "formatsiya": self.nazva,
            "stan": "aktyvovano",
            "tsilisnist": self.tsilisnist_riven,
            "komponenty": {
                "legenda_si": "hotova",
                "arkhetypy": len(self.dvyhun_arkhetypiv.arkhetypy),
                "vuzly": len(self.prostir_legendy.vuzly)
            },
            "chas": self.ostannya_aktyvatsiya.isoformat()
        }
    
    def vidchuttya_tsilisnosti(self) -> float:
        """
        Повернути поточне відчуття цілісності (0.0 - 1.0)
        
        Returns:
            Рівень цілісності
        """
        if not self.aktyvna:
            return 0.0
        
        # Цілісність залежить від:
        # - наявності активних оповідей
        # - зв'язності графа
        # - активації легенди
        
        bazovyy_riven = 0.5
        
        if self.v_legendi:
            bazovyy_riven += 0.2
        
        if self.potochna_opovid:
            bazovyy_riven += 0.15
        
        if len(self.opovidach.istoriyi) > 0:
            bazovyy_riven += 0.15
        
        return min(bazovyy_riven, 1.0)
    
    def proyav_v_ui(self) -> Dict[str, Any]:
        """
        Повернути дані для відображення в UI
        
        Returns:
            Словник з даними для UI
        """
        return {
            "nazva": self.nazva,
            "symvol": "📖",
            "aktyvna": self.aktyvna,
            "tsilisnist": self.vidchuttya_tsilisnosti(),
            "v_legendi": self.v_legendi,
            "kilkist_istoriy": len(self.opovidach.istoriyi),
            "potochnyy_vuzol": self.prostir_legendy.potochnyy_vuzol,
            "ostanni_opovidi": self.opovidach.otrymaty_ostanni_opovidi(3)
        }
    
    def plesty_zv_yaznist(self, podiyi: List[str]) -> Dict[str, Any]:
        """
        Плетіння зв'язності між подіями
        
        Основний метод Казкара - створення зв'язної оповіді з окремих подій
        
        Args:
            podiyi: список описів подій
            
        Returns:
            Словник з оповіддю та зв'язками
        """
        if not self.aktyvna:
            return {
                "pomylka": "Казкар не активовано",
                "tsilisnist": 0.0
            }
        
        # Створити оповідь
        opovid = self.opovidach.stvoryt_opovid(podiyi)
        self.potochna_opovid = opovid
        
        # Оновити рівень цілісності
        self.tsilisnist_riven = self.vidchuttya_tsilisnosti()
        
        return {
            "typ": "zv_yaznist_splетена",
            "opovid": opovid,
            "tsilisnist": self.tsilisnist_riven,
            "vidchuttya": "rozuminnya_zv_yazku"
        }
    
    def uviyty_v_legendu(self) -> Dict[str, Any]:
        """
        Увійти у Легенду Сі
        
        Активація інтерактивного поля знання
        
        Returns:
            Словник з даними входу
        """
        if not self.aktyvna:
            return {
                "pomylka": "Казкар не активовано"
            }
        
        self.v_legendi = True
        aktyvatsiya = self.prostir_legendy.aktyvuvaty()
        
        # Оновити цілісність
        self.tsilisnist_riven = self.vidchuttya_tsilisnosti()
        
        return {
            "typ": "vkhid_do_legendy",
            "aktyvatsiya": aktyvatsiya,
            "tsilisnist": self.tsilisnist_riven,
            "vidchuttya": "zanurennya_v_sens"
        }
    
    def navihuvaty_po_legendi(self, vuzol_id: str) -> Dict[str, Any]:
        """
        Навігувати по Легенді Сі
        
        Args:
            vuzol_id: ідентифікатор вузла для переходу
            
        Returns:
            Дані навігації
        """
        if not self.v_legendi:
            return {
                "pomylka": "Не в Легенді Сі. Спочатку викличте uviyty_v_legendu()"
            }
        
        return self.prostir_legendy.navihuvaty_do(vuzol_id)
    
    def poshuk_sensu(self, zapyt: str) -> Dict[str, Any]:
        """
        Семантичний пошук по Легенді Сі
        
        Args:
            zapyt: текст для пошуку
            
        Returns:
            Результати пошуку
        """
        rezultaty_vuzly = self.prostir_legendy.poshuk_po_sensu(zapyt)
        analiz_arkhetypiv = self.dvyhun_arkhetypiv.aналіzuvaty_tekst(zapyt)
        
        return {
            "zapyt": zapyt,
            "znahkheni_vuzly": rezultaty_vuzly,
            "arkhetypy": analiz_arkhetypiv,
            "kilkist_rezultativ": len(rezultaty_vuzly)
        }
    
    def eksportuvaty_legendu(self) -> Dict[str, Any]:
        """
        Експортувати повну структуру Легенди Сі
        
        Returns:
            Повна структура для візуалізації
        """
        graf_data = self.prostir_legendy.eksportuvaty_graf()
        viz_data = self.semantychnyi_graf.eksportuvaty_dlya_vizualizatsiyi()
        
        return {
            "legenda": graf_data,
            "vizualizatsiya": viz_data,
            "arkhetypy": self.dvyhun_arkhetypiv.otrymaty_vsi_arkhetypy()
        }
