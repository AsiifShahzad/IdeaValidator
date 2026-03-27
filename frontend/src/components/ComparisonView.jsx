import { useState, useEffect } from 'react';
import { RadarChart, PolarGrid, PolarAngleAxis, Radar, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import IdeaTypeBadge from './IdeaTypeBadge';

const IDEA_TYPES = ['business', 'dev_project', 'research', 'content', 'physical_product', 'social_impact'];

function levelToNum(level) {
  return level === 'high' ? 80 : level === 'medium' ? 50 : level === 'low' ? 25 : 0;
}

export default function ComparisonView({ results }) {
  const [filterType, setFilterType] = useState('all');
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);

  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 768);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);
  const [selected, setSelected]     = useState([0, 1]);

  // Filter by idea type
  const filtered = filterType === 'all'
    ? results
    : results.filter(r => (r.idea_type || '') === filterType);

  // Available types in current results
  const availableTypes = [...new Set(results.map(r => r.idea_type).filter(Boolean))];

  // Items to compare
  const item1 = filtered[selected[0]];
  const item2 = filtered[selected[1]];

  if (results.length < 2) {
    return (
      <div style={{
        padding: '24px', borderRadius: '12px',
        background: 'rgba(96,165,250,0.06)', border: '1px solid rgba(96,165,250,0.2)',
        color: '#60a5fa', fontSize: '14px',
        fontFamily: "'DM Mono', monospace",
      }}>
        ℹ Validate at least 2 ideas to enable comparison.
      </div>
    );
  }

  const radarData = item1 && item2 ? [
    { axis: 'Score',       A: ((item1.overall_score ?? 0) * 10), B: ((item2.overall_score ?? 0) * 10) },
    { axis: 'Demand',      A: levelToNum(item1.demand?.level),   B: levelToNum(item2.demand?.level)   },
    { axis: 'Low Risk',    A: 100 - levelToNum(item1.risk?.level), B: 100 - levelToNum(item2.risk?.level) },
    { axis: 'Confidence',  A: item1.confidence_percent ?? 0,     B: item2.confidence_percent ?? 0     },
  ] : [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', width: '100%' }}>

      {/* Header + filter */}
      <div style={{ display: 'flex', flexDirection: isMobile ? 'column' : 'row', alignItems: isMobile ? 'flex-start' : 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px', width: '100%' }}>
        <div style={{ width: isMobile ? '100%' : 'auto' }}>
          <h2 style={{ fontSize: isMobile ? '20px' : '22px', fontWeight: '800', color: '#f8fafc', margin: 0, fontFamily: "'DM Mono', monospace" }}>
            Compare Ideas
          </h2>
          <p style={{ color: '#ffffff', fontSize: isMobile ? '12px' : '13px', marginTop: '4px' }}>
            Filter by type to compare apples to apples
          </p>
        </div>

        {/* Type filter dropdown */}
        <select
          value={filterType}
          onChange={e => { setFilterType(e.target.value); setSelected([0, 1]); }}
          style={{
            padding: '8px 14px', borderRadius: '8px',
            background: '#1e293b', border: '1px solid #334155',
            color: '#94a3b8', fontSize: isMobile ? '11px' : '12px',
            fontFamily: "'DM Mono', monospace",
            cursor: 'pointer', outline: 'none',
          }}
        >
          <option value="all">All Types</option>
          {availableTypes.map(t => (
            <option key={t} value={t}>{t.replace('_', ' ')}</option>
          ))}
        </select>
      </div>

      {filtered.length < 2 ? (
        <div style={{
          padding: '20px', borderRadius: '10px',
          background: 'rgba(251,191,36,0.06)', border: '1px solid rgba(251,191,36,0.2)',
          color: '#06b6d4', fontSize: '13px', fontFamily: "'DM Mono', monospace",
        }}>
          ⚠ Only {filtered.length} {filterType} idea{filtered.length === 1 ? '' : 's'} found.
          Validate more {filterType} ideas or change the filter.
        </div>
      ) : (
        <>
          {/* Idea selectors */}
          <div style={{ display: 'grid', gridTemplateColumns: isMobile ? '1fr' : '1fr 1fr', gap: '12px' }}>
            {[0, 1].map(slot => (
              <div key={slot}>
                <div style={{
                  fontSize: isMobile ? '14px' : '18px', fontWeight: '700', letterSpacing: '0.1em',
                  color: slot === 0 ? '#60a5fa' : '#a78bfa',
                  fontFamily: "'DM Mono', monospace', textTransform: 'uppercase",
                  marginBottom: '6px',
                }}>
                  {slot === 0 ? '◈ Idea A' : '◈ Idea B'}
                </div>
                <select
                  value={selected[slot]}
                  onChange={e => {
                    const next = [...selected];
                    next[slot] = parseInt(e.target.value);
                    setSelected(next);
                  }}
                  style={{
                    width: '100%', padding: '8px 12px', borderRadius: '8px',
                    background: '#1e293b', border: `1px solid ${slot === 0 ? 'rgba(96,165,250,0.3)' : 'rgba(167,139,250,0.3)'}`,
                    color: '#94a3b8', fontSize: isMobile ? '11px' : '12px',
                    fontFamily: "'DM Mono', monospace",
                    cursor: 'pointer', outline: 'none',
                  }}
                >
                  {filtered.map((r, i) => (
                    <option key={i} value={i}>
                      {r.idea?.slice(0, 55)}... ({r.verdict})
                    </option>
                  ))}
                </select>
              </div>
            ))}
          </div>

          {/* Side-by-side score cards */}
          {item1 && item2 && (
            <div style={{ display: 'grid', gridTemplateColumns: isMobile ? '1fr' : '1fr 1fr', gap: '12px' }}>
              {[item1, item2].map((item, idx) => {
                const color   = idx === 0 ? '#60a5fa' : '#a78bfa';
                const verdict = item.verdict;
                const vc      = verdict === 'GO' ? '#34d399' : verdict === 'MAYBE' ? '#06b6d4' : '#fb7185';
                return (
                  <div key={idx} style={{
                    padding: isMobile ? '16px' : '20px', borderRadius: '12px',
                    background: '#0a1628', border: `1px solid ${color}20`,
                  }}>
                    <div style={{ marginBottom: '12px' }}>
                      <IdeaTypeBadge type={item.idea_type} />
                    </div>
                    <p style={{ color: '#64748b', fontSize: isMobile ? '11px' : '12px', margin: '10px 0 14px', lineHeight: '1.4' }}>
                      {item.idea?.slice(0, 80)}...
                    </p>
                    <div style={{ display: 'flex', alignItems: 'baseline', gap: isMobile ? '6px' : '8px', marginBottom: '12px', flexWrap: 'wrap' }}>
                      <span style={{ fontSize: isMobile ? '28px' : '36px', fontWeight: '800', color, fontFamily: "'DM Mono', monospace" }}>
                        {(item.overall_score ?? 0).toFixed(1)}
                      </span>
                      <span style={{ color: '#4f6482', fontSize: isMobile ? '10px' : '12px' }}>/10</span>
                      <span style={{
                        marginLeft: isMobile ? 'auto' : 'auto', padding: '4px 10px', borderRadius: '6px',
                        fontSize: isMobile ? '10px' : '12px', fontWeight: '700', fontFamily: "'DM Mono', monospace",
                        color: vc, background: `${vc}15`, whiteSpace: 'nowrap',
                      }}>{verdict}</span>
                    </div>
                    <div style={{ fontSize: isMobile ? '10px' : '11px', color: '#4f6482', fontFamily: "'DM Mono', monospace" }}>
                      {item.confidence_percent}% confidence
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Radar chart */}
          {radarData.length > 0 && (
            <div style={{ padding: '20px', background: '#0a1628', borderRadius: '12px', border: '1px solid #1e293b' }}>
              <div style={{
                fontSize: '11px', fontWeight: '700', letterSpacing: '0.1em',
                textTransform: 'uppercase', color: '#4f6482',
                marginBottom: '16px', fontFamily: "'DM Mono', monospace",
              }}>
                Multi-Dimensional Analysis
              </div>
              <ResponsiveContainer width="100%" height={280}>
                <RadarChart data={radarData}>
                  <PolarGrid stroke="#1e293b" />
                  <PolarAngleAxis dataKey="axis" tick={{ fill: '#4f6482', fontSize: 11, fontFamily: "'DM Mono', monospace" }} />
                  <Radar name={`Idea A`} dataKey="A" stroke="#60a5fa" fill="#60a5fa" fillOpacity={0.15} strokeWidth={2} />
                  <Radar name={`Idea B`} dataKey="B" stroke="#a78bfa" fill="#a78bfa" fillOpacity={0.15} strokeWidth={2} />
                  <Legend wrapperStyle={{ fontSize: '11px', fontFamily: "'DM Mono', monospace", color: '#64748b' }} />
                  <Tooltip
                    contentStyle={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '8px', fontSize: '12px' }}
                    labelStyle={{ color: '#94a3b8' }}
                  />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Success/failure side by side */}
          {item1 && item2 && (
            <div style={{ display: 'grid', gridTemplateColumns: isMobile ? '1fr' : '1fr 1fr', gap: '12px' }}>
              {[item1, item2].map((item, idx) => {
                const color = idx === 0 ? '#60a5fa' : '#a78bfa';
                return (
                  <div key={idx} style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    <div style={{ padding: '14px 16px', borderRadius: '10px', background: '#0a1628', border: '1px solid rgba(52,211,153,0.15)' }}>
                      <div style={{ fontSize: '10px', color: '#34d399', fontWeight: '700', letterSpacing: '0.1em', textTransform: 'uppercase', fontFamily: "'DM Mono', monospace", marginBottom: '10px' }}>
                        ✓ Success Factors
                      </div>
                      {(item.success_factors || []).slice(0, 3).map((f, i) => (
                        <div key={i} style={{ fontSize: '12px', color: '#64748b', lineHeight: '1.5', marginBottom: '6px', paddingLeft: '12px', borderLeft: '2px solid rgba(52,211,153,0.3)' }}>
                          {f}
                        </div>
                      ))}
                    </div>
                    <div style={{ padding: '14px 16px', borderRadius: '10px', background: '#0a1628', border: '1px solid rgba(251,113,133,0.15)' }}>
                      <div style={{ fontSize: '10px', color: '#fb7185', fontWeight: '700', letterSpacing: '0.1em', textTransform: 'uppercase', fontFamily: "'DM Mono', monospace", marginBottom: '10px' }}>
                        ✕ Failure Risks
                      </div>
                      {(item.failure_reasons || []).slice(0, 2).map((r, i) => (
                        <div key={i} style={{ fontSize: '12px', color: '#64748b', lineHeight: '1.5', marginBottom: '6px', paddingLeft: '12px', borderLeft: '2px solid rgba(251,113,133,0.3)' }}>
                          {r}
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </>
      )}
    </div>
  );
}