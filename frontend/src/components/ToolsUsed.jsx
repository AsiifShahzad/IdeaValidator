import { useState } from 'react';

const TOOL_INFO = {
  tavily:        { icon: '🔍', label: 'Web Search',      desc: 'Searching the web for recent articles, discussions, and mentions of your idea.' },
  github:        { icon: '⌥', label: 'GitHub',          desc: 'Exploring GitHub repositories to see how many similar projects already exist.' },
  npm_trends:    { icon: '📦', label: 'NPM Registry',    desc: 'Checking npm package popularity and developer adoption rates.' },
  product_hunt:  { icon: '🚀', label: 'Product Hunt',   desc: 'Looking for similar product launches to see community reception and feedback.' },
  arxiv:         { icon: '📄', label: 'Research Papers', desc: 'Researching academic papers and studies related to your idea.' },
  google_trends: { icon: '📈', label: 'Search Trends',   desc: 'Checking how search interest in this topic is trending over time.' },
  reddit:        { icon: '💬', label: 'Reddit',         desc: 'Exploring Reddit discussions to find real community conversations and feedback.' },
  news:          { icon: '📰', label: 'News Coverage',   desc: 'Finding recent news articles to track media attention and public sentiment.' },
  crunchbase:    { icon: '💼', label: 'Funding Data',    desc: 'Researching startup funding activity and investment trends in this space.' },
  google_scholar:{ icon: '🎓', label: 'Scholar',        desc: 'Searching academic citations to measure scholarly interest and research depth.' },
};

function ToolBadge({ toolName, isMobile }) {
  const [showTip, setShowTip] = useState(false);
  const info = TOOL_INFO[toolName] || { icon: '⚙', label: toolName, desc: 'Data source used in this analysis.' };

  return (
    <div style={{ position: 'relative', display: 'inline-block' }}
      onMouseEnter={() => !isMobile && setShowTip(true)}
      onMouseLeave={() => setShowTip(false)}
    >
      <button style={{
        display:      'inline-flex',
        alignItems:   'center',
        gap:          isMobile ? '4px' : '5px',
        padding:      isMobile ? '4px 8px' : '5px 10px',
        borderRadius: '6px',
        fontSize:     isMobile ? '9px' : '11px',
        fontWeight:   '600',
        letterSpacing:'0.04em',
        color:        '#94a3b8',
        background:   '#1e293b',
        border:       '1px solid #334155',
        cursor:       'pointer',
        fontFamily:   "'DM Mono', monospace",
        transition:   'all 0.15s',
      }}
        onMouseEnter={e => {
          e.currentTarget.style.color = '#f8fafc';
          e.currentTarget.style.borderColor = '#06b6d4';
          e.currentTarget.style.background = '#1e2d3d';
        }}
        onMouseLeave={e => {
          e.currentTarget.style.color = '#94a3b8';
          e.currentTarget.style.borderColor = '#334155';
          e.currentTarget.style.background = '#1e293b';
        }}
      >
        <span style={{ fontSize: isMobile ? '13px' : '14px' }}>{info.icon}</span>
        {!isMobile && info.label}
      </button>

      {showTip && !isMobile && (
        <div style={{
          position:   'absolute',
          bottom:     'calc(100% + 8px)',
          left:       '50%',
          transform:  'translateX(-50%)',
          background: '#0f172a',
          border:     '1px solid #334155',
          borderRadius:'8px',
          padding:    '10px 14px',
          width:      '220px',
          fontSize:   '12px',
          color:      '#cbd5e1',
          lineHeight: '1.5',
          zIndex:     100,
          boxShadow:  '0 8px 24px rgba(0,0,0,0.4)',
          pointerEvents: 'none',
        }}>
          <div style={{ fontWeight: '700', color: '#f8fafc', marginBottom: '4px', fontFamily: "'DM Mono', monospace" }}>
            {info.icon} {info.label}
          </div>
          {info.desc}
          {/* Arrow */}
          <div style={{
            position: 'absolute', bottom: '-5px', left: '50%',
            transform: 'translateX(-50%) rotate(45deg)',
            width: '8px', height: '8px',
            background: '#0f172a', border: '1px solid #334155',
            borderTop: 'none', borderLeft: 'none',
          }} />
        </div>
      )}
    </div>
  );
}

export default function ToolsUsed({ tools = [], isMobile = false }) {
  if (!tools.length) return null;

  return (
    <div style={{ padding: isMobile ? '14px 12px' : '16px 20px', background: '#0a1628', borderRadius: '10px', border: '1px solid #1e293b' }}>
      <div style={{
        fontSize: isMobile ? '9px' : '10px', fontWeight: '700', letterSpacing: '0.12em',
        textTransform: 'uppercase', color: '#4f6482',
        marginBottom: '12px', fontFamily: "'DM Mono', monospace",
        wordBreak: 'break-word', maxWidth: '100%',
      }}>
        Data Sources Used
      </div>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: isMobile ? '5px' : '6px' }}>
        {tools.map(tool => <ToolBadge key={tool} toolName={tool} isMobile={isMobile} />)}
      </div>
    </div>
  );
}