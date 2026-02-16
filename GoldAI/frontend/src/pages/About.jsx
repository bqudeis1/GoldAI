import React from 'react';
import { motion } from 'framer-motion';
import { Github, Linkedin, Mail, ShieldAlert, Cpu, Layers } from 'lucide-react';
import './About.css';

const team = [
  {
    name: "Baha Qudeisat",
    role: "Founder & Lead Software Engineer",
    specialty: "Full-Stack Development of Real-Time Financial Intelligence Platforms",
    icon: <ShieldAlert className="text-yellow-500" size={24} />,
    img: "/Baha.png", 
    socials: {
      linkedin: "https://www.linkedin.com/in/baha-qudeisat/",
      github: "https://github.com/bqudeis1",
      email: "mailto:bqudeisat@gmail.com" // Added mailto: prefix for functionality
    }
  },
  {
    name: "Ibrahim Shalakhti",
    role: "System Architect",
    specialty: "High-Performance Backend Engineering & Real-Time Data Processing",
    icon: <Layers className="text-blue-500" size={24} />,
    img: "/Ibra.png",
    socials: {
      linkedin: "https://www.linkedin.com/in/ibrahim-shalakhti/",
      github: "https://github.com/ibrahim-shalakhti",
      email: "mailto:ibrahimshalakhti@gmail.com"
    }
  },
  {
    name: "Abdallah Abed rabboh",
    role: "AI Engineer",
    specialty: "Backend Engineering for AI-Driven Data Pipelines & Predictive Systems",
    icon: <Cpu className="text-orange-500" size={24} />,
    img: "/Abed.png",
    socials: {
      email: "abdullahshlool45@gmail.com" 
      // github and linkedin removed
    }
  }
];

function About() {
  return (
    <div className="about-container">
      <motion.div 
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        className="about-header"
      >
        <h1 className="about-title">The Architects<span className="text-yellow-500">.</span></h1>
        <p className="about-subtitle">The specialized unit behind King Sniper intelligence.</p>
      </motion.div>

      <div className="team-grid">
        {team.map((member, index) => (
          <motion.div 
            key={index}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.15, duration: 0.5 }}
            className="member-card"
          >
            <div className="member-visual">
              <img src={member.img} alt={member.name} className="member-image" />
              <div className="member-overlay">
                <div className="social-links">
                  {/* Conditional Rendering: Only show if the link exists */}
                  {member.socials.github && (
                    <a href={member.socials.github} target="_blank" rel="noopener noreferrer">
                      <Github className="social-icon" size={20} />
                    </a>
                  )}
                  {member.socials.linkedin && (
                    <a href={member.socials.linkedin} target="_blank" rel="noopener noreferrer">
                      <Linkedin className="social-icon" size={20} />
                    </a>
                  )}
                  {member.socials.email && (
                    <a href={member.socials.email}>
                      <Mail className="social-icon" size={20} />
                    </a>
                  )}
                </div>
              </div>
            </div>
            
            <div className="member-details">
              <div className="flex items-center gap-3 mb-4">
                <div className="role-icon-bg">{member.icon}</div>
                <div>
                  <span className="role-badge">{member.role}</span>
                  <h3 className="member-name">{member.name}</h3>
                </div>
              </div>
              <p className="member-specialty">{member.specialty}</p>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}

export default About;