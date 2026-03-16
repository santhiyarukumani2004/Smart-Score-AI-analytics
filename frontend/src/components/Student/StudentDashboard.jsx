import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import TweetStress from './TweetStress';
import MemeSarcasm from './MemeSarcasm';
import DifficultyClassification from './DifficultyClassification';
import DifficultTopics from './DifficultTopics';
import ProfileMenu from '../Common/ProfileMenu';
import { ChartLoader } from '../Common/LoadingSpinner';
import './StudentDashboard.css';

// ========== GOOGLE AI DASHBOARD STYLES ==========
const styles = {
  container: {
    minHeight: '100vh',
    background: '#202124',
    fontFamily: "'Poppins', sans-serif",
    color: '#e8eaed'
  },
  header: {
    background: '#2d2e30',
    borderBottom: '1px solid #3c4043',
    padding: '20px 32px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    position: 'relative'
  },
  headerLeft: {
    display: 'flex',
    alignItems: 'center',
    gap: 16
  },
  studentLogo: {
    width: 48,
    height: 48,
    borderRadius: '50%',
    background: '#4285F4',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: 24,
    color: 'white',
    fontWeight: 600
  },
  title: {
    margin: 0,
    fontSize: 24,
    fontWeight: 600,
    color: '#e8eaed',
    fontFamily: "'Poppins', sans-serif",
    letterSpacing: '-0.5px'
  },
  subtitle: {
    margin: '4px 0 0',
    fontSize: 14,
    color: '#9aa0a6',
    fontFamily: "'Poppins', sans-serif",
    fontWeight: 400
  },
  headerRight: {
    display: 'flex',
    alignItems: 'center',
    gap: 16
  },
  examBadge: {
    padding: '6px 16px',
    background: '#35363a',
    border: '1px solid #3c4043',
    borderRadius: 100,
    color: '#e8eaed',
    fontSize: 13,
    fontWeight: 500,
    fontFamily: "'Poppins', sans-serif"
  },
  profileIconBtn: {
    background: 'none',
    border: 'none',
    cursor: 'pointer',
    padding: 0,
    position: 'relative'
  },
  profileIcon: {
    width: 40,
    height: 40,
    borderRadius: '50%',
    background: '#4285F4',
    color: 'white',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: 18,
    fontWeight: 500,
    textTransform: 'uppercase',
    transition: 'all 0.2s ease',
    border: '2px solid transparent',
    fontFamily: "'Poppins', sans-serif",
    ':hover': {
      transform: 'scale(1.05)',
      boxShadow: '0 2px 8px rgba(66, 133, 244, 0.3)',
      borderColor: '#ffffff'
    }
  },
  profileMenuWrapper: {
    position: 'absolute',
    top: 80,
    right: 32,
    zIndex: 1000,
    animation: 'slideDown 0.2s ease'
  },
  tabsContainer: {
    display: 'flex',
    gap: 8,
    padding: '0 32px',
    marginTop: 24,
    flexWrap: 'wrap'
  },
  tabBtn: {
    padding: '10px 24px',
    background: 'transparent',
    border: 'none',
    borderRadius: 100,
    color: '#9aa0a6',
    fontSize: 14,
    fontWeight: 500,
    fontFamily: "'Poppins', sans-serif",
    cursor: 'pointer',
    transition: 'all 0.2s',
    display: 'flex',
    alignItems: 'center',
    gap: 8
  },
  activeTab: {
    background: '#4285F4',
    color: 'white'
  },
  content: {
    padding: 32
  },
  loadingContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '60vh'
  },
  spinner: {
    width: 48,
    height: 48,
    border: '4px solid #3c4043',
    borderTopColor: '#4285F4',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite'
  },
  loadingText: {
    marginTop: 16,
    color: '#9aa0a6',
    fontSize: 14,
    fontFamily: "'Poppins', sans-serif"
  },
  errorContainer: {
    textAlign: 'center',
    padding: 60,
    background: '#2d2e30',
    borderRadius: 12,
    border: '1px solid #3c4043',
    margin: 32
  },
  errorMessage: {
    color: '#EA4335',
    fontSize: 14,
    fontFamily: "'Poppins', sans-serif",
    marginBottom: 16
  },
  retryBtn: {
    padding: '10px 24px',
    background: '#4285F4',
    color: 'white',
    border: 'none',
    borderRadius: 100,
    cursor: 'pointer',
    fontWeight: 500,
    fontSize: 14,
    fontFamily: "'Poppins', sans-serif",
    transition: 'all 0.2s',
    ':hover': {
      background: '#5a95f5',
      transform: 'translateY(-1px)',
      boxShadow: '0 4px 8px rgba(66,133,244,0.3)'
    }
  }
};

const StudentDashboard = ({ studentData }) => {
  const [activeMenu, setActiveMenu] = useState('tweet-stress');
  const [showProfile, setShowProfile] = useState(false);
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const profileRef = useRef(null);
  const profileButtonRef = useRef(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        profileRef.current && 
        !profileRef.current.contains(event.target) &&
        !profileButtonRef.current?.contains(event.target)
      ) {
        setShowProfile(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    // Add keyframes for animations
    const styleSheet = document.createElement("style");
    styleSheet.textContent = `
      @keyframes slideDown {
        from {
          opacity: 0;
          transform: translateY(-10px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }
      
      @keyframes spin {
        to {
          transform: rotate(360deg);
        }
      }
    `;
    document.head.appendChild(styleSheet);

    return () => {
      document.head.removeChild(styleSheet);
    };
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const exam = studentData?.competitiveExam || 'GENERAL';
      console.log('Fetching dashboard for exam:', exam);
      
      const response = await axios.get(
        `http://localhost:5000/api/student/dashboard/${exam}`
      );
      
      console.log('Dashboard API Response:', response.data);
      setDashboardData(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setError('Failed to load dashboard data. Please try again.');
      setLoading(false);
    }
  };

  const toggleProfile = () => {
    setShowProfile(!showProfile);
  };

  const closeProfile = () => {
    setShowProfile(false);
  };

  if (loading) {
    return (
      <div className="student-dashboard-container" style={styles.container}>
        <div style={styles.loadingContainer}>
          <div style={styles.spinner}></div>
          <p style={styles.loadingText}>Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="student-dashboard-container" style={styles.container}>
        <div style={styles.errorContainer}>
          <p style={styles.errorMessage}>{error}</p>
          <button onClick={fetchDashboardData} style={styles.retryBtn}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="student-dashboard-container" style={styles.container}>
      {/* Header with Student Logo - Matching Teacher Dashboard */}
      <div style={styles.header}>
        <div style={styles.headerLeft}>
          <div style={styles.studentLogo}>
            {studentData?.name?.charAt(0)?.toUpperCase() || '👨‍🎓'}
          </div>
          <div>
            <h1 style={styles.title}>
              {studentData?.name ? `${studentData.name}'s Dashboard` : 'Student Dashboard'}
            </h1>
            <p style={styles.subtitle}>
              Track your learning progress and exam preparation
            </p>
          </div>
        </div>
        
        <div style={styles.headerRight}>
          {studentData?.competitiveExam && (
            <span style={styles.examBadge}>
              Target: {studentData.competitiveExam}
            </span>
          )}
          
          <button 
            ref={profileButtonRef}
            style={styles.profileIconBtn}
            onClick={toggleProfile}
            aria-label="Profile menu"
          >
            <div style={styles.profileIcon}>
              {studentData?.name?.charAt(0)?.toUpperCase() || 'U'}
            </div>
          </button>
        </div>
      </div>

      {/* Profile Menu Popup */}
      {showProfile && (
        <div ref={profileRef} style={styles.profileMenuWrapper}>
          <ProfileMenu data={studentData} onClose={closeProfile} />
        </div>
      )}

      {/* Navigation Tabs - Matching Teacher Dashboard */}
      <div style={styles.tabsContainer}>
        <button
          style={{
            ...styles.tabBtn,
            ...(activeMenu === 'tweet-stress' ? styles.activeTab : {})
          }}
          onClick={() => setActiveMenu('tweet-stress')}
        >
          <span>📊</span>
          Tweet Stress
        </button>
        <button
          style={{
            ...styles.tabBtn,
            ...(activeMenu === 'meme-sarcasm' ? styles.activeTab : {})
          }}
          onClick={() => setActiveMenu('meme-sarcasm')}
        >
          <span>😂</span>
          Meme Sarcasm
        </button>
        <button
          style={{
            ...styles.tabBtn,
            ...(activeMenu === 'difficulty' ? styles.activeTab : {})
          }}
          onClick={() => setActiveMenu('difficulty')}
        >
          <span>📈</span>
          Difficulty
        </button>
        <button
          style={{
            ...styles.tabBtn,
            ...(activeMenu === 'topics' ? styles.activeTab : {})
          }}
          onClick={() => setActiveMenu('topics')}
        >
          <span>🎯</span>
          Difficult Topics
        </button>
      </div>

      {/* Content Area */}
      <div style={styles.content}>
        {activeMenu === 'tweet-stress' && (
          <div className="scrollable-content">
            <TweetStress 
              data={dashboardData?.tweet_yearly || []} 
              overallStats={dashboardData?.tweet_stats || {}} 
            />
          </div>
        )}

        {activeMenu === 'meme-sarcasm' && (
          <div className="scrollable-content">
            <MemeSarcasm 
              data={dashboardData?.meme_stats || {}} 
              yearlyData={dashboardData?.meme_trend || []}
              yearlyStressDistribution={dashboardData?.yearly_stress_distribution || []} 
            />
          </div>
        )}

        {activeMenu === 'difficulty' && (
          <div className="scrollable-content">
            <DifficultyClassification 
              classification={dashboardData?.difficulty_classification || []}
              subjectComparison={dashboardData?.subject_comparison || []}
              yearData={dashboardData?.year_difficulty || []}
              stressPieData={dashboardData?.stress_distribution_pie || {}}
              mostDifficultTopics={dashboardData?.most_difficult_topics || []}
              difficultyDistribution={dashboardData?.difficulty_distribution || {}}
            />
          </div>
        )}

        {activeMenu === 'topics' && (
          <div className="scrollable-content">
            <DifficultTopics 
              data={dashboardData?.topics || []}
              top3Hardest={dashboardData?.top3_hardest || []}
              top3Easiest={dashboardData?.top3_easiest || []}
              subjectComparison={dashboardData?.subject_comparison || []}
              mostDifficultTopics={dashboardData?.most_difficult_topics || []}
              recommendations={dashboardData?.ai_recommendations || []}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default StudentDashboard;