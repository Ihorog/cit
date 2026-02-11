"""
Тести для модуля пропозицій моменту (MomentPorady)

Перевіряє функціональність системи пропозицій для Ci-момент
"""
import sys
import os

# Додати кореневу директорію до шляху
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime
from zdibnosti.kazkar.porady import MomentPorady
from zdibnosti.kazkar.prostir_legendy import ProstirLegendy


def test_basic_moment_propozitsiya():
    """Тест базової пропозиції для моменту"""
    print("Тест 1: Базова пропозиція для моменту...")

    porady = MomentPorady()
    moment = datetime.now()

    propozitsiya = porady.daty_moment_propozitsiu(
        potochnyy_moment=moment
    )

    assert propozitsiya is not None
    assert "propozitsiya" in propozitsiya
    assert "diya" in propozitsiya
    assert "typ" in propozitsiya
    assert propozitsiya["typ"] == "moment_propozitsiya"

    print("✓ Базова пропозиція працює")


def test_moment_vuzol_propozitsiya():
    """Тест пропозиції коли користувач у вузлі 'момент'"""
    print("\nТест 2: Пропозиція для вузла 'момент'...")

    prostir = ProstirLegendy()
    porady = MomentPorady(prostir_legendy=prostir)
    moment = datetime.now()

    propozitsiya = porady.daty_moment_propozitsiu(
        potochnyy_moment=moment,
        potochnyy_vuzol="moment"
    )

    assert propozitsiya is not None
    assert "propozitsiya" in propozitsiya
    assert "arkhetyp" in propozitsiya
    assert propozitsiya["arkhetyp"] == "Цикл"

    print("✓ Пропозиція для вузла 'момент' працює")
    print(f"  Текст: {propozitsiya['propozitsiya']}")


def test_prysutnist_vuzol_propozitsiya():
    """Тест пропозиції коли користувач у центрі (присутність)"""
    print("\nТест 3: Пропозиція для центру 'присутність'...")

    prostir = ProstirLegendy()
    porady = MomentPorady(prostir_legendy=prostir)
    moment = datetime.now()

    propozitsiya = porady.daty_moment_propozitsiu(
        potochnyy_moment=moment,
        potochnyy_vuzol="prysutnist"
    )

    assert propozitsiya is not None
    assert "propozitsiya" in propozitsiya
    assert "diya" in propozitsiya

    print("✓ Пропозиція для центру працює")
    print(f"  Текст: {propozitsiya['propozitsiya']}")


def test_custom_vuzol_propozitsiya():
    """Тест пропозиції для користувацького вузла"""
    print("\nТест 4: Пропозиція для користувацького вузла...")

    prostir = ProstirLegendy()
    porady = MomentPorady(prostir_legendy=prostir)
    moment = datetime.now()

    propozitsiya = porady.daty_moment_propozitsiu(
        potochnyy_moment=moment,
        potochnyy_vuzol="tysha"  # Вузол "Тиша"
    )

    assert propozitsiya is not None
    assert "propozitsiya" in propozitsiya
    assert "diya" in propozitsiya

    print("✓ Пропозиція для користувацького вузла працює")
    print(f"  Текст: {propozitsiya['propozitsiya']}")


def test_opovid_propozitsiya():
    """Тест пропозиції на основі оповіді"""
    print("\nТест 5: Пропозиція на основі оповіді...")

    porady = MomentPorady()

    # Оповідь з архетипом Циклу (архетип Моменту)
    opovid = {
        "arkhetyp": {
            "nazva": "Цикл",
            "opys": "Повторення з трансформацією"
        },
        "opovid": "Тестова оповідь"
    }

    propozitsiya = porady.daty_propozytsiyi_dlya_opovidі(opovid)

    assert propozitsiya is not None
    assert "typ" in propozitsiya
    assert propozitsiya["typ"] == "opovid_propozitsiya"
    # Check that the suggestion contains relevant Ukrainian text
    assert "propozitsiya" in propozitsiya
    assert len(propozitsiya["propozitsiya"]) > 0

    print("✓ Пропозиція для оповіді працює")
    print(f"  Текст: {propozitsiya['propozitsiya']}")


def test_istoriya_propozytsi():
    """Тест історії пропозицій"""
    print("\nТест 6: Історія пропозицій...")

    porady = MomentPorady()
    moment = datetime.now()

    # Створити кілька пропозицій
    for i in range(5):
        porady.daty_moment_propozitsiu(
            potochnyy_moment=moment,
            potochnyy_vuzol=None if i % 2 == 0 else "moment"
        )

    istoriya = porady.otrymaty_istoriyu(kilkist=3)

    assert len(istoriya) == 3
    assert "chas" in istoriya[0]
    assert "propozitsiya" in istoriya[0]

    print(f"✓ Історія пропозицій працює (збережено {len(istoriya)} записів)")


def test_statystyka_propozytsi():
    """Тест статистики пропозицій"""
    print("\nТест 7: Статистика пропозицій...")

    porady = MomentPorady()
    moment = datetime.now()

    # Створити кілька пропозицій
    for i in range(10):
        vuzol = None if i % 3 == 0 else ("moment" if i % 2 == 0 else "prysutnist")
        porady.daty_moment_propozitsiu(
            potochnyy_moment=moment,
            potochnyy_vuzol=vuzol
        )

    statystyka = porady.otrymaty_statystyku()

    assert "zahalna_kilkist" in statystyka
    assert statystyka["zahalna_kilkist"] == 10
    assert "po_typakh" in statystyka
    assert len(statystyka["po_typakh"]) > 0

    print(f"✓ Статистика працює")
    print(f"  Загальна кількість: {statystyka['zahalna_kilkist']}")
    print(f"  По типах: {statystyka['po_typakh']}")


def test_propozitsiya_with_prostir():
    """Тест інтеграції з ProstirLegendy"""
    print("\nТест 8: Інтеграція з ProstirLegendy...")

    prostir = ProstirLegendy()
    prostir.aktyvuvaty()

    porady = MomentPorady(prostir_legendy=prostir)
    moment = datetime.now()

    # Навігувати до вузла "момент"
    prostir.navihuvaty_do("moment")

    # Отримати пропозицію
    propozitsiya = porady.daty_moment_propozitsiu(
        potochnyy_moment=moment,
        potochnyy_vuzol="moment"
    )

    assert propozitsiya is not None
    assert "propozitsiya" in propozitsiya

    print("✓ Інтеграція з ProstirLegendy працює")


def test_different_arkhetypy_propozytsi():
    """Тест пропозицій для різних архетипів"""
    print("\nТест 9: Пропозиції для різних архетипів...")

    porady = MomentPorady()

    arkhetypy = ["Поріг", "Творення", "Рефлексія", "Цикл", "Зв'язок", "Мандрівка", "Перетворення"]

    for arkhetyp in arkhetypy:
        opovid = {
            "arkhetyp": {
                "nazva": arkhetyp
            }
        }

        propozitsiya = porady.daty_propozytsiyi_dlya_opovidі(opovid)

        assert propozitsiya is not None
        assert "propozitsiya" in propozitsiya

        print(f"  ✓ {arkhetyp}: {propozitsiya['propozitsiya'][:50]}...")


def test_propozitsiya_limit():
    """Тест обмеження історії пропозицій"""
    print("\nТест 10: Обмеження історії пропозицій (макс 50)...")

    porady = MomentPorady()
    moment = datetime.now()

    # Створити 100 пропозицій
    for i in range(100):
        porady.daty_moment_propozitsiu(
            potochnyy_moment=moment
        )

    # Історія має зберігати лише останні 50
    statystyka = porady.otrymaty_statystyku()
    assert statystyka["zahalna_kilkist"] == 50

    print("✓ Обмеження історії працює (збережено тільки останні 50)")


def run_all_tests():
    """Запустити всі тести"""
    print("=" * 60)
    print("Тестування модуля MomentPorady")
    print("=" * 60)

    tests = [
        test_basic_moment_propozitsiya,
        test_moment_vuzol_propozitsiya,
        test_prysutnist_vuzol_propozitsiya,
        test_custom_vuzol_propozitsiya,
        test_opovid_propozitsiya,
        test_istoriya_propozytsi,
        test_statystyka_propozytsi,
        test_propozitsiya_with_prostir,
        test_different_arkhetypy_propozytsi,
        test_propozitsiya_limit
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"✗ Тест {test_func.__name__} провалився: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ Тест {test_func.__name__} викликав помилку: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"Результати: {passed} пройдено, {failed} провалено")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
