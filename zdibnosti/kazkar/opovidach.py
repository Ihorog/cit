"""
Оповідач — генератор оповідей з подій

Створює зв'язні оповіді з послідовності подій,
використовуючи архетипи та семантичний граф
"""
from typing import Dict, Any, List
from datetime import datetime


class Opovidach:
    """
    Генератор оповідей на основі подій та архетипів
    """
    
    def __init__(self, dvyhun_arkhetypiv, prostir_legendy):
        """
        Args:
            dvyhun_arkhetypiv: екземпляр DvyhunArkhetypiv
            prostir_legendy: екземпляр ProstirLegendy
        """
        self.dvyhun = dvyhun_arkhetypiv
        self.legenda = prostir_legendy
        self.istoriyi: List[Dict[str, Any]] = []
    
    def stvoryt_opovid(self, podiyi: List[str], kontekst: str = "") -> Dict[str, Any]:
        """
        Створити оповідь з послідовності подій
        
        Args:
            podiyi: список описів подій
            kontekst: додатковий контекст
            
        Returns:
            Словник з оповіддю
        """
        # Визначити спільний архетип
        arkhetyp = self.dvyhun.znayty_spilnyy_arkhetyp(podiyi)
        
        # Створити структуровану оповідь
        opovid = {
            "id": len(self.istoriyi) + 1,
            "chas_stvorennya": datetime.now().isoformat(),
            "podiyi": podiyi,
            "kontekst": kontekst,
            "arkhetyp": arkhetyp.do_dict() if arkhetyp else None,
            "kilkist_podiy": len(podiyi)
        }
        
        # Додати до історії
        self.istoriyi.append(opovid)
        
        return opovid
    
    def zv_yazaty_z_vuzlom(self, opovid_id: int, vuzol_id: str) -> bool:
        """
        Зв'язати оповідь з вузлом семантичного графа
        
        Args:
            opovid_id: ідентифікатор оповіді
            vuzol_id: ідентифікатор вузла
            
        Returns:
            True, якщо успішно зв'язано
        """
        if opovid_id < 1 or opovid_id > len(self.istoriyi):
            return False
        
        vuzol = self.legenda.otrymaty_vuzol(vuzol_id)
        if not vuzol:
            return False
        
        # Додати зв'язок
        opovid = self.istoriyi[opovid_id - 1]
        if 'zv_yazani_vuzly' not in opovid:
            opovid['zv_yazani_vuzly'] = []
        
        if vuzol_id not in opovid['zv_yazani_vuzly']:
            opovid['zv_yazani_vuzly'].append(vuzol_id)
        
        return True
    
    def otrymaty_opovid(self, opovid_id: int) -> Dict[str, Any]:
        """
        Отримати оповідь за ідентифікатором
        
        Args:
            opovid_id: ідентифікатор оповіді
            
        Returns:
            Словник з оповіддю або помилка
        """
        if opovid_id < 1 or opovid_id > len(self.istoriyi):
            return {"pomylka": "Оповідь не знайдено"}
        
        return self.istoriyi[opovid_id - 1]
    
    def otrymaty_ostanni_opovidi(self, kilkist: int = 5) -> List[Dict[str, Any]]:
        """
        Отримати останні N оповідей
        
        Args:
            kilkist: кількість оповідей
            
        Returns:
            Список оповідей
        """
        return self.istoriyi[-kilkist:]
    
    def poshuk_po_arkhetypu(self, arkhetyp_id: str) -> List[Dict[str, Any]]:
        """
        Знайти всі оповіді з певним архетипом
        
        Args:
            arkhetyp_id: ідентифікатор архетипу
            
        Returns:
            Список оповідей
        """
        return [
            opovid
            for opovid in self.istoriyi
            if opovid.get('arkhetyp') and opovid['arkhetyp']['id'] == arkhetyp_id
        ]
    
    def eksportuvaty_istoriyu(self) -> Dict[str, Any]:
        """
        Експортувати всю історію оповідей
        
        Returns:
            Словник з усіма оповідями
        """
        return {
            "kilkist_istoriy": len(self.istoriyi),
            "istoriyi": self.istoriyi,
            "chas_eksportu": datetime.now().isoformat()
        }
