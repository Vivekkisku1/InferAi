import { useState, useEffect, useCallback } from 'react'

const API_BASE = 'http://localhost:8000'
const ACCENT = '#38bdf8'
const BG = '#0a0f1e'
const PANEL = '#111827'
const BORDER = '#1e293b'
const MUTED = '#94a3b8'
const TEXT = '#e2e8f0'

const MODELS = [
  { id: 'llama3-8b-8192', label: 'Llama 3 8B' },
  { id: 'llama3-70b-8192', label: 'Llama 3 70B' },
  { id: 'mixtral-8x7b-32768', label: 'Mixtral 8x7B' },
]

const styles = {
  page: {
    minHeight: '100vh',
    background: BG,
    color: TEXT,
    fontFamily: 'system-ui, -apple-system, Segoe UI, Roboto, sans-serif',
    margin: 0,
  },
  authWrap: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
  },
  authCard: {
    width: '100%',
    maxWidth: 420,
    background: PANEL,
    border: `1px solid ${BORDER}`,
    borderRadius: 16,
    padding: 32,
    boxShadow: '0 25px 50px rgba(0,0,0,0.4)',
  },
  logo: {
    fontSize: 28,
    fontWeight: 700,
    marginBottom: 8,
    background: `linear-gradient(135deg, ${ACCENT}, #818cf8)`,
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
  },
  subtitle: { color: MUTED, marginBottom: 24, fontSize: 14 },
  label: { display: 'block', fontSize: 13, color: MUTED, marginBottom: 6 },
  input: {
    width: '100%',
    boxSizing: 'border-box',
    padding: '10px 12px',
    marginBottom: 16,
    background: BG,
    border: `1px solid ${BORDER}`,
    borderRadius: 8,
    color: TEXT,
    fontSize: 14,
    outline: 'none',
  },
  btn: {
    width: '100%',
    padding: '12px 16px',
    background: ACCENT,
    color: BG,
    border: 'none',
    borderRadius: 8,
    fontWeight: 600,
    fontSize: 14,
    cursor: 'pointer',
  },
  btnGhost: {
    padding: '8px 14px',
    background: 'transparent',
    color: MUTED,
    border: `1px solid ${BORDER}`,
    borderRadius: 8,
    cursor: 'pointer',
    fontSize: 13,
  },
  btnDanger: {
    padding: '6px 12px',
    background: 'transparent',
    color: '#f87171',
    border: '1px solid #7f1d1d',
    borderRadius: 6,
    cursor: 'pointer',
    fontSize: 12,
  },
  link: {
    background: 'none',
    border: 'none',
    color: ACCENT,
    cursor: 'pointer',
    fontSize: 13,
    textDecoration: 'underline',
  },
  error: {
    background: 'rgba(248,113,113,0.1)',
    border: '1px solid #7f1d1d',
    color: '#fca5a5',
    padding: '10px 12px',
    borderRadius: 8,
    marginBottom: 16,
    fontSize: 13,
  },
  layout: { display: 'flex', minHeight: '100vh' },
  sidebar: {
    width: 220,
    background: PANEL,
    borderRight: `1px solid ${BORDER}`,
    padding: 24,
    display: 'flex',
    flexDirection: 'column',
  },
  navItem: (active) => ({
    display: 'block',
    width: '100%',
    textAlign: 'left',
    padding: '10px 14px',
    marginBottom: 6,
    background: active ? 'rgba(56,189,248,0.15)' : 'transparent',
    color: active ? ACCENT : MUTED,
    border: active ? `1px solid ${ACCENT}` : '1px solid transparent',
    borderRadius: 8,
    cursor: 'pointer',
    fontSize: 14,
    fontWeight: active ? 600 : 400,
  }),
  main: { flex: 1, padding: 32, overflow: 'auto' },
  heading: { fontSize: 22, fontWeight: 600, marginBottom: 24, marginTop: 0 },
  cardGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: 16,
    marginBottom: 32,
  },
  statCard: {
    background: PANEL,
    border: `1px solid ${BORDER}`,
    borderRadius: 12,
    padding: 20,
  },
  statValue: { fontSize: 32, fontWeight: 700, color: ACCENT, marginTop: 8 },
  statLabel: { fontSize: 13, color: MUTED },
  panel: {
    background: PANEL,
    border: `1px solid ${BORDER}`,
    borderRadius: 12,
    padding: 20,
  },
  row: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '12px 0',
    borderBottom: `1px solid ${BORDER}`,
  },
  chatBox: {
    height: 360,
    overflowY: 'auto',
    marginBottom: 16,
    padding: 12,
    background: BG,
    borderRadius: 8,
    border: `1px solid ${BORDER}`,
  },
  msgUser: {
    textAlign: 'right',
    marginBottom: 12,
  },
  msgAssistant: {
    textAlign: 'left',
    marginBottom: 12,
  },
  bubbleUser: {
    display: 'inline-block',
    maxWidth: '85%',
    padding: '10px 14px',
    background: 'rgba(56,189,248,0.2)',
    border: `1px solid ${ACCENT}`,
    borderRadius: '12px 12px 4px 12px',
    fontSize: 14,
    textAlign: 'left',
  },
  bubbleAssistant: {
    display: 'inline-block',
    maxWidth: '85%',
    padding: '10px 14px',
    background: PANEL,
    border: `1px solid ${BORDER}`,
    borderRadius: '12px 12px 12px 4px',
    fontSize: 14,
    textAlign: 'left',
  },
}

function loadStoredKeys() {
  try {
    return JSON.parse(sessionStorage.getItem('inferai_raw_keys') || '{}')
  } catch {
    return {}
  }
}

function saveStoredKey(id, key) {
  const map = loadStoredKeys()
  map[id] = key
  sessionStorage.setItem('inferai_raw_keys', JSON.stringify(map))
}

function App() {
  const [token, setToken] = useState(() => localStorage.getItem('inferai_token') || '')
  const [email, setEmail] = useState(() => localStorage.getItem('inferai_email') || '')
  const [authMode, setAuthMode] = useState('login')
  const [authEmail, setAuthEmail] = useState('')
  const [authPassword, setAuthPassword] = useState('')
  const [authError, setAuthError] = useState('')
  const [authLoading, setAuthLoading] = useState(false)

  const [activeTab, setActiveTab] = useState('overview')
  const [apiKeys, setApiKeys] = useState([])
  const [usageItems, setUsageItems] = useState([])
  const [loading, setLoading] = useState(false)
  const [actionError, setActionError] = useState('')

  const [newKeyName, setNewKeyName] = useState('')
  const [createdKeyReveal, setCreatedKeyReveal] = useState(null)

  const [playgroundModel, setPlaygroundModel] = useState(MODELS[0].id)
  const [playgroundKeyId, setPlaygroundKeyId] = useState('')
  const [playgroundKeyManual, setPlaygroundKeyManual] = useState('')
  const [chatInput, setChatInput] = useState('')
  const [messages, setMessages] = useState([])
  const [chatLoading, setChatLoading] = useState(false)

  const logout = () => {
    localStorage.removeItem('inferai_token')
    localStorage.removeItem('inferai_email')
    setToken('')
    setEmail('')
    setApiKeys([])
    setUsageItems([])
    setMessages([])
  }

  const authHeaders = useCallback(
    () => ({
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    }),
    [token]
  )

  const fetchApiKeys = useCallback(async () => {
    if (!token) return
    const res = await fetch(`${API_BASE}/api-keys`, { headers: authHeaders() })
    if (!res.ok) throw new Error('Failed to load API keys')
    const data = await res.json()
    setApiKeys(data)
    if (data.length && !playgroundKeyId) {
      setPlaygroundKeyId(String(data[0].id))
    }
  }, [token, authHeaders, playgroundKeyId])

  const fetchUsage = useCallback(async () => {
    if (!token) return
    const res = await fetch(`${API_BASE}/usage?limit=100`, { headers: authHeaders() })
    if (!res.ok) throw new Error('Failed to load usage')
    const data = await res.json()
    setUsageItems(data.items || [])
  }, [token, authHeaders])

  const refreshDashboard = useCallback(async () => {
    setLoading(true)
    setActionError('')
    try {
      await Promise.all([fetchApiKeys(), fetchUsage()])
    } catch (e) {
      setActionError(e.message)
    } finally {
      setLoading(false)
    }
  }, [fetchApiKeys, fetchUsage])

  useEffect(() => {
    if (token) refreshDashboard()
  }, [token, refreshDashboard])

  const handleAuth = async (e) => {
    e.preventDefault()
    setAuthError('')
    setAuthLoading(true)
    const path = authMode === 'login' ? '/auth/login' : '/auth/register'
    try {
      const res = await fetch(`${API_BASE}${path}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: authEmail, password: authPassword }),
      })
      const data = await res.json().catch(() => ({}))
      if (!res.ok) {
        const detail = data.detail
        const msg = Array.isArray(detail)
          ? detail.map((d) => d.msg || JSON.stringify(d)).join(', ')
          : detail || data.message || 'Authentication failed'
        throw new Error(typeof msg === 'string' ? msg : 'Authentication failed')
      }
      const accessToken = data.access_token
      if (!accessToken) throw new Error('No access token returned')
      localStorage.setItem('inferai_token', accessToken)
      localStorage.setItem('inferai_email', authEmail)
      setToken(accessToken)
      setEmail(authEmail)
      setAuthPassword('')
    } catch (err) {
      setAuthError(err.message)
    } finally {
      setAuthLoading(false)
    }
  }

  const handleCreateKey = async () => {
    if (!newKeyName.trim()) return
    setActionError('')
    try {
      const res = await fetch(`${API_BASE}/api-keys`, {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify({ name: newKeyName.trim() }),
      })
      const data = await res.json().catch(() => ({}))
      if (!res.ok) throw new Error(data.detail || 'Failed to create key')
      saveStoredKey(String(data.id), data.key)
      setCreatedKeyReveal(data.key)
      setNewKeyName('')
      setPlaygroundKeyId(String(data.id))
      setPlaygroundKeyManual(data.key)
      await fetchApiKeys()
    } catch (e) {
      setActionError(e.message)
    }
  }

  const handleDeleteKey = async (keyId) => {
    setActionError('')
    try {
      const res = await fetch(`${API_BASE}/api-keys/${keyId}`, {
        method: 'DELETE',
        headers: authHeaders(),
      })
      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data.detail || 'Failed to delete key')
      }
      await fetchApiKeys()
    } catch (e) {
      setActionError(e.message)
    }
  }

  const getPlaygroundApiKey = () => {
    const stored = loadStoredKeys()
    if (playgroundKeyId && stored[playgroundKeyId]) return stored[playgroundKeyId]
    return playgroundKeyManual.trim()
  }

  const handleSendChat = async () => {
    const content = chatInput.trim()
    if (!content) return
    const apiKey = getPlaygroundApiKey()
    if (!apiKey) {
      setActionError('Select an API key or paste one (raw key shown only once at creation)')
      return
    }

    const userMsg = { role: 'user', content }
    const nextMessages = [...messages, userMsg]
    setMessages(nextMessages)
    setChatInput('')
    setChatLoading(true)
    setActionError('')

    try {
      const res = await fetch(`${API_BASE}/v1/chat/completions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': apiKey,
        },
        body: JSON.stringify({
          model: playgroundModel,
          messages: nextMessages,
          max_tokens: 1024,
          temperature: 0.7,
        }),
      })
      const data = await res.json().catch(() => ({}))
      if (!res.ok) {
        const detail = data.detail || data.error || 'Inference failed'
        throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail))
      }
      const assistantContent =
        data.choices?.[0]?.message?.content || JSON.stringify(data, null, 2)
      setMessages([...nextMessages, { role: 'assistant', content: assistantContent }])
      fetchUsage()
    } catch (e) {
      setActionError(e.message)
      setMessages(nextMessages)
    } finally {
      setChatLoading(false)
    }
  }

  const totalTokens = usageItems.reduce(
    (sum, log) => sum + (log.input_tokens || 0) + (log.output_tokens || 0),
    0
  )

  if (!token) {
    return (
      <div style={styles.page}>
        <div style={styles.authWrap}>
          <div style={styles.authCard}>
            <div style={styles.logo}>InferAI</div>
            <p style={styles.subtitle}>Developer dashboard for your inference API</p>
            {authError ? <div style={styles.error}>{authError}</div> : null}
            <form onSubmit={handleAuth}>
              <label style={styles.label}>Email</label>
              <input
                style={styles.input}
                type="email"
                value={authEmail}
                onChange={(e) => setAuthEmail(e.target.value)}
                placeholder="you@company.com"
                required
              />
              <label style={styles.label}>Password</label>
              <input
                style={styles.input}
                type="password"
                value={authPassword}
                onChange={(e) => setAuthPassword(e.target.value)}
                placeholder="••••••••"
                required
              />
              <button type="submit" style={styles.btn} disabled={authLoading}>
                {authLoading ? 'Please wait…' : authMode === 'login' ? 'Sign in' : 'Create account'}
              </button>
            </form>
            <p style={{ marginTop: 20, fontSize: 13, color: MUTED, textAlign: 'center' }}>
              {authMode === 'login' ? 'No account? ' : 'Already registered? '}
              <button
                type="button"
                style={styles.link}
                onClick={() => {
                  setAuthMode(authMode === 'login' ? 'register' : 'login')
                  setAuthError('')
                }}
              >
                {authMode === 'login' ? 'Register' : 'Sign in'}
              </button>
            </p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div style={styles.page}>
      <div style={styles.layout}>
        <aside style={styles.sidebar}>
          <div style={styles.logo}>InferAI</div>
          <p style={{ ...styles.subtitle, marginBottom: 32 }}>{email}</p>
          {['overview', 'keys', 'playground'].map((tab) => (
            <button
              key={tab}
              type="button"
              style={styles.navItem(activeTab === tab)}
              onClick={() => setActiveTab(tab)}
            >
              {tab === 'overview' ? 'Overview' : tab === 'keys' ? 'API Keys' : 'Playground'}
            </button>
          ))}
          <div style={{ flex: 1 }} />
          <button type="button" style={styles.btnGhost} onClick={logout}>
            Sign out
          </button>
        </aside>

        <main style={styles.main}>
          {actionError ? <div style={styles.error}>{actionError}</div> : null}
          {loading && activeTab === 'overview' ? (
            <p style={{ color: MUTED }}>Loading…</p>
          ) : null}

          {activeTab === 'overview' && (
            <>
              <h1 style={styles.heading}>Overview</h1>
              <div style={styles.cardGrid}>
                <div style={styles.statCard}>
                  <div style={styles.statLabel}>API Keys</div>
                  <div style={styles.statValue}>{apiKeys.length}</div>
                </div>
                <div style={styles.statCard}>
                  <div style={styles.statLabel}>Total Requests</div>
                  <div style={styles.statValue}>{usageItems.length}</div>
                </div>
                <div style={styles.statCard}>
                  <div style={styles.statLabel}>Tokens Used</div>
                  <div style={styles.statValue}>{totalTokens.toLocaleString()}</div>
                </div>
              </div>
              <div style={styles.panel}>
                <h3 style={{ marginTop: 0, fontSize: 16 }}>Recent activity</h3>
                {usageItems.length === 0 ? (
                  <p style={{ color: MUTED, fontSize: 14 }}>No requests yet. Try the Playground.</p>
                ) : (
                  usageItems.slice(0, 5).map((log) => (
                    <div key={log.id} style={styles.row}>
                      <span style={{ fontSize: 14 }}>{log.model_id}</span>
                      <span style={{ fontSize: 13, color: MUTED }}>
                        {(log.input_tokens || 0) + (log.output_tokens || 0)} tokens · {log.status}
                      </span>
                    </div>
                  ))
                )}
              </div>
            </>
          )}

          {activeTab === 'keys' && (
            <>
              <h1 style={styles.heading}>API Keys</h1>
              <div style={{ ...styles.panel, marginBottom: 24 }}>
                <h3 style={{ marginTop: 0, fontSize: 15 }}>Create new key</h3>
                <div style={{ display: 'flex', gap: 12 }}>
                  <input
                    style={{ ...styles.input, marginBottom: 0, flex: 1 }}
                    placeholder="Key name (e.g. production)"
                    value={newKeyName}
                    onChange={(e) => setNewKeyName(e.target.value)}
                  />
                  <button
                    type="button"
                    style={{ ...styles.btn, width: 'auto', padding: '10px 20px' }}
                    onClick={handleCreateKey}
                  >
                    Create
                  </button>
                </div>
                {createdKeyReveal ? (
                  <div
                    style={{
                      marginTop: 16,
                      padding: 12,
                      background: 'rgba(56,189,248,0.1)',
                      border: `1px solid ${ACCENT}`,
                      borderRadius: 8,
                      fontSize: 13,
                      wordBreak: 'break-all',
                    }}
                  >
                    <strong style={{ color: ACCENT }}>Copy now — shown once:</strong>
                    <br />
                    {createdKeyReveal}
                  </div>
                ) : null}
              </div>
              <div style={styles.panel}>
                <h3 style={{ marginTop: 0, fontSize: 15 }}>Your keys</h3>
                {apiKeys.length === 0 ? (
                  <p style={{ color: MUTED }}>No API keys yet.</p>
                ) : (
                  apiKeys.map((k) => (
                    <div key={k.id} style={styles.row}>
                      <div>
                        <div style={{ fontWeight: 500 }}>{k.name}</div>
                        <div style={{ fontSize: 12, color: MUTED }}>
                          {String(k.id).slice(0, 8)}… ·{' '}
                          {k.is_active ? 'active' : 'inactive'}
                        </div>
                      </div>
                      <button
                        type="button"
                        style={styles.btnDanger}
                        onClick={() => handleDeleteKey(k.id)}
                      >
                        Delete
                      </button>
                    </div>
                  ))
                )}
              </div>
            </>
          )}

          {activeTab === 'playground' && (
            <>
              <h1 style={styles.heading}>Playground</h1>
              <div style={{ ...styles.panel, marginBottom: 16 }}>
                <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', marginBottom: 12 }}>
                  <div style={{ flex: 1, minWidth: 180 }}>
                    <label style={styles.label}>Model</label>
                    <select
                      style={styles.input}
                      value={playgroundModel}
                      onChange={(e) => setPlaygroundModel(e.target.value)}
                    >
                      {MODELS.map((m) => (
                        <option key={m.id} value={m.id}>
                          {m.label}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div style={{ flex: 1, minWidth: 180 }}>
                    <label style={styles.label}>API Key (session)</label>
                    <select
                      style={styles.input}
                      value={playgroundKeyId}
                      onChange={(e) => {
                        setPlaygroundKeyId(e.target.value)
                        const stored = loadStoredKeys()
                        setPlaygroundKeyManual(stored[e.target.value] || '')
                      }}
                    >
                      <option value="">— Select key —</option>
                      {apiKeys.map((k) => (
                        <option key={k.id} value={String(k.id)}>
                          {k.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
                <label style={styles.label}>X-API-Key (paste if not created this session)</label>
                <input
                  style={{ ...styles.input, marginBottom: 0 }}
                  type="password"
                  placeholder="sk-…"
                  value={playgroundKeyManual}
                  onChange={(e) => setPlaygroundKeyManual(e.target.value)}
                />
              </div>
              <div style={styles.panel}>
                <div style={styles.chatBox}>
                  {messages.length === 0 ? (
                    <p style={{ color: MUTED, fontSize: 14 }}>Send a message to test your API.</p>
                  ) : (
                    messages.map((msg, i) => (
                      <div
                        key={i}
                        style={msg.role === 'user' ? styles.msgUser : styles.msgAssistant}
                      >
                        <span
                          style={
                            msg.role === 'user' ? styles.bubbleUser : styles.bubbleAssistant
                          }
                        >
                          {msg.content}
                        </span>
                      </div>
                    ))
                  )}
                </div>
                <div style={{ display: 'flex', gap: 12 }}>
                  <input
                    style={{ ...styles.input, marginBottom: 0, flex: 1 }}
                    placeholder="Type your message…"
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault()
                        handleSendChat()
                      }
                    }}
                    disabled={chatLoading}
                  />
                  <button
                    type="button"
                    style={{ ...styles.btn, width: 'auto', padding: '10px 24px' }}
                    onClick={handleSendChat}
                    disabled={chatLoading}
                  >
                    {chatLoading ? '…' : 'Send'}
                  </button>
                </div>
              </div>
            </>
          )}
        </main>
      </div>
    </div>
  )
}

export default App
