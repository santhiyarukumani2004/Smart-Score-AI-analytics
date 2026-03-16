import React, { useState, useEffect } from 'react';
import { Pie, Bar } from 'react-chartjs-2';
import './TeacherDashboard.css';

const TopicAnalysis = ({ data = [] }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterDifficulty, setFilterDifficulty] = useState('all');
  const [chartView, setChartView] = useState('pie');
  const [chartKey, setChartKey] = useState(0);
  const [processedData, setProcessedData] = useState([]);
  const [uniqueTopics, setUniqueTopics] = useState([]);
  const [maxOccurrences, setMaxOccurrences] = useState(1);

  console.log('TopicAnalysis received:', data.length, 'topics');

  useEffect(() => {
    // Process the data when it changes
    if (data && data.length > 0) {
      // First, remove duplicates (same subject + same topic)
      const uniqueMap = new Map();
      
      data.forEach(item => {
        const key = `${item.subject}|${item.topic}`;
        if (!uniqueMap.has(key)) {
          uniqueMap.set(key, item);
        }
      });
      
      const uniqueData = Array.from(uniqueMap.values());
      console.log(`Removed duplicates: ${data.length} -> ${uniqueData.length} unique topics`);
      
      // Find max occurrences for confidence scaling
      const maxOcc = Math.max(...uniqueData.map(item => parseInt(item.occurrences) || 1));
      setMaxOccurrences(maxOcc);
      
      // Process unique data
      const processed = uniqueData.map(item => {
        // 1. Handle zero counts - set default to 1
        const tweetCount = Math.max(1, parseInt(item.tweet_count) || 1);
        const memeCount = Math.max(1, parseInt(item.meme_count) || 1);
        const paperCount = parseInt(item.paper_count) || 0;
        const occurrences = parseInt(item.occurrences) || 1;
        
        // 2. Handle zero stress - set default to 0.1
        const tweetStress = Math.max(0.1, parseFloat(item.tweet_stress) || 0.1);
        const memeStress = Math.max(0.1, parseFloat(item.meme_stress) || 0.1);
        const paperDiff = Math.max(0.1, parseFloat(item.paper_difficulty) || 0.1);
        
        // 3. Use the existing overall_difficulty from API (no recalculation)
        const overallDiff = parseFloat(item.overall_difficulty) || 
                           (tweetStress + memeStress + paperDiff) / 3;
        
        // 4. Calculate confidence based on occurrences and difficulty
        // Higher occurrences = higher confidence
        // Higher difficulty also contributes to confidence
        const occurrenceFactor = occurrences / maxOcc;
        const difficultyFactor = overallDiff / 5.0; // Normalize to 0-1
        
        // Combine factors (60% weight on occurrences, 40% on difficulty)
        let confidence = (occurrenceFactor * 0.6 + difficultyFactor * 0.4) * 100;
        
        // Ensure confidence is between 0-100 and round to integer
        confidence = Math.min(100, Math.max(0, Math.round(confidence)));
        
        return {
          ...item,
          tweet_count: tweetCount,
          meme_count: memeCount,
          paper_count: paperCount,
          occurrences: occurrences,
          tweet_stress: tweetStress,
          meme_stress: memeStress,
          paper_difficulty: paperDiff,
          overall_difficulty: overallDiff,
          confidence: confidence
        };
      });
      
      setUniqueTopics(uniqueData.length);
      setProcessedData(processed);
    }
  }, [data]);

  // If no data, show message
  if (!data || data.length === 0) {
    return (
      <div className="topic-analysis-container" style={styles.container}>
        <div style={styles.header}>
          <h1 style={styles.title}>📚 Topic-wise Analysis</h1>
        </div>
        <div style={styles.noData}>
          <p>No topic data available</p>
        </div>
      </div>
    );
  }

  // Helper function to safely parse numbers
  const safeParseFloat = (value) => {
    if (value === null || value === undefined || value === '') return 0;
    const parsed = parseFloat(value);
    return isNaN(parsed) ? 0 : parsed;
  };

  // Updated thresholds: 
  // Low: 1.00 - 2.00
  // Medium: 2.01 - 2.90
  // Hard: 2.91 - 5.00
  const getDifficultyColor = (score) => {
    const numScore = safeParseFloat(score);
    if (numScore >= 2.91) return '#EA4335'; // Google Red
    if (numScore >= 2.01) return '#FBBC05'; // Google Yellow
    return '#34A853'; // Google Green
  };

  const getDifficultyLabel = (score) => {
    const numScore = safeParseFloat(score);
    if (numScore >= 2.91) return 'Hard';
    if (numScore >= 2.01) return 'Medium';
    return 'Low';
  };

  // Get confidence level color
  const getConfidenceColor = (confidence) => {
    if (confidence >= 70) return '#34A853'; // Google Green
    if (confidence >= 40) return '#FBBC05'; // Google Yellow
    return '#EA4335'; // Google Red
  };

  // Get confidence level label
  const getConfidenceLabel = (confidence) => {
    if (confidence >= 70) return 'High';
    if (confidence >= 40) return 'Medium';
    return 'Low';
  };

  const filterTopics = () => {
    return processedData.filter(item => {
      const matchesSearch = 
        (item.subject?.toLowerCase() || '').includes(searchTerm.toLowerCase()) ||
        (item.topic?.toLowerCase() || '').includes(searchTerm.toLowerCase());
      
      const score = safeParseFloat(item.overall_difficulty);
      const level = getDifficultyLabel(score);
      
      const matchesDifficulty = filterDifficulty === 'all' || level === filterDifficulty;
      
      return matchesSearch && matchesDifficulty;
    });
  };

  const filteredTopics = filterTopics();

  // Difficulty Distribution Pie Chart with updated thresholds
  const difficultyCounts = {
    Hard: filteredTopics.filter(t => safeParseFloat(t.overall_difficulty) >= 2.91).length,
    Medium: filteredTopics.filter(t => {
      const score = safeParseFloat(t.overall_difficulty);
      return score >= 2.01 && score <= 2.90;
    }).length,
    Low: filteredTopics.filter(t => safeParseFloat(t.overall_difficulty) <= 2.00).length
  };

  const pieData = {
    labels: ['Hard (2.91-5.0)', 'Medium (2.01-2.90)', 'Low (1.0-2.0)'],
    datasets: [{
      data: [difficultyCounts.Hard, difficultyCounts.Medium, difficultyCounts.Low],
      backgroundColor: ['#EA4335', '#FBBC05', '#34A853'],
      borderWidth: 0
    }]
  };

  // Top 10 Subjects Bar Chart (using unique topics)
  const subjectCounts = {};
  filteredTopics.forEach(item => {
    const subject = item.subject || 'Unknown';
    subjectCounts[subject] = (subjectCounts[subject] || 0) + 1;
  });

  const topSubjects = Object.entries(subjectCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10);

  const barData = {
    labels: topSubjects.map(([subject]) => subject),
    datasets: [{
      label: 'Number of Unique Topics',
      data: topSubjects.map(([, count]) => count),
      backgroundColor: topSubjects.map((_, i) => {
        const colors = ['#4285F4', '#EA4335', '#FBBC05', '#34A853', '#9AA0A6', '#4285F4', '#EA4335', '#FBBC05', '#34A853', '#9AA0A6'];
        return colors[i % colors.length];
      }),
      borderWidth: 0,
      borderRadius: 8
    }]
  };

  const chartOptions = {
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
    }
  };

  const barOptions = {
    ...chartOptions,
    scales: {
      y: { 
        beginAtZero: true, 
        grid: { color: '#3c4043' }, 
        ticks: { color: '#9aa0a6' },
        title: { display: true, text: 'Topic Count', color: '#9aa0a6' }
      },
      x: { 
        grid: { display: false }, 
        ticks: { color: '#9aa0a6', maxRotation: 45, minRotation: 45 } 
      }
    }
  };

  // Handle chart view change with complete remount
  const handleChartViewChange = (view) => {
    setChartView(view);
    setChartKey(prev => prev + 1);
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
    metricsGrid: {
      display: 'grid',
      gridTemplateColumns: 'repeat(3, 1fr)',
      gap: 16,
      marginBottom: 24
    },
    metricCard: {
      background: '#2d2e30',
      padding: 20,
      borderRadius: 12,
      border: '1px solid #3c4043'
    },
    metricValue: {
      margin: '0 0 4px 0',
      fontSize: 32,
      fontWeight: 500,
      color: '#e8eaed'
    },
    metricLabel: {
      margin: 0,
      fontSize: 14,
      color: '#9aa0a6'
    },
    metricTrend: {
      margin: '8px 0 0',
      fontSize: 12,
      color: '#34A853'
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
      flexWrap: 'wrap',
      gap: 24
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
    chartsSection: {
      background: '#2d2e30',
      borderRadius: 16,
      padding: 24,
      border: '1px solid #3c4043',
      marginBottom: 24
    },
    chartHeader: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: 20
    },
    chartTitle: {
      margin: 0,
      fontSize: 18,
      fontWeight: 500,
      color: '#e8eaed'
    },
    chartToggle: {
      display: 'flex',
      gap: 8,
      background: '#35363a',
      padding: 4,
      borderRadius: 100
    },
    toggleBtn: {
      padding: '8px 16px',
      border: 'none',
      borderRadius: 100,
      cursor: 'pointer',
      fontSize: 13,
      fontWeight: 500,
      transition: 'all 0.2s',
      background: 'transparent',
      color: '#9aa0a6'
    },
    toggleBtnActive: {
      background: '#4285F4',
      color: 'white'
    },
    chartsGrid: {
      display: 'grid',
      gridTemplateColumns: '1fr 1fr',
      gap: 20
    },
    chartCard: {
      background: '#35363a',
      borderRadius: 12,
      padding: 16
    },
    chartWrapper: {
      height: 300,
      width: '100%'
    },
    statsSummary: {
      background: '#35363a',
      borderRadius: 12,
      padding: 20
    },
    statsList: {
      display: 'flex',
      flexDirection: 'column',
      gap: 12,
      marginTop: 12
    },
    statRow: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: '8px 0',
      borderBottom: '1px solid #3c4043'
    },
    statLabel: {
      color: '#9aa0a6',
      fontSize: 14
    },
    statValue: {
      color: '#e8eaed',
      fontWeight: 500,
      fontSize: 16
    },
    tableSection: {
      background: '#2d2e30',
      borderRadius: 16,
      padding: 24,
      border: '1px solid #3c4043'
    },
    searchContainer: {
      display: 'flex',
      gap: 12,
      marginBottom: 20
    },
    searchInput: {
      flex: 1,
      padding: '12px 16px',
      background: '#35363a',
      border: '1px solid #3c4043',
      borderRadius: 100,
      color: '#e8eaed',
      fontSize: 14,
      outline: 'none'
    },
    filterSelect: {
      padding: '12px 24px',
      background: '#35363a',
      border: '1px solid #3c4043',
      borderRadius: 100,
      color: '#e8eaed',
      fontSize: 14,
      cursor: 'pointer',
      outline: 'none'
    },
    tableContainer: {
      overflowX: 'auto',
      borderRadius: 12,
      border: '1px solid #3c4043'
    },
    table: {
      width: '100%',
      borderCollapse: 'collapse',
      minWidth: 1200,
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
      width: 80,
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
      display: 'inline-block'
    },
    tableFooter: {
      padding: '16px',
      textAlign: 'center',
      color: '#9aa0a6',
      fontSize: 13,
      borderTop: '1px solid #3c4043'
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
    <div className="topic-analysis-container" style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <div>
          <h1 style={styles.title}>📚 Topic-wise Analysis</h1>
          <p style={styles.subtitle}>
            {filteredTopics.length} unique topics • Updated real-time
          </p>
        </div>
      </div>

      {/* Stats Cards */}
      <div style={styles.metricsGrid}>
        <div style={styles.metricCard}>
          <h3 style={styles.metricValue}>{data.length}</h3>
          <p style={styles.metricLabel}>Total Records</p>
          <p style={styles.metricTrend}>including duplicates</p>
        </div>
        <div style={styles.metricCard}>
          <h3 style={styles.metricValue}>{processedData.length}</h3>
          <p style={styles.metricLabel}>Unique Topics</p>
          <p style={styles.metricTrend}>after deduplication</p>
        </div>
        <div style={styles.metricCard}>
          <h3 style={styles.metricValue}>{data.length - processedData.length}</h3>
          <p style={styles.metricLabel}>Repeated Topics</p>
          <p style={styles.metricTrend}>same subject+topic</p>
        </div>
      </div>

      {/* Info Box */}
      <div style={styles.infoBox}>
        <h3 style={styles.infoTitle}>📊 Difficulty & Confidence Guide</h3>
        <div style={styles.infoStats}>
          <div style={styles.infoItem}>
            <div style={{...styles.infoDot, background: '#EA4335'}} />
            <span>Hard: 2.91-5.0</span>
          </div>
          <div style={styles.infoItem}>
            <div style={{...styles.infoDot, background: '#FBBC05'}} />
            <span>Medium: 2.01-2.90</span>
          </div>
          <div style={styles.infoItem}>
            <div style={{...styles.infoDot, background: '#34A853'}} />
            <span>Low: 1.0-2.0</span>
          </div>
          <div style={styles.infoItem}>
            <div style={{...styles.infoDot, background: '#34A853'}} />
            <span>Confidence: High ≥70%</span>
          </div>
          <div style={styles.infoItem}>
            <div style={{...styles.infoDot, background: '#FBBC05'}} />
            <span>Confidence: Medium 40-69%</span>
          </div>
          <div style={styles.infoItem}>
            <div style={{...styles.infoDot, background: '#EA4335'}} />
            <span>Confidence: Low &lt;40%</span>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div style={styles.chartsSection}>
        <div style={styles.chartHeader}>
          <h3 style={styles.chartTitle}>📊 Topic Analysis Charts</h3>
          <div style={styles.chartToggle}>
            <button 
              style={{
                ...styles.toggleBtn,
                ...(chartView === 'pie' ? styles.toggleBtnActive : {})
              }}
              onClick={() => handleChartViewChange('pie')}
            >
              🥧 Pie Chart
            </button>
            <button 
              style={{
                ...styles.toggleBtn,
                ...(chartView === 'bar' ? styles.toggleBtnActive : {})
              }}
              onClick={() => handleChartViewChange('bar')}
            >
              📊 Bar Chart
            </button>
          </div>
        </div>

        <div style={styles.chartsGrid}>
          {/* Chart 1 - Main Chart */}
          <div style={styles.chartCard}>
            <h4 style={{ margin: '0 0 16px 0', color: '#e8eaed', fontSize: 14 }}>
              {chartView === 'pie' ? 'Difficulty Distribution' : 'Top 10 Subjects by Topic Count'}
            </h4>
            <div style={styles.chartWrapper} key={`wrapper-${chartKey}`}>
              {chartView === 'pie' ? (
                <Pie data={pieData} options={chartOptions} />
              ) : (
                <Bar data={barData} options={barOptions} />
              )}
            </div>
          </div>

          {/* Chart 2 - Stats Summary */}
          <div style={styles.statsSummary}>
            <h4 style={{ margin: 0, color: '#e8eaed', fontSize: 14 }}>Quick Stats</h4>
            <div style={styles.statsList}>
              <div style={styles.statRow}>
                <span style={styles.statLabel}>Unique Topics:</span>
                <span style={styles.statValue}>{filteredTopics.length}</span>
              </div>
              <div style={styles.statRow}>
                <span style={{...styles.statLabel, color: '#EA4335'}}>Hard (2.91-5.0):</span>
                <span style={styles.statValue}>{difficultyCounts.Hard}</span>
              </div>
              <div style={styles.statRow}>
                <span style={{...styles.statLabel, color: '#FBBC05'}}>Medium (2.01-2.90):</span>
                <span style={styles.statValue}>{difficultyCounts.Medium}</span>
              </div>
              <div style={styles.statRow}>
                <span style={{...styles.statLabel, color: '#34A853'}}>Low (1.0-2.0):</span>
                <span style={styles.statValue}>{difficultyCounts.Low}</span>
              </div>
              <div style={styles.statRow}>
                <span style={styles.statLabel}>Avg Difficulty:</span>
                <span style={styles.statValue}>
                  {filteredTopics.length > 0 
                    ? (filteredTopics.reduce((sum, t) => sum + safeParseFloat(t.overall_difficulty), 0) / filteredTopics.length).toFixed(2)
                    : '0.00'}
                </span>
              </div>
              <div style={styles.statRow}>
                <span style={styles.statLabel}>Max Occurrences:</span>
                <span style={styles.statValue}>{maxOccurrences}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Table Section */}
      <div style={styles.tableSection}>
        <div style={styles.chartHeader}>
          <h3 style={styles.chartTitle}>📋 Topic Summary Table</h3>
          <div style={styles.searchContainer}>
            <input
              type="text"
              placeholder="Search subjects or topics..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={styles.searchInput}
            />
            <select 
              value={filterDifficulty} 
              onChange={(e) => setFilterDifficulty(e.target.value)}
              style={styles.filterSelect}
            >
              <option value="all">All Difficulties</option>
              <option value="Hard">🔴 Hard (2.91-5.0)</option>
              <option value="Medium">🟠 Medium (2.01-2.90)</option>
              <option value="Low">🟢 Low (1.0-2.0)</option>
            </select>
          </div>
        </div>

        <div style={styles.tableContainer}>
          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.th}>Subject</th>
                <th style={styles.th}>Topic</th>
                <th style={styles.th}>Occ</th>
                <th style={styles.th}>Tweets</th>
                <th style={styles.th}>Tweet Stress</th>
                <th style={styles.th}>Memes</th>
                <th style={styles.th}>Meme Stress</th>
                <th style={styles.th}>Papers</th>
                <th style={styles.th}>Paper Diff</th>
                <th style={styles.th}>Overall Diff</th>
                <th style={styles.th}>Confidence</th>
                <th style={styles.th}>Level</th>
              </tr>
            </thead>
            <tbody>
              {filteredTopics.slice(0, 50).map((item, index) => {
                const overallDiff = safeParseFloat(item.overall_difficulty);
                const tweetStress = safeParseFloat(item.tweet_stress);
                const memeStress = safeParseFloat(item.meme_stress);
                const paperDiff = safeParseFloat(item.paper_difficulty);
                const confidence = item.confidence || 0;
                const confidenceColor = getConfidenceColor(confidence);
                const diffColor = getDifficultyColor(overallDiff);
                const diffLabel = getDifficultyLabel(overallDiff);
                
                return (
                  <tr key={`${item.subject}-${item.topic}-${index}`} style={index % 2 === 0 ? styles.rowEven : styles.rowOdd}>
                    <td style={styles.td}>{item.subject || 'N/A'}</td>
                    <td style={styles.td}>{item.topic || 'N/A'}</td>
                    <td style={styles.td}>{item.occurrences || 1}</td>
                    <td style={styles.td}>{item.tweet_count || 1}</td>
                    <td style={styles.td}>{tweetStress.toFixed(2)}</td>
                    <td style={styles.td}>{item.meme_count || 1}</td>
                    <td style={styles.td}>{memeStress.toFixed(2)}</td>
                    <td style={styles.td}>{item.paper_count || 0}</td>
                    <td style={styles.td}>{paperDiff.toFixed(2)}</td>
                    <td style={styles.td}>
                      <div style={styles.scoreContainer}>
                        <span style={{ color: diffColor, fontWeight: 500, minWidth: 45 }}>
                          {overallDiff.toFixed(2)}
                        </span>
                        <div style={styles.progressBar}>
                          <div style={{...styles.progressFill, width: `${(overallDiff / 5) * 100}%`, backgroundColor: diffColor}} />
                        </div>
                      </div>
                    </td>
                    <td style={styles.td}>
                      <div style={styles.scoreContainer}>
                        <span style={{ color: confidenceColor, fontWeight: 500, minWidth: 35 }}>
                          {confidence}%
                        </span>
                        <div style={styles.progressBar}>
                          <div style={{...styles.progressFill, width: `${confidence}%`, backgroundColor: confidenceColor}} />
                        </div>
                      </div>
                    </td>
                    <td style={styles.td}>
                      <span style={{
                        ...styles.badge,
                        background: diffLabel === 'Hard' ? '#EA433520' : 
                                   diffLabel === 'Medium' ? '#FBBC0520' : '#34A85320',
                        color: diffLabel === 'Hard' ? '#EA4335' : 
                               diffLabel === 'Medium' ? '#FBBC05' : '#34A853',
                        border: `1px solid ${diffLabel === 'Hard' ? '#EA4335' : 
                                            diffLabel === 'Medium' ? '#FBBC05' : '#34A853'}`
                      }}>
                        {diffLabel}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          <div style={styles.tableFooter}>
            Showing {Math.min(50, filteredTopics.length)} of {filteredTopics.length} unique topics
          </div>
        </div>
      </div>

      {/* Legend */}
      <div style={styles.legend}>
        <div style={styles.legendItem}>
          <div style={{ width: 16, height: 16, background: '#EA4335', borderRadius: 4 }} />
          <span>Hard (2.91-5.0)</span>
        </div>
        <div style={styles.legendItem}>
          <div style={{ width: 16, height: 16, background: '#FBBC05', borderRadius: 4 }} />
          <span>Medium (2.01-2.90)</span>
        </div>
        <div style={styles.legendItem}>
          <div style={{ width: 16, height: 16, background: '#34A853', borderRadius: 4 }} />
          <span>Low (1.0-2.0)</span>
        </div>
        <div style={styles.legendItem}>
          <div style={{ width: 16, height: 16, background: '#34A853', borderRadius: 4 }} />
          <span>High Confidence (≥70%)</span>
        </div>
        <div style={styles.legendItem}>
          <div style={{ width: 16, height: 16, background: '#FBBC05', borderRadius: 4 }} />
          <span>Medium Confidence (40-69%)</span>
        </div>
        <div style={styles.legendItem}>
          <div style={{ width: 16, height: 16, background: '#EA4335', borderRadius: 4 }} />
          <span>Low Confidence (&lt;40%)</span>
        </div>
      </div>
    </div>
  );
};

export default TopicAnalysis;