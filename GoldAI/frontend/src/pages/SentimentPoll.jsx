import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { TrendingUp, TrendingDown, Brain, Users, Info } from 'lucide-react';
import './SentimentPoll.css';

const SentimentPoll = () => {
  const [pollData, setPollData] = useState({ bullish: 0, bearish: 0 });
  const [aiConviction, setAiConviction] = useState(50); 
  
  const [hasVoted, setHasVoted] = useState(() => {
    const today = new Date().toDateString();
    return localStorage.getItem('ks_user_voted_sentiment') === today;
  });

  // 1. LOAD CROWD DATA
  useEffect(() => {
    fetch('/api/sentiment')
      .then(res => res.json())
      .then(data => setPollData(data))
      .catch(err => console.error("Error loading sentiment:", err));
  }, []);

  // 2. LISTEN TO LIVE AI DATA (WebSocket)
  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const socket = new WebSocket(`${protocol}//${window.location.host}/ws`);
    
    socket.onmessage = (event) => {
      const state = JSON.parse(event.data);
      if (state.ai_conviction !== undefined) {
        setAiConviction(state.ai_conviction);
      }
    };
    
    return () => socket.close();
  }, []);

  // 3. HANDLE VOTE
  const handleVote = async (type) => {
    if (hasVoted) return;
    try {
      const response = await fetch(`/api/sentiment/${type}`, { method: 'POST' });
      if (response.ok) {
        const updatedData = await response.json();
        setPollData(updatedData);
        const today = new Date().toDateString();
        setHasVoted(true);
        localStorage.setItem('ks_user_voted_sentiment', today);
      }
    } catch (error) {
      console.error("Vote failed:", error);
    }
  };

  const totalVotes = (pollData.bullish || 0) + (pollData.bearish || 0);
  const bullPercentage = totalVotes > 0 ? Math.round((pollData.bullish / totalVotes) * 100) : 50;

  return (
    <div className="sentiment-container">
      <div className="content-scroller custom-scrollbar">
        <div className="sentiment-inner">
          <header className="sentiment-header">
            <h1 className="about-title">Global Sentiment<span className="text-yellow-500">.</span></h1>
            <p className="node-text font-mono uppercase tracking-[0.4em]">Human_Intuition vs AI_Logic // Node_07</p>
          </header>

          <div className="comparison-grid">
            {/* HUMAN SENTIMENT CARD */}
            <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} className="sentiment-card">
              <div className="card-top">
                <Users className="text-slate-500" size={20} />
                <span className="card-label">CROWD_SENTIMENT</span>
              </div>
              <div className="vote-display">
                <div className="sentiment-value">{bullPercentage}% BULLISH</div>
                <div className="vote-count-meta">{totalVotes} ANALYSTS_VOTED</div>
              </div>
              <div className="progress-bar-container">
                <div className="progress-bg">
                  <motion.div 
                    initial={{ width: 0 }} 
                    animate={{ width: `${bullPercentage}%` }} 
                    className="progress-fill bullish"
                  />
                </div>
                <div className="progress-labels">
                  <span>BULLISH</span>
                  <span>BEARISH</span>
                </div>
              </div>
              {!hasVoted ? (
                <div className="vote-actions">
                  <button onClick={() => handleVote('bullish')} className="vote-btn bull">
                    <TrendingUp size={18} /> BUY_GOLD
                  </button>
                  <button onClick={() => handleVote('bearish')} className="vote-btn bear">
                    <TrendingDown size={18} /> SELL_GOLD
                  </button>
                </div>
              ) : (
                <div className="voted-confirmation">VOTE_LOCKED_UNTIL_NEXT_CYCLE</div>
              )}
            </motion.div>

            {/* AI CONVICTION CARD */}
            <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="sentiment-card ai-locked">
              <div className="card-top">
                <Brain className="text-yellow-500" size={20} />
                <span className="card-label text-yellow-500/50">AI_CONVICTION_NODE</span>
              </div>
              <div className="vote-display">
                <div className="sentiment-value text-yellow-500">{aiConviction}% BULLISH</div>
                <div className="vote-count-meta">KING_SNIPER_V4_LOGIC</div>
              </div>
              <div className="progress-bar-container">
                <div className="progress-bg">
                  <motion.div 
                    initial={{ width: 0 }} 
                    animate={{ width: `${aiConviction}%` }} 
                    className="progress-fill ai"
                  />
                </div>
                <div className="progress-labels">
                  <span>BULLISH</span>
                  <span>BEARISH</span>
                </div>
              </div>
              <div className="ai-status-note">
                <Info size={12} />
                <span>AI_LOGIC_IS_FIXED_PER_CANDLE_CLOSE</span>
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SentimentPoll; // THIS WAS MISSING