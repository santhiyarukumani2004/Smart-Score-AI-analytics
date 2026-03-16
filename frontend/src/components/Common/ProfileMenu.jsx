import React from 'react';
import { useNavigate } from 'react-router-dom';
import './ProfileMenu.css';

const ProfileMenu = ({ data, onClose }) => {
  const navigate = useNavigate();

  // Format date for display
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleLogout = () => {
    // Clear all storage
    localStorage.clear();
    sessionStorage.clear();
    
    // Navigate to home page
    navigate('/', { replace: true });
    
    // Close the profile menu
    onClose();
  };

  const handleEditProfile = () => {
    alert('Edit profile feature coming soon!');
    onClose();
  };

  return (
    <div className="profile-popup">
      <div className="profile-header">
        <h3>Profile Information</h3>
        <button className="close-btn" onClick={onClose}>×</button>
      </div>
      
      <div className="profile-avatar">
        {data?.name?.charAt(0) || 'U'}
      </div>

      <div className="profile-details">
        {/* Basic Info Section */}
        <div className="profile-section">
          <h4 className="profile-section-title">Basic Information</h4>
          <div className="profile-info-row">
            <span className="info-label">Full Name</span>
            <span className="info-value">{data?.name || 'Not provided'}</span>
          </div>

          <div className="profile-info-row">
            <span className="info-label">Email</span>
            <span className="info-value">{data?.email || 'Not provided'}</span>
          </div>

          <div className="profile-info-row">
            <span className="info-label">Phone</span>
            <span className="info-value">{data?.phone || 'Not provided'}</span>
          </div>
        </div>

        {/* Student-specific fields */}
        {(data?.currentStudy || data?.course || data?.major || data?.competitiveExam || data?.tnpscGroup) && (
          <>
            <div className="profile-divider"></div>
            <div className="profile-section">
              <h4 className="profile-section-title">Academic Information</h4>
              
              {data?.currentStudy && (
                <div className="profile-info-row">
                  <span className="info-label">Current Study</span>
                  <span className="info-value capitalize">{data.currentStudy}</span>
                </div>
              )}

              {data?.course && (
                <div className="profile-info-row">
                  <span className="info-label">Course</span>
                  <span className="info-value">{data.course}</span>
                </div>
              )}

              {data?.major && (
                <div className="profile-info-row">
                  <span className="info-label">Major</span>
                  <span className="info-value">{data.major}</span>
                </div>
              )}

              {data?.competitiveExam && (
                <div className="profile-info-row">
                  <span className="info-label">Target Exam</span>
                  <span className="info-value exam-badge-small">{data.competitiveExam}</span>
                </div>
              )}

              {data?.tnpscGroup && (
                <div className="profile-info-row">
                  <span className="info-label">TNPSC Group</span>
                  <span className="info-value">{data.tnpscGroup}</span>
                </div>
              )}
            </div>
          </>
        )}

        {/* Teacher-specific fields */}
        {(data?.institution || data?.department || data?.experience || data?.subjects?.length > 0 || data?.exams?.length > 0) && (
          <>
            <div className="profile-divider"></div>
            <div className="profile-section">
              <h4 className="profile-section-title">Professional Information</h4>
              
              {data?.institution && (
                <div className="profile-info-row">
                  <span className="info-label">Institution</span>
                  <span className="info-value">{data.institution}</span>
                </div>
              )}

              {data?.department && (
                <div className="profile-info-row">
                  <span className="info-label">Department</span>
                  <span className="info-value">{data.department}</span>
                </div>
              )}

              {data?.experience && (
                <div className="profile-info-row">
                  <span className="info-label">Experience</span>
                  <span className="info-value">{data.experience} years</span>
                </div>
              )}

              {data?.subjects && data.subjects.length > 0 && (
                <div className="profile-info-row">
                  <span className="info-label">Subjects</span>
                  <div className="tags-container">
                    {data.subjects.map((subject, index) => (
                      <span key={index} className="subject-tag">{subject}</span>
                    ))}
                  </div>
                </div>
              )}

              {data?.exams && data.exams.length > 0 && (
                <div className="profile-info-row">
                  <span className="info-label">Exams</span>
                  <div className="tags-container">
                    {data.exams.map((exam, index) => (
                      <span key={index} className="exam-tag">{exam}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </>
        )}

        {/* Location fields */}
        {(data?.city || data?.state) && (
          <>
            <div className="profile-divider"></div>
            <div className="profile-section">
              <h4 className="profile-section-title">Location</h4>
              
              {data?.city && (
                <div className="profile-info-row">
                  <span className="info-label">City</span>
                  <span className="info-value">{data.city}</span>
                </div>
              )}
              
              {data?.state && (
                <div className="profile-info-row">
                  <span className="info-label">State</span>
                  <span className="info-value">{data.state}</span>
                </div>
              )}
            </div>
          </>
        )}

        {/* Needs/Interests */}
        {data?.needs && data.needs.length > 0 && (
          <>
            <div className="profile-divider"></div>
            <div className="profile-section">
              <h4 className="profile-section-title">Interests</h4>
              <div className="needs-tags">
                {data.needs.map((need, index) => (
                  <span key={index} className="need-tag">
                    {need.replace('_', ' ')}
                  </span>
                ))}
              </div>
            </div>
          </>
        )}

        {/* Last active (if available) */}
        {data?.lastActive && (
          <div className="profile-section last-active">
            <div className="profile-info-row">
              <span className="info-label">Last Active</span>
              <span className="info-value">{formatDate(data.lastActive)}</span>
            </div>
          </div>
        )}
      </div>

      <div className="profile-actions">
        <button className="edit-profile-btn" onClick={handleEditProfile}>
          ✏️ Edit Profile
        </button>
        <button className="logout-btn" onClick={handleLogout}>
          🚪 Logout
        </button>
      </div>
    </div>
  );
};

export default ProfileMenu;