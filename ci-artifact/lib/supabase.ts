import { createClient, SupabaseClient } from '@supabase/supabase-js';

let _supabase: SupabaseClient | null = null;

/**
 * Server-side Supabase client using the Service Role Key.
 * Lazily initialized — safe during build when env vars are absent.
 * Must only be used in server components and API routes.
 */
export function getSupabase(): SupabaseClient {
  if (!_supabase) {
    const url = process.env.SUPABASE_URL;
    const key = process.env.SUPABASE_SERVICE_ROLE_KEY;
    if (!url || !key) {
      throw new Error('Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY');
    }
    _supabase = createClient(url, key);
  }
  return _supabase;
}
