import React from 'react';
import { Pie } from 'react-chartjs-2';

const DifficultTopics = ({ 
  data = [], 
  top3Hardest = [], 
  top3Easiest = [],
  recommendations = []
}) => {
  console.log('DifficultTopics received:', { data, top3Hardest, top3Easiest, recommendations });

  if (!data || data.length === 0) {
    return (
      <div style={styles.container}>
        <div style={styles.header}>
          <h2 style={styles.title}>🎯 Topic Difficulty Analysis</h2>
        </div>
        <div style={styles.noData}>
          <p>No topic data available for this exam.</p>
        </div>
      </div>
    );
  }

  // Find max occurrences to calculate confidence percentage
  const maxOccurrences = Math.max(...data.map(item => item.occurrences || 1));
  
  // Process data with new thresholds
  const processedData = data.map(item => {
    const score = item.difficulty || item.fused_difficulty_score || 0;
    const occurrences = item.occurrences || 1;
    
    // Calculate contribution percentages (30% tweets, 20% memes, 50% papers)
    const tweetContribution = 30;
    const memeContribution = 20;
    const paperContribution = 50;
    
    // NEW THRESHOLDS:
    // 3.00 to 5.00 -> Hard
    // 2.00 to 2.99 -> Medium
    // 0.00 to 1.99 -> Low
    let level = "Low";
    if (score >= 3.0) {
      level = "Hard";
    } else if (score >= 2.0) {
      level = "Medium";
    } else {
      level = "Low";
    }
    
    // Calculate confidence based on occurrence count
    // More occurrences = higher confidence
    // Map occurrences to 0-100% scale based on max occurrences
    const confidencePercent = Math.round((occurrences / maxOccurrences) * 100);
    
    return {
      ...item,
      difficulty: score,
      level: level,
      difficulty_label: level,
      occurrences: occurrences,
      confidence: confidencePercent,
      tweetContribution,
      memeContribution,
      paperContribution
    };
  });

  // Calculate statistics using processed data
  const totalTopics = processedData.length;
  const totalOccurrences = processedData.reduce((sum, t) => sum + (t.occurrences || 1), 0);
  
  const hardTopics = processedData.filter(t => t.level === 'Hard');
  const mediumTopics = processedData.filter(t => t.level === 'Medium');
  const lowTopics = processedData.filter(t => t.level === 'Low');
  
  const avgDifficulty = (processedData.reduce((sum, t) => sum + t.difficulty, 0) / totalTopics).toFixed(2);
  const avgConfidence = Math.round(processedData.reduce((sum, t) => sum + t.confidence, 0) / totalTopics);
  const maxDifficulty = Math.max(...processedData.map(t => t.difficulty));
  const minDifficulty = Math.min(...processedData.map(t => t.difficulty));

  // Sort for hardest/easiest
  const sortedByDifficulty = [...processedData].sort((a, b) => b.difficulty - a.difficulty);
  const top3HardestList = sortedByDifficulty.slice(0, 3);
  const top3EasiestList = sortedByDifficulty.slice(-3).reverse();

  // Prepare pie chart data
  const pieData = {
    labels: ['Hard (3.0-5.0)', 'Medium (2.0-2.99)', 'Low (0-1.99)'],
    datasets: [
      {
        data: [hardTopics.length, mediumTopics.length, lowTopics.length],
        backgroundColor: ['#EA4335', '#FBBC05', '#34A853'],
        borderWidth: 0
      }
    ]
  };

  // Contribution Pie Chart Data (30% tweets, 20% memes, 50% papers)
  const contributionPieData = {
    labels: ['Tweets (30%)', 'Memes (20%)', 'Papers (50%)'],
    datasets: [
      {
        data: [30, 20, 50],
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

  const contributionOptions = {
    ...options,
    plugins: {
      ...options.plugins,
      tooltip: {
        ...options.plugins.tooltip,
        callbacks: {
          label: function(context) {
            return `${context.label}: ${context.raw}%`;
          }
        }
      }
    }
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
    statsGridThree: {
      display: 'grid',
      gridTemplateColumns: 'repeat(3, 1fr)',
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
    recommendationsCard: {
      background: '#2d2e30',
      borderRadius: 12,
      padding: 20,
      border: '1px solid #3c4043',
      marginBottom: 24
    },
    recommendationsList: {
      display: 'flex',
      flexDirection: 'column',
      gap: 12,
      marginTop: 16
    },
    recommendationItem: {
      display: 'flex',
      alignItems: 'center',
      gap: 16,
      padding: 12,
      background: '#35363a',
      borderRadius: 8
    },
    recRank: {
      width: 24,
      height: 24,
      borderRadius: '50%',
      background: '#4285F4',
      color: 'white',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontSize: 12,
      fontWeight: 500
    },
    recContent: {
      flex: 1,
      display: 'flex',
      flexDirection: 'column',
      gap: 4
    },
    recTopic: {
      fontWeight: 600,
      color: '#e8eaed'
    },
    recSubject: {
      fontSize: 11,
      color: '#9aa0a6'
    },
    recReason: {
      fontSize: 11,
      color: '#34A853'
    },
    recScore: {
      padding: '4px 8px',
      background: '#EA433520',
      color: '#EA4335',
      borderRadius: 100,
      fontSize: 11,
      fontWeight: 500
    },
    topTopicsRow: {
      display: 'grid',
      gridTemplateColumns: '1fr 1fr',
      gap: 20,
      marginBottom: 24
    },
    topTopicsSection: {
      background: '#2d2e30',
      borderRadius: 12,
      padding: 20,
      border: '1px solid #3c4043'
    },
    sectionTitle: {
      margin: '0 0 16px 0',
      fontSize: 16,
      fontWeight: 500,
      display: 'flex',
      alignItems: 'center',
      gap: 8
    },
    titleIcon: {
      fontSize: 20
    },
    topicsVerticalList: {
      display: 'flex',
      flexDirection: 'column',
      gap: 12
    },
    topicListItem: {
      display: 'flex',
      alignItems: 'center',
      gap: 12,
      padding: 12,
      background: '#35363a',
      borderRadius: 8
    },
    topicRank: {
      width: 24,
      height: 24,
      borderRadius: '50%',
      background: '#4285F4',
      color: 'white',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontSize: 12,
      fontWeight: 500
    },
    topicInfo: {
      flex: 1,
      display: 'flex',
      flexDirection: 'column',
      gap: 2
    },
    topicName: {
      fontWeight: 500,
      color: '#e8eaed'
    },
    topicSubject: {
      fontSize: 11,
      color: '#9aa0a6'
    },
    topicOccurrences: {
      fontSize: 10,
      color: '#9aa0a6'
    },
    topicScore: {
      display: 'flex',
      alignItems: 'center',
      gap: 8,
      minWidth: 100
    },
    scoreBar: {
      width: 60,
      height: 4,
      background: '#3c4043',
      borderRadius: 2,
      overflow: 'hidden'
    },
    scoreFill: {
      height: '100%',
      borderRadius: 2
    },
    scoreValue: {
      fontSize: 12,
      fontWeight: 600,
      minWidth: 35
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
    summaryCard: {
      background: '#2d2e30',
      borderRadius: 12,
      padding: 20,
      border: '1px solid #3c4043',
      marginBottom: 24
    },
    summaryGrid: {
      display: 'grid',
      gridTemplateColumns: 'repeat(3, 1fr)',
      gap: 16,
      marginBottom: 16
    },
    summaryItem: {
      background: '#35363a',
      padding: 16,
      borderRadius: 8
    },
    summaryLabel: {
      color: '#9aa0a6',
      fontSize: 12,
      display: 'block',
      marginBottom: 8
    },
    summaryValue: {
      color: '#e8eaed',
      fontWeight: 600,
      fontSize: 16
    },
    summaryScore: {
      fontSize: 13,
      marginTop: 4
    },
    contributionSection: {
      background: '#35363a',
      padding: 16,
      borderRadius: 8,
      marginTop: 8
    },
    contributionTitle: {
      color: '#e8eaed',
      marginBottom: 12,
      fontSize: 14,
      fontWeight: 500
    },
    contributionRow: {
      display: 'flex',
      gap: 16,
      flexWrap: 'wrap'
    },
    contributionItem: {
      flex: 1,
      minWidth: 150
    },
    contributionLabel: {
      display: 'flex',
      justifyContent: 'space-between',
      marginBottom: 4
    },
    contributionText: {
      color: '#9aa0a6',
      fontSize: 12
    },
    contributionValue: {
      fontWeight: 600
    },
    progressBar: {
      height: 6,
      background: '#3c4043',
      borderRadius: 3,
      overflow: 'hidden'
    },
    progressFill: {
      height: '100%',
      borderRadius: 3
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
      minWidth: 900,
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
      gap: 8
    },
    badge: {
      padding: '4px 12px',
      borderRadius: 100,
      fontSize: 11,
      fontWeight: 500,
      display: 'inline-block',
      fontFamily: "'Poppins', sans-serif"
    },
    footnote: {
      marginTop: 8,
      padding: 12,
      background: '#35363a',
      borderRadius: 8,
      fontSize: 11,
      color: '#9aa0a6',
      textAlign: 'right'
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

  return (
    <div style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <h2 style={styles.title}>🎯 Topic Difficulty Analysis</h2>
        <p style={styles.subtitle}>Detailed analysis of topic difficulty levels and patterns</p>
      </div>
      
      {/* Stats Cards - First Row */}
      <div style={styles.statsGrid}>
        <div style={styles.statCard}>
          <p style={styles.statLabel}>Unique Topics</p>
          <h3 style={styles.statValue}>{totalTopics}</h3>
          <p style={styles.statTrend}>Distinct topics</p>
        </div>
        
        <div style={styles.statCard}>
          <p style={styles.statLabel}>Total Occurrences</p>
          <h3 style={styles.statValue}>{totalOccurrences}</h3>
          <p style={styles.statTrend}>Including repetitions</p>
        </div>
        
        <div style={styles.statCard}>
          <p style={styles.statLabel}>Avg Difficulty</p>
          <h3 style={{...styles.statValue, color: avgDifficulty >= 3.0 ? '#EA4335' : avgDifficulty >= 2.0 ? '#FBBC05' : '#34A853'}}>
            {avgDifficulty}
          </h3>
          <p style={styles.statTrend}>/5.0 scale</p>
        </div>
        
        <div style={styles.statCard}>
          <p style={styles.statLabel}>Avg Confidence</p>
          <h3 style={{...styles.statValue, color: avgConfidence >= 70 ? '#34A853' : avgConfidence >= 40 ? '#FBBC05' : '#EA4335'}}>
            {avgConfidence}%
          </h3>
          <p style={styles.statTrend}>Based on occurrences</p>
        </div>
      </div>

      {/* Second Row - Difficulty Distribution Stats */}
      <div style={styles.statsGridThree}>
        <div style={styles.statCard}>
          <p style={styles.statLabel}>Hard (3.0-5.0)</p>
          <h3 style={{...styles.statValue, color: '#EA4335'}}>{hardTopics.length}</h3>
          <p style={styles.statTrend}>{((hardTopics.length/totalTopics)*100).toFixed(1)}%</p>
        </div>
        
        <div style={styles.statCard}>
          <p style={styles.statLabel}>Medium (2.0-2.99)</p>
          <h3 style={{...styles.statValue, color: '#FBBC05'}}>{mediumTopics.length}</h3>
          <p style={styles.statTrend}>{((mediumTopics.length/totalTopics)*100).toFixed(1)}%</p>
        </div>
        
        <div style={styles.statCard}>
          <p style={styles.statLabel}>Low (0-1.99)</p>
          <h3 style={{...styles.statValue, color: '#34A853'}}>{lowTopics.length}</h3>
          <p style={styles.statTrend}>{((lowTopics.length/totalTopics)*100).toFixed(1)}%</p>
        </div>
      </div>

      {/* Info Box */}
      <div style={styles.infoBox}>
        <h4 style={styles.infoTitle}>🎯 Topic Analysis</h4>
        <p style={{ margin: 0, color: '#9aa0a6', fontSize: 13 }}>
          Based on exam_summary table - {totalTopics} unique topics, {totalOccurrences} total occurrences
        </p>
        <div style={styles.infoStats}>
          <div style={styles.infoItem}>
            <div style={{...styles.infoDot, background: '#EA4335'}} />
            <span>Hard (≥3.0): {hardTopics.length}</span>
          </div>
          <div style={styles.infoItem}>
            <div style={{...styles.infoDot, background: '#FBBC05'}} />
            <span>Medium (2.0-2.99): {mediumTopics.length}</span>
          </div>
          <div style={styles.infoItem}>
            <div style={{...styles.infoDot, background: '#34A853'}} />
            <span>Low (0-1.99): {lowTopics.length}</span>
          </div>
          <div style={styles.infoItem}>
            <div style={{...styles.infoDot, background: '#4285F4'}} />
            <span>Max Occurrences: {maxOccurrences}</span>
          </div>
        </div>
      </div>

      {/* AI Recommendations */}
      {recommendations.length > 0 && (
        <div style={styles.recommendationsCard}>
          <h4 style={styles.infoTitle}>🤖 AI Recommended Focus Topics</h4>
          <div style={styles.recommendationsList}>
            {recommendations.map((rec, index) => (
              <div key={index} style={styles.recommendationItem}>
                <span style={styles.recRank}>{index + 1}</span>
                <div style={styles.recContent}>
                  <span style={styles.recTopic}>{rec.topic}</span>
                  <span style={styles.recSubject}>{rec.subject}</span>
                  <span style={styles.recReason}>{rec.reason}</span>
                </div>
                <span style={styles.recScore}>{rec.difficulty.toFixed(2)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Two Column Layout for Top 3 Sections */}
      <div style={styles.topTopicsRow}>
        {/* Top 3 Hardest */}
        {top3HardestList.length > 0 && (
          <div style={styles.topTopicsSection}>
            <h4 style={{...styles.sectionTitle, color: '#EA4335'}}>
              <span style={styles.titleIcon}>🔥</span> Top 3 Hardest Topics (≥3.0)
            </h4>
            <div style={styles.topicsVerticalList}>
              {top3HardestList.map((item, index) => (
                <div key={index} style={styles.topicListItem}>
                  <span style={styles.topicRank}>{index + 1}</span>
                  <div style={styles.topicInfo}>
                    <span style={styles.topicName}>{item.topic}</span>
                    <span style={styles.topicSubject}>{item.subject}</span>
                    <span style={styles.topicOccurrences}>appears {item.occurrences} times</span>
                  </div>
                  <div style={styles.topicScore}>
                    <div style={styles.scoreBar}>
                      <div 
                        style={{ 
                          ...styles.scoreFill,
                          width: `${(item.difficulty / 5) * 100}%`,
                          background: '#EA4335'
                        }} 
                      />
                    </div>
                    <span style={{...styles.scoreValue, color: '#EA4335'}}>{item.difficulty.toFixed(2)}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Top 3 Easiest */}
        {top3EasiestList.length > 0 && (
          <div style={styles.topTopicsSection}>
            <h4 style={{...styles.sectionTitle, color: '#34A853'}}>
              <span style={styles.titleIcon}>✅</span> Top 3 Easiest Topics (&lt;2.0)
            </h4>
            <div style={styles.topicsVerticalList}>
              {top3EasiestList.map((item, index) => (
                <div key={index} style={styles.topicListItem}>
                  <span style={styles.topicRank}>{index + 1}</span>
                  <div style={styles.topicInfo}>
                    <span style={styles.topicName}>{item.topic}</span>
                    <span style={styles.topicSubject}>{item.subject}</span>
                    <span style={styles.topicOccurrences}>appears {item.occurrences} times</span>
                  </div>
                  <div style={styles.topicScore}>
                    <div style={styles.scoreBar}>
                      <div 
                        style={{ 
                          ...styles.scoreFill,
                          width: `${(item.difficulty / 5) * 100}%`,
                          background: '#34A853'
                        }} 
                      />
                    </div>
                    <span style={{...styles.scoreValue, color: '#34A853'}}>{item.difficulty.toFixed(2)}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Charts Grid - Two Pies */}
      <div style={styles.chartGrid}>
        {/* Difficulty Distribution Pie */}
        <div style={styles.chartCard}>
          <h5 style={styles.chartTitle}>Difficulty Distribution</h5>
          <div style={{ height: 250 }}>
            <Pie data={pieData} options={options} />
          </div>
        </div>
        
        {/* Contribution Distribution Pie */}
        <div style={styles.chartCard}>
          <h5 style={styles.chartTitle}>Contribution Breakdown</h5>
          <div style={{ height: 250 }}>
            <Pie data={contributionPieData} options={contributionOptions} />
          </div>
          <div style={{ 
            display: 'flex',
            justifyContent: 'center',
            gap: 16,
            marginTop: 12
          }}>
            <span style={{ color: '#4285F4', fontSize: 11 }}>📊 Tweets: 30%</span>
            <span style={{ color: '#FBBC05', fontSize: 11 }}>😂 Memes: 20%</span>
            <span style={{ color: '#34A853', fontSize: 11 }}>📄 Papers: 50%</span>
          </div>
        </div>
      </div>

      {/* Enhanced Summary Card with Contributions */}
      <div style={styles.summaryCard}>
        <h5 style={{ margin: '0 0 16px 0', fontSize: 15, fontWeight: 500 }}>📊 Detailed Summary</h5>
        <div style={styles.summaryGrid}>
          <div style={styles.summaryItem}>
            <span style={styles.summaryLabel}>Hardest Topic</span>
            <span style={styles.summaryValue}>{top3HardestList[0]?.topic || 'N/A'}</span>
            <div style={{...styles.summaryScore, color: '#EA4335'}}>
              Score: {top3HardestList[0]?.difficulty.toFixed(2) || 'N/A'}
            </div>
          </div>
          
          <div style={styles.summaryItem}>
            <span style={styles.summaryLabel}>Easiest Topic</span>
            <span style={styles.summaryValue}>{top3EasiestList[0]?.topic || 'N/A'}</span>
            <div style={{...styles.summaryScore, color: '#34A853'}}>
              Score: {top3EasiestList[0]?.difficulty.toFixed(2) || 'N/A'}
            </div>
          </div>
          
          <div style={styles.summaryItem}>
            <span style={styles.summaryLabel}>Most Frequent</span>
            <span style={styles.summaryValue}>{processedData.find(t => t.occurrences === maxOccurrences)?.topic || 'N/A'}</span>
            <div style={{...styles.summaryScore, color: '#FBBC05'}}>
              {maxOccurrences} occurrences
            </div>
          </div>
        </div>

        {/* Contribution Breakdown */}
        <div style={styles.contributionSection}>
          <h6 style={styles.contributionTitle}>📊 Score Contribution Breakdown</h6>
          <div style={styles.contributionRow}>
            <div style={styles.contributionItem}>
              <div style={styles.contributionLabel}>
                <span style={styles.contributionText}>Tweets:</span>
                <span style={{...styles.contributionValue, color: '#4285F4'}}>30%</span>
              </div>
              <div style={styles.progressBar}>
                <div style={{...styles.progressFill, width: '30%', backgroundColor: '#4285F4'}} />
              </div>
            </div>
            
            <div style={styles.contributionItem}>
              <div style={styles.contributionLabel}>
                <span style={styles.contributionText}>Memes:</span>
                <span style={{...styles.contributionValue, color: '#FBBC05'}}>20%</span>
              </div>
              <div style={styles.progressBar}>
                <div style={{...styles.progressFill, width: '20%', backgroundColor: '#FBBC05'}} />
              </div>
            </div>
            
            <div style={styles.contributionItem}>
              <div style={styles.contributionLabel}>
                <span style={styles.contributionText}>Papers:</span>
                <span style={{...styles.contributionValue, color: '#34A853'}}>50%</span>
              </div>
              <div style={styles.progressBar}>
                <div style={{...styles.progressFill, width: '50%', backgroundColor: '#34A853'}} />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Full Topics Table with Confidence based on Occurrences */}
      <div style={styles.tableContainer}>
        <h4 style={styles.tableTitle}>📋 Complete Topic Ranking (Unique Topics)</h4>
        <div style={{ overflowX: 'auto' }}>
          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.th}>Rank</th>
                <th style={styles.th}>Subject</th>
                <th style={styles.th}>Topic</th>
                <th style={styles.th}>Difficulty Score</th>
                <th style={styles.th}>Occurrences</th>
                <th style={styles.th}>Confidence %</th>
                <th style={styles.th}>Status</th>
              </tr>
            </thead>
            <tbody>
              {processedData.map((item, index) => {
                const level = item.level;
                const confidence = item.confidence;
                
                // Status emoji and color based on level
                let statusEmoji = '🟢';
                let statusColor = '#34A853';
                let statusText = 'Low';
                
                if (level === 'Hard') {
                  statusEmoji = '🔴';
                  statusColor = '#EA4335';
                  statusText = 'Hard';
                } else if (level === 'Medium') {
                  statusEmoji = '🟠';
                  statusColor = '#FBBC05';
                  statusText = 'Medium';
                }
                
                // Confidence color (based on percentage)
                const confidenceColor = confidence < 30 ? '#EA4335' : 
                                       confidence < 60 ? '#FBBC05' : '#34A853';
                
                return (
                  <tr key={index} style={index % 2 === 0 ? styles.rowEven : styles.rowOdd}>
                    <td style={styles.td}>{index + 1}</td>
                    <td style={styles.td}>{item.subject}</td>
                    <td style={styles.td}>{item.topic}</td>
                    <td style={styles.td}>
                      <div style={styles.progressContainer}>
                        <span style={{ color: level === 'Hard' ? '#EA4335' : level === 'Medium' ? '#FBBC05' : '#34A853', fontWeight: 500 }}>
                          {item.difficulty.toFixed(2)}
                        </span>
                        <div style={styles.scoreBar}>
                          <div 
                            style={{ 
                              width: `${(item.difficulty / 5) * 100}%`,
                              height: '100%',
                              backgroundColor: level === 'Hard' ? '#EA4335' : 
                                            level === 'Medium' ? '#FBBC05' : '#34A853',
                              borderRadius: 2
                            }} 
                          />
                        </div>
                      </div>
                    </td>
                    <td style={styles.td}>
                      <span style={{ 
                        fontWeight: 500,
                        color: item.occurrences > 10 ? '#EA4335' : 
                               item.occurrences > 5 ? '#FBBC05' : '#34A853'
                      }}>
                        {item.occurrences}x
                      </span>
                    </td>
                    <td style={styles.td}>
                      <div style={styles.progressContainer}>
                        <span style={{ color: confidenceColor, fontWeight: 500 }}>{confidence}%</span>
                        <div style={styles.scoreBar}>
                          <div 
                            style={{ 
                              width: `${confidence}%`,
                              height: '100%',
                              backgroundColor: confidenceColor,
                              borderRadius: 2
                            }} 
                          />
                        </div>
                      </div>
                    </td>
                    <td style={styles.td}>
                      <span style={{
                        ...styles.badge,
                        backgroundColor: statusColor + '20',
                        color: statusColor,
                        border: `1px solid ${statusColor}`
                      }}>
                        {statusEmoji} {statusText}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
      
      {/* Confidence Note */}
      <div style={styles.footnote}>
        <strong>Confidence:</strong> Based on occurrence frequency (higher occurrences = higher confidence) • 
        <strong> Max Occurrences:</strong> {maxOccurrences} times = 100% confidence • 
        <strong> Contribution Formula:</strong> 30% Tweets + 20% Memes + 50% Papers
      </div>
    </div>
  );
};

export default DifficultTopics;