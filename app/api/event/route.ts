import { NextResponse } from "next/server";
import { getSupabaseAdmin, isPersistenceConfigured } from "@/lib/storage/supabase";

export const runtime = "nodejs";

type EventPayload = {
  eventName?: string;
  sessionId?: string;
  context?: string;
  artifactId?: string;
  orderId?: string;
  timestamp?: string;
  [key: string]: unknown;
};

export async function POST(request: Request) {
  const payload = (await request.json()) as EventPayload;

  if (!payload.eventName || !payload.sessionId) {
    return NextResponse.json({ ok: false, error: "eventName and sessionId are required" }, { status: 400 });
  }

  if (!isPersistenceConfigured()) {
    return NextResponse.json({ ok: true, persisted: false, reason: "persistence_not_configured" });
  }

  const supabase = getSupabaseAdmin();
  if (!supabase) {
    return NextResponse.json({ ok: true, persisted: false, reason: "supabase_unavailable" });
  }

  const { error } = await supabase.from("ci_events").insert({
    session_id: payload.sessionId,
    event_name: payload.eventName,
    context: payload.context ?? null,
    artifact_id: payload.artifactId ?? null,
    order_id: payload.orderId ?? null,
    metadata: payload,
    created_at: payload.timestamp ?? new Date().toISOString(),
  });

  if (error) {
    return NextResponse.json({ ok: false, error: error.message }, { status: 500 });
  }

  return NextResponse.json({ ok: true, persisted: true });
}
