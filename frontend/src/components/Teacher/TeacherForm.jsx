import React, { useState, useEffect } from 'react';
import axios from 'axios';
import LoadingSpinner from '../Common/LoadingSpinner';
import './TeacherForm.css';

const TeacherForm = ({ onRegister }) => {
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    email: '',
    qualification: '',
    specialization: '',
    experience: '',
    institute: '',
    subjects: [],
    exams: [],
    preferred_exams: [] // For filtering dashboard data
  });

  const [subjects, setSubjects] = useState([]);
  const [exams, setExams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [errors, setErrors] = useState({});
  const [experienceValue, setExperienceValue] = useState(0);

  useEffect(() => {
    fetchDropdownData();
  }, []);

  const fetchDropdownData = async () => {
    try {
      // Simulate loading delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const subjectsList = [
        'Physics', 'Chemistry', 'Mathematics', 'Biology', 
        'Computer Science', 'History', 'Geography', 'Polity', 
        'Economy', 'English', 'Tamil', 'Commerce'
      ];
      
      const examsList = [
        'JEE', 'NEET', 'GATE', 'TNPSC', 'UPSC', 'NET', 'SET',
        'CBSE', 'ICSE', 'State Board'
      ];
      
      setSubjects(subjectsList);
      setExams(examsList);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching data:', error);
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

  const handleExperienceChange = (e) => {
    const value = e.target.value;
    setExperienceValue(value);
    setFormData(prev => ({ ...prev, experience: value }));
  };

  const toggleSubject = (subject) => {
    setFormData(prev => {
      const newSubjects = prev.subjects.includes(subject)
        ? prev.subjects.filter(s => s !== subject)
        : [...prev.subjects, subject];
      return { ...prev, subjects: newSubjects };
    });
  };

  const toggleExam = (exam) => {
    setFormData(prev => {
      const newExams = prev.exams.includes(exam)
        ? prev.exams.filter(e => e !== exam)
        : [...prev.exams, exam];
      return { ...prev, exams: newExams };
    });
  };

  const togglePreferredExam = (exam) => {
    setFormData(prev => {
      const newPreferred = prev.preferred_exams.includes(exam)
        ? prev.preferred_exams.filter(e => e !== exam)
        : [...prev.preferred_exams, exam];
      return { ...prev, preferred_exams: newPreferred };
    });
  };

  const validateForm = () => {
    const newErrors = {};
    if (!formData.name) newErrors.name = 'Name is required';
    if (!formData.phone) newErrors.phone = 'Phone number is required';
    if (!formData.email) newErrors.email = 'Email is required';
    if (!formData.qualification) newErrors.qualification = 'Qualification is required';
    if (!formData.institute) newErrors.institute = 'Institute name is required';
    if (formData.subjects.length === 0) newErrors.subjects = 'Please select at least one subject';
    if (formData.exams.length === 0) newErrors.exams = 'Please select at least one exam';
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    setSubmitting(true);
    
    try {
      // Send data to backend - matches teacher_register API
      const response = await axios.post('http://localhost:5000/api/teacher/register', {
        name: formData.name,
        email: formData.email,
        phone: formData.phone,
        qualification: formData.qualification,
        specialization: formData.specialization,
        experience: parseInt(formData.experience),
        institute: formData.institute,
        subjects: formData.subjects,
        exams: formData.exams,
        preferred_exams: formData.preferred_exams // For filtering dashboard
      });
      
      if (response.data.success) {
        // Pass data to parent component
        onRegister({
          ...formData,
          teacher_id: response.data.teacher_id
        });
      }
    } catch (error) {
      console.error('Registration error:', error);
      setErrors({ submit: 'Registration failed. Please try again.' });
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="teacher-form-container">
        <LoadingSpinner text="Loading academic portal..." />
      </div>
    );
  }

  return (
    <div className="teacher-form-container">
      {/* Fixed Header */}
      <div className="teacher-form-header">
        <h2>Teacher Registration</h2>
        <p>Join our academic excellence program</p>
      </div>
      
      {/* Scrollable Content */}
      <div className="teacher-form-content">
        {errors.submit && (
          <div className="error-container">
            <span>⚠️</span> {errors.submit}
          </div>
        )}
        
        <form id="teacher-form" onSubmit={handleSubmit}>
          {/* Personal Information Section */}
          <div className="teacher-form-section">
            <h3>
              <span>1</span>
              Personal Information
            </h3>
            
            <div className="teacher-form-row">
              {/* Name field with floating label */}
              <div className="teacher-float-group">
                <input
                  type="text"
                  name="name"
                  id="teacher-name"
                  value={formData.name}
                  onChange={handleChange}
                  placeholder="Enter your full name"
                  className={errors.name ? 'error' : ''}
                />
                <label htmlFor="teacher-name">Full Name *</label>
                {errors.name && <small>{errors.name}</small>}
              </div>

              {/* Phone field with floating label */}
              <div className="teacher-float-group">
                <input
                  type="tel"
                  name="phone"
                  id="teacher-phone"
                  value={formData.phone}
                  onChange={handleChange}
                  placeholder="+91 98765 43210"
                  className={errors.phone ? 'error' : ''}
                />
                <label htmlFor="teacher-phone">Phone Number *</label>
                {errors.phone && <small>{errors.phone}</small>}
              </div>
            </div>

            {/* Email field with floating label */}
            <div className="teacher-float-group">
              <input
                type="email"
                name="email"
                id="teacher-email"
                value={formData.email}
                onChange={handleChange}
                placeholder="teacher@institution.edu"
                className={errors.email ? 'error' : ''}
              />
              <label htmlFor="teacher-email">Email Address *</label>
              {errors.email && <small>{errors.email}</small>}
            </div>
          </div>

          {/* Professional Information Section */}
          <div className="teacher-form-section">
            <h3>
              <span>2</span>
              Professional Information
            </h3>
            
            {/* Qualification field with floating label */}
            <div className="teacher-float-group">
              <input
                type="text"
                name="qualification"
                id="teacher-qualification"
                value={formData.qualification}
                onChange={handleChange}
                placeholder="e.g., M.Sc, B.Ed, Ph.D"
                className={errors.qualification ? 'error' : ''}
              />
              <label htmlFor="teacher-qualification">Highest Qualification *</label>
              {errors.qualification && <small>{errors.qualification}</small>}
            </div>

            {/* Specialization field with floating label */}
            <div className="teacher-float-group">
              <input
                type="text"
                name="specialization"
                id="teacher-specialization"
                value={formData.specialization}
                onChange={handleChange}
                placeholder="e.g., Organic Chemistry, Quantum Physics"
              />
              <label htmlFor="teacher-specialization">Specialization</label>
            </div>

            {/* Institute field with floating label */}
            <div className="teacher-float-group">
              <input
                type="text"
                name="institute"
                id="teacher-institute"
                value={formData.institute}
                onChange={handleChange}
                placeholder="Name of your institution"
                className={errors.institute ? 'error' : ''}
              />
              <label htmlFor="teacher-institute">Institution/College *</label>
              {errors.institute && <small>{errors.institute}</small>}
            </div>

            {/* Experience (regular group - not floating) */}
            <div className="teacher-form-group">
              <label className="teacher-form-label">Teaching Experience</label>
              <div className="teacher-experience-card">
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                  <span>Years of experience:</span>
                  <span style={{ 
                    background: '#b45309', 
                    color: 'white', 
                    padding: '0.25rem 1rem', 
                    borderRadius: '20px',
                    fontWeight: 'bold'
                  }}>
                    {experienceValue} years
                  </span>
                </div>
                <div className="teacher-experience-slider">
                  <input
                    type="range"
                    min="0"
                    max="40"
                    value={experienceValue}
                    onChange={handleExperienceChange}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Expertise Section */}
          <div className="teacher-form-section">
            <h3>
              <span>3</span>
              Areas of Expertise
            </h3>
            
            <div className="teacher-form-group">
              <label className="teacher-form-label">Subjects you teach *</label>
              <div className="teacher-subject-tags">
                {subjects.map(subject => (
                  <span
                    key={subject}
                    className={`teacher-subject-tag ${formData.subjects.includes(subject) ? 'selected' : ''}`}
                    onClick={() => toggleSubject(subject)}
                  >
                    {subject}
                    {formData.subjects.includes(subject) && ' ✓'}
                  </span>
                ))}
              </div>
              {errors.subjects && <small>{errors.subjects}</small>}
              <div className="teacher-helper-text">
                <i>ℹ️</i> Click on subjects to select/deselect
              </div>
            </div>

            <div className="teacher-form-group">
              <label className="teacher-form-label">Exams you prepare students for *</label>
              <div className="teacher-subject-tags">
                {exams.map(exam => (
                  <span
                    key={exam}
                    className={`teacher-subject-tag ${formData.exams.includes(exam) ? 'selected' : ''}`}
                    onClick={() => toggleExam(exam)}
                  >
                    {exam}
                    {formData.exams.includes(exam) && ' ✓'}
                  </span>
                ))}
              </div>
              {errors.exams && <small>{errors.exams}</small>}
              <div className="teacher-helper-text">
                <i>ℹ️</i> Click on exams to select/deselect
              </div>
            </div>

            {/* Filter Preferences Section */}
            <div className="teacher-form-group" style={{ marginTop: '2rem' }}>
              <label className="teacher-form-label">Dashboard Filter Preferences</label>
              <p style={{ color: '#94a3b8', fontSize: '0.9rem', marginBottom: '1rem' }}>
                Select exams you want to see in your dashboard (leave empty to see all)
              </p>
              <div className="teacher-subject-tags">
                {exams.map(exam => (
                  <span
                    key={`pref-${exam}`}
                    className={`teacher-subject-tag ${formData.preferred_exams.includes(exam) ? 'selected' : ''}`}
                    onClick={() => togglePreferredExam(exam)}
                    style={{ background: formData.preferred_exams.includes(exam) ? '#3b82f6' : '#2d3748' }}
                  >
                    {exam}
                    {formData.preferred_exams.includes(exam) && ' ✓'}
                  </span>
                ))}
              </div>
              <div className="teacher-helper-text">
                <i>🔍</i> These will be used to filter your dashboard data
              </div>
            </div>
          </div>
        </form>
      </div>
      
      {/* Fixed Footer with Submit Button */}
      <div className="teacher-form-footer">
        <button 
          type="submit"
          form="teacher-form"
          className="teacher-submit-btn"
          disabled={submitting}
        >
          {submitting ? (
            <>
              <span className="button-loader">
                <div className="spinner small"></div>
              </span>
              Processing...
            </>
          ) : '📋 Complete Registration'}
        </button>
      </div>
    </div>
  );
};

export default TeacherForm;