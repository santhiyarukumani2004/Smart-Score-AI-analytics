import React from 'react';
import { useNavigate } from 'react-router-dom';

const Header = () => {
  const navigate = useNavigate();

  return (
    <header style={{
      background: 'rgba(255, 255, 255, 0.1)',
      backdropFilter: 'blur(10px)',
      padding: '1rem 2rem',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      zIndex: 1000
    }}>
      <div 
        onClick={() => navigate('/')}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '1rem',
          cursor: 'pointer'
        }}
      >
        <img src="/logo.png" alt="Logo" style={{ height: '40px' }} />
        <h2 style={{ color: 'white', margin: 0 }}>Smart Score AI</h2>
      </div>
    </header>
  );
};

export default Header;