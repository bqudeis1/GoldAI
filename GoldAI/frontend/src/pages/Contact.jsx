import React from 'react';
import { motion } from 'framer-motion';
import { Mail, Phone, MessageSquare, Linkedin, Globe, ShieldCheck } from 'lucide-react';
import './Contact.css';

const contacts = [
  {
    name: "Baha Qudeisat",
    role: "Founder & Lead Software Engineer",
    email: "bqudeisat@gmail.com",
    phone: "+962 782859507",
    specialty: "Full-Stack Development",
    linkedin: "https://www.linkedin.com/in/baha-qudeisat/",
    color: "border-yellow-500/30"
  },
  {
    name: "Ibrahim Shalakhti",
    role: "Systems Architect",
    email: "ibrahimshalakhti@gmail.com",
    phone: "+962 770629370",
    specialty: "Backend Engineering",
    linkedin: "https://www.linkedin.com/in/ibrahim-shalakhti/",
    color: "border-blue-500/30"
  },
  {
    name: "Abdallah Abed rabboh",
    role: "AI Engineer",
    email: "abdullahshlool45@gmail.com",
    phone: "+962 786979708",
    specialty: "Backend Engineering for AI Data Pipelines",
    color: "border-orange-500/30"
    // No linkedin/globe for Abdallah
  }
];

function Contact() {
  return (
    <div className="contact-container">
      <div className="contact-scroller custom-scrollbar">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="contact-header"
        >
          <div className="header-icon-wrapper">
            <ShieldCheck className="text-yellow-500" size={40} />
          </div>
          <h1 className="contact-title">Contact Hub<span className="text-yellow-500">.</span></h1>
          <p className="contact-subtitle">Secure communication channels for the KINGS. specialized unit.</p>
        </motion.div>

        <div className="contact-grid">
          {contacts.map((person, index) => (
            <motion.div 
              key={index}
              initial={{ opacity: 0, x: -30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`contact-card ${person.color}`}
            >
              <div className="card-top">
                <span className="role-tag">{person.role}</span>
                <h3 className="person-name">{person.name}</h3>
                <p className="person-specialty">{person.specialty}</p>
              </div>

              <div className="contact-methods">
                <a href={`mailto:${person.email}`} className="method-item group">
                  <Mail size={16} className="text-slate-500 group-hover:text-yellow-500 transition-colors" />
                  <span className="method-text">{person.email}</span>
                </a>
                <a href={`tel:${person.phone.replace(/\s/g, '')}`} className="method-item group">
                  <Phone size={16} className="text-slate-500 group-hover:text-yellow-500 transition-colors" />
                  <span className="method-text">{person.phone}</span>
                </a>
              </div>

              <div className="card-actions">
                <button 
                  onClick={() => window.location.href = `mailto:${person.email}`}
                  className="action-btn"
                >
                  <MessageSquare size={14} />
                  <span>Secure Message</span>
                </button>
                <div className="social-mini-links">
                  {person.linkedin && (
                    <a href={person.linkedin} target="_blank" rel="noopener noreferrer">
                      <Linkedin size={18} className="social-mini-icon hover:text-blue-400" />
                    </a>
                  )}
                  {/* Globe icon removed for members without specific portfolio sites */}
                  <Globe size={18} className="social-mini-icon opacity-20" />
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Contact;