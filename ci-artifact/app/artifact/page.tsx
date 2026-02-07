'use client';

import { useState, useEffect } from 'react';
import type { CiContext, CiStatus } from '@/lib/ci-engine';

type FlowState = 'landing' | 'threshold' | 'manifesting' | 'result' | 'seal';

const SALT: Record<CiContext, number> = { career: 1, love: 2, timing: 3 };
const STATES: CiStatus[] = ['PROCEED', 'HOLD', 'NOT_NOW'];

function getCiStatusClient(context: CiContext, lockedMinuteUtc: number): CiStatus {
  const seed = Number(lockedMinuteUtc) + (SALT[context] ?? 0);
  return STATES[((seed % 3) + 3) % 3];
}

function formatStatus(status: CiStatus): string {
  return status === 'NOT_NOW' ? 'NOT NOW' : status;
}

export default function ArtifactPage() {
  const [flow, setFlow] = useState<FlowState>('landing');
  const [context, setContext] = useState<CiContext>('career');
  const [status, setStatus] = useState<CiStatus | null>(null);
  const [lockedMinute, setLockedMinute] = useState<number>(0);
  const [opacity, setOpacity] = useState(0);
  const [artifactCode, setArtifactCode] = useState('');

  const handleLock = () => {
    setFlow('threshold');
  };

  const handleConfirm = () => {
    const minute = Math.floor(Date.now() / 60000);
    setLockedMinute(minute);
    const result = getCiStatusClient(context, minute);
    setStatus(result);
    setArtifactCode(`CI-${minute}-${context.slice(0, 3).toUpperCase()}`);
    setFlow('manifesting');
  };

  useEffect(() => {
    if (flow === 'manifesting') {
      const fadeIn = setTimeout(() => setOpacity(1), 50);
      const transition = setTimeout(() => setFlow('result'), 3000);
      return () => {
        clearTimeout(fadeIn);
        clearTimeout(transition);
      };
    }
  }, [flow]);

  const handleSeal = async () => {
    setFlow('seal');
    try {
      const res = await fetch('/api/stripe/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          artifact_code: artifactCode,
          context,
          status,
          locked_minute_utc: lockedMinute,
        }),
      });
      const data = await res.json();
      if (data.url) {
        window.location.href = data.url;
      }
    } catch {
      // Stripe checkout creation failed
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.title}>ci-Artifact</h1>

        {flow === 'landing' && (
          <div style={styles.section}>
            <p style={styles.subtitle}>Select Context</p>
            <div style={styles.contextGrid}>
              {(['career', 'love', 'timing'] as CiContext[]).map((c) => (
                <button
                  key={c}
                  onClick={() => setContext(c)}
                  style={{
                    ...styles.contextBtn,
                    ...(context === c ? styles.contextBtnActive : {}),
                  }}
                >
                  {c}
                </button>
              ))}
            </div>
            <button onClick={handleLock} style={styles.primaryBtn}>
              Lock a moment
            </button>
          </div>
        )}

        {flow === 'threshold' && (
          <div style={styles.section}>
            <p style={styles.momentText}>This moment will be locked</p>
            <p style={styles.contextLabel}>{context}</p>
            <button onClick={handleConfirm} style={styles.primaryBtn}>
              Confirm
            </button>
          </div>
        )}

        {flow === 'manifesting' && (
          <div
            style={{
              ...styles.section,
              opacity,
              transition: 'opacity 3s ease-in-out',
            }}
          >
            <p style={styles.manifestingText}>manifesting...</p>
          </div>
        )}

        {flow === 'result' && status && (
          <div style={styles.section}>
            <p style={styles.statusText}>{formatStatus(status)}</p>
            <p style={styles.contextLabel}>{context}</p>
            <button onClick={handleSeal} style={styles.sealBtn}>
              Seal this moment · $5
            </button>
          </div>
        )}

        {flow === 'seal' && (
          <div style={styles.section}>
            <p style={styles.subtitle}>Redirecting to payment...</p>
          </div>
        )}
      </div>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: '#0b0f14',
    color: '#e8eef6',
    fontFamily: 'system-ui, -apple-system, sans-serif',
    padding: '16px',
  },
  card: {
    background: '#1a1f28',
    border: '1px solid rgba(255,255,255,0.08)',
    borderRadius: '12px',
    padding: '32px',
    maxWidth: '480px',
    width: '100%',
    textAlign: 'center' as const,
  },
  title: {
    fontSize: '24px',
    marginBottom: '24px',
    background: 'linear-gradient(135deg, #4f89ff 0%, #10a37f 100%)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
  },
  section: {
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    gap: '16px',
  },
  subtitle: {
    color: '#b0b8c8',
    fontSize: '16px',
  },
  contextGrid: {
    display: 'flex',
    gap: '8px',
    width: '100%',
    justifyContent: 'center',
  },
  contextBtn: {
    flex: 1,
    padding: '12px',
    background: '#252d37',
    border: '1px solid rgba(255,255,255,0.08)',
    borderRadius: '8px',
    color: '#b0b8c8',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: 600,
    textTransform: 'capitalize' as const,
  },
  contextBtnActive: {
    background: 'rgba(79,137,255,0.2)',
    borderColor: '#4f89ff',
    color: '#4f89ff',
  },
  primaryBtn: {
    width: '100%',
    padding: '14px',
    background: '#4f89ff',
    border: 'none',
    borderRadius: '8px',
    color: 'white',
    fontSize: '16px',
    fontWeight: 600,
    cursor: 'pointer',
    marginTop: '8px',
  },
  momentText: {
    fontSize: '18px',
    color: '#e8eef6',
  },
  contextLabel: {
    fontSize: '14px',
    color: '#b0b8c8',
    textTransform: 'capitalize' as const,
  },
  manifestingText: {
    fontSize: '20px',
    color: '#b0b8c8',
    letterSpacing: '2px',
  },
  statusText: {
    fontSize: '36px',
    fontWeight: 700,
    letterSpacing: '2px',
  },
  sealBtn: {
    width: '100%',
    padding: '14px',
    background: '#10a37f',
    border: 'none',
    borderRadius: '8px',
    color: 'white',
    fontSize: '16px',
    fontWeight: 600,
    cursor: 'pointer',
    marginTop: '8px',
  },
};
