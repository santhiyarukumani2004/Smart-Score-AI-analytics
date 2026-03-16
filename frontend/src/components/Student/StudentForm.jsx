import React, { useState, useEffect } from 'react';
import axios from 'axios';
import LoadingSpinner from '../Common/LoadingSpinner';
import './StudentForm.css';

const StudentForm = ({ onRegister }) => {
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    email: '',
    city: '',
    state: '',
    currentStudy: '',
    course: '',
    major: '',
    competitiveExam: '',
    tnpscGroup: '',
    needs: []
  });

  const [courses, setCourses] = useState({});
  const [majors, setMajors] = useState({});
  const [tnpscGroups, setTnpscGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [errors, setErrors] = useState({});

  useEffect(() => {
    fetchDropdownData();
  }, []);

  const fetchDropdownData = async () => {
    try {
      // Simulate loading delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const [coursesRes, majorsRes, groupsRes] = await Promise.all([
        axios.get('http://localhost:5000/api/courses'),
        axios.get('http://localhost:5000/api/majors'),
        axios.get('http://localhost:5000/api/tnpsc-groups')
      ]);
      
      setCourses(coursesRes.data);
      setMajors(majorsRes.data);
      setTnpscGroups(groupsRes.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching dropdown data:', error);
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: null }));
    }
  };

  const handleNeedsChange = (e) => {
    const options = e.target.options;
    const selected = [];
    for (let i = 0; i < options.length; i++) {
      if (options[i].selected) {
        selected.push(options[i].value);
      }
    }
    setFormData(prev => ({ ...prev, needs: selected }));
  };

  const validateForm = () => {
    const newErrors = {};
    if (!formData.name) newErrors.name = 'Name is required';
    if (!formData.phone) newErrors.phone = 'Phone number is required';
    if (!formData.email) newErrors.email = 'Email is required';
    if (!formData.currentStudy) newErrors.currentStudy = 'Please select your current study';
    if (!formData.competitiveExam) newErrors.competitiveExam = 'Please select a competitive exam';
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    setSubmitting(true);
    
    try {
      const response = await axios.post('http://localhost:5000/api/student/register', formData);
      if (response.data.success) {
        onRegister(formData);
      }
    } catch (error) {
      console.error('Registration error:', error);
      setErrors({ submit: 'Registration failed. Please try again.' });
      setSubmitting(false);
    }
  };

  const getEnabledExams = () => {
    if (formData.currentStudy === 'school') {
      return ['NEET', 'JEE'];
    } else if (formData.currentStudy === 'bachelor') {
      return ['GATE', 'TNPSC'];
    } else if (formData.currentStudy === 'master') {
      return ['NET', 'SET', 'GATE'];
    }
    return [];
  };

  const getEnabledMajors = () => {
    if (['NET', 'SET', 'GATE'].includes(formData.competitiveExam)) {
      return ['Computer Science'];
    }
    return Object.keys(majors || {});
  };

  if (loading) {
    return (
      <div className="student-form-container">
        <LoadingSpinner text="Loading your learning journey..." />
      </div>
    );
  }

  return (
    <div className="student-form-container">
      {/* Fixed Header */}
      <div className="student-form-header">
        <h2>Student Registration</h2>
        <p>Start your learning journey with us! 🚀</p>
      </div>
      
      {/* Scrollable Content */}
      <div className="student-form-content">
        {errors.submit && (
          <div className="error-container">
            <span>⚠️</span> {errors.submit}
          </div>
        )}
        
        <form id="student-form" onSubmit={handleSubmit}>
          {/* Personal Information Section */}
          <div className="student-form-section">
            <h3>
              <span>1</span>
              Personal Information
            </h3>
            
            {/* Row 1: Name and Phone */}
            <div className="student-form-row">
              <div className="student-float-group">
                <input
                  type="text"
                  name="name"
                  id="student-name"
                  value={formData.name}
                  onChange={handleChange}
                  placeholder="Enter your full name"
                  className={errors.name ? 'error' : ''}
                />
                <label htmlFor="student-name">Full Name *</label>
                {errors.name && <small>{errors.name}</small>}
              </div>

              <div className="student-float-group">
                <input
                  type="tel"
                  name="phone"
                  id="student-phone"
                  value={formData.phone}
                  onChange={handleChange}
                  placeholder="Enter 10-digit mobile number"
                  className={errors.phone ? 'error' : ''}
                />
                <label htmlFor="student-phone">Phone Number *</label>
                {errors.phone && <small>{errors.phone}</small>}
              </div>
            </div>

            {/* Email Field */}
            <div className="student-float-group">
              <input
                type="email"
                name="email"
                id="student-email"
                value={formData.email}
                onChange={handleChange}
                placeholder="Enter your email address"
                className={errors.email ? 'error' : ''}
              />
              <label htmlFor="student-email">Email Address *</label>
              {errors.email && <small>{errors.email}</small>}
            </div>

            {/* Row 2: City and State */}
            <div className="student-form-row">
              <div className="student-float-group">
                <input
                  type="text"
                  name="city"
                  id="student-city"
                  value={formData.city}
                  onChange={handleChange}
                  placeholder="Enter your city"
                />
                <label htmlFor="student-city">City</label>
              </div>

              <div className="student-float-group">
                <input
                  type="text"
                  name="state"
                  id="student-state"
                  value={formData.state}
                  onChange={handleChange}
                  placeholder="Enter your state"
                />
                <label htmlFor="student-state">State</label>
              </div>
            </div>
          </div>

          {/* Academic Information Section */}
          <div className="student-form-section">
            <h3>
              <span>2</span>
              Academic Information
            </h3>
            
            {/* Current Study */}
            <div className="student-form-group">
              <label className="student-form-label">
                <span>📚</span> Current Study *
              </label>
              <select
                name="currentStudy"
                value={formData.currentStudy}
                onChange={handleChange}
                className={`student-select ${errors.currentStudy ? 'error' : ''}`}
              >
                <option value="">Select your current study level</option>
                <option value="school">🎒 School (10th, 11th, 12th)</option>
                <option value="bachelor">📖 Bachelor Degree</option>
                <option value="master">🎓 Master Degree</option>
              </select>
              {errors.currentStudy && <small>{errors.currentStudy}</small>}
            </div>

            {/* Course (conditional) */}
            {formData.currentStudy && (
              <div className="student-form-group">
                <label className="student-form-label">
                  <span>📋</span> Course
                </label>
                <select
                  name="course"
                  value={formData.course}
                  onChange={handleChange}
                  className="student-select"
                >
                  <option value="">Select your course</option>
                  {formData.currentStudy === 'school' && courses.school?.map(course => (
                    <option key={course} value={course}>{course}</option>
                  ))}
                  {formData.currentStudy === 'bachelor' && courses.bachelor?.map(course => (
                    <option key={course} value={course}>{course}</option>
                  ))}
                  {formData.currentStudy === 'master' && courses.master?.map(course => (
                    <option key={course} value={course}>{course}</option>
                  ))}
                </select>
              </div>
            )}

            {/* Competitive Exam */}
            <div className="student-form-group">
              <label className="student-form-label">
                <span>🎯</span> Target Exam *
              </label>
              <select
                name="competitiveExam"
                value={formData.competitiveExam}
                onChange={handleChange}
                className={`student-select ${errors.competitiveExam ? 'error' : ''}`}
              >
                <option value="">Select your target exam</option>
                <option value="NEET" disabled={!getEnabledExams().includes('NEET')}>🩺 NEET</option>
                <option value="JEE" disabled={!getEnabledExams().includes('JEE')}>⚙️ JEE</option>
                <option value="GATE" disabled={!getEnabledExams().includes('GATE')}>💻 GATE</option>
                <option value="TNPSC" disabled={!getEnabledExams().includes('TNPSC')}>🏛️ TNPSC</option>
                <option value="NET" disabled={!getEnabledExams().includes('NET')}>📚 NET</option>
                <option value="SET" disabled={!getEnabledExams().includes('SET')}>📝 SET</option>
              </select>
              {errors.competitiveExam && <small>{errors.competitiveExam}</small>}
            </div>

            {/* Major */}
            <div className="student-form-group">
              <label className="student-form-label">
                <span>🔬</span> Major/Specialization
              </label>
              <select
                name="major"
                value={formData.major}
                onChange={handleChange}
                className="student-select"
              >
                <option value="">Select your specialization</option>
                {getEnabledMajors().map(major => (
                  <option key={major} value={major}>{major}</option>
                ))}
              </select>
            </div>

            {/* TNPSC Group (conditional) */}
            {formData.competitiveExam === 'TNPSC' && (
              <div className="student-form-group">
                <label className="student-form-label">
                  <span>📌</span> TNPSC Group
                </label>
                <select
                  name="tnpscGroup"
                  value={formData.tnpscGroup}
                  onChange={handleChange}
                  className="student-select"
                >
                  <option value="">Select TNPSC Group</option>
                  {tnpscGroups.map(group => (
                    <option key={group} value={group}>{group}</option>
                  ))}
                </select>
              </div>
            )}
          </div>

          {/* Preferences Section */}
          <div className="student-form-section">
            <h3>
              <span>3</span>
              Learning Preferences
            </h3>
            
            {/* Needs (Multiple Select) */}
            <div className="student-form-group">
              <label className="student-form-label">
                <span>💡</span> What do you need help with?
              </label>
              <select
                multiple
                value={formData.needs}
                onChange={handleNeedsChange}
                className="student-select"
                style={{ minHeight: '140px' }}
              >
                <option value="stress_analysis">📊 Stress Level Analysis</option>
                <option value="topic_difficulty">📈 Topic Difficulty Analysis</option>
                <option value="meme_analysis">😂 Meme Sarcasm Analysis</option>
                <option value="study_plan">📅 Personalized Study Plan</option>
                <option value="practice_questions">✍️ Practice Questions</option>
              </select>
              <div className="student-helper-text">
                <i>ℹ️</i> Hold Ctrl/Cmd to select multiple options
              </div>
            </div>
          </div>
        </form>
      </div>
      
      {/* Fixed Footer with Submit Button */}
      <div className="student-form-footer">
        <button 
          type="submit"
          form="student-form"
          className="student-submit-btn"
          disabled={submitting}
        >
          {submitting ? (
            <>
              <span className="button-loader">
                <div className="spinner small"></div>
              </span>
              Registering...
            </>
          ) : '🎓 Start Learning Journey'}
        </button>
      </div>
    </div>
  );
};

export default StudentForm;