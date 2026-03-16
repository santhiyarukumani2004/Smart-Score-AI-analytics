import React from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Layout/Header';
import Footer from '../components/Layout/Footer';
import './HomePage.css';

const HomePage = () => {
  const navigate = useNavigate();

  // Log to console to check if component is rendering
  console.log('HomePage is rendering');

  return (
    <>
      <Header />
      <div className="home-container">
        <div className="home-content">
          {/* Logo Container with Spinning Animation */}
          <div className="logo-container">
            <img 
              src="/logo.png" 
              alt="Smart Score AI Logo" 
              className="spinning-logo"
            />
          </div>
          
          {/* Removed h1 home-title, replaced with logo above */}
          
          <p className="home-description">
            An intelligent platform that analyzes exam stress patterns from social media,
            memes, and academic papers to help students and teachers optimize learning strategies.
          </p>
          <div className="button-container">
            <button 
              className="portal-button student-button"
              onClick={() => navigate('/student')}
            >
             🎓 Student Portal
            </button>
            <button 
              className="portal-button teacher-button"
              onClick={() => navigate('/teacher')}
            >
             📈 Teacher Portal
            </button>
          </div>
        </div>
      </div>
      <Footer />
    </>
  );
};

export default HomePage;