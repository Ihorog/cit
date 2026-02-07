"""
Семантичний граф — структура зв'язків між сенсами

Цей модуль відповідає за роботу з графом семантичних зв'язків,
побудову шляхів та аналіз структури.
"""
from typing import Dict, Any, List, Optional, Set
from collections import deque


class SemantychnyyGraf:
    """
    Семантичний граф для роботи зі зв'язками між вузлами
    """
    
    def __init__(self):
        self.graf: Dict[str, Set[str]] = {}
        
    def dodaty_vuzol(self, vuzol_id: str) -> None:
        """
        Додати вузол до графа
        
        Args:
            vuzol_id: ідентифікатор вузла
        """
        if vuzol_id not in self.graf:
            self.graf[vuzol_id] = set()
    
    def dodaty_zv_yazok(self, vid: str, do: str) -> None:
        """
        Додати зв'язок між вузлами (двосторонній)
        
        Args:
            vid: вузол джерело
            do: вузол призначення
        """
        self.dodaty_vuzol(vid)
        self.dodaty_vuzol(do)
        self.graf[vid].add(do)
        self.graf[do].add(vid)  # Двосторонній зв'язок
    
    def znayty_shlyakh(self, start: str, kinets: str) -> Optional[List[str]]:
        """
        Знайти найкоротший шлях між вузлами (BFS)
        
        Args:
            start: початковий вузол
            kinets: кінцевий вузол
            
        Returns:
            Список вузлів шляху або None, якщо шляху немає
        """
        if start not in self.graf or kinets not in self.graf:
            return None
        
        if start == kinets:
            return [start]
        
        # Breadth-First Search
        cherha = deque([[start]])
        vidvidani = {start}
        
        while cherha:
            shlyakh = cherha.popleft()
            potochnyy = shlyakh[-1]
            
            for susid in self.graf.get(potochnyy, []):
                if susid == kinets:
                    return shlyakh + [susid]
                
                if susid not in vidvidani:
                    vidvidani.add(susid)
                    cherha.append(shlyakh + [susid])
        
        return None
    
    def otrymaty_susidiv(self, vuzol_id: str) -> List[str]:
        """
        Отримати всіх сусідів вузла
        
        Args:
            vuzol_id: ідентифікатор вузла
            
        Returns:
            Список ідентифікаторів сусідніх вузлів
        """
        return list(self.graf.get(vuzol_id, set()))
    
    def otrymaty_vidstan_do_vuzla(self, start: str, kinets: str) -> int:
        """
        Отримати відстань між двома вузлами
        
        Args:
            start: початковий вузол
            kinets: кінцевий вузол
            
        Returns:
            Кількість кроків або -1, якщо шляху немає
        """
        shlyakh = self.znayty_shlyakh(start, kinets)
        if shlyakh is None:
            return -1
        return len(shlyakh) - 1
    
    def otrymaty_vsi_vuzly_v_radiusi(self, start: str, radius: int) -> List[str]:
        """
        Отримати всі вузли в радіусі від початкового
        
        Args:
            start: початковий вузол
            radius: радіус пошуку
            
        Returns:
            Список вузлів у радіусі
        """
        if start not in self.graf:
            return []
        
        rezultat = set()
        cherha = deque([(start, 0)])
        vidvidani = {start}
        
        while cherha:
            vuzol, vidstan = cherha.popleft()
            
            if vidstan <= radius:
                rezultat.add(vuzol)
                
                for susid in self.graf.get(vuzol, []):
                    if susid not in vidvidani:
                        vidvidani.add(susid)
                        cherha.append((susid, vidstan + 1))
        
        return list(rezultat)
    
    def otrymaty_stupin_vuzla(self, vuzol_id: str) -> int:
        """
        Отримати ступінь вузла (кількість зв'язків)
        
        Args:
            vuzol_id: ідентифікатор вузла
            
        Returns:
            Кількість зв'язків
        """
        return len(self.graf.get(vuzol_id, set()))
    
    def otrymaty_tsentralni_vuzly(self, top_n: int = 5) -> List[tuple]:
        """
        Отримати найбільш центральні вузли (з найбільшою кількістю зв'язків)
        
        Args:
            top_n: кількість вузлів для повернення
            
        Returns:
            Список кортежів (vuzol_id, stupin)
        """
        stupeni = [(vuzol, self.otrymaty_stupin_vuzla(vuzol)) for vuzol in self.graf]
        return sorted(stupeni, key=lambda x: x[1], reverse=True)[:top_n]
    
    def eksportuvaty_dlya_vizualizatsiyi(self) -> Dict[str, Any]:
        """
        Експортувати граф у форматі для візуалізації
        
        Returns:
            Словник з nodes та edges для D3.js або подібних бібліотек
        """
        nodes = [{"id": vuzol} for vuzol in self.graf]
        edges = []
        
        # Збираємо всі ребра (уникаємо дублікатів)
        obrobbleni = set()
        for vid, susidy in self.graf.items():
            for do in susidy:
                # Створюємо унікальний ключ для ребра
                klyuch = tuple(sorted([vid, do]))
                if klyuch not in obrobbleni:
                    edges.append({"source": vid, "target": do})
                    obrobbleni.add(klyuch)
        
        return {
            "nodes": nodes,
            "edges": edges,
            "kilkist_vuzliv": len(nodes),
            "kilkist_zv_yazkiv": len(edges)
        }
