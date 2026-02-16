import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronUp, Zap, Smartphone, Send, Database } from 'lucide-react';
import './FeaturePipeline.css';

// 1. ICON MAP
const iconMap = {
  Zap: <Zap size={18}/>,
  Smartphone: <Smartphone size={18}/>,
  Send: <Send size={18}/>,
  Database: <Database size={18}/>
};

const FeaturePipeline = () => {
  // 2. STATE: Initialize empty (Wait for server data)
  const [features, setFeatures] = useState([]);

  // 3. USER VOTES: Keep this local to prevent spamming from the same browser
  const [userVotes, setUserVotes] = useState(() => {
    const saved = localStorage.getItem('ks_user_voted_ids');
    return saved ? JSON.parse(saved) : [];
  });

  // 4. LOAD DATA FROM SERVER ON STARTUP
  useEffect(() => {
    fetch('/api/features')
      .then(res => res.json())
      .then(data => {
        // Sort by votes (Highest first)
        const sorted = data.sort((a, b) => b.votes - a.votes);
        setFeatures(sorted);
      })
      .catch(err => console.error("Error loading features:", err));
  }, []);

  // 5. SAVE USER VOTE HISTORY LOCALLY
  useEffect(() => {
    localStorage.setItem('ks_user_voted_ids', JSON.stringify(userVotes));
  }, [userVotes]);

  // 6. HANDLE VOTE (Server Sync)
  const handleUpvote = async (id) => {
    if (userVotes.includes(id)) return; // Prevent double vote

    try {
      // Send vote to server
      const response = await fetch(`/api/vote/${id}`, { method: 'POST' });
      
      if (response.ok) {
        const updatedList = await response.json();
        // Server returns the updated list, so we sort and save it
        setFeatures(updatedList.sort((a, b) => b.votes - a.votes));
        
        // Mark as voted locally
        setUserVotes(prev => [...prev, id]);
      }
    } catch (error) {
      console.error("Vote failed:", error);
    }
  };

  return (
    <div className="pipeline-container">
      <div className="content-scroller custom-scrollbar">
        <div className="pipeline-inner">
          <header className="pipeline-header">
            <h1 className="about-title">Feature Pipeline<span className="text-yellow-500">.</span></h1>
            <p className="node-text font-mono uppercase tracking-[0.4em]">Persistence_Secure // Node_06</p>
          </header>

          <div className="pipeline-grid">
            <AnimatePresence mode="popLayout">
              {features.length === 0 ? (
                 <div className="text-gray-500 italic p-4">Loading pipeline data...</div>
              ) : (
                features.map((feature) => {
                  const hasVoted = userVotes.includes(feature.id);
                  return (
                    <motion.div layout key={feature.id} className={`feature-card ${hasVoted ? 'voted' : ''}`}>
                      <div className="feature-vote-side">
                        <button 
                          onClick={() => handleUpvote(feature.id)}
                          disabled={hasVoted}
                          className="vote-btn"
                        >
                          <ChevronUp className={hasVoted ? 'text-slate-800' : 'text-yellow-500'} size={32} />
                          <span className="vote-count">{feature.votes}</span>
                        </button>
                      </div>
                      
                      <div className="feature-content">
                        <div className="feature-meta">
                          <span className="category-tag">{feature.category}</span>
                          <div className="feature-icon-wrapper">{iconMap[feature.iconKey]}</div>
                        </div>
                        <h3 className="feature-title">{feature.title}</h3>
                        <p className="feature-description">{feature.description}</p>
                        {hasVoted && <span className="voted-status-text">VOTE_LOCKED</span>}
                      </div>
                    </motion.div>
                  );
                })
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FeaturePipeline;