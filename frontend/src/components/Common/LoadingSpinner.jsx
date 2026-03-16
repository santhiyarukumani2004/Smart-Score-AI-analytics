import React from 'react';
import './LoadingSpinner.css';

const LoadingSpinner = ({ 
  size = 'medium', 
  text = 'Loading...',
  fullScreen = false 
}) => {
  return (
    <div className={`loading-container ${fullScreen ? 'fullscreen' : ''}`}>
      <div className={`spinner ${size}`}></div>
      {text && <p className="loading-text">{text}</p>}
    </div>
  );
};

// Variants for different use cases
export const PageLoader = () => (
  <LoadingSpinner fullScreen={true} text="Loading Smart Score AI..." />
);

export const ChartLoader = () => (
  <div className="chart-loader">
    <div className="spinner medium"></div>
    <p className="loading-text">Loading chart data...</p>
  </div>
);

export const ButtonLoader = () => (
  <span className="button-loader">
    <div className="spinner small"></div>
  </span>
);

export const SkeletonLoader = () => (
  <div className="skeleton-loader">
    <div className="skeleton-line"></div>
    <div className="skeleton-line"></div>
    <div className="skeleton-line"></div>
    <div className="skeleton-line"></div>
  </div>
);

export const PulseLoader = ({ text = 'Loading...' }) => (
  <div className="loading-container">
    <div className="pulse-loader">
      <div className="pulse-dot"></div>
      <div className="pulse-dot"></div>
      <div className="pulse-dot"></div>
    </div>
    {text && <p className="loading-text">{text}</p>}
  </div>
);

export const ProgressLoader = ({ text = 'Loading...' }) => (
  <div className="loading-container">
    <div className="progress-loader">
      <div className="progress-bar"></div>
    </div>
    {text && <p className="loading-text">{text}</p>}
  </div>
);

export const InitialLoader = () => (
  <div className="initial-loader">
    <div className="initial-loader-content">
      <div className="spinner large"></div>
      <p className="loading-text">Smart Score AI</p>
    </div>
  </div>
);

export default LoadingSpinner;