import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Send, BarChart3, TrendingUp, DollarSign, Users, Sparkles, Clock } from 'lucide-react';
import './App.css';

const API_URL = 'http://127.0.0.1:8000';

function App() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [dataOverview, setDataOverview] = useState(null);
  const [conversationHistory, setConversationHistory] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDataOverview();
  }, []);

  const fetchDataOverview = async () => {
    try {
      const { data } = await axios.get(`${API_URL}/api/data-overview`);
      setDataOverview(data);
      setError(null);
    } catch (error) {
      console.error('Error fetching overview:', error);
      setError('Unable to connect to backend. Please ensure it is running on port 8000.');
    }
  };

  const handleQuery = async () => {
    if (!query.trim()) return;
    
    setLoading(true);
    setError(null);
    const userQuery = query;
    
    // Add user message to history
    const newHistory = [...conversationHistory, { 
      type: 'user', 
      text: userQuery,
      timestamp: new Date().toLocaleTimeString()
    }];
    setConversationHistory(newHistory);
    setQuery('');
    
    try {
      const { data } = await axios.post(`${API_URL}/api/query`, { query: userQuery });
      
      // Add agent response to history
      setConversationHistory([
        ...newHistory,
        { 
          type: 'agent', 
          text: data.response, 
          data: data.data_summary,
          timestamp: new Date().toLocaleTimeString()
        }
      ]);
      
      setResponse(data);
    } catch (error) {
      console.error('Error:', error);
      setConversationHistory([
        ...newHistory,
        { 
          type: 'error', 
          text: 'Error connecting to SAGE backend. Please ensure it is running on port 8000.',
          timestamp: new Date().toLocaleTimeString()
        }
      ]);
      setError('Query failed. Check backend connection.');
    } finally {
      setLoading(false);
    }
  };

  const exampleQueries = [
    "What are the top performing regions by revenue?",
    "Show me customer metrics",
    "Analyze sales trends over time",
    "Which region has the highest sales?",
    "Compare North and South regions"
  ];

  const handleExampleClick = (exampleQuery) => {
    setQuery(exampleQuery);
  };

  const clearConversation = () => {
    setConversationHistory([]);
    setResponse(null);
    setError(null);
  };

  return (
    <div className="App">
      <header className="header">
        <div className="header-content">
          <div className="header-left">
            <BarChart3 size={32} color="#667eea" />
            <div>
              <h1>SAGE - Specialty Agentic AI</h1>
              <p className="subtitle">
                <Sparkles size={14} style={{display: 'inline', marginRight: '4px'}} />
                Powered by Google ADK
              </p>
            </div>
          </div>
          {conversationHistory.length > 0 && (
            <button className="clear-button" onClick={clearConversation}>
              Clear Chat
            </button>
          )}
        </div>
      </header>

      <div className="container">
        {/* Error Banner */}
        {error && (
          <div className="error-banner">
            <strong>⚠️ Connection Error:</strong> {error}
          </div>
        )}

        {/* Overview Panel */}
        <div className="overview-panel">
          <h2>📊 Business Metrics Overview</h2>
          {dataOverview && dataOverview.summary ? (
            <div className="stats">
              <div className="stat-card">
                <div className="stat-icon dollar">
                  <DollarSign size={24} />
                </div>
                <div className="stat-content">
                  <span className="stat-label">Total Revenue</span>
                  <strong className="stat-value">
                    ${(dataOverview.summary.total_revenue || 0).toLocaleString()}
                  </strong>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-icon trending">
                  <TrendingUp size={24} />
                </div>
                <div className="stat-content">
                  <span className="stat-label">Total Sales</span>
                  <strong className="stat-value">
                    {(dataOverview.summary.total_sales || 0).toLocaleString()}
                  </strong>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-icon users">
                  <Users size={24} />
                </div>
                <div className="stat-content">
                  <span className="stat-label">Total Customers</span>
                  <strong className="stat-value">
                    {(dataOverview.summary.total_customers || 0).toLocaleString()}
                  </strong>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-icon chart">
                  <BarChart3 size={24} />
                </div>
                <div className="stat-content">
                  <span className="stat-label">Active Regions</span>
                  <strong className="stat-value">
                    {(dataOverview.summary.regions || []).length}
                  </strong>
                  <span className="stat-sublabel">
                    {(dataOverview.summary.regions || []).join(', ')}
                  </span>
                </div>
              </div>
            </div>
          ) : (
            <div className="loading-overview">
              <div className="loading-spinner"></div>
              <span>Loading data...</span>
            </div>
          )}
        </div>

        {/* Query Panel */}
        <div className="query-panel">
          <h2>💬 Ask SAGE Anything</h2>
          
          {/* Example Queries */}
          {conversationHistory.length === 0 && (
            <div className="examples">
              <p className="examples-label">✨ Try these examples:</p>
              <div className="example-chips">
                {exampleQueries.map((example, i) => (
                  <button 
                    key={i} 
                    className="example-chip"
                    onClick={() => handleExampleClick(example)}
                  >
                    {example}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Conversation History */}
          {conversationHistory.length > 0 && (
            <div className="conversation">
              {conversationHistory.map((msg, i) => (
                <div key={i} className={`message ${msg.type}`}>
                  <div className="message-header">
                    {msg.type === 'user' && <strong>👤 You</strong>}
                    {msg.type === 'agent' && <strong>🤖 SAGE</strong>}
                    {msg.type === 'error' && <strong>⚠️ Error</strong>}
                    <span className="message-time">
                      <Clock size={12} /> {msg.timestamp}
                    </span>
                  </div>
                  <div className="message-content">
                    <p>{msg.text}</p>
                  </div>
                </div>
              ))}
              {loading && (
                <div className="message agent loading-message">
                  <div className="message-header">
                    <strong>🤖 SAGE</strong>
                  </div>
                  <div className="message-content">
                    <div className="typing-indicator">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                    <p className="thinking-text">Analyzing your data...</p>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Input */}
          <div className="input-container">
            <div className="input-group">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask about sales, revenue, customers, or trends..."
                onKeyPress={(e) => e.key === 'Enter' && !loading && handleQuery()}
                disabled={loading}
              />
              <button 
                onClick={handleQuery} 
                disabled={loading || !query.trim()}
                className="send-button"
              >
                {loading ? (
                  <div className="button-spinner"></div>
                ) : (
                  <Send size={20} />
                )}
              </button>
            </div>
            <p className="input-hint">
              💡 Tip: Ask specific questions about regions, metrics, or trends
            </p>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="footer">
        <p>Built with Google Agent Development Kit (ADK) • FastAPI • React</p>
      </footer>
    </div>
  );
}

export default App;