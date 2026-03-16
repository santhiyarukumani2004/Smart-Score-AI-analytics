import React from 'react';
import { Bar, Line } from 'react-chartjs-2';
import './TeacherDashboard.css';

const YearAnalysis = ({ data = [], selectedExam = 'all' }) => {
  console.log('YearAnalysis received:', data.length, 'years', 'for exam:', selectedExam);

  // Helper function to get difficulty level and color (Google colors)
  const getDifficultyInfo = (value) => {
    const numValue = parseFloat(value) || 0;
    if (numValue >= 2.8) {
      return { 
        level: 'Hard', 
        color: '#EA4335', // Google Red
        bgColor: '#EA433520',
        secondaryColor: '#EA4335'
      };
    } else if (numValue >= 1.0) {
      return { 
        level: 'Medium', 
        color: '#FBBC05', // Google Yellow
        bgColor: '#FBBC0520',
        secondaryColor: '#FBBC05'
      };
    } else {
      return { 
        level: 'Easy', 
        color: '#34A853', // Google Green
        bgColor: '#34A85320',
        secondaryColor: '#34A853'
      };
    }
  };

  if (!data || data.length === 0) {
    return (
      <div style={styles.container}>
        <div style={styles.header}>
          <div>
            <h1 style={styles.title}>📅 Year-wise Analysis</h1>
            <p style={styles.subtitle}>{selectedExam !== 'all' ? selectedExam : 'All Exams'}</p>
          </div>
        </div>
        <div style={styles.noData}>
          <p>No year data available for the selected exam</p>
          <p style={{ color: '#9aa0a6', marginTop: 8 }}>
            {selectedExam !== 'all' 
              ? `No data found for ${selectedExam}. Try selecting a different exam.`
              : 'No year data available in the database.'}
          </p>
        </div>
      </div>
    );
  }

  const years = data.map(d => d.year);
  
  // Bar Chart Data with Google colors
  const barData = {
    labels: years,
    datasets: [
      {
        label: 'Tweet Stress',
        data: data.map(d => d.tweet_stress),
        backgroundColor: '#4285F4', // Google Blue
        borderColor: '#4285F4',
        borderWidth: 0,
        borderRadius: 8
      },
      {
        label: 'Meme Stress',
        data: data.map(d => d.meme_stress),
        backgroundColor: '#FBBC05', // Google Yellow
        borderColor: '#FBBC05',
        borderWidth: 0,
        borderRadius: 8
      },
      {
        label: 'Paper Difficulty',
        data: data.map(d => d.paper_difficulty),
        backgroundColor: '#34A853', // Google Green
        borderColor: '#34A853',
        borderWidth: 0,
        borderRadius: 8
      }
    ]
  };

  // Line Chart Data with Neo4j-inspired styling
  const lineData = {
    labels: years,
    datasets: [
      {
        label: 'Fused Difficulty',
        data: data.map(d => d.fused_difficulty),
        borderColor: '#4285F4',
        backgroundColor: 'rgba(66, 133, 244, 0.1)',
        tension: 0.4,
        fill: true,
        pointBackgroundColor: data.map(d => {
          const diff = parseFloat(d.fused_difficulty) || 0;
          if (diff >= 2.8) return '#EA4335';
          if (diff >= 1.0) return '#FBBC05';
          return '#34A853';
        }),
        pointBorderColor: '#202124',
        pointBorderWidth: 2,
        pointRadius: 6,
        pointHoverRadius: 8,
        borderWidth: 3
      }
    ]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    animation: false,
    plugins: {
      legend: { 
        position: 'bottom',
        labels: { color: '#e8eaed', font: { size: 11 } }
      },
      tooltip: { 
        backgroundColor: '#202124',
        titleColor: '#e8eaed',
        bodyColor: '#9aa0a6',
        padding: 12,
        cornerRadius: 8
      }
    },
    scales: {
      y: { 
        beginAtZero: true, 
        max: 4.0,
        grid: { color: '#3c4043' }, 
        ticks: { color: '#9aa0a6' },
        title: { display: true, text: 'Stress Level', color: '#9aa0a6' }
      },
      x: { 
        grid: { display: false }, 
        ticks: { color: '#9aa0a6' } 
      }
    }
  };

  // Google AI Dashboard Styles
  const styles = {
    container: {
      padding: 32,
      background: '#202124',
      borderRadius: 16,
      color: '#e8eaed',
      fontFamily: 'Google Sans, system-ui, -apple-system, sans-serif',
      minHeight: '100vh'
    },
    header: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: 32,
      paddingBottom: 16,
      borderBottom: '1px solid #3c4043'
    },
    title: {
      margin: 0,
      fontSize: 28,
      fontWeight: 500,
      color: '#e8eaed',
      letterSpacing: '-0.5px'
    },
    subtitle: {
      margin: '4px 0 0',
      fontSize: 14,
      color: '#9aa0a6'
    },
    infoBox: {
      background: '#2d2e30',
      padding: 20,
      borderRadius: 12,
      border: '1px solid #3c4043',
      marginBottom: 24
    },
    infoTitle: {
      margin: '0 0 12px 0',
      fontSize: 16,
      fontWeight: 500,
      color: '#e8eaed'
    },
    infoStats: {
      display: 'flex',
      gap: 24,
      flexWrap: 'wrap'
    },
    infoItem: {
      display: 'flex',
      alignItems: 'center',
      gap: 8
    },
    infoDot: {
      width: 12,
      height: 12,
      borderRadius: '50%'
    },
    chartsGrid: {
      display: 'grid',
      gridTemplateColumns: '1fr 1fr',
      gap: 20,
      marginBottom: 24
    },
    chartCard: {
      background: '#2d2e30',
      borderRadius: 16,
      padding: 20,
      border: '1px solid #3c4043'
    },
    chartTitle: {
      margin: '0 0 16px 0',
      fontSize: 16,
      fontWeight: 500,
      color: '#e8eaed'
    },
    chartWrapper: {
      height: 350,
      width: '100%'
    },
    tableCard: {
      background: '#2d2e30',
      borderRadius: 16,
      padding: 24,
      border: '1px solid #3c4043'
    },
    tableTitle: {
      margin: '0 0 20px 0',
      fontSize: 18,
      fontWeight: 500,
      color: '#e8eaed'
    },
    tableContainer: {
      overflowX: 'auto',
      borderRadius: 12,
      border: '1px solid #3c4043'
    },
    table: {
      width: '100%',
      borderCollapse: 'collapse',
      minWidth: 1000,
      fontSize: 13
    },
    th: {
      background: '#35363a',
      color: '#9aa0a6',
      padding: '16px',
      textAlign: 'left',
      fontWeight: 500,
      fontSize: 12,
      textTransform: 'uppercase',
      letterSpacing: '0.5px'
    },
    td: {
      padding: '12px 16px',
      borderBottom: '1px solid #3c4043',
      color: '#e8eaed'
    },
    rowEven: {
      background: '#2d2e30'
    },
    rowOdd: {
      background: '#313234'
    },
    scoreContainer: {
      display: 'flex',
      alignItems: 'center',
      gap: 12
    },
    progressBar: {
      width: 100,
      height: 4,
      background: '#3c4043',
      borderRadius: 2,
      overflow: 'hidden'
    },
    progressFill: {
      height: '100%',
      borderRadius: 2
    },
    badge: {
      padding: '4px 12px',
      borderRadius: 100,
      fontSize: 11,
      fontWeight: 500,
      display: 'inline-block',
      border: '1px solid'
    },
    legend: {
      display: 'flex',
      gap: 24,
      marginTop: 24,
      padding: 16,
      background: '#2d2e30',
      borderRadius: 12,
      border: '1px solid #3c4043',
      justifyContent: 'center',
      flexWrap: 'wrap'
    },
    legendItem: {
      display: 'flex',
      alignItems: 'center',
      gap: 8
    },
    noData: {
      textAlign: 'center',
      padding: 60,
      color: '#9aa0a6',
      background: '#2d2e30',
      borderRadius: 12,
      border: '1px dashed #3c4043'
    }
  };

  return (
    <div style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <div>
          <h1 style={styles.title}>📅 Year-wise Analysis</h1>
          <p style={styles.subtitle}>
            {selectedExam !== 'all' ? selectedExam : 'All Exams'} • {data.length} years analyzed
          </p>
        </div>
      </div>

      {/* Threshold Info Box */}
      <div style={styles.infoBox}>
        <h3 style={styles.infoTitle}>📊 Difficulty Thresholds</h3>
        <div style={styles.infoStats}>
          <div style={styles.infoItem}>
            <div style={{...styles.infoDot, background: '#EA4335'}} />
            <span>Hard: ≥ 2.8</span>
          </div>
          <div style={styles.infoItem}>
            <div style={{...styles.infoDot, background: '#FBBC05'}} />
            <span>Medium: 1.0 - 2.79</span>
          </div>
          <div style={styles.infoItem}>
            <div style={{...styles.infoDot, background: '#34A853'}} />
            <span>Easy: &lt; 1.0</span>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div style={styles.chartsGrid}>
        <div style={styles.chartCard}>
          <h3 style={styles.chartTitle}>Stress Sources by Year</h3>
          <div style={styles.chartWrapper}>
            <Bar key={`bar-${selectedExam}`} data={barData} options={options} />
          </div>
        </div>
        
        <div style={styles.chartCard}>
          <h3 style={styles.chartTitle}>Fused Difficulty Trend</h3>
          <div style={styles.chartWrapper}>
            <Line key={`line-${selectedExam}`} data={lineData} options={options} />
          </div>
        </div>
      </div>

      {/* Table */}
      <div style={styles.tableCard}>
        <h3 style={styles.tableTitle}>Year-wise Summary Table</h3>
        <div style={styles.tableContainer}>
          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.th}>Year</th>
                <th style={styles.th}>Exams</th>
                <th style={styles.th}>Tweet Stress</th>
                <th style={styles.th}>Meme Stress</th>
                <th style={styles.th}>Paper Diff</th>
                <th style={styles.th}>Fused Diff</th>
                <th style={styles.th}>Level</th>
                <th style={styles.th}>Total Entries</th>
              </tr>
            </thead>
            <tbody>
              {data.map((item, index) => {
                const tweetInfo = getDifficultyInfo(item.tweet_stress);
                const memeInfo = getDifficultyInfo(item.meme_stress);
                const paperInfo = getDifficultyInfo(item.paper_difficulty);
                const fusedInfo = getDifficultyInfo(item.fused_difficulty);
                
                return (
                  <tr key={index} style={index % 2 === 0 ? styles.rowEven : styles.rowOdd}>
                    <td style={styles.td}><strong style={{ color: '#e8eaed' }}>{item.year}</strong></td>
                    <td style={styles.td}>{item.exam_count}</td>
                    
                    {/* Tweet Stress with Progress Bar */}
                    <td style={styles.td}>
                      <div style={styles.scoreContainer}>
                        <span style={{ color: tweetInfo.color, fontWeight: 500, minWidth: 40 }}>
                          {item.tweet_stress}
                        </span>
                        <div style={styles.progressBar}>
                          <div 
                            style={{ 
                              width: `${(item.tweet_stress / 4) * 100}%`,
                              height: '100%',
                              backgroundColor: tweetInfo.color,
                              borderRadius: 2
                            }} 
                          />
                        </div>
                      </div>
                    </td>
                    
                    {/* Meme Stress with Progress Bar */}
                    <td style={styles.td}>
                      <div style={styles.scoreContainer}>
                        <span style={{ color: memeInfo.color, fontWeight: 500, minWidth: 40 }}>
                          {item.meme_stress}
                        </span>
                        <div style={styles.progressBar}>
                          <div 
                            style={{ 
                              width: `${(item.meme_stress / 4) * 100}%`,
                              height: '100%',
                              backgroundColor: memeInfo.color,
                              borderRadius: 2
                            }} 
                          />
                        </div>
                      </div>
                    </td>
                    
                    {/* Paper Diff with Progress Bar */}
                    <td style={styles.td}>
                      <div style={styles.scoreContainer}>
                        <span style={{ color: paperInfo.color, fontWeight: 500, minWidth: 40 }}>
                          {item.paper_difficulty}
                        </span>
                        <div style={styles.progressBar}>
                          <div 
                            style={{ 
                              width: `${(item.paper_difficulty / 4) * 100}%`,
                              height: '100%',
                              backgroundColor: paperInfo.color,
                              borderRadius: 2
                            }} 
                          />
                        </div>
                      </div>
                    </td>
                    
                    {/* Fused Diff with Progress Bar */}
                    <td style={styles.td}>
                      <div style={styles.scoreContainer}>
                        <span style={{ color: fusedInfo.color, fontWeight: 500, minWidth: 40 }}>
                          {item.fused_difficulty}
                        </span>
                        <div style={styles.progressBar}>
                          <div 
                            style={{ 
                              width: `${(item.fused_difficulty / 4) * 100}%`,
                              height: '100%',
                              backgroundColor: fusedInfo.color,
                              borderRadius: 2
                            }} 
                          />
                        </div>
                      </div>
                    </td>
                    
                    {/* Level Badge */}
                    <td style={styles.td}>
                      <span style={{
                        ...styles.badge,
                        background: fusedInfo.bgColor,
                        color: fusedInfo.color,
                        borderColor: fusedInfo.color
                      }}>
                        {fusedInfo.level}
                      </span>
                    </td>
                    
                    <td style={styles.td}>{item.total_entries}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Legend */}
      <div style={styles.legend}>
        <div style={styles.legendItem}>
          <div style={{ width: 16, height: 16, background: '#EA4335', borderRadius: 4 }} />
          <span>Hard (≥ 2.8)</span>
        </div>
        <div style={styles.legendItem}>
          <div style={{ width: 16, height: 16, background: '#FBBC05', borderRadius: 4 }} />
          <span>Medium (1.0 - 2.79)</span>
        </div>
        <div style={styles.legendItem}>
          <div style={{ width: 16, height: 16, background: '#34A853', borderRadius: 4 }} />
          <span>Easy (&lt; 1.0)</span>
        </div>
      </div>
    </div>
  );
};

export default YearAnalysis;