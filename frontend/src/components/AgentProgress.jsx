import { useEffect, useState, useRef } from 'react';

const API_BASE = 'https://ideavalidator-8h1j.onrender.com';

const AGENT_STEPS = [
  { id: 'classifier',          label: 'Classifier',    desc: 'Detecting idea type & assigning tools' },
  { id: 'research',            label: 'Research',      desc: 'Gathering data from external sources' },
  { id: 'demand_analyst',      label: 'Demand',        desc: 'Estimating market demand signals' },
  { id: 'competition_analyst', label: 'Competition',   desc: 'Mapping the competitive landscape' },
  { id: 'risk_analyst',        label: 'Risk',          desc: 'Identifying top failure risks' },
  { id: 'decision',            label: 'Decision',      desc: 'Synthesizing final verdict' },
  { id: 'reflection',          label: 'Reflection',    desc: 'Auditing analysis quality' },
];

export default function AgentProgress({ idea, onComplete }) {
  const [stepStatus, setStepStatus] = useState({});  // { agentId: 'pending' | 'running' | 'complete' | 'error' }
  const [durations, setDurations]   = useState({});
  const [error, setError]           = useState('');
  const [done, setDone]             = useState(false);
  const startTimes                  = useRef({});
  const esRef                       = useRef(null);

  useEffect(() => {
    if (!idea) return;

    // Mark all steps as pending
    const initial = {};
    AGENT_STEPS.forEach(s => { initial[s.id] = 'pending'; });
    setStepStatus(initial);

    // Open SSE connection
    const encoded = encodeURIComponent(idea);
    const es      = new EventSource(`${API_BASE}/validate-idea/stream?idea=${encoded}`);
    esRef.current = es;

    es.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        const { agent, status, duration_ms } = data;

        if (status === 'pending') return;

        if (status === 'complete') {
          if (agent === 'pipeline') {
            // Pipeline done — fetch full result
            setDone(true);
            fetch(`${API_BASE}/validate-idea`, {
              method:  'POST',
              headers: { 'Content-Type': 'application/json' },
              body:    JSON.stringify({ idea }),
            })
              .then(r => r.json())
              .then(result => onComplete(result))
              .catch(err => setError('Failed to fetch result: ' + err.message));
            es.close();
            return;
          }

          setStepStatus(prev => ({ ...prev, [agent]: 'complete' }));
          setDurations(prev => ({ ...prev, [agent]: duration_ms || 0 }));

          // Mark next step as running
          const idx = AGENT_STEPS.findIndex(s => s.id === agent);
          if (idx >= 0 && idx + 1 < AGENT_STEPS.length) {
            setStepStatus(prev => ({ ...prev, [AGENT_STEPS[idx + 1].id]: 'running' }));
          }
        }

        if (status === 'error') {
          setError(data.error || 'Pipeline error');
          es.close();
        }

      } catch {}
    };

    es.onerror = () => {
      setError('Connection lost. Please try again.');
      es.close();
    };

    // Mark first step as running
    setStepStatus(prev => ({ ...prev, classifier: 'running' }));

    return () => es.close();
  }, [idea]);

  if (error) {
    return (
      <div style={{
        padding: '16px 20px', borderRadius: '10px',
        background: 'rgba(251,113,133,0.08)', border: '1px solid rgba(251,113,133,0.3)',
        color: '#fb7185', fontSize: '14px',
      }}>
        ⚠ {error}
      </div>
    );
  }

  return (
    <div style={{ width: '100%', maxWidth: '560px', margin: '0 auto' }}>
      <div style={{
        fontSize: '11px', fontWeight: '700', letterSpacing: '0.12em',
        textTransform: 'uppercase', color: '#4f6482',
        marginBottom: '24px', fontFamily: "'DM Mono', monospace",
      }}>
        Pipeline Running
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
        {AGENT_STEPS.map((step, i) => {
          const status = stepStatus[step.id] || 'pending';
          const isRunning  = status === 'running';
          const isComplete = status === 'complete';
          const isPending  = status === 'pending';

          return (
            <div key={step.id} style={{
              display:      'flex',
              alignItems:   'center',
              gap:          '14px',
              padding:      '12px 16px',
              borderRadius: '8px',
              background:   isRunning ? 'rgba(251,191,36,0.06)' : isComplete ? 'rgba(52,211,153,0.04)' : 'transparent',
              border:       `1px solid ${isRunning ? 'rgba(251,191,36,0.2)' : isComplete ? 'rgba(52,211,153,0.1)' : 'transparent'}`,
              transition:   'all 0.3s ease',
            }}>
              {/* Status dot */}
              <div style={{
                flexShrink: 0,
                width:  '28px', height: '28px',
                borderRadius: '50%',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: '12px',
                background: isComplete ? 'rgba(52,211,153,0.15)'
                           : isRunning  ? 'rgba(6,182,212,0.15)'
                           : '#1e293b',
              border: `1px solid ${isComplete ? 'rgba(52,211,153,0.4)' : isRunning ? 'rgba(6,182,212,0.4)' : '#334155'}`,
              color: isComplete ? '#34d399' : isRunning ? '#06b6d4' : '#4f6482',
                animation: isRunning ? 'pulse 1.5s ease-in-out infinite' : 'none',
              }}>
                {isComplete ? '✓' : isRunning ? '◉' : String(i + 1).padStart(2, '0')}
              </div>

              {/* Label & desc */}
              <div style={{ flex: 1 }}>
                <div style={{
                  fontSize:   '13px',
                  fontWeight: '600',
                  color:      isComplete ? '#94a3b8' : isRunning ? '#f8fafc' : '#4f6482',
                  fontFamily: "'DM Mono', monospace",
                  transition: 'color 0.3s',
                }}>
                  {step.label}
                </div>
                {isRunning && (
                  <div style={{ fontSize: '11px', color: '#06b6d4', marginTop: '1px' }}>
                    {step.desc}
                  </div>
                )}
              </div>

              {/* Duration */}
              {isComplete && durations[step.id] > 0 && (
                <div style={{
                  fontSize: '10px', color: '#4f6482',
                  fontFamily: "'DM Mono', monospace",
                }}>
                  {durations[step.id]}ms
                </div>
              )}

              {/* Running spinner bar */}
              {isRunning && (
                <div style={{
                  width: '40px', height: '3px',
                  borderRadius: '2px', background: '#1e293b', overflow: 'hidden',
                }}>
                  <div style={{
                    height: '100%', width: '40%',
                    background: '#06b6d4', borderRadius: '2px',
                    animation: 'slide 1s ease-in-out infinite alternate',
                  }} />
                </div>
              )}
            </div>
          );
        })}
      </div>

      {done && (
        <div style={{
          marginTop: '20px', padding: '12px 16px',
          borderRadius: '8px', background: 'rgba(52,211,153,0.08)',
          border: '1px solid rgba(52,211,153,0.2)',
          color: '#34d399', fontSize: '13px', textAlign: 'center',
          fontFamily: "'DM Mono', monospace",
        }}>
          ✓ Analysis complete — loading results...
        </div>
      )}

      <style>{`
        @keyframes pulse { 0%,100% { opacity:1 } 50% { opacity:0.4 } }
        @keyframes slide { from { transform: translateX(-100%) } to { transform: translateX(250%) } }
      `}</style>
    </div>
  );
}