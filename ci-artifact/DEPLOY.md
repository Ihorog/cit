# ci-Artifact — Deploy Guide

## Структура MVP

```
ci-artifact/
├── app/
│   ├── api/stripe/
│   │   ├── checkout/route.ts   ← створює Stripe Checkout Session
│   │   └── webhook/route.ts    ← обробляє checkout.session.completed
│   ├── artifact/page.tsx       ← головна сторінка (Lock a moment)
│   ├── verify/[code]/page.tsx  ← перевірка sealed artifact
│   ├── layout.tsx
│   └── page.tsx                ← redirect → /artifact
├── components/
│   └── ArtifactCard.tsx        ← UI-обгортка
├── lib/
│   ├── ci-engine.ts            ← детерміністичний движок статусів
│   └── supabase.ts             ← серверний Supabase client
├── supabase/
│   └── schema.sql              ← SQL-схема для бази
├── package.json
├── next.config.mjs
└── tsconfig.json
```

## 1. Supabase (~5 хв)

1. Зайти на [supabase.com](https://supabase.com) → **New Project** → назва `ci-moment`
2. **SQL Editor** → вставити вміст `db/schema.sql` → **Run**
3. **Settings → API** → скопіювати:
   - `Project URL` → це `SUPABASE_URL`
   - `service_role key` (secret) → це `SUPABASE_SERVICE_ROLE_KEY`

## 2. Stripe (~5 хв)

1. Зайти на [dashboard.stripe.com](https://dashboard.stripe.com)
2. Увімкнути **Test Mode**
3. **Developers → API Keys** → скопіювати `Secret key` → це `STRIPE_SECRET_KEY`
4. Webhook додамо після deploy (крок 3)

## 3. Vercel (~5 хв)

```bash
cd ci-artifact
npm install
vercel link
```

Додати env vars у Vercel Dashboard:

| Variable | Значення |
|----------|----------|
| `SUPABASE_URL` | з кроку 1 |
| `SUPABASE_SERVICE_ROLE_KEY` | з кроку 1 |
| `STRIPE_SECRET_KEY` | з кроку 2 |
| `NEXT_PUBLIC_URL` | `https://your-domain.vercel.app` |

Деплой:

```bash
vercel --prod
```

## 4. Stripe Webhook (після deploy)

1. Stripe Dashboard → **Developers → Webhooks** → **Add endpoint**
2. URL: `https://your-domain.vercel.app/api/stripe/webhook`
3. Events: `checkout.session.completed`
4. Скопіювати **Signing secret** → це `STRIPE_WEBHOOK_SECRET`
5. Додати `STRIPE_WEBHOOK_SECRET` у Vercel Dashboard → Environment Variables
6. **Redeploy**:

```bash
vercel --prod
```

## Перевірка

```bash
# Health (має відкритись головна сторінка)
curl https://your-domain.vercel.app/artifact

# Локально
cd ci-artifact
cp .env.local.example .env.local
# заповнити реальні ключі
npm run dev
# відкрити http://localhost:3000
```

## Env vars (повний список)

```
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
NEXT_PUBLIC_URL=
```
