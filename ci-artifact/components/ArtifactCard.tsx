import type { ReactNode } from 'react';

interface ArtifactCardProps {
  title?: string;
  children: ReactNode;
}

export default function ArtifactCard({ title, children }: ArtifactCardProps) {
  return (
    <div style={styles.container}>
      <div style={styles.card}>
        {title && <h1 style={styles.title}>{title}</h1>}
        {children}
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
};
