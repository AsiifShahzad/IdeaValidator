import { useState, useEffect } from 'react';
import { FiTrendingUp, FiSwords, FiAlertTriangle, FiArrowRight } from 'react-icons/fi';
import FactorsCard   from './FactorsCard';
import ToolsUsed     from './ToolsUsed';

// ── Score ring ─────────────────────────────────────────────────────────────────
function ScoreRing({ score, isMobile }) {
  const size = isMobile ? 100 : 140;
  const radius = size / 2.6;
  const circ   = 2 * Math.PI * radius;
  const fill   = (score / 10) * circ;
  const color  = score >= 7 ? '#34d399' : score >= 4 ? '#06b6d4' : '#fb7185';
  return (
    <div style={{ position: 'relative', width: `${size}px`, height: `${size}px`, flexShrink: 0, margin: isMobile ? '0 auto' : 0 }}>
      <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
        <circle cx={size/2} cy={size/2} r={radius} fill="none" stroke="#1e293b" strokeWidth="6" />
        <circle cx={size/2} cy={size/2} r={radius} fill="none" stroke={color} strokeWidth="6"
          strokeDasharray={`${fill} ${circ}`} strokeLinecap="round"
          style={{ transition: 'stroke-dasharray 1s ease' }} />
      </svg>
      <div style={{ position:'absolute', inset:0, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center' }}>
        <span style={{ fontSize: isMobile ? '22px' : '32px', fontWeight:'800', color, fontFamily:"'DM Mono',monospace" }}>{score?.toFixed(1)}</span>
        <span style={{ fontSize: isMobile ? '9px' : '11px', color:'#4f6482' }}>/ 10</span>
      </div>
    </div>
  );
}

// ── Metric card with "why" explanation ────────────────────────────────────────
function MetricCard({ label, value, why, color, icon, isMobile }) {
  const [open, setOpen] = useState(true);
  const levelNum = value === 'high' ? 85 : value === 'medium' ? 50 : value === 'low' ? 20 : null;
  const displayVal = typeof value === 'number' ? `${value}/10` : value;

  return (
    <div
      onClick={() => setOpen(!open)}
      style={{
        padding: isMobile ? '12px 12px' : '14px 16px',
        borderRadius:'10px',
        background: open ? '#0f172a' : '#0a1628',
        border:`1px solid ${open ? color + '40' : '#1e293b'}`,
        cursor:'pointer', transition:'all 0.2s',
      }}
    >
      <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', marginBottom: levelNum !== null ? '10px' : 0 }}>
        <div style={{ display:'flex', alignItems:'center', gap: isMobile ? '6px' : '8px' }}>
          <span style={{ fontSize: isMobile ? '14px' : '16px', color: '#06b6d4', display: 'flex', alignItems: 'center' }}>{icon}</span>
          <span style={{ fontSize: isMobile ? '9px' : '11px', fontWeight:'700', letterSpacing:'0.08em', textTransform:'uppercase', color:'#ffffff', fontFamily:"'DM Mono',monospace" }}>{label}</span>
        </div>
        <div style={{ display:'flex', alignItems:'center', gap: isMobile ? '6px' : '8px' }}>
          <span style={{ fontSize: isMobile ? '11px' : '13px', fontWeight:'700', color, fontFamily:"'DM Mono',monospace" }}>{displayVal}</span>
          <span style={{ fontSize: isMobile ? '8px' : '10px', color:'#4f6482', transition:'transform 0.2s', transform: open ? 'rotate(180deg)' : 'none' }}>▾</span>
        </div>
      </div>

      {levelNum !== null && (
        <div style={{ height:'3px', borderRadius:'2px', background:'#1e293b', overflow:'hidden' }}>
          <div style={{ height:'100%', borderRadius:'2px', background:color, width:`${levelNum}%`, transition:'width 1s ease' }} />
        </div>
      )}

      {open && why && (
        <div style={{ marginTop:'10px', paddingTop:'10px', borderTop:'1px solid #1e293b', fontSize: isMobile ? '11px' : '12px', color:'#94a3b8', lineHeight:'1.6' }}>
          {why}
        </div>
      )}
      {open && !why && (
        <div style={{ marginTop:'10px', paddingTop:'10px', borderTop:'1px solid #1e293b', fontSize: isMobile ? '11px' : '12px', color:'#4f6482', fontStyle:'italic' }}>
          No detail available.
        </div>
      )}
    </div>
  );
}

// ── Next steps ─────────────────────────────────────────────────────────────────
function NextSteps({ steps = [], isMobile }) {
  if (!steps.length) return null;
  return (
      <div style={{ padding: isMobile ? '16px' : '20px', borderRadius:'12px', background:'rgba(6,182,212,0.04)', border:'1px solid rgba(6,182,212,0.15)' }}>
      <div style={{ fontSize: isMobile ? '10px' : '11px', fontWeight:'700', letterSpacing:'0.1em', textTransform:'uppercase', color:'#ffffff', marginBottom:'14px', fontFamily:"'DM Mono',monospace", wordBreak: 'break-word', maxWidth: '100%', display: 'flex', alignItems: 'center', gap: '6px' }}>
        <FiArrowRight size={isMobile ? 14 : 16} style={{ color: '#06b6d4' }} /> What To Do Next
      </div>
      <div style={{ display:'flex', flexDirection:'column', gap:'10px' }}>
        {steps.map((step, i) => (
          <div key={i} style={{ display:'flex', gap: isMobile ? '10px' : '12px', alignItems:'flex-start' }}>
            <div style={{
              flexShrink:0, width: isMobile ? '20px' : '22px', height: isMobile ? '20px' : '22px', borderRadius:'6px',
              background:'rgba(6,182,212,0.1)', border:'1px solid rgba(6,182,212,0.25)',
              display:'flex', alignItems:'center', justifyContent:'center',
              fontSize: isMobile ? '9px' : '11px', fontWeight:'700', color:'#06b6d4', fontFamily:"'DM Mono',monospace",
            }}>{i+1}</div>
            <span style={{ fontSize: isMobile ? '12px' : '13px', color:'#cbd5e1', lineHeight:'1.6', paddingTop:'2px' }}>{step}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Reasoning block ────────────────────────────────────────────────────────────
function Reasoning({ text, isMobile }) {
  if (!text) return null;
  // Guard: if LLM accidentally put a next-step in reasoning, don't show it as summary
  const isMisplaced = text.length < 80 || text.startsWith('Search') || text.startsWith('Post in') || text.startsWith('Reach out');
  if (isMisplaced) return null;
  return (
    <div style={{ padding: isMobile ? '16px' : '20px', borderRadius:'12px', background:'#080f1a', border:'1px solid #1e293b' }}>
      <div style={{ fontSize: isMobile ? '10px' : '11px', fontWeight:'700', letterSpacing:'0.1em', textTransform:'uppercase', color:'#4f6482', marginBottom:'12px', fontFamily:"'DM Mono',monospace", wordBreak: 'break-word', maxWidth: '100%' }}>
        Analysis Summary
      </div>
      <p style={{ color:'#94a3b8', fontSize: isMobile ? '13px' : '14px', lineHeight:'1.75', margin:0 }}>{text}</p>
    </div>
  );
}
// ── Verdict explanation with descriptions ────────────────────────────────────
function VerdictExplanation({ verdict, score, confidence, isMobile }) {
  const verdictConfig = {
    GO: {
      title: 'Go Ahead! 🚀',
      description: `Your idea scores ${score.toFixed(1)}/10 with ${confidence}% confidence. This high score indicates strong market potential, manageable competition, and acceptable risks. You have a solid foundation to proceed with development and market testing.`,
      color: '#34d399',
      bg: 'rgba(52,211,153,0.08)',
    },
    MAYBE: {
      title: 'Worth Exploring 🤔',
      description: `Your idea scores ${score.toFixed(1)}/10 with ${confidence}% confidence. This moderate score suggests potential but with some considerations. Do more research on specific weak areas, test your assumptions with target users, and refine your approach before a full launch.`,
      color: '#06b6d4',
      bg: 'rgba(6,182,212,0.08)',
    },
    'NOT GO': {
      title: 'Reconsider or Pivot ⚠️',
      description: `Your idea scores ${score.toFixed(1)}/10 with ${confidence}% confidence. This lower score indicates significant challenges—either high market saturation, unmanageable risks, or weak demand signals. Consider pivoting the idea, targeting a different market, or revisiting it after market conditions change.`,
      color: '#fb7185',
      bg: 'rgba(251,113,133,0.08)',
    },
  };

  const config = verdictConfig[verdict] || verdictConfig['MAYBE'];

  return (
    <div style={{
      padding: isMobile ? '14px 12px' : '16px 18px',
      borderRadius: '12px',
      background: config.bg,
      border: `1px solid ${config.color}30`,
      marginBottom: '16px',
    }}>
      <div style={{
        fontSize: isMobile ? '13px' : '14px',
        fontWeight: '700',
        color: config.color,
        fontFamily: "'DM Mono', monospace",
        marginBottom: '8px',
      }}>
        {config.title}
      </div>
      <p style={{
        fontSize: isMobile ? '12px' : '13px',
        color: '#cbd5e1',
        lineHeight: '1.7',
        margin: 0,
      }}>
        {config.description}
      </p>
    </div>
  );
}
// ── Main ResultCard ────────────────────────────────────────────────────────────
export default function ResultCard({ result }) {
  if (!result) return null;
  
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);
  
  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 768);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const score   = result.overall_score ?? result.score ?? 0;
  const conf    = result.confidence_percent ?? result.confidence ?? 0;
  const verdict = result.verdict || (score >= 7 ? 'GO' : score >= 4 ? 'MAYBE' : 'NO GO');

  const verdictColor = verdict === 'GO' ? '#34d399' : verdict === 'MAYBE' ? '#06b6d4' : '#fb7185';
  const verdictBg    = verdict === 'GO' ? 'rgba(52,211,153,0.08)' : verdict === 'MAYBE' ? 'rgba(251,191,36,0.08)' : 'rgba(251,113,133,0.08)';

  const demand      = result.demand      || {};
  const competition = result.competition || {};
  const risk        = result.risk        || {};

  return (
    <div style={{ display:'flex', flexDirection:'column', gap:'16px' }}>

      {/* Verdict badge */}
      <div style={{ display:'flex', justifyContent:'flex-start' }}>
        <div style={{ padding: isMobile ? '6px 14px' : '6px 18px', borderRadius:'8px', background:verdictBg, border:`1px solid ${verdictColor}30`, color:verdictColor, fontWeight:'800', fontSize: isMobile ? '12px' : '14px', fontFamily:"'DM Mono',monospace", letterSpacing:'0.1em' }}>
          {verdict}
        </div>
      </div>

      {/* Verdict explanation with description */}
      <VerdictExplanation verdict={verdict} score={score} confidence={conf} isMobile={isMobile} />

      {/* Score + confidence */}
      <div style={{ 
        display:'grid', 
        gridTemplateColumns: isMobile ? '1fr' : 'auto 1fr', 
        gap: isMobile ? '16px' : 'clamp(16px, 4vw, 24px)',
        alignItems:'center',
        padding: isMobile ? '16px' : 'clamp(16px, 4vw, 24px)',
        background:'#0a1628',
        borderRadius:'12px',
        border:'1px solid #1e293b'
      }}>
        <ScoreRing score={score} isMobile={isMobile} />
        <div style={{ display:'flex', flexDirection:'column', gap:'12px' }}>
          <div>
            <div style={{ display:'flex', justifyContent:'space-between', marginBottom:'6px' }}>
              <span style={{ fontSize: isMobile ? '9px' : '11px', color:'#4f6482', fontFamily:"'DM Mono',monospace", textTransform:'uppercase', letterSpacing:'0.06em' }}>Confidence</span>
              <span style={{ fontSize: isMobile ? '11px' : '12px', color:'#60a5fa', fontFamily:"'DM Mono',monospace", fontWeight:'700' }}>{conf}%</span>
            </div>
            <div style={{ height:'4px', borderRadius:'2px', background:'#1e293b', overflow:'hidden' }}>
              <div style={{ height:'100%', borderRadius:'2px', background:'#60a5fa', width:`${conf}%`, transition:'width 1s ease' }} />
            </div>
          </div>
          <p style={{ fontSize: isMobile ? '11px' : '12px', color:'#4f6482', lineHeight:'1.5', margin:0, fontStyle:'italic' }}>
            Click any metric below to see why
          </p>
        </div>
      </div>

      {/* Metric cards — each clickable with "why" */}
      <div style={{ 
        display:'grid', 
        gridTemplateColumns: isMobile ? '1fr' : '1fr 1fr', 
        gap:'8px' 
      }}>
        <MetricCard label="Demand"      value={demand.level      || 'medium'} why={result.demand_why}      color="#34d399" icon={<FiTrendingUp size={isMobile ? 14 : 16} color="#06b6d4" />} isMobile={isMobile} />
        <MetricCard label="Competition" value={competition.level || 'medium'} why={result.competition_why} color="#fb7185" icon={<FiSwords size={isMobile ? 14 : 16} color="#06b6d4" />} isMobile={isMobile} />
        <MetricCard label="Risk"        value={['high','medium','low'].includes(risk.level) ? risk.level : 'medium'}        why={result.risk_why}        color="#f97316" icon={<FiAlertTriangle size={isMobile ? 14 : 16} color="#06b6d4" />} isMobile={isMobile} />
      </div>

      {/* Tools */}
      <ToolsUsed tools={result.tools_used || result.tools_assigned || []} isMobile={isMobile} />

      {/* Reasoning — plain language summary */}
      <Reasoning text={result.reasoning} isMobile={isMobile} />

      {/* Success/failure factors */}
      <FactorsCard
        successFactors={result.success_factors || []}
        failureReasons={result.failure_reasons || []}
        isMobile={isMobile}
      />

      {/* Next steps */}
      <NextSteps steps={result.next_steps || []} isMobile={isMobile} />

      {/* Similar past ideas */}
      {result.similar_past_ideas?.length > 0 && (
        <div style={{ padding: isMobile ? '14px 12px' : '16px 18px', borderRadius:'10px', background:'#080f1a', border:'1px solid #1e293b' }}>
          <div style={{ fontSize: isMobile ? '9px' : '11px', fontWeight:'700', letterSpacing:'0.1em', textTransform:'uppercase', color:'#4f6482', marginBottom:'12px', fontFamily:"'DM Mono',monospace", wordBreak: 'break-word', maxWidth: '100%', wordBreak: 'break-word', maxWidth: '100%' }}>
            Similar Past Validations
          </div>
          <div style={{ display:'flex', flexDirection:'column', gap:'8px' }}>
            {result.similar_past_ideas.map((s, i) => {
              const vc = s.verdict === 'GO' ? '#34d399' : s.verdict === 'MAYBE' ? '#fbbf24' : '#fb7185';
              return (
                <div key={i} style={{ display:'flex', justifyContent:'space-between', alignItems:'center', gap: isMobile ? '8px' : '12px', padding: isMobile ? '6px 8px' : '8px 12px', borderRadius:'7px', background:'#0a1628', border:'1px solid #1e293b', flexWrap: isMobile ? 'wrap' : 'nowrap' }}>
                  <span style={{ color:'#64748b', fontSize: isMobile ? '11px' : '12px', flex:1, minWidth: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{s.idea?.slice(0,60)}...</span>
                  <div style={{ display:'flex', gap: isMobile ? '6px' : '8px', flexShrink:0 }}>
                    <span style={{ padding: isMobile ? '2px 6px' : '2px 8px', borderRadius:'4px', fontSize: isMobile ? '9px' : '11px', fontFamily:"'DM Mono',monospace", fontWeight:'700', color:vc, background:`${vc}15`, whiteSpace:'nowrap' }}>{s.verdict}</span>
                    <span style={{ fontSize: isMobile ? '9px' : '11px', color:'#4f6482', fontFamily:"'DM Mono',monospace", whiteSpace:'nowrap' }}>{(s.similarity*100).toFixed(0)}%</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}