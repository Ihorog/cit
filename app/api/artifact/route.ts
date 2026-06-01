import { NextResponse } from "next/server";
import { getSupabaseAdmin, isPersistenceConfigured } from "@/lib/storage/supabase";

export const runtime = "nodejs";

type ArtifactPayload = {
  sessionId?: string;
  source?: string;
  artifact?: {
    artifactId?: string;
    artifactCode?: string;
    verifyHash?: string;
    context?: string;
    status?: string;
    lockedMinute?: number;
    createdAt?: string;
  };
};

export async function POST(request: Request) {
  const payload = (await request.json()) as ArtifactPayload;
  const artifact = payload.artifact;

  if (!payload.sessionId || !artifact?.artifactId || !artifact.artifactCode || !artifact.verifyHash || !artifact.context || !artifact.status) {
    return NextResponse.json({ ok: false, error: "sessionId and complete artifact are required" }, { status: 400 });
  }

  if (!isPersistenceConfigured()) {
    return NextResponse.json({ ok: true, persisted: false, reason: "persistence_not_configured" });
  }

  const supabase = getSupabaseAdmin();
  if (!supabase) {
    return NextResponse.json({ ok: true, persisted: false, reason: "supabase_unavailable" });
  }

  const { error } = await supabase.from("ci_artifacts").upsert(
    {
      id: artifact.artifactId,
      artifact_code: artifact.artifactCode,
      verify_hash: artifact.verifyHash,
      session_id: payload.sessionId,
      context: artifact.context,
      result_status: artifact.status,
      locked_minute: artifact.lockedMinute ?? null,
      source: payload.source ?? null,
      is_verified: false,
      created_at: artifact.createdAt ?? new Date().toISOString(),
    },
    { onConflict: "id" }
  );

  if (error) {
    return NextResponse.json({ ok: false, error: error.message }, { status: 500 });
  }

  return NextResponse.json({ ok: true, persisted: true });
}
