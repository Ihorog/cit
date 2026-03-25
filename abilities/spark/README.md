# ⚡ Spark Ability

Аналітичний двигун Apache Spark для CIT-організму.
Охоплює всі 7 репозиторіїв екосистеми Cimeika.

## Активація

```bash
# 1. Завантажити дані з GitHub
curl -X POST http://localhost:8000/api/spark/ingest

# 2. Запустити Spark pipeline
curl -X POST http://localhost:8000/api/spark/run

# 3. Ad-hoc запит
curl "http://localhost:8000/api/spark/query?sql=SELECT+repo,role,COUNT(*)+FROM+corpus+GROUP+BY+repo,role"
```

## Репозиторії

| Репо | Роль | Партиція |
|---|---|---|
| `Ihorog/cit` | core_toolkit | `role=core_toolkit` |
| `Ihorog/ci_gitapi` | auth_gateway | `role=auth_gateway` |
| `Ihorog/cimeika-unified` | unified_platform | `role=unified_platform` |
| `Ihorog/cimeika-backend` | edge_runtime | `role=edge_runtime` |
| `Ihorog/ci-memory` | shared_memory | `role=shared_memory` |
| `Ihorog/ciwiki` | knowledge_base | `role=knowledge_base` |
| `Ihorog/media` | media_assets | `role=media_assets` |

## Сумісність

- ✅ **Termux** — `local[*]`, 512m RAM
- ❌ **Vercel Edge** — PySpark несумісний
- ❌ **Cloudflare Workers** — TypeScript-only runtime; дані `cimeika-backend` завантажуються як raw corpus

## Структура виводу

```
dani/spark/
├── raw/
│   ├── raw_corpus.json     ← GitHub API pull
│   └── role_index.json     ← індекс по ролях
└── indexed/
    └── corpus/
        ├── role=core_toolkit/
        ├── role=auth_gateway/
        ├── role=unified_platform/
        ├── role=edge_runtime/
        ├── role=shared_memory/
        ├── role=knowledge_base/
        └── role=media_assets/
```
