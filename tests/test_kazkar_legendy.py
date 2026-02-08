"""
Тести для функціональності Казкара та Легенди Сі
Перевірка динамічного створення та редагування вузлів
"""

import sys
import os
from pathlib import Path

# Додати батьківську директорію до шляху для імпортів
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from zdibnosti.kazkar.prostir_legendy import ProstirLegendy, SemantychnyyVuzol


def test_stvoryty_novyy_vuzol_uspishno():
    """Тест успішного створення нового вузла"""
    print("Тестування створення нового вузла...")
    
    legenda = ProstirLegendy()
    
    # Створити новий вузол
    rezultat = legenda.stvoryty_novyy_vuzol(
        vuzol_id="test_vuzol",
        nazva="Тестовий Вузол",
        opys="Опис тестового вузла",
        hlybyna=1,
        zv_yazani_vuzly=["prysutnist"],
        rezonansni_sensy=["тест", "перевірка"],
        arkhetyp="Творення"
    )
    
    # Перевірити успішність
    assert rezultat["uspishno"] is True, "Створення вузла має бути успішним"
    assert "novyy_vuzol" in rezultat, "Результат має містити новий вузол"
    assert rezultat["novyy_vuzol"]["id"] == "test_vuzol", "ID вузла має співпадати"
    assert rezultat["novyy_vuzol"]["nazva"] == "Тестовий Вузол", "Назва має співпадати"
    
    # Перевірити, що вузол додано до графа
    assert "test_vuzol" in legenda.vuzly, "Вузол має бути в графі"
    assert legenda.vuzly["test_vuzol"].nazva == "Тестовий Вузол"
    
    # Перевірити зворотній зв'язок
    assert "test_vuzol" in legenda.vuzly["prysutnist"].zv_yazani_vuzly, \
        "Зворотній зв'язок має бути створено"
    
    print("✓ Створення нового вузла працює коректно")
    print(f"  Новий вузол: {rezultat['novyy_vuzol']['nazva']}")


def test_stvoryty_vuzol_z_isnuyuchym_id():
    """Тест спроби створення вузла з існуючим ID"""
    print("Тестування створення вузла з існуючим ID...")
    
    legenda = ProstirLegendy()
    
    # Спробувати створити вузол з ID, що вже існує
    rezultat = legenda.stvoryty_novyy_vuzol(
        vuzol_id="prysutnist",  # Вже існує
        nazva="Дублікат",
        opys="Спроба дублікату",
        hlybyna=0
    )
    
    # Перевірити, що операція не успішна
    assert rezultat["uspishno"] is False, "Створення дублікату має бути неуспішним"
    assert "pomylka" in rezultat, "Результат має містити помилку"
    assert "вже існує" in rezultat["pomylka"], "Помилка має вказувати на дублікат"
    
    print("✓ Перевірка дублікатів працює коректно")


def test_stvoryty_vuzol_z_neisnuyuchym_zvyazkom():
    """Тест створення вузла з неіснуючим зв'язаним вузлом"""
    print("Тестування створення вузла з неіснуючим зв'язком...")
    
    legenda = ProstirLegendy()
    
    # Спробувати створити вузол зі зв'язком до неіснуючого вузла
    rezultat = legenda.stvoryty_novyy_vuzol(
        vuzol_id="test_vuzol2",
        nazva="Тест 2",
        opys="Тест з неіснуючим зв'язком",
        hlybyna=1,
        zv_yazani_vuzly=["neisnuyuchyy_vuzol"]
    )
    
    # Перевірити, що операція не успішна
    assert rezultat["uspishno"] is False, "Має бути помилка"
    assert "pomylka" in rezultat, "Результат має містити помилку"
    assert "не існує" in rezultat["pomylka"], "Помилка має вказувати на неіснуючий вузол"
    
    print("✓ Валідація зв'язків працює коректно")


def test_dodaty_zv_yazok_uspishno():
    """Тест успішного додавання зв'язку між вузлами"""
    print("Тестування додавання зв'язку...")
    
    legenda = ProstirLegendy()
    
    # Додати зв'язок між існуючими вузлами
    rezultat = legenda.dodaty_zv_yazok("tysha", "dostatnist")
    
    # Перевірити успішність
    assert rezultat["uspishno"] is True, "Додавання зв'язку має бути успішним"
    assert "zv_yazok" in rezultat, "Результат має містити інформацію про зв'язок"
    
    # Перевірити двосторонній зв'язок
    assert "dostatnist" in legenda.vuzly["tysha"].zv_yazani_vuzly, \
        "Прямий зв'язок має існувати"
    assert "tysha" in legenda.vuzly["dostatnist"].zv_yazani_vuzly, \
        "Зворотній зв'язок має існувати"
    
    print("✓ Додавання зв'язку працює коректно")


def test_dodaty_zv_yazok_z_neisnuyuchym_vuzlom():
    """Тест додавання зв'язку з неіснуючим вузлом"""
    print("Тестування додавання зв'язку з неіснуючим вузлом...")
    
    legenda = ProstirLegendy()
    
    # Спробувати додати зв'язок з неіснуючим вузлом
    rezultat = legenda.dodaty_zv_yazok("tysha", "neisnuyuchyy")
    
    # Перевірити, що операція не успішна
    assert rezultat["uspishno"] is False, "Має бути помилка"
    assert "pomylka" in rezultat, "Результат має містити помилку"
    
    print("✓ Валідація зв'язків при додаванні працює коректно")


def test_dodaty_isnuyuchyy_zv_yazok():
    """Тест додавання вже існуючого зв'язку"""
    print("Тестування додавання існуючого зв'язку...")
    
    legenda = ProstirLegendy()
    
    # Спробувати додати зв'язок, що вже існує
    rezultat = legenda.dodaty_zv_yazok("prysutnist", "tysha")
    
    # Перевірити, що операція не успішна
    assert rezultat["uspishno"] is False, "Дублювання зв'язку має бути неуспішним"
    assert "pomylka" in rezultat, "Результат має містити помилку"
    assert "вже існує" in rezultat["pomylka"], "Помилка має вказувати на дублікат"
    
    print("✓ Перевірка дублікатів зв'язків працює коректно")


def test_onovyty_vuzol_uspishno():
    """Тест успішного оновлення вузла"""
    print("Тестування оновлення вузла...")
    
    legenda = ProstirLegendy()
    
    # Оновити існуючий вузол
    rezultat = legenda.onovyty_vuzol(
        vuzol_id="tysha",
        nazva="Нова Тиша",
        opys="Оновлений опис тиші"
    )
    
    # Перевірити успішність
    assert rezultat["uspishno"] is True, "Оновлення має бути успішним"
    assert "onovlenyy_vuzol" in rezultat, "Результат має містити оновлений вузол"
    
    # Перевірити, що поля оновлено
    vuzol = legenda.vuzly["tysha"]
    assert vuzol.nazva == "Нова Тиша", "Назва має бути оновлена"
    assert vuzol.opys == "Оновлений опис тиші", "Опис має бути оновлений"
    
    print("✓ Оновлення вузла працює коректно")


def test_onovyty_neisnuyuchyy_vuzol():
    """Тест оновлення неіснуючого вузла"""
    print("Тестування оновлення неіснуючого вузла...")
    
    legenda = ProstirLegendy()
    
    # Спробувати оновити неіснуючий вузол
    rezultat = legenda.onovyty_vuzol(
        vuzol_id="neisnuyuchyy",
        nazva="Тест"
    )
    
    # Перевірити, що операція не успішна
    assert rezultat["uspishno"] is False, "Має бути помилка"
    assert "pomylka" in rezultat, "Результат має містити помилку"
    
    print("✓ Валідація при оновленні працює коректно")


def test_vydalyty_vuzol_uspishno():
    """Тест успішного видалення вузла"""
    print("Тестування видалення вузла...")
    
    legenda = ProstirLegendy()
    
    # Створити тестовий вузол
    legenda.stvoryty_novyy_vuzol(
        vuzol_id="test_dlya_vydalennya",
        nazva="Для видалення",
        opys="Тестовий вузол для видалення",
        hlybyna=1,
        zv_yazani_vuzly=["prysutnist"]
    )
    
    # Переконатися, що вузол існує
    assert "test_dlya_vydalennya" in legenda.vuzly
    
    # Видалити вузол
    rezultat = legenda.vydalyty_vuzol("test_dlya_vydalennya")
    
    # Перевірити успішність
    assert rezultat["uspishno"] is True, "Видалення має бути успішним"
    assert "vydalenyy_vuzol" in rezultat, "Результат має містити видалений вузол"
    
    # Перевірити, що вузол видалено
    assert "test_dlya_vydalennya" not in legenda.vuzly, "Вузол має бути видалений"
    
    # Перевірити, що зв'язки видалено
    assert "test_dlya_vydalennya" not in legenda.vuzly["prysutnist"].zv_yazani_vuzly, \
        "Зв'язки з вузлом мають бути видалені"
    
    print("✓ Видалення вузла працює коректно")


def test_kompleksnyy_stsenariy():
    """Комплексний тест: створення, оновлення, зв'язування"""
    print("Виконання комплексного сценарію...")
    
    legenda = ProstirLegendy()
    pochatkovа_kilkist = len(legenda.vuzly)
    
    # 1. Створити новий вузол
    legenda.stvoryty_novyy_vuzol(
        vuzol_id="harmonia",
        nazva="Гармонія",
        opys="Стан внутрішньої гармонії",
        hlybyna=2,
        zv_yazani_vuzly=["dostatnist"],
        rezonansni_sensy=["гармонія", "баланс", "рівновага"],
        arkhetyp="Зв'язок"
    )
    
    # 2. Створити ще один вузол
    legenda.stvoryty_novyy_vuzol(
        vuzol_id="radist",
        nazva="Радість",
        opys="Природна радість буття",
        hlybyna=1,
        rezonansni_sensy=["радість", "щастя", "світло"]
    )
    
    # 3. Додати зв'язок між новими вузлами
    rezultat_zvyazok = legenda.dodaty_zv_yazok("harmonia", "radist")
    assert rezultat_zvyazok["uspishno"] is True
    
    # 4. Оновити один з вузлів
    rezultat_onovlennya = legenda.onovyty_vuzol(
        vuzol_id="radist",
        arkhetyp="Творення",
        hlybyna=2
    )
    assert rezultat_onovlennya["uspishno"] is True
    
    # 5. Перевірити фінальний стан
    assert len(legenda.vuzly) == pochatkovа_kilkist + 2, "Має бути 2 нових вузли"
    assert "radist" in legenda.vuzly["harmonia"].zv_yazani_vuzly
    assert legenda.vuzly["radist"].arkhetyp == "Творення"
    assert legenda.vuzly["radist"].hlybyna == 2
    
    print("✓ Комплексний сценарій виконано успішно")
    print(f"  Створено 2 нових вузли, загальна кількість: {len(legenda.vuzly)}")


def run_all_tests():
    """Запустити всі тести"""
    print("=" * 60)
    print("Тестування Легенди Сі - Динамічне редагування")
    print("=" * 60)
    print()
    
    tests = [
        test_stvoryty_novyy_vuzol_uspishno,
        test_stvoryty_vuzol_z_isnuyuchym_id,
        test_stvoryty_vuzol_z_neisnuyuchym_zvyazkom,
        test_dodaty_zv_yazok_uspishno,
        test_dodaty_zv_yazok_z_neisnuyuchym_vuzlom,
        test_dodaty_isnuyuchyy_zv_yazok,
        test_onovyty_vuzol_uspishno,
        test_onovyty_neisnuyuchyy_vuzol,
        test_vydalyty_vuzol_uspishno,
        test_kompleksnyy_stsenariy
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
            print()
        except AssertionError as e:
            failed += 1
            print(f"✗ Тест провалено: {test.__name__}")
            print(f"  Помилка: {str(e)}")
            print()
        except Exception as e:
            failed += 1
            print(f"✗ Виняток у тесті {test.__name__}")
            print(f"  {type(e).__name__}: {str(e)}")
            print()
    
    print("=" * 60)
    print(f"Результати: {passed} пройдено, {failed} провалено")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
