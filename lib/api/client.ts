import type { CiArtifact } from "@/lib/artifacts/artifact";
import type { CiTelemetryEvent } from "@/lib/telemetry/events";

async function postJson<T>(url: string, payload: unknown): Promise<T | null> {
  try {
    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      console.warn(`[ci api] ${url} returned ${response.status}`);
      return null;
    }

    return (await response.json()) as T;
  } catch (error) {
    console.warn(`[ci api] ${url} failed`, error);
    return null;
  }
}

export function persistSession(input: {
  sessionId: string;
  anonymousUserId?: string;
  source?: string;
  utmSource?: string;
  utmMedium?: string;
  utmCampaign?: string;
  referrer?: string;
  deviceType?: string;
}) {
  return postJson<{ ok: boolean; persisted: boolean }>("/api/session", input);
}

export function persistEvent(event: CiTelemetryEvent) {
  return postJson<{ ok: boolean; persisted: boolean }>("/api/event", event);
}

export function persistArtifact(input: {
  sessionId: string;
  source?: string;
  artifact: CiArtifact;
}) {
  return postJson<{ ok: boolean; persisted: boolean }>("/api/artifact", input);
}
