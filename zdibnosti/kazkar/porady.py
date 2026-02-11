"""
Пoради (Suggestions) — Механізм пропозицій для Ci-момент

Цей модуль надає контекстуальні пропозиції на основі:
- Поточного моменту часу
- Позиції користувача у Легенді Сі
- Історії навігації
- Резонансу між подіями та семантичними вузлами

Філософія:
Пропозиції — це не команди, а м'які орієнтири.
Як подих: природно виникають, не нав'язуються.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import random


class MomentPorady:
    """
    Механізм пропозицій для моменту присутності

    Generates contextual suggestions based on:
    - Current moment context
    - User's position in the Legend
    - Semantic resonance
    - Archetypes
    """

    def __init__(self, prostir_legendy=None):
        """
        Args:
            prostir_legendy: ProstirLegendy instance (optional)
        """
        self.prostir_legendy = prostir_legendy
        self.istoriya_propozytsi: List[Dict[str, Any]] = []

    def daty_moment_propozitsiu(
        self,
        potochnyy_moment: datetime,
        potochnyy_vuzol: Optional[str] = None,
        kontekst: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Надати пропозицію на основі поточного моменту

        Args:
            potochnyy_moment: поточний час
            potochnyy_vuzol: ID поточного вузла у Легенді (опційно)
            kontekst: додатковий контекст (опційно)

        Returns:
            Словник з пропозицією та її обґрунтуванням
        """
        # Базова пропозиція для моменту
        propozitsiya = {
            "typ": "moment_propozitsiya",
            "chas": potochnyy_moment.isoformat(),
            "potochnyy_vuzol": potochnyy_vuzol
        }

        # Якщо користувач у вузлі "момент"
        if potochnyy_vuzol == "moment":
            propozitsiya.update(self._propozitsiya_dlya_moment_vuzla())
        # Якщо у центрі (присутність)
        elif potochnyy_vuzol == "prysutnist":
            propozitsiya.update(self._propozitsiya_z_tsentru())
        # Якщо є інформація про легенду
        elif self.prostir_legendy and potochnyy_vuzol:
            propozitsiya.update(self._propozitsiya_z_vuzla(potochnyy_vuzol))
        # Загальна пропозиція
        else:
            propozitsiya.update(self._zahalna_propozitsiya())

        # Зберегти пропозицію в історії
        self.istoriya_propozytsi.append({
            "chas": potochnyy_moment.isoformat(),
            "propozitsiya": propozitsiya
        })

        # Тримати лише останні 50 пропозицій
        if len(self.istoriya_propozytsi) > 50:
            self.istoriya_propozytsi = self.istoriya_propozytsi[-50:]

        return propozitsiya

    def _propozitsiya_dlya_moment_vuzla(self) -> Dict[str, Any]:
        """
        Пропозиція коли користувач у вузлі "Момент"
        """
        propozytsiyi = [
            {
                "tekst": "Момент містить вічність. Досліди зв'язок з Часом.",
                "diya": "navihuvaty",
                "tsel_vuzol": "chas",
                "pryychyna": "Час — це природне продовження Моменту"
            },
            {
                "tekst": "Повернися до центру Присутності.",
                "diya": "navihuvaty",
                "tsel_vuzol": "prysutnist",
                "pryychyna": "Момент народжується з Присутності"
            },
            {
                "tekst": "Момент — це архетип Циклу. Досліди Цикл глибше.",
                "diya": "doslidyty_arkhetyp",
                "arkhetyp": "Цикл",
                "pryychyna": "Момент резонує з архетипом Циклу"
            }
        ]

        # Вибрати випадкову пропозицію
        vybranyy = random.choice(propozytsiyi)

        return {
            "propozitsiya": vybranyy["tekst"],
            "diya": vybranyy["diya"],
            "detalі": {
                "tsel_vuzol": vybranyy.get("tsel_vuzol"),
                "arkhetyp": vybranyy.get("arkhetyp")
            },
            "pryychyna": vybranyy["pryychyna"],
            "arkhetyp": "Цикл"
        }

    def _propozitsiya_z_tsentru(self) -> Dict[str, Any]:
        """
        Пропозиція коли користувач у центрі (Присутність)
        """
        propozytsiyi = [
            {
                "tekst": "З центру Присутності відкривається Момент.",
                "diya": "navihuvaty",
                "tsel_vuzol": "moment",
                "pryychyna": "Момент — один з трьох первинних шляхів"
            },
            {
                "tekst": "Присутність веде до Тиші та Достатності.",
                "diya": "doslidyty",
                "pryychyna": "Три шляхи з центру: Тиша, Достатність, Момент"
            },
            {
                "tekst": "Ти у центрі. Відчуй Присутність повністю.",
                "diya": "zafiksuvaty_moment",
                "pryychyna": "Присутність — це практика моменту 'тепер'"
            }
        ]

        vybranyy = random.choice(propozytsiyi)

        return {
            "propozitsiya": vybranyy["tekst"],
            "diya": vybranyy["diya"],
            "detalі": {
                "tsel_vuzol": vybranyy.get("tsel_vuzol")
            },
            "pryychyna": vybranyy["pryychyna"]
        }

    def _propozitsiya_z_vuzla(self, vuzol_id: str) -> Dict[str, Any]:
        """
        Пропозиція на основі поточного вузла

        Args:
            vuzol_id: ID поточного вузла
        """
        if not self.prostir_legendy:
            return self._zahalna_propozitsiya()

        vuzol = self.prostir_legendy.otrymaty_vuzol(vuzol_id)
        if not vuzol:
            return self._zahalna_propozitsiya()

        # Якщо є зв'язані вузли
        if vuzol.zv_yazani_vuzly:
            # Перевірити чи "момент" серед зв'язаних
            if "moment" in vuzol.zv_yazani_vuzly:
                return {
                    "propozitsiya": f"З {vuzol.nazva} відкривається шлях до Моменту.",
                    "diya": "navihuvaty",
                    "detalі": {
                        "tsel_vuzol": "moment",
                        "zvyazok": True
                    },
                    "pryychyna": f"{vuzol.nazva} пов'язаний з Моментом"
                }
            else:
                # Запропонувати один з зв'язаних вузлів
                nastupnyy = random.choice(vuzol.zv_yazani_vuzly)
                nastupnyy_vuzol = self.prostir_legendy.otrymaty_vuzol(nastupnyy)
                nazva_nastupnoho = nastupnyy_vuzol.nazva if nastupnyy_vuzol else nastupnyy

                return {
                    "propozitsiya": f"З {vuzol.nazva} можна дослідити {nazva_nastupnoho}.",
                    "diya": "navihuvaty",
                    "detalі": {
                        "tsel_vuzol": nastupnyy,
                        "zvyazok": True
                    },
                    "pryychyna": f"Семантичний зв'язок між вузлами"
                }

        # Якщо немає зв'язків
        return {
            "propozitsiya": f"Досліди {vuzol.nazva} глибше або поверніться до Присутності.",
            "diya": "refleksiya",
            "detalі": {},
            "pryychyna": "Поглиблення у поточний вузол"
        }

    def _zahalna_propozitsiya(self) -> Dict[str, Any]:
        """
        Загальна пропозиція (fallback)
        """
        propozytsiyi = [
            {
                "tekst": "Зафіксуй момент 'тепер'. Увійди в Присутність.",
                "diya": "zafiksuvaty_moment",
                "pryychyna": "Базова практика присутності"
            },
            {
                "tekst": "Активуй Легенду Сі і досліди семантичний простір.",
                "diya": "aktyvuvaty_legendu",
                "pryychyna": "Вхід у інтерактивне поле знання"
            },
            {
                "tekst": "Момент — точка в часі, що містить вічність.",
                "diya": "navihuvaty",
                "tsel_vuzol": "moment",
                "pryychyna": "Дослідження концепту Моменту"
            }
        ]

        vybranyy = random.choice(propozytsiyi)

        return {
            "propozitsiya": vybranyy["tekst"],
            "diya": vybranyy["diya"],
            "detalі": {
                "tsel_vuzol": vybranyy.get("tsel_vuzol")
            },
            "pryychyna": vybranyy["pryychyna"]
        }

    def daty_propozytsiyi_dlya_opovidі(
        self,
        opovid: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Надати пропозиції на основі оповіді (narrative)

        Args:
            opovid: згенерована оповідь з архетипом

        Returns:
            Пропозиція для дослідження
        """
        arkhetyp = opovid.get("arkhetyp", {}).get("nazva")

        # Якщо архетип "Цикл" — це архетип Моменту
        if arkhetyp == "Цикл":
            return {
                "typ": "opovid_propozitsiya",
                "propozitsiya": "Твоя оповідь резонує з архетипом Циклу — це архетип Моменту. Досліди вузол 'Момент' у Легенді Сі.",
                "diya": "navihuvaty",
                "detalі": {
                    "tsel_vuzol": "moment",
                    "arkhetyp": "Цикл"
                },
                "pryychyna": "Архетип Циклу пов'язаний з Моментом",
                "chas": datetime.now().isoformat()
            }

        # Для інших архетипів
        propozytsiyi_po_arkhetypakh = {
            "Поріг": "Ти на порозі. Досліди Присутність — центр всього.",
            "Творення": "Творення виникає з Достатності. Досліди цей вузол.",
            "Рефлексія": "Рефлексія потребує Тиші. Увійди у цей простір.",
            "Зв'язок": "Зв'язки плетуться через Баланс. Досліди цю гармонію.",
            "Мандрівка": "Мандрівка веде до Мудрості. Продовжуй шлях.",
            "Перетворення": "Перетворення приходить через Прийняття."
        }

        tekst = propozytsiyi_po_arkhetypakh.get(
            arkhetyp,
            "Твоя оповідь має унікальний резонанс. Досліди Легенду Сі."
        )

        return {
            "typ": "opovid_propozitsiya",
            "propozitsiya": tekst,
            "diya": "doslidyty_arkhetyp",
            "detalі": {
                "arkhetyp": arkhetyp
            },
            "pryychyna": f"Оповідь резонує з архетипом {arkhetyp}",
            "chas": datetime.now().isoformat()
        }

    def otrymaty_istoriyu(self, kilkist: int = 10) -> List[Dict[str, Any]]:
        """
        Отримати історію пропозицій

        Args:
            kilkist: кількість останніх пропозицій

        Returns:
            Список пропозицій
        """
        return self.istoriya_propozytsi[-kilkist:]

    def otrymaty_statystyku(self) -> Dict[str, Any]:
        """
        Отримати статистику пропозицій

        Returns:
            Статистика по типах дій та пропозицій
        """
        if not self.istoriya_propozytsi:
            return {
                "zahalna_kilkist": 0,
                "po_typakh": {}
            }

        # Підрахувати типи дій
        typy_diy = {}
        for zapis in self.istoriya_propozytsi:
            prop = zapis.get("propozitsiya", {})
            diya = prop.get("diya", "nevidomо")
            typy_diy[diya] = typy_diy.get(diya, 0) + 1

        return {
            "zahalna_kilkist": len(self.istoriya_propozytsi),
            "po_typakh": typy_diy,
            "ostannya_chas": self.istoriya_propozytsi[-1]["chas"] if self.istoriya_propozytsi else None
        }
