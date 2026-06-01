import { NextResponse } from "next/server";
import { getSupabaseAdmin, isPersistenceConfigured } from "@/lib/storage/supabase";

export const runtime = "nodejs";

type SessionPayload = {
  sessionId?: string;
  anonymousUserId?: string;
  source?: string;
  utmSource?: string;
  utmMedium?: string;
  utmCampaign?: string;
  referrer?: string;
  deviceType?: string;
};

export async function POST(request: Request) {
  const payload = (await request.json()) as SessionPayload;

  if (!payload.sessionId) {
    return NextResponse.json({ ok: false, error: "sessionId is required" }, { status: 400 });
  }

  if (!isPersistenceConfigured()) {
    return NextResponse.json({ ok: true, persisted: false, reason: "persistence_not_configured" });
  }

  const supabase = getSupabaseAdmin();
  if (!supabase) {
    return NextResponse.json({ ok: true, persisted: false, reason: "supabase_unavailable" });
  }

  const { error } = await supabase.from("ci_sessions").upsert(
    {
      id: payload.sessionId,
      anonymous_user_id: payload.anonymousUserId ?? null,
      source: payload.source ?? null,
      utm_source: payload.utmSource ?? null,
      utm_medium: payload.utmMedium ?? null,
      utm_campaign: payload.utmCampaign ?? null,
      referrer: payload.referrer ?? null,
      device_type: payload.deviceType ?? null,
    },
    { onConflict: "id" }
  );

  if (error) {
    return NextResponse.json({ ok: false, error: error.message }, { status: 500 });
  }

  return NextResponse.json({ ok: true, persisted: true });
}
