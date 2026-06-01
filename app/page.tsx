"use client";

import { useMemo, useState } from "react";
import { createArtifact, type CiArtifact } from "@/lib/artifacts/artifact";
import { calculateStatus, CI_CONTEXTS, getLockedMinute, getStatusCopy, type CiContext } from "@/lib/engine/status";
import { buildCheckoutUrl } from "@/lib/payments/gumroad";
import { createSessionId, trackEvent } from "@/lib/telemetry/events";

export default function HomePage() {
  const [sessionId] = useState(() => createSessionId());
  const [selectedContext, setSelectedContext] = useState<CiContext | null>(null);
  const [artifact, setArtifact] = useState<CiArtifact | null>(null);

  const source = typeof document !== "undefined" ? document.referrer || "direct" : "direct";

  useMemo(() => {
    trackEvent({ eventName: "page_view", sessionId, source, route: "/" });
  }, [sessionId, source]);

  function selectContext(context: CiContext) {
    setSelectedContext(context);
    trackEvent({ eventName: "context_selected", sessionId, source, context });
  }

  function renderResult() {
    if (!selectedContext) return;

    const lockedMinute = getLockedMinute();
    const status = calculateStatus(selectedContext, lockedMinute);
    const nextArtifact = createArtifact({ context: selectedContext, status, lockedMinute });

    setArtifact(nextArtifact);
    trackEvent({
      eventName: "result_rendered",
      sessionId,
      source,
      context: selectedContext,
      artifactId: nextArtifact.artifactId,
      verifyHash: nextArtifact.verifyHash,
    });
  }

  function sealMoment() {
    if (!artifact) return;

    trackEvent({
      eventName: "seal_clicked",
      sessionId,
      source,
      context: artifact.context,
      artifactId: artifact.artifactId,
      verifyHash: artifact.verifyHash,
    });

    const checkoutUrl = buildCheckoutUrl({
      artifactId: artifact.artifactId,
      verifyHash: artifact.verifyHash,
      sessionId,
      source,
    });

    trackEvent({
      eventName: "gumroad_checkout_opened",
      sessionId,
      source,
      context: artifact.context,
      artifactId: artifact.artifactId,
      verifyHash: artifact.verifyHash,
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
            <button key={item.id} className="ci-button" onClick={() => selectContext(item.id)}>
              <strong>{item.label}</strong>
              <br />
              <span className="ci-muted">{item.description}</span>
            </button>
          ))}
        </div>

        {selectedContext && !artifact ? (
          <div style={{ marginTop: 28 }}>
            <p className="ci-muted">Context selected: {selectedContext}</p>
            <button className="ci-button" onClick={renderResult}>Reveal result</button>
          </div>
        ) : null}

        {artifact ? (
          <div style={{ marginTop: 32 }}>
            <p className="ci-kicker">Result</p>
            <h2 style={{ margin: 0, fontSize: 36 }}>{artifact.status}</h2>
            <p className="ci-lead">{getStatusCopy(artifact.status)}</p>
            <p className="ci-muted">Artifact: {artifact.artifactCode}</p>
            <p className="ci-muted">Verify hash: {artifact.verifyHash}</p>
            <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginTop: 20 }}>
              <button className="ci-button" onClick={sealMoment}>Seal this moment</button>
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
