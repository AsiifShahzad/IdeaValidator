import { useState } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

const EXAMPLES = [
  'A SaaS tool that auto-generates legal contracts for freelancers',
  'Open-source React component library for data visualization',
  'YouTube cooking channel focused on 30-minute Pakistani recipes',
  'NGO to bring digital literacy to rural school children',
];

export default function IdeaInput({ onSubmit }) {
  const [idea,    setIdea]    = useState('');
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState('');

  const handleSubmit = async () => {
    if (!idea.trim()) { setError('Please describe your idea first.'); return; }
    setLoading(true);
    setError('');
    try {
      onSubmit(idea.trim());
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to start validation.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', width: '100%', boxSizing: 'border-box' }}>
      <style>{`
        textarea::placeholder {
          color: #4f6482;
          opacity: 1;
        }
      `}</style>
      <div style={{ position: 'relative' }}>
        <textarea
          value={idea}
          onChange={e => setIdea(e.target.value)}
          placeholder="Describe your idea in detail — include the problem you're solving and your target audience..."
          disabled={loading}
          rows={5}
          style={{
            width:        '100%',
            padding:      '16px',
            borderRadius: '10px',
            background:   'transparent',
            border:       '1px solid rgba(6,182,212,0.4)',
            color:        '#e2e8f0',
            fontSize:     '14px',
            lineHeight:   '1.6',
            resize:       'vertical',
            outline:      'none',
            fontFamily:   "system-ui, sans-serif",
            transition:   'border-color 0.2s',
            boxSizing:    'border-box',
          }}
          onFocus={e  => e.target.style.borderColor = 'rgba(6,182,212,0.6)'}
          onBlur={e   => e.target.style.borderColor = 'rgba(6,182,212,0.4)'}
        />
        <div style={{
          position: 'absolute', bottom: '10px', right: '14px',
          fontSize: '11px', color: '#4f6482', fontFamily: "'DM Mono', monospace",
        }}>
          {idea.length} chars
        </div>
      </div>

      {/* Example prompts */}
      <div>
        <div style={{ fontSize: '11px', color: '#ffffff', fontFamily: "'DM Mono', monospace", marginBottom: '8px', letterSpacing: '0.08em', textTransform: 'uppercase' }}>
          Try an example
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
          {EXAMPLES.map((ex, i) => (
            <button key={i} onClick={() => setIdea(ex)} style={{
              padding:      '5px 12px',
              borderRadius: '6px',
              background:   'transparent',
              border:       '1px solid #1e293b',
              color:        '#ffffff',
              fontSize:     '12px',
              cursor:       'pointer',
              transition:   'all 0.15s',
              textAlign:    'left',
            }}
              onMouseEnter={e => { e.target.style.borderColor = '#334155'; e.target.style.color = '#94a3b8'; }}
              onMouseLeave={e => { e.target.style.borderColor = '#1e293b'; e.target.style.color = '#ffffff'; }}
            >
              {ex.slice(0, 40)}…
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div style={{
          padding: '10px 14px', borderRadius: '8px',
          background: 'rgba(251,113,133,0.08)', border: '1px solid rgba(251,113,133,0.25)',
          color: '#fb7185', fontSize: '13px',
        }}>
          {error}
        </div>
      )}

      <button
        onClick={handleSubmit}
        disabled={loading || !idea.trim()}
        style={{
          padding:      '9px 18px',
          borderRadius: '8px',
          background:   loading || !idea.trim() ? '#1e293b' : 'rgba(6,182,212,0.1)',
          border:       loading || !idea.trim() ? '1px solid #1e293b' : '1px solid rgba(6,182,212,0.25)',
          color:        loading || !idea.trim() ? '#ffffff' : '#06b6d4',
          fontWeight:   '700',
          fontSize:     '12px',
          cursor:       loading || !idea.trim() ? 'not-allowed' : 'pointer',
          fontFamily:   "'DM Mono', monospace",
          letterSpacing:'0.05em',
          transition:   'all 0.15s',
          display:      'flex',
          alignItems:   'center',
          justifyContent: 'center',
          whiteSpace:   'nowrap',
        }}
        onMouseEnter={e => { if (!loading && idea.trim()) { e.target.style.background = 'rgba(6,182,212,0.2)'; e.target.style.borderColor = 'rgba(6,182,212,0.4)'; } }}
        onMouseLeave={e => { if (!loading && idea.trim()) { e.target.style.background = 'rgba(6,182,212,0.1)'; e.target.style.borderColor = 'rgba(6,182,212,0.25)'; } }}
      >
        {loading ? 'Starting...' : '→ Validate Idea'}
      </button>
    </div>
  );
}