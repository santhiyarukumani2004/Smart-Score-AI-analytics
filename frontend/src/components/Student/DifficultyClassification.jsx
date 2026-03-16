import React from 'react';
import { Bar, Pie, Line } from 'react-chartjs-2';

const DifficultyClassification = ({ 
  classification = [], 
  subjectComparison = [], 
  yearData = [],
  stressPieData = {},
  difficultyDistribution = {}
}) => {
  console.log('DifficultyClassification received:', { 
    classification, 
    subjectComparison, 
    yearData, 
    stressPieData,
    difficultyDistribution
  });

  const hasData = classification.length > 0 && classification.some(item => item.count > 0);
  const hasSubjectData = subjectComparison && subjectComparison.length > 0;
  
  // Calculate total topics from classification
  const totalTopics = classification.reduce((sum, item) => sum + item.count, 0);
  
  // Prepare charts data
  const years = yearData.map(item => item.year);
  
  // Line chart for year-wise trends
  const lineChartData = {
    labels: years,
    datasets: [
      {
        label: 'Tweet Stress',
        data: yearData.map(item => item.tweet_stress),
        borderColor: '#4285F4',
        backgroundColor: 'rgba(66, 133, 244, 0.1)',
        tension: 0.4,
        fill: false,
        borderWidth: 2,
        pointBackgroundColor: '#4285F4',
        pointBorderColor: '#202124',
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6
      },
      {
        label: 'Meme Stress',
        data: yearData.map(item => item.meme_stress),
        borderColor: '#FBBC05',
        backgroundColor: 'rgba(251, 188, 5, 0.1)',
        tension: 0.4,
        fill: false,
        borderWidth: 2,
        pointBackgroundColor: '#FBBC05',
        pointBorderColor: '#202124',
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6
      },
      {
        label: 'Paper Difficulty',
        data: yearData.map(item => item.paper_difficulty),
        borderColor: '#34A853',
        backgroundColor: 'rgba(52, 168, 83, 0.1)',
        tension: 0.4,
        fill: false,
        borderWidth: 2,
        pointBackgroundColor: '#34A853',
        pointBorderColor: '#202124',
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6
      }
    ]
  };

  // Subject Bar Chart Data
  const subjectBarData = {
    labels: subjectComparison.map(item => item.subject),
    datasets: [
      {
        label: 'Number of Topics',
        data: subjectComparison.map(item => item.unique_topics),
        backgroundColor: subjectComparison.map((_, index) => {
          const colors = ['#4285F4', '#FBBC05', '#34A853', '#EA4335', '#9AA0A6'];
          return colors[index % colors.length];
        }),
        borderRadius: 8,
        borderWidth: 0
      }
    ]
  };

  // Difficulty Distribution Pie Chart
  const difficultyPieData = {
    labels: ['Hard', 'Medium', 'Easy'],
    datasets: [
      {
        data: [
          difficultyDistribution.hard || 0,
          difficultyDistribution.medium || 0,
          difficultyDistribution.easy || 0
        ],
        backgroundColor: ['#EA4335', '#FBBC05', '#34A853'],
        borderWidth: 0
      }
    ]
  };

  // Stress Source Pie Chart
  const stressSourcePieData = {
    labels: ['Tweet Stress', 'Meme Stress', 'Paper Difficulty'],
    datasets: [
      {
        data: [
          stressPieData.tweet_pct || 0,
          stressPieData.meme_pct || 0,
          stressPieData.paper_pct || 0
        ],
        backgroundColor: ['#4285F4', '#FBBC05', '#34A853'],
        borderWidth: 0
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
        labels: { color: '#e8eaed', font: { size: 11, family: "'Poppins', sans-serif" } }
      },
      tooltip: {
        backgroundColor: '#202124',
        titleColor: '#e8eaed',
        bodyColor: '#9aa0a6',
        padding: 12,
        cornerRadius: 8,
        titleFont: { size: 13, family: "'Poppins', sans-serif", weight: 500 },
        bodyFont: { size: 12, family: "'Poppins', sans-serif" }
      }
    }
  };

  const subjectBarOptions = {
    ...options,
    scales: {
      y: {
        beginAtZero: true,
        grid: { color: '#3c4043' },
        ticks: { color: '#9aa0a6', font: { size: 11, family: "'Poppins', sans-serif" } },
        title: {
          display: true,
          text: 'Number of Topics',
          color: '#9aa0a6',
          font: { size: 12, family: "'Poppins', sans-serif", weight: 500 }
        }
      },
      x: {
        grid: { display: false },
        ticks: { color: '#9aa0a6', maxRotation: 45, minRotation: 45, font: { size: 11, family: "'Poppins', sans-serif" } }
      }
    }
  };

  // Function to get color based on occurrence count
  const getOccurrenceColor = (count) => {
    if (count > 50) return '#EA4335';
    if (count > 20) return '#FBBC05';
    return '#34A853';
  };

  // Function to get occurrence level text
  const getOccurrenceLevel = (count) => {
    if (count > 50) return 'High';
    if (count > 20) return 'Medium';
    return 'Low';
  };

  // Google AI Dashboard Styles
  const styles = {
    container: {
      padding: 0,
      background: 'transparent',
      color: '#e8eaed',
      fontFamily: "'Poppins', sans-serif",
      width: '100%'
    },
    header: {
      marginBottom: 24
    },
    title: {
      margin: '0 0 8px 0',
      fontSize: 24,
      fontWeight: 600,
      color: '#e8eaed',
      fontFamily: "'Poppins', sans-serif",
      letterSpacing: '-0.5px'
    },
    subtitle: {
      margin: 0,
      fontSize: 14,
      color: '#9aa0a6',
      fontFamily: "'Poppins', sans-serif",
      fontWeight: 400
    },
    statsGrid: {
      display: 'grid',
      gridTemplateColumns: 'repeat(4, 1fr)',
      gap: 16,
      marginBottom: 24
    },
    statCard: {
      background: '#2d2e30',
      padding: 20,
      borderRadius: 12,
      border: '1px solid #3c4043',
      transition: 'all 0.2s ease'
    },
    statLabel: {
      margin: '0 0 8px 0',
      fontSize: 13,
      color: '#9aa0a6',
      fontWeight: 500,
      fontFamily: "'Poppins', sans-serif"
    },
    statValue: {
      margin: 0,
      fontSize: 28,
      fontWeight: 600,
      color: '#e8eaed',
      fontFamily: "'Poppins', sans-serif",
      lineHeight: 1.2
    },
    statTrend: {
      margin: '8px 0 0',
      fontSize: 12,
      color: '#9aa0a6',
      fontFamily: "'Poppins', sans-serif"
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
      color: '#e8eaed',
      fontFamily: "'Poppins', sans-serif"
    },
    infoStats: {
      display: 'flex',
      flexWrap: 'wrap',
      gap: 24,
      marginTop: 12
    },
    infoItem: {
      display: 'flex',
      alignItems: 'center',
      gap: 8,
      fontSize: 13,
      color: '#9aa0a6',
      fontFamily: "'Poppins', sans-serif"
    },
    infoDot: {
      width: 10,
      height: 10,
      borderRadius: '50%'
    },
    chartGrid: {
      display: 'grid',
      gridTemplateColumns: '1fr 1fr',
      gap: 20,
      marginBottom: 24
    },
    chartCard: {
      background: '#2d2e30',
      borderRadius: 12,
      padding: 20,
      border: '1px solid #3c4043'
    },
    chartTitle: {
      margin: '0 0 16px 0',
      fontSize: 15,
      fontWeight: 500,
      color: '#e8eaed',
      fontFamily: "'Poppins', sans-serif",
      textAlign: 'center'
    },
    chartWrapper: {
      background: '#2d2e30',
      borderRadius: 12,
      padding: 20,
      border: '1px solid #3c4043',
      height: '350px',
      marginBottom: 24
    },
    tableContainer: {
      background: '#2d2e30',
      borderRadius: 12,
      padding: 20,
      border: '1px solid #3c4043',
      marginTop: 24,
      overflowX: 'auto'
    },
    tableTitle: {
      margin: '0 0 16px 0',
      fontSize: 16,
      fontWeight: 500,
      color: '#e8eaed',
      fontFamily: "'Poppins', sans-serif"
    },
    table: {
      width: '100%',
      borderCollapse: 'collapse',
      minWidth: 800,
      fontSize: 13
    },
    th: {
      background: '#35363a',
      color: '#9aa0a6',
      padding: '12px 16px',
      textAlign: 'left',
      fontWeight: 500,
      fontSize: 12,
      textTransform: 'uppercase',
      letterSpacing: '0.5px',
      fontFamily: "'Poppins', sans-serif"
    },
    td: {
      padding: '12px 16px',
      borderBottom: '1px solid #3c4043',
      color: '#e8eaed',
      fontFamily: "'Poppins', sans-serif"
    },
    rowEven: {
      background: '#2d2e30'
    },
    rowOdd: {
      background: '#313234'
    },
    badge: {
      padding: '4px 12px',
      borderRadius: 100,
      fontSize: 11,
      fontWeight: 500,
      display: 'inline-block',
      fontFamily: "'Poppins', sans-serif"
    },
    legend: {
      display: 'flex',
      gap: 24,
      marginTop: 16,
      padding: 16,
      background: '#35363a',
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
      border: '1px dashed #3c4043',
      fontFamily: "'Poppins', sans-serif"
    }
  };

  if (!hasData && !hasSubjectData && yearData.length === 0) {
    return (
      <div style={styles.container}>
        <div style={styles.header}>
          <h2 style={styles.title}>📈 Difficulty Analysis</h2>
        </div>
        <div style={styles.noData}>
          <p>No difficulty data available for this exam.</p>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <h2 style={styles.title}>📈 Difficulty Analysis</h2>
        <p style={styles.subtitle}>Comprehensive analysis of topic difficulty levels</p>
      </div>
      
      {/* Stats Cards - First Row */}
      {hasData && (
        <>
          <div style={styles.statsGrid}>
            {/* Total Topics Box */}
            <div style={styles.statCard}>
              <p style={styles.statLabel}>Total Topics</p>
              <h3 style={styles.statValue}>{totalTopics}</h3>
              <p style={styles.statTrend}>All topics</p>
            </div>
            
            {/* Hard Topics Box */}
            <div style={styles.statCard}>
              <p style={styles.statLabel}>Hard Topics</p>
              <h3 style={{...styles.statValue, color: '#EA4335'}}>
                {classification.find(c => c.level === 'Hard')?.count || 0}
              </h3>
              <p style={styles.statTrend}>
                {classification.find(c => c.level === 'Hard')?.percentage || 0}% of total
              </p>
            </div>
            
            {/* Medium Topics Box */}
            <div style={styles.statCard}>
              <p style={styles.statLabel}>Medium Topics</p>
              <h3 style={{...styles.statValue, color: '#FBBC05'}}>
                {classification.find(c => c.level === 'Medium')?.count || 0}
              </h3>
              <p style={styles.statTrend}>
                {classification.find(c => c.level === 'Medium')?.percentage || 0}% of total
              </p>
            </div>
            
            {/* Easy Topics Box */}
            <div style={styles.statCard}>
              <p style={styles.statLabel}>Easy Topics</p>
              <h3 style={{...styles.statValue, color: '#34A853'}}>
                {classification.find(c => c.level === 'Easy')?.count || 0}
              </h3>
              <p style={styles.statTrend}>
                {classification.find(c => c.level === 'Easy')?.percentage || 0}% of total
              </p>
            </div>
          </div>

          {/* Info Box */}
          <div style={styles.infoBox}>
            <h4 style={styles.infoTitle}>📊 Difficulty Overview</h4>
            <p style={{ margin: 0, color: '#9aa0a6', fontSize: 13 }}>Analysis based on exam_summary table</p>
            <div style={styles.infoStats}>
              {classification.map(item => (
                <div key={item.level} style={styles.infoItem}>
                  <div style={{
                    ...styles.infoDot,
                    background: item.level === 'Hard' ? '#EA4335' : 
                               item.level === 'Medium' ? '#FBBC05' : '#34A853'
                  }} />
                  <span>{item.level}: {item.count} ({item.percentage}%)</span>
                </div>
              ))}
            </div>
          </div>
        </>
      )}

      {/* Charts Grid - First Row */}
      <div style={styles.chartGrid}>
        {/* Difficulty Distribution Pie Chart */}
        {difficultyDistribution.total > 0 && (
          <div style={styles.chartCard}>
            <h5 style={styles.chartTitle}>Difficulty Distribution</h5>
            <div style={{ height: 250 }}>
              <Pie data={difficultyPieData} options={options} />
            </div>
          </div>
        )}

        {/* Stress Source Pie Chart */}
        {stressPieData.total > 0 && (
          <div style={styles.chartCard}>
            <h5 style={styles.chartTitle}>Stress Source Distribution</h5>
            <div style={{ height: 250 }}>
              <Pie data={stressSourcePieData} options={options} />
            </div>
          </div>
        )}
      </div>

      {/* Subject Comparison Bar Chart */}
      {hasSubjectData && (
        <div style={styles.chartWrapper}>
          <h4 style={{...styles.chartTitle, marginBottom: 16}}>
            📊 Subjects by Topic Count
          </h4>
          <div style={{ height: 300 }}>
            <Bar data={subjectBarData} options={subjectBarOptions} />
          </div>
        </div>
      )}

      {/* Subject Summary Table with Color-coded Range */}
      {hasSubjectData && (
        <div style={{ marginTop: 24 }}>
          <h4 style={{ color: '#e8eaed', marginBottom: 16, fontSize: 16, fontWeight: 500 }}>📋 Subject Summary</h4>
          <div style={styles.tableContainer}>
            <div style={{ overflowX: 'auto' }}>
              <table style={styles.table}>
                <thead>
                  <tr>
                    <th style={styles.th}>Subject</th>
                    <th style={styles.th}>Total Occurrences</th>
                    <th style={styles.th}>Unique Topics</th>
                    <th style={styles.th}>Avg Difficulty</th>
                    <th style={styles.th}>Occurrence Level</th>
                  </tr>
                </thead>
                <tbody>
                  {subjectComparison.map((item, index) => {
                    const occurrenceColor = getOccurrenceColor(item.total_occurrences);
                    const occurrenceLevel = getOccurrenceLevel(item.total_occurrences);
                    
                    return (
                      <tr key={index} style={index % 2 === 0 ? styles.rowEven : styles.rowOdd}>
                        <td style={styles.td}><strong>{item.subject}</strong></td>
                        <td style={styles.td}>
                          <span style={{ 
                            color: occurrenceColor, 
                            fontWeight: 500,
                            backgroundColor: occurrenceColor + '20',
                            padding: '4px 8px',
                            borderRadius: 100,
                            display: 'inline-block'
                          }}>
                            {item.total_occurrences}
                          </span>
                        </td>
                        <td style={styles.td}>{item.unique_topics}</td>
                        <td style={styles.td}>{item.avg_difficulty}</td>
                        <td style={styles.td}>
                          <span style={{
                            ...styles.badge,
                            backgroundColor: occurrenceColor + '20',
                            color: occurrenceColor,
                            border: `1px solid ${occurrenceColor}`
                          }}>
                            {occurrenceLevel}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
          
          {/* Legend for occurrence levels */}
          <div style={styles.legend}>
            <div style={styles.legendItem}>
              <div style={{ width: 16, height: 16, background: '#EA4335', borderRadius: 4 }} />
              <span style={{ color: '#e8eaed' }}>High Occurrence (&gt;50)</span>
            </div>
            <div style={styles.legendItem}>
              <div style={{ width: 16, height: 16, background: '#FBBC05', borderRadius: 4 }} />
              <span style={{ color: '#e8eaed' }}>Medium Occurrence (21-50)</span>
            </div>
            <div style={styles.legendItem}>
              <div style={{ width: 16, height: 16, background: '#34A853', borderRadius: 4 }} />
              <span style={{ color: '#e8eaed' }}>Low Occurrence (≤20)</span>
            </div>
          </div>
        </div>
      )}

      {/* Year-wise Trends Line Chart */}
      {yearData.length > 0 && (
        <div style={{ marginTop: 32 }}>
          <h4 style={{ color: '#e8eaed', marginBottom: 16, fontSize: 16, fontWeight: 500 }}>📅 Year-wise Stress Trends</h4>
          <div style={styles.chartWrapper}>
            <div style={{ height: 300 }}>
              <Line data={lineChartData} options={options} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DifficultyClassification;