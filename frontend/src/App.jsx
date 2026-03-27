import { useState, useEffect } from 'react';
import { MdAddCircle, MdCompareArrows, MdClose, MdMenu, MdDeleteOutline } from 'react-icons/md';
import IdeaInput      from './components/IdeaInput';
import AgentProgress  from './components/AgentProgress';
import ResultCard     from './components/ResultCard';
import ComparisonView from './components/ComparisonView';
import IdeaTypeBadge  from './components/IdeaTypeBadge';

function App() {
  const [view,        setView]        = useState('input');
  const [currentIdea, setCurrentIdea] = useState('');
  const [currentResult, setCurrentResult] = useState(null);
  const [pastResults, setPastResults] = useState([]);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);

  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 768);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  useEffect(() => {
    try {
      const saved = localStorage.getItem('iv_results');
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length > 0) {
          setPastResults(parsed);
          console.log(`✓ Loaded ${parsed.length} past results from storage`);
        }
      }
    } catch (err) {
      console.error('Failed to load past results:', err);
    }
  }, []);

  useEffect(() => {
    try {
      if (pastResults.length > 0) {
        localStorage.setItem('iv_results', JSON.stringify(pastResults));
        console.log(`✓ Saved ${pastResults.length} results to storage`);
      }
    } catch (err) {
      console.error('Failed to save past results:', err);
      if (err.name === 'QuotaExceededError') {
        alert('Storage limit exceeded. Some old results may be lost.');
        // Keep only last 10 results if quota exceeded
        const limited = pastResults.slice(0, 10);
        localStorage.setItem('iv_results', JSON.stringify(limited));
      }
    }
  }, [pastResults]);

  const handleSubmit = (idea) => {
    setCurrentIdea(idea);
    setView('progress');
    setSidebarOpen(false);
  };

  const handleComplete = (result) => {
    setCurrentResult(result);
    setPastResults(prev => [result, ...prev]);
    setView('result');
    setSidebarOpen(false);
  };

  const handleNew = () => {
    setCurrentIdea('');
    setCurrentResult(null);
    setView('input');
    setSidebarOpen(false);
  };

  const verdictColor = (v) =>
    v === 'GO' ? '#34d399' : v === 'MAYBE' ? '#06b6d4' : '#fb7185';

  return (
    <div style={{
      minHeight:   '100vh',
      display:     'flex',
      background:  'linear-gradient(135deg, #000000 0%, #0d1b3d 50%, #1a2f5a 100%)',
      color:       '#e2e8f0',
      fontFamily:  "system-ui, -apple-system, sans-serif",
      flexDirection: isMobile ? 'column' : 'row',
    }}>
      {/* Google Fonts & Responsive Styles */}
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Inter:wght@700;800;900&display=swap');
        * { box-sizing: border-box; }
        body { word-wrap: break-word; overflow-wrap: break-word; }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 2px; }
        select option { background: #1e293b; }
        
        @media (max-width: 768px) {
          body { font-size: 14px; }
          * { word-break: break-word; }
        }
        
        @media (max-width: 480px) {
          body { font-size: 13px; }
        }
      `}</style>

      {/* Mobile Menu Toggle */}
      {isMobile && (
        <button 
          onClick={() => setSidebarOpen(!sidebarOpen)}
          style={{
            position: 'fixed',
            top: '16px',
            right: '16px',
            zIndex: 1000,
            background: '#0f172a',
            border: '1px solid #1e293b',
            borderRadius: '6px',
            color: '#06b6d4',
            padding: '8px 12px',
            cursor: 'pointer',
            fontSize: '20px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          {sidebarOpen ? <MdClose size={20} /> : <MdMenu size={20} />}
        </button>
      )}

      {/* Sidebar Overlay for Mobile */}
      {isMobile && sidebarOpen && (
        <div 
          onClick={() => setSidebarOpen(false)}
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0,0,0,0.6)',
            zIndex: 998,
          }}
        />
      )}

      {/* Sidebar */}
      <aside style={{
        width:      isMobile ? '75vw' : '260px',
        maxHeight:  isMobile ? '100vh' : '100vh',
        flexShrink: 0,
        background: isMobile ? '#0a0f1a' : 'transparent',
        borderRight: '1px solid #1e293b',
        borderBottom: 'none',
        padding:    isMobile ? '60px 20px 20px' : '28px 20px',
        display:    isMobile && !sidebarOpen ? 'none' : 'flex',
        flexDirection: 'column',
        gap:        '0px',
        overflowY:  'visible',
        maxWidth:   isMobile ? '75vw' : '260px',
        position:   isMobile && sidebarOpen ? 'fixed' : 'sticky',
        top:        isMobile && sidebarOpen ? '0' : '0',
        left:       isMobile && sidebarOpen ? '0' : 'auto',
        zIndex:     isMobile && sidebarOpen ? 999 : 'auto',
        height:     isMobile && sidebarOpen ? '100vh' : 'auto',
      }}>
        {/* Logo */}
        <div style={{ paddingBottom: '12px' }}>
          <div style={{
            fontSize:   '33px',
            fontWeight: '800',
            color:      '#f8fafc',
            fontFamily: "'Inter', sans-serif",
            letterSpacing: '-0.02em',
          }}>
            idea<span style={{ color: '#06b6d4' }}>Validator</span>
          </div>
          <div style={{
            fontSize:   '13px',
            color:      '#ffffff',
            marginTop:  '2px',
            letterSpacing: '0.1em',
            textTransform: 'uppercase',
            fontFamily: "'DM Mono', monospace",
          }}>
            AI-Powered Analysis
          </div>
        </div>

        {/* Nav */}
        <nav style={{ display: 'flex', flexDirection: 'column', gap: '4px', paddingTop: '12px', paddingBottom: '28px' }}>
          {[
            { id: 'input',      icon: <MdAddCircle />, label: 'New Validation' },
            { id: 'compare', icon: <MdCompareArrows />, label: 'Compare Ideas' },
          ].map(item => (
            <button key={item.id} onClick={() => setView(item.id)} style={{
              padding:    '9px 12px',
              borderRadius:'7px',
              background: view === item.id || item.id === 'input' ? 'rgba(6,182,212,0.1)' : 'transparent',
              border:     `1px solid ${view === item.id || item.id === 'input' ? 'rgba(6,182,212,0.2)' : 'transparent'}`,
              color:      view === item.id || item.id === 'input' ? '#06b6d4' : '#4f6482',
              fontSize:   '13px',
              fontWeight: '600',
              cursor:     'pointer',
              textAlign:  'left',
              display:    'flex',
              gap:        '8px',
              alignItems: 'center',
              transition: 'all 0.15s',
              fontFamily: "'DM Mono', monospace",
            }}>
              <span style={{ display: 'flex', color: view === item.id || item.id === 'input' ? '#06b6d4' : '#4f6482' }}>{item.icon}</span>
              {item.label}
            </button>
          ))}
        </nav>

        {/* Past results */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', marginTop: '28px', marginBottom: '28px', paddingBottom: '28px', minHeight: '0' }}>
          <div style={{
            fontSize:   '10px',
            fontWeight: '700',
            letterSpacing: '0.1em',
            textTransform: 'uppercase',
            color:      '#ffffff',
            marginBottom:'12px',
            fontFamily: "'DM Mono', monospace",
          }}>
            History ({pastResults.length})
          </div>

          {pastResults.length === 0 ? (
            <p style={{ fontSize: '10px', color: '#ffffff', fontStyle: 'italic' }}>
              No validations yet.
            </p>
          ) : (
            <div style={{ overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '4px', flex: 1 }}>
              {pastResults.map((r, i) => (
                <button key={i} onClick={() => { setCurrentResult(r); setView('result'); }} style={{
                  padding:    '10px 10px',
                  borderRadius:'7px',
                  background: currentResult === r ? '#0f172a' : 'transparent',
                  border:     `1px solid ${currentResult === r ? '#1e293b' : 'transparent'}`,
                  cursor:     'pointer',
                  textAlign:  'left',
                  transition: 'all 0.15s',
                }}
                  onMouseEnter={e => { if (currentResult !== r) e.currentTarget.style.background = '#0a1628'; }}
                  onMouseLeave={e => { if (currentResult !== r) e.currentTarget.style.background = 'transparent'; }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
                    <span style={{
                      width: '8px', height: '8px', borderRadius: '50%',
                      background: verdictColor(r.verdict), flexShrink: 0,
                    }} />
                    <span style={{
                      fontSize: '12px', fontWeight: '700',
                      color: verdictColor(r.verdict),
                      fontFamily: "'DM Mono', monospace",
                    }}>
                      {(r.overall_score ?? 0).toFixed(1)}
                    </span>
                    <span style={{ fontSize: '10px', color: '#4f6482', marginLeft: 'auto', fontFamily: "'DM Mono', monospace" }}>
                      {r.verdict}
                    </span>
                  </div>
                  <p style={{
                    fontSize: '11px', color: '#a5b4fc',
                    overflow: 'hidden', textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap', margin: 0,
                  }}>
                    {r.idea?.slice(0, 38)}...
                  </p>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Clear history */}
        {pastResults.length > 0 && (
          <button onClick={() => { setPastResults([]); handleNew(); }} style={{
            padding:    '7px 12px',
            marginTop:  '12px',
            borderRadius:'6px',
            background: 'transparent',
            border:     '1px solid #1e293b',
            color:      '#4f6482',
            fontSize:   '11px',
            cursor:     'pointer',
            fontFamily: "'DM Mono', monospace",
            letterSpacing: '0.06em',
            transition: 'all 0.15s',
            display:    'flex',
            gap:        '6px',
            alignItems: 'center',
          }}
            onMouseEnter={e => { e.target.style.borderColor = '#06b6d4'; e.target.style.color = '#06b6d4'; }}
            onMouseLeave={e => { e.target.style.borderColor = '#1e293b'; e.target.style.color = '#4f6482'; }}
          >
            <MdDeleteOutline size={14} /> Clear History
          </button>
        )}
      </aside>

      {/* Main */}
      <main style={{
        flex:       1,
        padding:    '40px 32px',
        overflowY:  'auto',
        width:      '100%',
        display:    'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'flex-start',
        boxSizing:  'border-box',
      }}>
        <div style={{ width: '100%', maxWidth: '800px', boxSizing: 'border-box' }}>

        {view === 'input' && (
          <div style={{ width: '100%' }}>
            <h1 style={{
              fontSize:      '32px',
              fontWeight:    '800',
              fontFamily:    "'Inter', sans-serif",
              color:         '#f8fafc',
              margin:        '0 0 6px',
              letterSpacing: '-0.03em',
              wordBreak:     'break-word',
              maxWidth:      '100%',
            }}>
              Validate Your <span style={{ color: '#06b6d4' }}>Idea</span>
            </h1>
            <p style={{ color: '#ffffff', fontSize: '14px', marginBottom: '32px', lineHeight: '1.6', margin: '0 0 32px 0' }}>
              Describe your idea and our AI pipeline will analyze demand, competition, and risk in parallel.
            </p>
            <IdeaInput onSubmit={handleSubmit} />
          </div>
        )}

        {view === 'progress' && (
          <div style={{ width: '100%' }}>
            <h1 style={{
              fontSize:      '28px',
              fontWeight:    '800',
              fontFamily:    "'Inter', sans-serif",
              color:         '#f8fafc',
              margin:        '0 0 12px',
              letterSpacing: '-0.03em',
              wordBreak:     'break-word',
              maxWidth:      '100%',
            }}>
              Analyzing...
            </h1>
            <p style={{ color: '#a5b4fc', fontSize: '13px', marginBottom: '32px', fontFamily: "'DM Mono', monospace", wordBreak: 'break-word', whiteSpace: 'normal', lineHeight: '1.5', margin: '0 0 32px 0' }}>
              "{currentIdea.slice(0, 70)}{currentIdea.length > 70 ? '...' : ''}"
            </p>
            <AgentProgress idea={currentIdea} onComplete={handleComplete} />
          </div>
        )}

        {view === 'result' && currentResult && (
          <div>
            <h1 style={{
              fontSize:      '28px',
              fontWeight:    '800',
              fontFamily:    "'Inter', sans-serif",
              color:         '#f8fafc',
              margin:        '0 0 28px',
              letterSpacing: '-0.03em',
              wordBreak:     'break-word',
              maxWidth:      '100%',
            }}>
              Results
            </h1>
            <ResultCard result={currentResult} />
          </div>
        )}

        {view === 'compare' && (
          <div>
            <ComparisonView results={pastResults} />
          </div>
        )}
        </div>
      </main>
    </div>
  );
}

export default App;