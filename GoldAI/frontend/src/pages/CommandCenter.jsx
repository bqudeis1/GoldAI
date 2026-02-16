import React, { useEffect, useState, useRef } from 'react';
import { createChart, ColorType, AreaSeries } from 'lightweight-charts';
import { Shield, Zap, TrendingUp } from 'lucide-react';
import './CommandCenter.css';

function CommandCenter({ lifetimeProfit = 0 }) {
  // Layer 1: Guaranteed fallback state
  const [liveData, setLiveData] = useState({ 
    price: 0, 
    prediction: 'CONNECTING...', 
    ai_conviction: 0 
  });

  const chartContainerRef = useRef(null);
  const chartRef = useRef(null);
  const seriesRef = useRef(null);

  // Layer 2: The Firewall
  const displayPrice = liveData?.price ?? 0;
  // Ensure we always have a string for the status
  const displayStatus = String(liveData?.status || liveData?.prediction || "SCANNING...");

  const getFontSize = () => {
    // CRASH PROTECTION: displayStatus is guaranteed to be a string here
    const len = displayStatus.length;
    if (window.innerWidth < 768) return len > 6 ? '1.8rem' : '3.5rem';
    return len > 6 ? '2.5rem' : '4.5rem';
  };

  useEffect(() => {
    if (!chartContainerRef.current) return;

    const chart = createChart(chartContainerRef.current, {
      layout: { 
        background: { type: ColorType.Solid, color: 'transparent' }, 
        textColor: '#64748b',
        fontFamily: 'JetBrains Mono',
      },
      width: chartContainerRef.current.clientWidth,
      height: 400,
      grid: {
        vertLines: { color: 'rgba(255, 255, 255, 0.02)' },
        horzLines: { color: 'rgba(255, 255, 255, 0.02)' },
      },
    });

    const areaSeries = chart.addSeries(AreaSeries, { 
      lineColor: '#eab308',
      topColor: 'rgba(234, 179, 8, 0.3)',
      bottomColor: 'rgba(234, 179, 8, 0)',
    });
    
    // Seed with initial flat line to look alive before data comes
    areaSeries.setData([
        { time: Math.floor(Date.now() / 1000) - 300, value: 0 },
        { time: Math.floor(Date.now() / 1000) - 60, value: 0 },
    ]);

    seriesRef.current = areaSeries;
    chartRef.current = chart;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const socket = new WebSocket(`${protocol}//${window.location.host}/ws`);

    socket.onmessage = (event) => {
      try {
        const state = JSON.parse(event.data);
        if (!state) return;
        
        setLiveData({
          price: state.price ?? 0,
          prediction: state.status ?? state.prediction ?? "LIVE",
          ai_conviction: state.ai_conviction ?? 0
        });

        // Only update chart if price is real (greater than 0)
        if (seriesRef.current && (state.price ?? 0) > 0) {
          seriesRef.current.update({
            time: Math.floor(Date.now() / 1000),
            value: state.price,
          });
        }
      } catch (e) { console.error("Data error", e); }
    };

    const resizeObserver = new ResizeObserver(entries => {
      if (!entries?.[0] || !chartRef.current) return;
      chartRef.current.applyOptions({ width: entries[0].contentRect.width });
    });
    resizeObserver.observe(chartContainerRef.current);

    return () => {
      resizeObserver.disconnect();
      socket.close();
      chart.remove();
    };
  }, []);

  return (
    <div className="command-center-container">
      <div className="content-scroller custom-scrollbar">
        <div className="inner-layout">
          <header className="blade-header">
            <img src="/logo.png" alt="KING SNIPER" className="header-logo" />
            <div className="status-pill">
              <div className="status-indicator">
                <span className="indicator-ping"></span>
                <span className="indicator-dot"></span>
              </div>
              <span className="status-text uppercase text-[9px]">System_Online_V4.0</span>
            </div>
          </header>

          <section className="metrics-grid">
            <div className="metric-card">
              <span className="metric-label"><Zap size={12} className="icon-gold"/> LIVE XAU/USD</span>
              <div className="metric-value font-mono">
                ${displayPrice > 0 ? displayPrice.toLocaleString(undefined, {minimumFractionDigits: 2}) : "---.--"}
              </div>
            </div>

            <div className="metric-card signal-highlight flex flex-col justify-center overflow-hidden">
              <span className="metric-label flex items-center justify-center gap-2">
                <Shield size={10}/> ACTIVE_SIGNAL
              </span>
              <div 
                className="signal-value-expanded italic uppercase"
                style={{ 
                    fontSize: getFontSize(), 
                    color: displayStatus === 'BUY' ? '#22c55e' : displayStatus === 'SELL' ? '#ef4444' : '#eab308' 
                }}
              >
                {displayStatus}
              </div>
            </div>

            <div className="metric-card">
              <span className="metric-label"><TrendingUp size={12} className="icon-green"/> LIFETIME_PROFIT</span>
              <div className="metric-value font-mono profit">+${lifetimeProfit ?? 0}</div>
            </div>
          </section>

          <div className="chart-section-expanded">
            <div ref={chartContainerRef} className="chart-canvas" style={{ minHeight: '400px' }}></div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default CommandCenter;