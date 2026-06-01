create table if not exists ci_sessions (
  id text primary key,
  anonymous_user_id text,
  source text,
  utm_source text,
  utm_medium text,
  utm_campaign text,
  referrer text,
  device_type text,
  created_at timestamptz default now()
);

create table if not exists ci_events (
  id uuid primary key default gen_random_uuid(),
  session_id text references ci_sessions(id),
  event_name text not null,
  context text,
  artifact_id text,
  order_id text,
  metadata jsonb default '{}'::jsonb,
  created_at timestamptz default now()
);

create table if not exists ci_artifacts (
  id text primary key,
  artifact_code text unique not null,
  verify_hash text unique not null,
  session_id text references ci_sessions(id),
  context text not null,
  result_status text not null,
  locked_minute bigint,
  source text,
  sealed_at timestamptz,
  order_id text,
  is_verified boolean default false,
  is_public_share_enabled boolean default false,
  created_at timestamptz default now()
);

create table if not exists ci_orders (
  id uuid primary key default gen_random_uuid(),
  external_provider text not null,
  external_order_id text unique not null,
  artifact_id text references ci_artifacts(id),
  session_id text references ci_sessions(id),
  amount_cents integer,
  currency text,
  product_type text,
  raw_status text,
  matched_at timestamptz,
  created_at timestamptz default now()
);

create table if not exists ci_consents (
  id uuid primary key default gen_random_uuid(),
  anonymous_user_id text,
  email_hash text,
  consent_type text not null,
  status text not null,
  source text,
  created_at timestamptz default now()
);

create table if not exists ci_memberships (
  id uuid primary key default gen_random_uuid(),
  anonymous_user_id text,
  external_provider text,
  external_membership_id text,
  status text,
  started_at timestamptz,
  renewed_at timestamptz,
  canceled_at timestamptz,
  created_at timestamptz default now()
);

create index if not exists ci_events_session_id_idx on ci_events(session_id);
create index if not exists ci_events_event_name_idx on ci_events(event_name);
create index if not exists ci_artifacts_verify_hash_idx on ci_artifacts(verify_hash);
create index if not exists ci_orders_external_order_id_idx on ci_orders(external_order_id);
