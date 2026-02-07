-- ci-Artifact-System v1.0.0
-- Supabase schema for the Moment Lock authority layer

create type ci_status as enum ('PROCEED', 'HOLD', 'NOT_NOW');
create type ci_context as enum ('career', 'love', 'timing');

create table public.artifacts (
  id uuid primary key default gen_random_uuid(),
  artifact_code text unique not null,
  context ci_context not null,
  status ci_status not null,
  locked_minute_utc bigint not null,
  locked_at_utc timestamptz not null default now(),
  is_sealed boolean not null default false,
  sealed_at_utc timestamptz,
  stripe_session_id text unique,
  verify_hash text unique not null,
  ip_hash text
);

alter table public.artifacts enable row level security;
-- No public policies! Server-side access only via Service Role.
