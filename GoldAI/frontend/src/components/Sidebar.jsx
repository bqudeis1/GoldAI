import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  LayoutDashboard, 
  History, 
  Info, 
  Mail, 
  MessageSquare, 
  Lightbulb,
  BarChart3 // Better icon for Sentiment
} from 'lucide-react';
import './Sidebar.css';

const Sidebar = ({ isOpen, onClose }) => {
  const location = useLocation();

  const menuItems = [
    { id: '01', name: 'Command Center', path: '/', icon: <LayoutDashboard size={18} /> },
    { id: '02', name: 'Execution Archive', path: '/archive', icon: <History size={18} /> },
    { id: '03', name: 'About Us', path: '/about', icon: <Info size={18} /> },
    { id: '04', name: 'Contact Us', path: '/contact', icon: <Mail size={18} /> },
    { id: '05', name: 'Feedback Terminal', path: '/feedback', icon: <MessageSquare size={18} /> },
    { id: '06', name: 'Feature Pipeline', path: '/pipeline', icon: <Lightbulb size={18} /> },
    { id: '07', name: 'Global Sentiment', path: '/sentiment', icon: <BarChart3 size={18} /> },
  ];

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="sidebar-overlay"
          />
          
          <motion.aside
            initial={{ x: '-100%' }}
            animate={{ x: 0 }}
            exit={{ x: '-100%' }}
            className="sidebar-container"
          >
            <div className="sidebar-header">
              <img src="/logo.png" alt="KING SNIPER" className="sidebar-logo-massive" />
              <div className="sidebar-brand-text">
                <h2 className="brand-title">KING SNIPER</h2>
                <p className="brand-subtitle">INSTITUTIONAL TERMINAL</p>
              </div>
            </div>

            <nav className="sidebar-nav">
              {menuItems.map((item) => {
                const isActive = location.pathname === item.path;
                return (
                  <Link
                    key={item.id}
                    to={item.path}
                    onClick={onClose}
                    className={`nav-item group ${isActive ? 'active' : ''}`}
                  >
                    <div className="nav-item-left">
                       <span className="nav-icon">{item.icon}</span>
                       <span className="nav-label">{item.name}</span>
                    </div>
                    <span className="nav-number">{item.id}</span>
                  </Link>
                );
              })}
            </nav>

            <div className="sidebar-footer">
                <p>SYSTEM_V4.0 // JORDAN_DC</p>
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
};

export default Sidebar;