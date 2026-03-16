import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import TopicAnalysis from './TopicAnalysis';
import YearAnalysis from './YearAnalysis';
import DecisionTree from './DecisionTree';
import KnowledgeGraph from './KnowledgeGraph';
import ProfileMenu from '../Common/ProfileMenu';
import { ChartLoader } from '../Common/LoadingSpinner';
import './TeacherDashboard.css';

const TeacherDashboard = ({ teacherData }) => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('topics');
  const [selectedExam, setSelectedExam] = useState('all');
  const [showProfile, setShowProfile] = useState(false);
  
  const profileRef = useRef(null);
  const profileButtonRef = useRef(null);

  useEffect(() => {
    fetchDashboardData(selectedExam);
  }, [selectedExam]);

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

  const fetchDashboardData = async (exam) => {
    try {
      setLoading(true);
      console.log(`Fetching teacher dashboard data for exam: ${exam}`);
      
      const url = exam === 'all' 
        ? 'http://localhost:5000/api/teacher/dashboard'
        : `http://localhost:5000/api/teacher/dashboard/${exam}`;
      
      const response = await axios.get(url);
      
      console.log('Teacher Dashboard API Response:', response.data);
      setDashboardData(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching teacher dashboard:', error);
      setError('Failed to load dashboard data');
      setLoading(false);
    }
  };

  const handleExamChange = (e) => {
    setSelectedExam(e.target.value);
  };

  const toggleProfile = () => {
    setShowProfile(!showProfile);
  };

  const closeProfile = () => {
    setShowProfile(false);
  };

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading teacher dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-container">
        <div className="error-container">
          <p className="error-message">{error}</p>
          <button onClick={() => fetchDashboardData(selectedExam)} className="retry-btn">
            Retry
          </button>
        </div>
      </div>
    );
  }

  // Use exams from API or fallback to common exams
  const availableExams = dashboardData?.available_exams || [
    'NEET', 'JEE', 'GATE', 'TNPSC', 'UPSC', 'NET', 'UGC NET',
    'MEDICAL SCIENCE', 'CBSE', 'ICSE'
  ];

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1 className="dashboard-title">👨‍🏫 Teacher Dashboard</h1>
        <div className="header-right">
          {teacherData?.name && (
            <>
              <span className="teacher-name">Welcome, {teacherData.name}</span>
              <button 
                ref={profileButtonRef}
                className="profile-icon-btn" 
                onClick={toggleProfile}
                aria-label="Profile menu"
              >
                <div className="profile-icon">
                  {teacherData?.name?.charAt(0) || 'T'}
                </div>
              </button>
            </>
          )}
        </div>
      </div>

      {/* Profile Menu Popup */}
      {showProfile && (
        <div ref={profileRef} className="profile-menu-wrapper">
          <ProfileMenu data={teacherData} onClose={closeProfile} />
        </div>
      )}

      {/* Exam Filter Bar */}
      <div className="filter-bar">
        <div className="filter-group">
          <label htmlFor="exam-filter">Filter by Exam:</label>
          <select 
            id="exam-filter"
            value={selectedExam} 
            onChange={handleExamChange}
            className="exam-select"
          >
            <option value="all">All Exams</option>
            {availableExams.sort().map(exam => (
              <option key={exam} value={exam}>{exam}</option>
            ))}
          </select>
        </div>
        {selectedExam !== 'all' && (
          <div className="filter-badge">
            Showing data for: <strong>{selectedExam}</strong>
          </div>
        )}
      </div>

      <div className="dashboard-tabs">
        <button 
          className={`tab-btn ${activeTab === 'topics' ? 'active' : ''}`}
          onClick={() => setActiveTab('topics')}
        >
          📚 Topic Analysis
        </button>
        <button 
          className={`tab-btn ${activeTab === 'year' ? 'active' : ''}`}
          onClick={() => setActiveTab('year')}
        >
          📅 Year Analysis
        </button>
        <button 
          className={`tab-btn ${activeTab === 'tree' ? 'active' : ''}`}
          onClick={() => setActiveTab('tree')}
        >
          🌳 Decision Tree
        </button>
        <button 
          className={`tab-btn ${activeTab === 'kg' ? 'active' : ''}`}
          onClick={() => setActiveTab('kg')}
        >
          🕸️ Knowledge Graph
        </button>
      </div>

      <div className="dashboard-content">
        {activeTab === 'topics' && dashboardData && (
          <TopicAnalysis 
            data={dashboardData.topic_summary || []} 
            selectedExam={selectedExam}
          />
        )}
        {activeTab === 'year' && dashboardData && (
          <YearAnalysis 
            data={dashboardData.year_chart_data || []} 
            selectedExam={selectedExam}
          />
        )}
        {activeTab === 'tree' && dashboardData?.tree_structure && (
          <DecisionTree 
            data={dashboardData.tree_structure} 
            selectedExam={selectedExam}
          />
        )}
        {activeTab === 'kg' && dashboardData && (
          <KnowledgeGraph 
            kgStats={dashboardData.kg_stats || {}}
            difficultyDistribution={dashboardData.difficulty_distribution || []}
            edgeData={dashboardData.edge_data || []}
            selectedExam={selectedExam}
          />
        )}
      </div>
    </div>
  );
};

export default TeacherDashboard;