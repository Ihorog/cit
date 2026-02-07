import { getSupabase } from '@/lib/supabase';
import { formatStatus } from '@/lib/ci-engine';
import type { CiStatus } from '@/lib/ci-engine';

export const dynamic = 'force-dynamic';

interface VerifyPageProps {
  params: Promise<{ code: string }>;
}

export default async function VerifyPage({ params }: VerifyPageProps) {
  const { code } = await params;

  const { data: artifact } = await getSupabase()
    .from('artifacts')
    .select('*')
    .eq('artifact_code', code)
    .single();

  if (!artifact || !artifact.is_sealed) {
    return (
      <div style={styles.container}>
        <div style={styles.card}>
          <p style={styles.issued}>Issued: NO</p>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.title}>ci-Artifact</h1>
        <div style={styles.field}>
          <span style={styles.label}>Artifact Code</span>
          <span style={styles.value}>{artifact.artifact_code}</span>
        </div>
        <div style={styles.field}>
          <span style={styles.label}>Context</span>
          <span style={styles.value}>{artifact.context}</span>
        </div>
        <div style={styles.field}>
          <span style={styles.label}>Status</span>
          <span style={styles.value}>{formatStatus(artifact.status as CiStatus)}</span>
        </div>
        <div style={styles.field}>
          <span style={styles.label}>Locked At</span>
          <span style={styles.value}>{new Date(artifact.locked_at_utc).toISOString()}</span>
        </div>
        <div style={styles.field}>
          <span style={styles.label}>Hash</span>
          <span style={{ ...styles.value, fontSize: '12px', wordBreak: 'break-all' as const }}>
            {artifact.verify_hash}
          </span>
        </div>
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
  },
  title: {
    fontSize: '20px',
    marginBottom: '24px',
    textAlign: 'center' as const,
  },
  issued: {
    fontSize: '18px',
    textAlign: 'center' as const,
    color: '#ff6b6b',
  },
  field: {
    display: 'flex',
    justifyContent: 'space-between',
    padding: '12px',
    background: '#252d37',
    borderRadius: '8px',
    marginBottom: '8px',
  },
  label: {
    color: '#b0b8c8',
    fontSize: '14px',
  },
  value: {
    color: '#e8eef6',
    fontSize: '14px',
    fontWeight: 600,
  },
};
