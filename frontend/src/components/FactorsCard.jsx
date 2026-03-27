export default function FactorsCard({ successFactors = [], failureReasons = [], isMobile = false }) {
  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: isMobile ? '1fr' : '1fr 1fr',
      gap: '1px',
      background: '#1e293b',
      border: '1px solid #1e293b',
      borderRadius: '12px',
      overflow: 'hidden',
    }}>
      {/* Success column */}
      <div style={{ background: '#0f172a', padding: isMobile ? '16px' : '20px' }}>
        <div style={{
          display: 'flex', alignItems: 'center', gap: isMobile ? '6px' : '8px',
          marginBottom: '16px',
        }}>
          <span style={{
            width: isMobile ? '20px' : '24px', height: isMobile ? '20px' : '24px', borderRadius: '50%',
            background: 'rgba(52,211,153,0.15)', display: 'flex',
            alignItems: 'center', justifyContent: 'center',
            fontSize: isMobile ? '10px' : '12px', color: '#34d399',
          }}>✓</span>
          <span style={{
            fontSize: isMobile ? '9px' : '11px', fontWeight: '700', letterSpacing: '0.1em',
            textTransform: 'uppercase', color: '#34d399', fontFamily: "'DM Mono', monospace",
            wordBreak: 'break-word', maxWidth: '100%',
          }}>Why It Could Succeed</span>
        </div>
        <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {successFactors.length === 0
            ? <li style={{ color: '#4f6482', fontSize: isMobile ? '12px' : '13px', fontStyle: 'italic' }}>No factors identified</li>
            : successFactors.map((f, i) => (
              <li key={i} style={{ display: 'flex', gap: isMobile ? '8px' : '10px', alignItems: 'flex-start' }}>
                <span style={{
                  flexShrink: 0, marginTop: '2px',
                  width: '16px', height: '16px', borderRadius: '4px',
                  background: 'rgba(52,211,153,0.1)', border: '1px solid rgba(52,211,153,0.3)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: '8px', color: '#34d399',
                }}>✓</span>
                <span style={{ color: '#cbd5e1', fontSize: isMobile ? '12px' : '13px', lineHeight: '1.5' }}>{f}</span>
              </li>
            ))
          }
        </ul>
      </div>

      {/* Failure column */}
      <div style={{ background: '#0f172a', padding: isMobile ? '16px' : '20px' }}>
        <div style={{
          display: 'flex', alignItems: 'center', gap: isMobile ? '6px' : '8px',
          marginBottom: '16px',
        }}>
          <span style={{
            width: isMobile ? '20px' : '24px', height: isMobile ? '20px' : '24px', borderRadius: '50%',
            background: 'rgba(251,113,133,0.15)', display: 'flex',
            alignItems: 'center', justifyContent: 'center',
            fontSize: isMobile ? '10px' : '12px', color: '#fb7185',
          }}>✕</span>
          <span style={{
            fontSize: isMobile ? '9px' : '11px', fontWeight: '700', letterSpacing: '0.1em',
            textTransform: 'uppercase', color: '#fb7185', fontFamily: "'DM Mono', monospace",
            wordBreak: 'break-word', maxWidth: '100%',
          }}>Why It Could Fail</span>
        </div>
        <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {failureReasons.length === 0
            ? <li style={{ color: '#4f6482', fontSize: isMobile ? '12px' : '13px', fontStyle: 'italic' }}>No risks identified</li>
            : failureReasons.map((r, i) => (
              <li key={i} style={{ display: 'flex', gap: isMobile ? '8px' : '10px', alignItems: 'flex-start' }}>
                <span style={{
                  flexShrink: 0, marginTop: '2px',
                  width: '16px', height: '16px', borderRadius: '4px',
                  background: 'rgba(251,113,133,0.1)', border: '1px solid rgba(251,113,133,0.3)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: '8px', color: '#fb7185',
                }}>✕</span>
                <span style={{ color: '#cbd5e1', fontSize: isMobile ? '12px' : '13px', lineHeight: '1.5' }}>{r}</span>
              </li>
            ))
          }
        </ul>
      </div>
    </div>
  );
}