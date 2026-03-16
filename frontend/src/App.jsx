import React, { useState, useEffect } from 'react'; // Add missing imports
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { InitialLoader } from './components/Common/LoadingSpinner';
// In App.jsx or index.js at the very top
import './config/chartConfig';
import HomePage from './pages/HomePage';
import StudentPortal from './pages/StudentPortal';
import TeacherPortal from './pages/TeacherPortal';
import './App.css';

function App() {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate initial loading
    const timer = setTimeout(() => setLoading(false), 2000);
    return () => clearTimeout(timer); // Cleanup timeout
  }, []);

  if (loading) {
    return <InitialLoader />;
  }
  
  return (
    <Router>
      <div className="app">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/student" element={<StudentPortal />} />
          <Route path="/teacher" element={<TeacherPortal />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;