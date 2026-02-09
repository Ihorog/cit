"""
API маршрути для Казкара

Endpoints для роботи з формацією Казкар та Легендою Сі
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from zdibnosti.kazkar import Kazkar

# Створення роутера
router = APIRouter()

# Глобальний екземпляр Казкара (в реальному додатку використовувати dependency injection)
kazkar_instance = Kazkar()


class PodijiRequest(BaseModel):
    """Модель для запиту створення оповіді"""
    podiyi: List[str]
    kontekst: str = ""


class PoshukRequest(BaseModel):
    """Модель для запиту пошуку"""
    zapyt: str


class NovoVuzolRequest(BaseModel):
    """Модель для створення нового вузла"""
    vuzol_id: str
    nazva: str
    opys: str
    hlybyna: int
    zv_yazani_vuzly: List[str] = []
    rezonansni_sensy: List[str] = []
    arkhetyp: Optional[str] = None


class ZvyazokRequest(BaseModel):
    """Модель для створення зв'язку між вузлами"""
    vuzol_id_1: str
    vuzol_id_2: str


class OnovlennyaVuzlaRequest(BaseModel):
    """Модель для оновлення вузла"""
    nazva: Optional[str] = None
    opys: Optional[str] = None
    hlybyna: Optional[int] = None
    rezonansni_sensy: Optional[List[str]] = None
    arkhetyp: Optional[str] = None


@router.get("/aktyvuvaty")
async def aktyvuvaty_kazkar() -> Dict[str, Any]:
    """
    Активувати формацію Казкар
    
    Returns:
        Стан активації
    """
    try:
        rezultat = kazkar_instance.aktyvuvaty()
        return rezultat
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/proyav")
async def proyav_kazkar() -> Dict[str, Any]:
    """
    Отримати прояв Казкара в UI
    
    Returns:
        Дані для відображення
    """
    try:
        return kazkar_instance.proyav_v_ui()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/plesty-zv-yaznist")
async def plesty_zv_yaznist(request: PodijiRequest) -> Dict[str, Any]:
    """
    Плести зв'язність між подіями
    
    Args:
        request: список подій та контекст
        
    Returns:
        Оповідь з зв'язками
    """
    try:
        return kazkar_instance.plesty_zv_yaznist(request.podiyi)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/legenda/aktyvuvaty")
async def aktyvuvaty_legendu() -> Dict[str, Any]:
    """
    Увійти у Легенду Сі
    
    Returns:
        Дані входу в легенду
    """
    try:
        return kazkar_instance.uviyty_v_legendu()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/legenda/navihuvaty/{vuzol_id}")
async def navihuvaty_do_vuzla(vuzol_id: str) -> Dict[str, Any]:
    """
    Навігувати до вузла в Легенді Сі
    
    Args:
        vuzol_id: ідентифікатор вузла
        
    Returns:
        Дані вузла та навігації
    """
    try:
        return kazkar_instance.navihuvaty_po_legendi(vuzol_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/legenda/poshuk")
async def poshuk_po_sensu(request: PoshukRequest) -> Dict[str, Any]:
    """
    Семантичний пошук по Легенді Сі
    
    Args:
        request: запит для пошуку
        
    Returns:
        Результати пошуку
    """
    try:
        return kazkar_instance.poshuk_sensu(request.zapyt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/legenda/eksport")
async def eksportuvaty_legendu() -> Dict[str, Any]:
    """
    Експортувати повну структуру Легенди Сі
    
    Returns:
        Повна структура графа
    """
    try:
        return kazkar_instance.eksportuvaty_legendu()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/arkhetypy")
async def otrymaty_arkhetypy() -> Dict[str, Any]:
    """
    Отримати всі 7 архетипів
    
    Returns:
        Список архетипів
    """
    try:
        arkhetypy = kazkar_instance.dvyhun_arkhetypiv.otrymaty_vsi_arkhetypy()
        return {
            "arkhetypy": arkhetypy,
            "kilkist": len(arkhetypy)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/opovidi/ostanni")
async def ostanni_opovidi(kilkist: int = 5) -> Dict[str, Any]:
    """
    Отримати останні оповіді
    
    Args:
        kilkist: кількість оповідей (за замовчуванням 5)
        
    Returns:
        Список оповідей
    """
    try:
        opovidi = kazkar_instance.opovidach.otrymaty_ostanni_opovidi(kilkist)
        return {
            "opovidi": opovidi,
            "kilkist": len(opovidi)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/legenda/vuzol")
async def stvoryty_vuzol(request: NovoVuzolRequest) -> Dict[str, Any]:
    """
    Створити новий семантичний вузол у Легенді Сі
    
    Args:
        request: дані нового вузла
        
    Returns:
        Результат створення вузла
    """
    try:
        rezultat = kazkar_instance.prostir_legendy.stvoryty_novyy_vuzol(
            vuzol_id=request.vuzol_id,
            nazva=request.nazva,
            opys=request.opys,
            hlybyna=request.hlybyna,
            zv_yazani_vuzly=request.zv_yazani_vuzly,
            rezonansni_sensy=request.rezonansni_sensy,
            arkhetyp=request.arkhetyp
        )
        
        # Оновити семантичний граф
        if rezultat.get("uspishno"):
            kazkar_instance.semantychnyi_graf.dodaty_vuzol(request.vuzol_id)
            for zv_id in request.zv_yazani_vuzly:
                kazkar_instance.semantychnyi_graf.dodaty_zv_yazok(request.vuzol_id, zv_id)
        
        return rezultat
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/legenda/zv-yazok")
async def dodaty_zvyazok(request: ZvyazokRequest) -> Dict[str, Any]:
    """
    Додати зв'язок між двома існуючими вузлами
    
    Args:
        request: ID двох вузлів для зв'язування
        
    Returns:
        Результат створення зв'язку
    """
    try:
        rezultat = kazkar_instance.prostir_legendy.dodaty_zv_yazok(
            vuzol_id_1=request.vuzol_id_1,
            vuzol_id_2=request.vuzol_id_2
        )
        
        # Оновити семантичний граф
        if rezultat.get("uspishno"):
            kazkar_instance.semantychnyi_graf.dodaty_zv_yazok(
                request.vuzol_id_1,
                request.vuzol_id_2
            )
        
        return rezultat
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/legenda/vuzol/{vuzol_id}")
async def onovyty_vuzol(vuzol_id: str, request: OnovlennyaVuzlaRequest) -> Dict[str, Any]:
    """
    Оновити існуючий вузол
    
    Args:
        vuzol_id: ID вузла для оновлення
        request: нові дані для вузла
        
    Returns:
        Результат оновлення
    """
    try:
        rezultat = kazkar_instance.prostir_legendy.onovyty_vuzol(
            vuzol_id=vuzol_id,
            nazva=request.nazva,
            opys=request.opys,
            hlybyna=request.hlybyna,
            rezonansni_sensy=request.rezonansni_sensy,
            arkhetyp=request.arkhetyp
        )
        return rezultat
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/legenda/vuzol/{vuzol_id}")
async def vydalyty_vuzol(vuzol_id: str) -> Dict[str, Any]:
    """
    Видалити вузол з Легенди Сі
    
    Args:
        vuzol_id: ID вузла для видалення
        
    Returns:
        Результат видалення
    """
    try:
        rezultat = kazkar_instance.prostir_legendy.vydalyty_vuzol(vuzol_id)
        
        # Оновити семантичний граф
        if rezultat.get("uspishno"):
            # Видалити вузол з графа (якщо метод існує)
            if hasattr(kazkar_instance.semantychnyi_graf, 'vydalyty_vuzol'):
                kazkar_instance.semantychnyi_graf.vydalyty_vuzol(vuzol_id)
        
        return rezultat
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
