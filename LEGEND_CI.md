# Legend CI

## Актуальна документація

- [CI Job: чистий зелений run](https://github.com/Ihorog/cit/actions/runs/23381927355/job/68022656210)
- [Документація у ciwiki](https://github.com/Ihorog/ciwiki/)
- https://www.cimeika.com.ua/legend/

---

## CI Pass Instructions (Березень 2026)

1. Додати у початок проблемного файлу:
```python
import datetime
```
2. Видалити рядок з global moment_porady_instance, якщо ця змінна не використовується, або призначити їй значення, якщо потрібна.
3. Внести зміни до коду, комітнути, пушнути у main.
4. Переконатись, що CI зелений (усі чекі пройдені).

---

> Легенду CI підтримувати у синхронізації з ciwiki та структурою проєкту.