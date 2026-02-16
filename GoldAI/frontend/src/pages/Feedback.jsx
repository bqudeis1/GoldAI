import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Target, Send, Star } from 'lucide-react';
import './Feedback.css';

function Feedback() {
  const [rating, setRating] = useState(0);
  const [hover, setHover] = useState(0);
  
  const [formData, setFormData] = useState({
    username: '',
    email: '', // Note: We won't send email to public feed for privacy
    comment: ''
  });

  // 1. Initialize with EMPTY array (No fake data)
  const [reviews, setReviews] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // 2. Load Real Reviews on Startup
  useEffect(() => {
    fetch('/api/feedback')
      .then(res => res.json())
      .then(data => setReviews(data))
      .catch(err => console.error("Error loading feedback:", err));
  }, []);

  // 3. Real Submission Handler
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.username || rating === 0) {
      alert("Please provide a USERNAME and CONVICTION_LEVEL.");
      return;
    }

    setIsSubmitting(true);

    const payload = {
      username: formData.username,
      stars: rating,
      comment: formData.comment || "No comment provided."
    };

    try {
      // THE REAL CONNECTION TO YOUR SERVER
      const response = await fetch('/api/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        const updatedList = await response.json();
        setReviews(updatedList); // Update list with server response
        setFormData({ username: '', email: '', comment: '' });
        setRating(0);
        alert("FEEDBACK_TRANSMITTED: Signal received by the Architects.");
      } else {
        alert("Transmission Failed: Server rejected the signal.");
      }
    } catch (error) {
      console.error("Transmission Error:", error);
      alert("Transmission Error: Check your connection.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const avgRating = reviews.length > 0 
    ? (reviews.reduce((acc, rev) => acc + rev.stars, 0) / reviews.length).toFixed(1) 
    : "0.0";

  return (
    <div className="feedback-container">
      <div className="content-scroller custom-scrollbar">
        <header className="feedback-header">
          <h1 className="about-title">Feedback Terminal<span className="text-yellow-500">.</span></h1>
          <div className="avg-display">
            <span className="avg-label">OVERALL_RATING</span>
            <div className="avg-value">
              <Target className="text-yellow-500" size={24} />
              <span>{avgRating} / 5.0</span>
            </div>
          </div>
        </header>

        <div className="feedback-layout">
          {/* Form Section */}
          <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} className="feedback-form-card">
            <h3 className="form-subtitle">SUBMIT_INTELLIGENCE</h3>
            
            <form onSubmit={handleSubmit}>
              <div className="input-group">
                <input 
                  type="text" 
                  placeholder="USERNAME" 
                  className="terminal-input"
                  value={formData.username}
                  onChange={(e) => setFormData({...formData, username: e.target.value})}
                  required
                />
                <input 
                  type="email" 
                  placeholder="EMAIL_ADDRESS" 
                  className="terminal-input"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  required
                />
              </div>

              <div className="rating-selector">
                <span className="selector-label">CONVICTION_LEVEL:</span>
                <div className="sniper-icons">
                  {[...Array(5)].map((_, index) => {
                    const ratingValue = index + 1;
                    return (
                      <button
                        key={index}
                        type="button"
                        className={`sniper-btn ${ratingValue <= (hover || rating) ? 'active' : ''}`}
                        onClick={() => setRating(ratingValue)}
                        onMouseEnter={() => setHover(ratingValue)}
                        onMouseLeave={() => setHover(0)}
                      >
                        <Target size={28} />
                      </button>
                    );
                  })}
                </div>
              </div>

              <textarea 
                placeholder="ADD_COMMENT (OPTIONAL)..." 
                className="terminal-textarea"
                value={formData.comment}
                onChange={(e) => setFormData({...formData, comment: e.target.value})}
              ></textarea>

              <button 
                type="submit" 
                className={`submit-btn ${isSubmitting ? 'opacity-50 cursor-not-allowed' : ''}`}
                disabled={isSubmitting}
              >
                <Send size={16} />
                <span>{isSubmitting ? 'TRANSMITTING...' : 'TRANSMIT_FEEDBACK'}</span>
              </button>
            </form>
          </motion.div>

          {/* Reviews List */}
          <div className="reviews-feed">
            <h3 className="form-subtitle">LATEST_TRANSMISSIONS</h3>
            <div className="reviews-list custom-scrollbar">
              {reviews.length === 0 ? (
                <div className="text-gray-500 italic p-4">Awaiting first transmission...</div>
              ) : (
                reviews.map((rev, index) => (
                  <motion.div 
                    layout
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    key={index} 
                    className="review-node"
                  >
                    <div className="review-top">
                      <span className="review-user">{rev.username || rev.user}</span>
                      <div className="review-stars">
                        {[...Array(rev.stars)].map((_, i) => (
                          <Star key={i} size={10} fill="#eab308" className="text-yellow-500" />
                        ))}
                      </div>
                    </div>
                    <p className="review-text">{rev.comment}</p>
                  </motion.div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Feedback;