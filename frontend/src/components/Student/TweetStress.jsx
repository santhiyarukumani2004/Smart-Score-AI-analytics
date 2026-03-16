import React, { useState } from 'react';
import { Line, Bar, Pie } from 'react-chartjs-2';

const TweetStress = ({ data, overallStats }) => {
  const [chartType, setChartType] = useState('line');

  console.log('TweetStress received data:', data);
  console.log('TweetStress received overallStats:', overallStats);

  // If no data, show message
  if (!overallStats || !overallStats.tweet_count) {
    return (
      <div style={styles.container}>
        <div style={styles.header}>
          <h2 style={styles.title}>📊 Tweet Stress Analysis</h2>
        </div>
        <div style={styles.noData}>
          <p>No tweet data available for this exam.</p>
          <div style={styles.debugInfo}>
            <p>Data received:</p>
            <pre>{JSON.stringify({ data, overallStats }, null, 2)}</pre>
          </div>
        </div>
      </div>
    );
  }

  const {
    tweet_count = 0,
    overall_stress = 0,
    high_stress = 0,
    medium_stress = 0,
    low_stress = 0,
    high_stress_pct = 0,
    medium_stress_pct = 0,
    low_stress_pct = 0,
    positive_pct = 0,
    negative_pct = 0,
    neutral_pct = 0,
    avg_difficulty = 0,
    topic_count = 0
  } = overallStats;

  const trendData = Array.isArray(data) ? data : [];
  
  // Line Chart Data for yearly trend (Stress Score by Year)
  const lineData = {
    labels: trendData.map(item => item.year || 'N/A'),
    datasets: [
      {
        label: 'Stress Score',
        data: trendData.map(item => item.stress || 0),
        borderColor: '#4285F4',
        backgroundColor: 'rgba(66, 133, 244, 0.1)',
        tension: 0.4,
        fill: true,
        pointBackgroundColor: trendData.map(item => {
          const stress = item.stress || 0;
          if (stress >= 70) return '#EA4335';
          if (stress >= 40) return '#FBBC05';
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

  // Bar Chart Data for stress distribution (High/Medium/Low counts)
  const stressBarData = {
    labels: ['High Stress', 'Medium Stress', 'Low Stress'],
    datasets: [
      {
        label: 'Tweet Count',
        data: [high_stress, medium_stress, low_stress],
        backgroundColor: ['#EA4335', '#FBBC05', '#34A853'],
        borderRadius: 8,
        borderWidth: 0
      }
    ]
  };

  // Bar Chart Data for Tweet Count by Year
  const tweetCountYearData = {
    labels: trendData.map(item => item.year || 'N/A'),
    datasets: [
      {
        label: 'Tweet Count',
        data: trendData.map(item => item.count || 0),
        backgroundColor: '#4285F4',
        borderRadius: 8,
        borderWidth: 0
      }
    ]
  };

  // Pie Chart Data for stress percentages
  const pieData = {
    labels: ['High Stress', 'Medium Stress', 'Low Stress'],
    datasets: [
      {
        data: [high_stress_pct, medium_stress_pct, low_stress_pct],
        backgroundColor: ['#EA4335', '#FBBC05', '#34A853'],
        borderWidth: 0
      }
    ]
  };

  // Sentiment Pie Chart
  const sentimentPieData = {
    labels: ['Positive', 'Negative', 'Neutral'],
    datasets: [
      {
        data: [positive_pct, negative_pct, neutral_pct],
        backgroundColor: ['#34A853', '#EA4335', '#9AA0A6'],
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
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: { color: '#3c4043' },
        ticks: { color: '#9aa0a6', font: { size: 11, family: "'Poppins', sans-serif" } },
        title: {
          display: true,
          text: 'Percentage (%)',
          color: '#9aa0a6',
          font: { size: 12, family: "'Poppins', sans-serif", weight: 500 }
        }
      },
      x: {
        grid: { display: false },
        ticks: { color: '#9aa0a6', font: { size: 11, family: "'Poppins', sans-serif" } }
      }
    }
  };

  const renderChart = () => {
    if (chartType === 'line' && trendData.length > 0) {
      return <Line data={lineData} options={options} />;
    } else if (chartType === 'bar') {
      return <Bar data={stressBarData} options={options} />;
    } else if (chartType === 'pie') {
      return <Pie data={pieData} options={options} />;
    }
    return <Line data={lineData} options={options} />;
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
    chartTypeSelector: {
      display: 'flex',
      gap: 8,
      marginBottom: 20,
      background: '#35363a',
      padding: 4,
      borderRadius: 100,
      width: 'fit-content'
    },
    chartTypeBtn: {
      padding: '8px 20px',
      border: 'none',
      borderRadius: 100,
      cursor: 'pointer',
      fontSize: 13,
      fontWeight: 500,
      fontFamily: "'Poppins', sans-serif",
      transition: 'all 0.2s',
      background: 'transparent',
      color: '#9aa0a6',
      display: 'flex',
      alignItems: 'center',
      gap: 6
    },
    chartTypeBtnActive: {
      background: '#4285F4',
      color: 'white'
    },
    chartWrapper: {
      background: '#2d2e30',
      borderRadius: 12,
      padding: 20,
      border: '1px solid #3c4043',
      height: '350px',
      marginBottom: 24
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
    progressContainer: {
      display: 'flex',
      alignItems: 'center',
      gap: 12
    },
    progressBar: {
      flex: 1,
      height: 6,
      background: '#3c4043',
      borderRadius: 3,
      overflow: 'hidden'
    },
    progressFill: {
      height: '100%',
      borderRadius: 3
    },
    badge: {
      padding: '4px 12px',
      borderRadius: 100,
      fontSize: 11,
      fontWeight: 500,
      display: 'inline-block',
      fontFamily: "'Poppins', sans-serif"
    },
    noData: {
      textAlign: 'center',
      padding: 60,
      color: '#9aa0a6',
      background: '#2d2e30',
      borderRadius: 12,
      border: '1px dashed #3c4043',
      fontFamily: "'Poppins', sans-serif"
    },
    debugInfo: {
      marginTop: 20,
      padding: 16,
      background: '#35363a',
      borderRadius: 8,
      textAlign: 'left',
      fontSize: 12,
      color: '#9aa0a6',
      overflowX: 'auto'
    }
  };

  return (
    <div style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <h2 style={styles.title}>📊 Tweet Stress Analysis</h2>
        <p style={styles.subtitle}>Real-time analysis of Twitter stress patterns</p>
      </div>
      
      {/* Stats Cards */}
      <div style={styles.statsGrid}>
        <div style={styles.statCard}>
          <p style={styles.statLabel}>Total Tweets</p>
          <h3 style={styles.statValue}>{tweet_count}</h3>
          <p style={styles.statTrend}>All time</p>
        </div>
        
        <div style={styles.statCard}>
          <p style={styles.statLabel}>Overall Stress</p>
          <h3 style={{...styles.statValue, color: overall_stress >= 70 ? '#EA4335' : overall_stress >= 40 ? '#FBBC05' : '#34A853'}}>
            {overall_stress.toFixed(1)}%
          </h3>
          <p style={styles.statTrend}>Average</p>
        </div>
        
        <div style={styles.statCard}>
          <p style={styles.statLabel}>Positive</p>
          <h3 style={{...styles.statValue, color: '#34A853'}}>{positive_pct.toFixed(1)}%</h3>
          <p style={styles.statTrend}>of tweets</p>
        </div>
        
        <div style={styles.statCard}>
          <p style={styles.statLabel}>Negative</p>
          <h3 style={{...styles.statValue, color: '#EA4335'}}>{negative_pct.toFixed(1)}%</h3>
          <p style={styles.statTrend}>of tweets</p>
        </div>
      </div>

      {/* Info Box */}
      <div style={styles.infoBox}>
        <h4 style={styles.infoTitle}>📈 Tweet Stress Analysis</h4>
        <p style={{ margin: 0, color: '#9aa0a6', fontSize: 13 }}>From Twitter data. Stress scores range from 0-100%.</p>
        <div style={styles.infoStats}>
          <div style={styles.infoItem}>
            <div style={{...styles.infoDot, background: '#4285F4'}} />
            <span>📊 Avg Stress: {overall_stress.toFixed(1)}%</span>
          </div>
          <div style={styles.infoItem}>
            <div style={{...styles.infoDot, background: '#34A853'}} />
            <span>😊 Positive: {positive_pct.toFixed(1)}%</span>
          </div>
          <div style={styles.infoItem}>
            <div style={{...styles.infoDot, background: '#EA4335'}} />
            <span>😞 Negative: {negative_pct.toFixed(1)}%</span>
          </div>
          <div style={styles.infoItem}>
            <div style={{...styles.infoDot, background: '#9AA0A6'}} />
            <span>😐 Neutral: {neutral_pct.toFixed(1)}%</span>
          </div>
        </div>
      </div>

      {/* Chart Type Selector */}
      <div style={styles.chartTypeSelector}>
        <button 
          style={{
            ...styles.chartTypeBtn,
            ...(chartType === 'line' ? styles.chartTypeBtnActive : {})
          }}
          onClick={() => setChartType('line')}
          disabled={trendData.length === 0}
        >
          <span>📈</span>
          Year Trend
        </button>
        <button 
          style={{
            ...styles.chartTypeBtn,
            ...(chartType === 'bar' ? styles.chartTypeBtnActive : {})
          }}
          onClick={() => setChartType('bar')}
        >
          <span>📊</span>
          Stress Distribution
        </button>
        <button 
          style={{
            ...styles.chartTypeBtn,
            ...(chartType === 'pie' ? styles.chartTypeBtnActive : {})
          }}
          onClick={() => setChartType('pie')}
        >
          <span>🥧</span>
          Stress %
        </button>
      </div>

      {/* Main Chart */}
      <div style={styles.chartWrapper}>
        {renderChart()}
      </div>

      {/* Two Charts Grid */}
      <div style={styles.chartGrid}>
        <div style={styles.chartCard}>
          <h5 style={styles.chartTitle}>Sentiment Distribution</h5>
          <div style={{ height: 250 }}>
            <Pie data={sentimentPieData} options={options} />
          </div>
        </div>
        <div style={styles.chartCard}>
          <h5 style={styles.chartTitle}>Tweet Count by Year</h5>
          <div style={{ height: 250 }}>
            {trendData.length > 0 ? (
              <Bar data={tweetCountYearData} options={options} />
            ) : (
              <p style={{ color: '#9aa0a6', textAlign: 'center', marginTop: 100 }}>No yearly data available</p>
            )}
          </div>
        </div>
      </div>

      {/* Year-wise Table Summary with Topic Labels */}
      <div style={styles.tableContainer}>
        <h4 style={styles.tableTitle}>📅 Year-wise Tweet Analysis</h4>
        <div style={{ overflowX: 'auto' }}>
          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.th}>Year</th>
                <th style={styles.th}>Tweet Count</th>
                <th style={styles.th}>Avg Stress (%)</th>
                <th style={styles.th}>Stress Level</th>
                <th style={styles.th}>Status</th>
                <th style={styles.th}>Topic Coverage</th>
              </tr>
            </thead>
            <tbody>
              {trendData.length > 0 ? (
                trendData.map((item, index) => {
                  const stress = item.stress || 0;
                  let stressLevel = 'Low';
                  let statusColor = '#34A853';
                  let statusText = '🟢 Good';
                  
                  if (stress >= 70) {
                    stressLevel = 'High';
                    statusColor = '#EA4335';
                    statusText = '🔴 Critical';
                  } else if (stress >= 40) {
                    stressLevel = 'Medium';
                    statusColor = '#FBBC05';
                    statusText = '🟠 Medium';
                  }
                  
                  // Determine topic coverage based on stress level
                  let topicCoverage = 'Normal';
                  let topicColor = '#9AA0A6';
                  if (stress >= 70) {
                    topicCoverage = 'High Focus Areas';
                    topicColor = '#EA4335';
                  } else if (stress >= 40) {
                    topicCoverage = 'Moderate Coverage';
                    topicColor = '#FBBC05';
                  } else {
                    topicCoverage = 'Standard Coverage';
                    topicColor = '#34A853';
                  }
                  
                  return (
                    <tr key={index} style={index % 2 === 0 ? styles.rowEven : styles.rowOdd}>
                      <td style={styles.td}><strong>{item.year || 'N/A'}</strong></td>
                      <td style={styles.td}>{item.count || 0}</td>
                      <td style={styles.td}>
                        <div style={styles.progressContainer}>
                          <span style={{ minWidth: '45px', color: statusColor, fontWeight: 500 }}>
                            {stress.toFixed(1)}%
                          </span>
                          <div style={styles.progressBar}>
                            <div 
                              style={{ 
                                width: `${stress}%`,
                                height: '100%',
                                backgroundColor: statusColor,
                                borderRadius: 3
                              }} 
                            />
                          </div>
                        </div>
                      </td>
                      <td style={styles.td}>
                        <span style={{ color: statusColor, fontWeight: 500 }}>
                          {stressLevel}
                        </span>
                      </td>
                      <td style={styles.td}>
                        <span style={{
                          ...styles.badge,
                          backgroundColor: statusColor + '20',
                          color: statusColor,
                          border: `1px solid ${statusColor}`
                        }}>
                          {statusText}
                        </span>
                      </td>
                      <td style={styles.td}>
                        <span style={{
                          ...styles.badge,
                          backgroundColor: topicColor + '15',
                          color: topicColor,
                          border: `1px solid ${topicColor}`
                        }}>
                          {topicCoverage}
                        </span>
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan="6" style={{ textAlign: 'center', padding: 24, color: '#9aa0a6' }}>
                    No yearly data available
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Topic Summary Section */}
      <div style={styles.tableContainer}>
        <h4 style={styles.tableTitle}>📚 Topic Summary Analysis</h4>
        <div style={{ overflowX: 'auto' }}>
          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.th}>Metric</th>
                <th style={styles.th}>Value</th>
                <th style={styles.th}>Status</th>
                <th style={styles.th}>Recommendation</th>
              </tr>
            </thead>
            <tbody>
              <tr style={styles.rowEven}>
                <td style={styles.td}><strong>Topics Covered</strong></td>
                <td style={styles.td}>{topic_count}</td>
                <td style={styles.td}>
                  <span style={{
                    ...styles.badge,
                    backgroundColor: topic_count > 20 ? '#34A85320' : topic_count > 10 ? '#FBBC0520' : '#EA433520',
                    color: topic_count > 20 ? '#34A853' : topic_count > 10 ? '#FBBC05' : '#EA4335',
                    border: `1px solid ${topic_count > 20 ? '#34A853' : topic_count > 10 ? '#FBBC05' : '#EA4335'}`
                  }}>
                    {topic_count > 20 ? '✅ Extensive' : topic_count > 10 ? '⚠️ Moderate' : '🔴 Limited'}
                  </span>
                </td>
                <td style={styles.td}>
                  {topic_count > 20 
                    ? 'Good coverage across topics' 
                    : topic_count > 10 
                    ? 'Consider expanding topic coverage' 
                    : 'Focus on covering more topics'}
                </td>
              </tr>
              <tr style={styles.rowOdd}>
                <td style={styles.td}><strong>Average Difficulty</strong></td>
                <td style={styles.td}>{avg_difficulty.toFixed(2)}/5</td>
                <td style={styles.td}>
                  <span style={{
                    ...styles.badge,
                    backgroundColor: avg_difficulty >= 3.5 ? '#EA433520' : avg_difficulty >= 2.5 ? '#FBBC0520' : '#34A85320',
                    color: avg_difficulty >= 3.5 ? '#EA4335' : avg_difficulty >= 2.5 ? '#FBBC05' : '#34A853',
                    border: `1px solid ${avg_difficulty >= 3.5 ? '#EA4335' : avg_difficulty >= 2.5 ? '#FBBC05' : '#34A853'}`
                  }}>
                    {avg_difficulty >= 3.5 ? '🔴 Hard' : avg_difficulty >= 2.5 ? '🟠 Medium' : '🟢 Easy'}
                  </span>
                </td>
                <td style={styles.td}>
                  {avg_difficulty >= 3.5 
                    ? 'Focus on practice and revision' 
                    : avg_difficulty >= 2.5 
                    ? 'Maintain consistent study' 
                    : 'Good foundation, can explore advanced topics'}
                </td>
              </tr>
              <tr style={styles.rowEven}>
                <td style={styles.td}><strong>Stress Distribution</strong></td>
                <td style={styles.td}>H:{high_stress} M:{medium_stress} L:{low_stress}</td>
                <td style={styles.td}>
                  <span style={{
                    ...styles.badge,
                    backgroundColor: high_stress > medium_stress ? '#EA433520' : '#FBBC0520',
                    color: high_stress > medium_stress ? '#EA4335' : '#FBBC05',
                    border: `1px solid ${high_stress > medium_stress ? '#EA4335' : '#FBBC05'}`
                  }}>
                    {high_stress > medium_stress ? '⚠️ High Stress' : 'Normal'}
                  </span>
                </td>
                <td style={styles.td}>
                  {high_stress > medium_stress 
                    ? 'Consider stress management techniques' 
                    : 'Stress levels are manageable'}
                </td>
              </tr>
              <tr style={styles.rowOdd}>
                <td style={styles.td}><strong>Sentiment Balance</strong></td>
                <td style={styles.td}>P:{positive_pct.toFixed(1)}% N:{negative_pct.toFixed(1)}%</td>
                <td style={styles.td}>
                  <span style={{
                    ...styles.badge,
                    backgroundColor: positive_pct > negative_pct ? '#34A85320' : '#EA433520',
                    color: positive_pct > negative_pct ? '#34A853' : '#EA4335',
                    border: `1px solid ${positive_pct > negative_pct ? '#34A853' : '#EA4335'}`
                  }}>
                    {positive_pct > negative_pct ? '😊 Positive' : '😞 Negative'}
                  </span>
                </td>
                <td style={styles.td}>
                  {positive_pct > negative_pct 
                    ? 'Positive sentiment indicates good engagement' 
                    : 'Address negative feedback points'}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Detailed Summary Table */}
      <div style={styles.tableContainer}>
        <h4 style={styles.tableTitle}>📊 Detailed Tweet Summary</h4>
        <div style={{ overflowX: 'auto' }}>
          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.th}>Metric</th>
                <th style={styles.th}>Count</th>
                <th style={styles.th}>Percentage</th>
                <th style={styles.th}>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr style={styles.rowEven}>
                <td style={styles.td}>High Stress</td>
                <td style={styles.td}>{high_stress}</td>
                <td style={styles.td}>{high_stress_pct.toFixed(1)}%</td>
                <td style={styles.td}>
                  <span style={{
                    ...styles.badge,
                    backgroundColor: high_stress_pct > 50 ? '#EA433520' : high_stress_pct > 30 ? '#FBBC0520' : '#34A85320',
                    color: high_stress_pct > 50 ? '#EA4335' : high_stress_pct > 30 ? '#FBBC05' : '#34A853',
                    border: `1px solid ${high_stress_pct > 50 ? '#EA4335' : high_stress_pct > 30 ? '#FBBC05' : '#34A853'}`
                  }}>
                    {high_stress_pct > 50 ? 'Critical' : high_stress_pct > 30 ? 'Moderate' : 'Normal'}
                  </span>
                </td>
              </tr>
              <tr style={styles.rowOdd}>
                <td style={styles.td}>Medium Stress</td>
                <td style={styles.td}>{medium_stress}</td>
                <td style={styles.td}>{medium_stress_pct.toFixed(1)}%</td>
                <td style={styles.td}>-</td>
              </tr>
              <tr style={styles.rowEven}>
                <td style={styles.td}>Low Stress</td>
                <td style={styles.td}>{low_stress}</td>
                <td style={styles.td}>{low_stress_pct.toFixed(1)}%</td>
                <td style={styles.td}>-</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default TweetStress;