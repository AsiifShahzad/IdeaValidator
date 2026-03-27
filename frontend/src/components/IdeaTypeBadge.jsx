const TYPE_CONFIG = {
  dev_project:      { label: 'Dev Project',      color: '#a78bfa', bg: 'rgba(167,139,250,0.12)', icon: '⟨/⟩' },
  business:         { label: 'Business',          color: '#2dd4bf', bg: 'rgba(45,212,191,0.12)',  icon: '◈' },
  research:         { label: 'Research',          color: '#60a5fa', bg: 'rgba(96,165,250,0.12)',  icon: '⊕' },
  content:          { label: 'Content',           color: '#fb7185', bg: 'rgba(251,113,133,0.12)', icon: '▶' },
  physical_product: { label: 'Physical Product',  color: '#06b6d4', bg: 'rgba(6,182,212,0.12)',  icon: '◎' },
  social_impact:    { label: 'Social Impact',     color: '#34d399', bg: 'rgba(52,211,153,0.12)',  icon: '❋' },
};

export default function IdeaTypeBadge({ type }) {
  const config = TYPE_CONFIG[type] || { label: type, color: '#94a3b8', bg: 'rgba(148,163,184,0.12)', icon: '◉' };

  return (
    <span style={{
      display:       'inline-flex',
      alignItems:    'center',
      gap:           '6px',
      padding:       '4px 12px',
      borderRadius:  '20px',
      fontSize:      '12px',
      fontWeight:    '600',
      letterSpacing: '0.05em',
      textTransform: 'uppercase',
      color:         config.color,
      background:    config.bg,
      border:        `1px solid ${config.color}30`,
      fontFamily:    "'DM Mono', monospace",
    }}>
      <span style={{ fontSize: '14px' }}>{config.icon}</span>
      {config.label}
    </span>
  );
}