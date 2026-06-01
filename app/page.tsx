"use client";

import { useEffect, useMemo, useState } from "react";
import { persistArtifact, persistEvent, persistSession } from "@/lib/api/client";
import { createArtifact, type CiArtifact } from "@/lib/artifacts/artifact";
import { calculateStatus, CI_CONTEXTS, getLockedMinute, getStatusCopy, type CiContext } from "@/lib/engine/status";
import { buildCheckoutUrl } from "@/lib/payments/gumroad";
import { createSessionId, trackEvent, type CiTelemetryEvent } from "@/lib/telemetry/events";

function getSource(): string {
  if (typeof document === "undefined") return "direct";
  return document.referrer || "direct";
}

function getDeviceType(): string {
  if (typeof navigator === "undefined") return "unknown";
  if (/Mobi|Android/i.test(navigator.userAgent)) return "mobile";
  return "desktop";
}

export default function HomePage() {
  const [sessionId] = useState(() => createSessionId());
  const [selectedContext, setSelectedContext] = useState<CiContext | null>(null);
  const [artifact, setArtifact] = useState<CiArtifact | null>(null);
  const [persistenceState, setPersistenceState] = useState("local_ready");

  const source = useMemo(() => getSource(), []);
  const deviceType = useMemo(() => getDeviceType(), []);

  async function emit(event: Omit<CiTelemetryEvent, "timestamp">) {
    const payload = trackEvent(event);
    await persistEvent(payload);
  }

  useEffect(() => {
    void persistSession({ sessionId, source, referrer: source, deviceType });
    void emit({ eventName: "page_view", sessionId, source, route: "/", deviceType });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId, source, deviceType]);

  async function selectContext(context: CiContext) {
    setSelectedContext(context);
    await emit({ eventName: "context_selected", sessionId, source, context, deviceType });
  }

  async function renderResult() {
    if (!selectedContext) return;

    const lockedMinute = getLockedMinute();
    const status = calculateStatus(selectedContext, lockedMinute);
    const nextArtifact = createArtifact({ context: selectedContext, status, lockedMinute });

    setArtifact(nextArtifact);
    setPersistenceState("artifact_created_local");

    const persisted = await persistArtifact({ sessionId, source, artifact: nextArtifact });
    setPersistenceState(persisted?.persisted ? "artifact_persisted" : "artifact_local_only");

    await emit({
      eventName: "result_rendered",
      sessionId,
      source,
      context: selectedContext,
      artifactId: nextArtifact.artifactId,
      verifyHash: nextArtifact.verifyHash,
      deviceType,
    });
  }

  async function sealMoment() {
    if (!artifact) return;

    await emit({
      eventName: "seal_clicked",
      sessionId,
      source,
      context: artifact.context,
      artifactId: artifact.artifactId,
      verifyHash: artifact.verifyHash,
      deviceType,
    });

    const checkoutUrl = buildCheckoutUrl({
      artifactId: artifact.artifactId,
      verifyHash: artifact.verifyHash,
      sessionId,
      source,
    });

    await emit({
      eventName: "gumroad_checkout_opened",
      sessionId,
      source,
      context: artifact.context,
      artifactId: artifact.artifactId,
      verifyHash: artifact.verifyHash,
      deviceType,
    });

    window.location.href = checkoutUrl;
  }

  return (
    <main className="ci-shell">
      <section className="ci-card">
        <p className="ci-kicker">Ci Moment v2</p>
        <h1 className="ci-title">Result → Seal → Artifact → Verify</h1>
        <p className="ci-lead">
          A personal moment signal and symbolic checkpoint. Not advice, not prediction, not therapy.
        </p>

        <div className="ci-grid" aria-label="Select context">
          {CI_CONTEXTS.map((item) => (
            <button key={item.id} className="ci-button" onClick={() => void selectContext(item.id)}>
              <strong>{item.label}</strong>
              <br />
              <span className="ci-muted">{item.description}</span>
            </button>
          ))}
        </div>

        {selectedContext && !artifact ? (
          <div style={{ marginTop: 28 }}>
            <p className="ci-muted">Context selected: {selectedContext}</p>
            <button className="ci-button" onClick={() => void renderResult()}>Reveal result</button>
          </div>
        ) : null}

        {artifact ? (
          <div style={{ marginTop: 32 }}>
            <p className="ci-kicker">Result</p>
            <h2 style={{ margin: 0, fontSize: 36 }}>{artifact.status}</h2>
            <p className="ci-lead">{getStatusCopy(artifact.status)}</p>
            <p className="ci-muted">Artifact: {artifact.artifactCode}</p>
            <p className="ci-muted">Verify hash: {artifact.verifyHash}</p>
            <p className="ci-muted">Persistence: {persistenceState}</p>
            <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginTop: 20 }}>
              <button className="ci-button" onClick={() => void sealMoment()}>Seal this moment</button>
              <a className="ci-button" href={`/verify/${artifact.verifyHash}`} style={{ textDecoration: "none" }}>
                Preview verify page
              </a>
            </div>
          </div>
        ) : null}
      </section>
    </main>
  );
}
