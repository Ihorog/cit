import Link from "next/link";

export default function VerifyPage({ params }: { params: { hash: string } }) {
  return (
    <main className="ci-shell">
      <section className="ci-card">
        <p className="ci-kicker">Artifact verification</p>
        <h1 className="ci-title">Verify a moment</h1>
        <p className="ci-lead">
          This page is the future public verification surface for a sealed Ci Moment artifact.
        </p>

        <div style={{ marginTop: 28 }}>
          <p className="ci-muted">Verify hash:</p>
          <code style={{ fontSize: 20 }}>{params.hash}</code>
        </div>

        <p className="ci-muted" style={{ marginTop: 28 }}>
          Current status: schema and route prepared. Durable artifact lookup will be connected in the next phase.
        </p>

        <Link className="ci-button" href="/" style={{ display: "inline-flex", marginTop: 24, textDecoration: "none" }}>
          Return to Ci Moment
        </Link>
      </section>
    </main>
  );
}
