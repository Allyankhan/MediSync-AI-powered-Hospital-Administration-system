import React, { useState, useRef, useEffect } from 'react';

function App() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([
    { role: 'assistant', content: '👋 Hello! I am your Hospital AI Assistant. Ask me to find records or schedule an appointment.' }
  ]);
  const [loading, setLoading] = useState(false);
  const [statusLog, setStatusLog] = useState(''); // Holds our cool streaming logs
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading, statusLog]);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    setStatusLog('📡 Connecting to neural cluster...');

    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: input,
          history: messages.slice(1),
        }),
      });

      // Set up a stream reader to capture chunk streams line-by-line
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let assistantReply = '';
      
      // Add an initial blank bubble for the incoming assistant text tokens
      setMessages((prev) => [...prev, { role: 'assistant', content: '' }]);

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              if (data.type === 'status') {
                setStatusLog(data.text); // Update the cool running status message
              } else if (data.type === 'token') {
                assistantReply += data.text;
                // Update the last message item inside our state array continuously
                setMessages((prev) => {
                  const updated = [...prev];
                  updated[updated.length - 1].content = assistantReply;
                  return updated;
                });
              } else if (data.type === 'error') {
                setStatusLog(`❌ ${data.text}`);
              }
            } catch (e) {
              // Handle potential partial JSON fragment boundaries gracefully
            }
          }
        }
      }
    } catch (error) {
      console.error("Streaming error:", error);
      setStatusLog('⚠️ Connection failed.');
    } finally {
      setLoading(false);
      setStatusLog(''); // Clear logs when finished generating
    }
  };

  return (
    <div style={styles.dashboardContainer}>
      {/* Sidebar Panel */}
      <div style={styles.sidebar}>
        <div style={styles.sidebarHeader}>
          <span style={styles.hospitalIcon}>🏥</span>
          <h2 style={styles.sidebarTitle}>MediSync Agent</h2>
        </div>
        <p style={styles.sidebarDesc}>LangGraph reactive core pipeline running with live streaming updates.</p>
        
        <div style={styles.capabilityList}>
          <div style={styles.capItem}>
            <span style={styles.capIcon}>📄</span>
            <div>
              <strong>Hospital RAG</strong>
              <div style={styles.capSub}>Semantic parsing over records</div>
            </div>
          </div>
          <div style={styles.capItem}>
            <span style={styles.capIcon}>🗄️</span>
            <div>
              <strong>Structured SQL</strong>
              <div style={styles.capSub}>Direct relational query schema</div>
            </div>
          </div>
        </div>

        <div style={styles.systemStatus}>
          <div style={styles.statusIndicator}></div>
          <span>Systems Nominal (Streaming SSE)</span>
        </div>
      </div>

      {/* Main Chat Interface */}
      <div style={styles.chatArea}>
        <div style={styles.chatHeader}>
          <div>
            <h3 style={styles.activeAgentTitle}>Hospital Intelligence Center</h3>
            <span style={styles.agentSub}>Active Framework: LangGraph Events v2</span>
          </div>
        </div>

        {/* Messages Stream */}
        <div style={styles.messagesContainer}>
          {messages.map((msg, index) => (
            // Hide blank bubbles if they happen to appear early
            (msg.content || msg.role === 'user') && (
              <div 
                key={index} 
                style={{
                  ...styles.messageRow,
                  justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start'
                }}
              >
                {msg.role !== 'user' && <div style={styles.assistantAvatar}>AI</div>}
                <div 
                  style={{
                    ...styles.messageBubble,
                    backgroundColor: msg.role === 'user' ? '#0284c7' : '#ffffff',
                    color: msg.role === 'user' ? '#ffffff' : '#334155',
                    borderRadius: msg.role === 'user' ? '16px 16px 2px 16px' : '16px 16px 16px 2px',
                    boxShadow: msg.role === 'user' ? '0 4px 12px rgba(2, 132, 199, 0.15)' : '0 4px 12px rgba(0,0,0,0.03)',
                  }}
                >
                  {msg.content}
                </div>
              </div>
            )
          ))}
          
          {/* Real-time Status Log Badge */}
          {statusLog && (
            <div style={styles.statusLogBadge}>
              <span style={styles.pulseDot}></span>
              {statusLog}
            </div>
          )}
          
          <div ref={chatEndRef} />
        </div>

        {/* Input Tray */}
        <form onSubmit={sendMessage} style={styles.inputForm}>
          <input 
            type="text" 
            value={input} 
            onChange={(e) => setInput(e.target.value)} 
            style={styles.chatInput} 
            placeholder="Ask a question about doctors, rooms, or book an appointment..."
            disabled={loading}
          />
          <button type="submit" style={styles.sendButton} disabled={loading || !input.trim()}>
            Send Stream
          </button>
        </form>
      </div>
    </div>
  );
}

const styles = {
  dashboardContainer: { display: 'flex', height: '100vh', width: '100vw', backgroundColor: '#f8fafc', overflow: 'hidden', fontFamily: '-apple-system, BlinkMacSystemFont, sans-serif' },
  sidebar: { width: '320px', backgroundColor: '#0f172a', color: '#94a3b8', padding: '24px', display: 'flex', flexDirection: 'column', borderRight: '1px solid #1e293b' },
  sidebarHeader: { display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' },
  hospitalIcon: { fontSize: '24px' },
  sidebarTitle: { color: '#f8fafc', margin: 0, fontSize: '20px', fontWeight: '600' },
  sidebarDesc: { fontSize: '13px', lineHeight: '1.5', margin: '0 0 32px 0', color: '#64748b' },
  capabilityList: { display: 'flex', flexDirection: 'column', gap: '20px', flexGrow: 1 },
  capItem: { display: 'flex', gap: '14px', alignItems: 'flex-start', fontSize: '14px' },
  capIcon: { fontSize: '18px', backgroundColor: '#1e293b', padding: '8px', borderRadius: '8px', color: '#38bdf8' },
  capSub: { fontSize: '12px', color: '#64748b', marginTop: '2px' },
  systemStatus: { display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: '#475569', borderTop: '1px solid #1e293b', paddingTop: '16px' },
  statusIndicator: { width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#10b981', boxShadow: '0 0 8px #10b981' },
  chatArea: { flexGrow: 1, display: 'flex', flexDirection: 'column', height: '100%' },
  chatHeader: { backgroundColor: '#ffffff', padding: '16px 32px', borderBottom: '1px solid #e2e8f0' },
  activeAgentTitle: { margin: 0, fontSize: '16px', fontWeight: '600', color: '#1e293b' },
  agentSub: { fontSize: '12px', color: '#94a3b8' },
  messagesContainer: { flexGrow: 1, padding: '32px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '20px', backgroundColor: '#f1f5f9' },
  messageRow: { display: 'flex', gap: '12px', maxWidth: '80%' },
  assistantAvatar: { width: '32px', height: '32px', borderRadius: '50%', backgroundColor: '#0f172a', color: '#38bdf8', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '11px', fontWeight: 'bold', flexShrink: 0 },
  messageBubble: { padding: '12px 18px', fontSize: '15px', lineHeight: '1.5', whiteSpace: 'pre-wrap' },
  statusLogBadge: { alignSelf: 'flex-start', display: 'inline-flex', alignItems: 'center', gap: '8px', backgroundColor: '#0f172a', color: '#38bdf8', padding: '8px 16px', borderRadius: '20px', fontSize: '13px', fontWeight: '500', boxShadow: '0 4px 12px rgba(0,0,0,0.1)', fontFamily: 'monospace', margin: '8px 0' },
  pulseDot: { width: '6px', height: '6px', backgroundColor: '#38bdf8', borderRadius: '50%', inlineSize: '6px' },
  inputForm: { backgroundColor: '#ffffff', padding: '20px 32px 32px 32px', borderTop: '1px solid #e2e8f0', display: 'flex', gap: '16px' },
  chatInput: { flexGrow: 1, padding: '14px 20px', borderRadius: '10px', border: '1px solid #ecf3f5', fontSize: '15px', outline: 'none', backgroundColor: '#040d16' },
  sendButton: { backgroundColor: '#0284c7', color: '#ffffff', border: 'none', padding: '0 24px', borderRadius: '10px', fontSize: '15px', fontWeight: '500', cursor: 'pointer' }
};

export default App;