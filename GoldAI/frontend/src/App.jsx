import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Menu, X } from 'lucide-react';

// Components & Pages
import Sidebar from './components/Sidebar';
import CommandCenter from './pages/CommandCenter';
import ExecutionArchive from './pages/ExecutionArchive'; // This page now fetches its own data
import About from './pages/About';
import Contact from './pages/Contact';
import Feedback from './pages/Feedback';
import FeaturePipeline from './pages/FeaturePipeline';
import SentimentPoll from './pages/SentimentPoll';

// Global Styles
import './App.css';

function App() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [lifetimeProfit, setLifetimeProfit] = useState("0.00");

  // --- NEW: FETCH REAL PROFIT FROM SERVER ---
  useEffect(() => {
    fetch('/api/archive')
      .then(res => res.json())
      .then(data => {
        // Calculate total profit from the real API data
        const total = data.reduce((acc, move) => acc + parseFloat(move.profit), 0);
        setLifetimeProfit(total.toFixed(2));
      })
      .catch(err => console.error("Error fetching profit data:", err));
  }, []);

  return (
    <Router>
      <div className="app-shell">
        
        {/* ELITE HAMBURGER TRIGGER */}
        <button 
          onClick={() => setIsMenuOpen(!isMenuOpen)}
          className="nav-trigger"
          aria-label="Toggle Menu"
        >
          <AnimatePresence mode="wait">
            <motion.div
              key={isMenuOpen ? 'close' : 'open'}
              initial={{ opacity: 0, rotate: -90, scale: 0.5 }}
              animate={{ opacity: 1, rotate: 0, scale: 1 }}
              exit={{ opacity: 0, rotate: 90, scale: 0.5 }}
              transition={{ duration: 0.2 }}
            >
              {isMenuOpen ? <X size={28} /> : <Menu size={28} />}
            </motion.div>
          </AnimatePresence>
        </button>

        {/* NAVIGATION OVERLAY */}
        <Sidebar isOpen={isMenuOpen} onClose={() => setIsMenuOpen(false)} />

        {/* MAIN CONTENT VIEWPORT */}
        <main className="main-viewport custom-scrollbar">
          <Routes>
            {/* Pass the REAL calculated profit to the Home Screen */}
            <Route path="/" element={<CommandCenter lifetimeProfit={lifetimeProfit} />} />
            
            {/* Archive page fetches its own data now, so no props needed */}
            <Route path="/archive" element={<ExecutionArchive />} />
            
            <Route path="/about" element={<About />} />
            <Route path="/contact" element={<Contact />} />
            <Route path="/feedback" element={<Feedback />} />
            <Route path="/pipeline" element={<FeaturePipeline />} />
            <Route path="/sentiment" element={<SentimentPoll />} />
          </Routes>
        </main>

        {/* GLOBAL LOGO WATERMARK */}
        <div className="fixed bottom-8 right-8 opacity-10 pointer-events-none select-none">
          <img src="/logo.png" alt="KINGS" className="w-24 h-auto" />
        </div>

      </div>
    </Router>
  );
}

export default App;