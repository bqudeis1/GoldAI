import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { History, TrendingUp, DollarSign, Target, ShieldCheck } from 'lucide-react';
import "./ExecutionArchive.css";

function ExecutionArchive() {
  const [data, setData] = useState([]);
  const [metrics, setMetrics] = useState({
    profit: 0,
    snipes: 0,
    rr: "0:0",
    accuracy: 0
  });

  // 1. FETCH REAL DATA FROM API
  useEffect(() => {
    fetch('/api/archive')
      .then(res => res.json())
      .then(tradeData => {
        setData(tradeData);
        calculateMetrics(tradeData);
      })
      .catch(err => console.error("Error loading archive:", err));
  }, []);

  // 2. DYNAMIC CALCULATION ENGINE
  const calculateMetrics = (trades) => {
    if (!Array.isArray(trades) || trades.length === 0) return;

    // Helper to clean profit strings (removes '+' and whitespace)
    const cleanVal = (val) => {
      if (!val) return 0;
      // Convert to string and remove '+' before parsing
      return parseFloat(val.toString().replace('+', '').trim());
    };

    // A. Lifetime Profit
    const totalProfit = trades.reduce((acc, move) => acc + cleanVal(move.profit), 0);

    // B. Accuracy (Wins vs Total)
    const wins = trades.filter(t => cleanVal(t.profit) > 0).length;
    const accuracy = ((wins / trades.length) * 100).toFixed(1);

    // C. Avg Risk:Reward (Approximation based on Avg Win / Avg Loss)
    const winningTrades = trades.filter(t => cleanVal(t.profit) > 0);
    const losingTrades = trades.filter(t => cleanVal(t.profit) < 0);

    const avgWin = winningTrades.length > 0 
      ? winningTrades.reduce((acc, t) => acc + cleanVal(t.profit), 0) / winningTrades.length 
      : 0;
    
    const avgLoss = losingTrades.length > 0 
      ? Math.abs(losingTrades.reduce((acc, t) => acc + cleanVal(t.profit), 0) / losingTrades.length) 
      : 1;

    const rrRatio = avgLoss > 0 ? `1:${(avgWin / avgLoss).toFixed(1)}` : "1:1";

    setMetrics({
      profit: totalProfit,
      snipes: trades.length,
      rr: rrRatio,
      accuracy: accuracy
    });
  };

  return (
    <div className="archive-container">
      <div className="content-scroller custom-scrollbar">
        <div className="inner-layout">
          <motion.header 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="archive-header"
          >
            <div className="header-main">
              <h1 className="archive-title">Execution Archive<span className="text-yellow-500">.</span></h1>
              <p className="node-text">HISTORICAL_INTELLIGENCE // XAU/USD_NODE</p>
            </div>
            <div className="status-badge">
              <ShieldCheck size={14} className="text-green-500" />
              <span>LOGS_ENCRYPTED</span>
            </div>
          </motion.header>

          <section className="metrics-grid">
            <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="metric-card">
              <span className="metric-label"><TrendingUp size={12} className="text-green-500"/> LIFETIME_PROFIT</span>
              <div className="metric-value text-green-400 font-mono">
                +${metrics.profit.toLocaleString(undefined, {minimumFractionDigits: 2})}
              </div>
            </motion.div>

            <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.1 }} className="metric-card">
              <span className="metric-label"><Target size={12} className="text-yellow-500"/> TOTAL_SNIPES</span>
              <div className="metric-value font-mono">{metrics.snipes}</div>
            </motion.div>

            <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.2 }} className="metric-card">
              <span className="metric-label"><DollarSign size={12} className="text-blue-500"/> AVG_RR_RATIO</span>
              <div className="metric-value font-mono">{metrics.rr}</div>
            </motion.div>

            <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.3 }} className="metric-card">
              <span className="metric-label"><History size={12} className="text-slate-500"/> ACCURACY</span>
              <div className="metric-value font-mono">{metrics.accuracy}%</div>
            </motion.div>
          </section>

          <div className="log-table-wrapper">
            <table className="log-table">
              <thead>
                <tr>
                  <th>TIMESTAMP</th>
                  <th>SIGNAL</th>
                  <th>PRICE_FLOW</th>
                  <th className="text-right">NET_RESULT</th>
                </tr>
              </thead>
              <tbody>
                {data.length === 0 ? (
                  <tr><td colSpan="4" className="text-center p-4 opacity-50">Initializing Archive...</td></tr>
                ) : (
                  data.map((move, index) => (
                    <motion.tr 
                      initial={{ opacity: 0, x: -10 }} 
                      animate={{ opacity: 1, x: 0 }} 
                      transition={{ delay: index * 0.05 }}
                      key={move.id || index}
                    >
                      <td className="row-date">{move.date}</td>
                      <td>
                        <span className={`signal-tag ${move.type.toLowerCase()}`}>
                          {move.type}
                        </span>
                      </td>
                      <td className="price-flow">
                        <span className="opacity-40">$</span>{move.entry} 
                        <span className="mx-2 text-yellow-500/30">→</span> 
                        <span className="opacity-40">$</span>{move.exit}
                      </td>
                      <td className={`profit-value text-right ${parseFloat(move.profit.toString().replace('+', '')) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {move.profit}
                      </td>
                    </motion.tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ExecutionArchive;