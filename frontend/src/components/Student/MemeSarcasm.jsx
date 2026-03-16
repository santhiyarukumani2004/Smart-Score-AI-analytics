import React, { useState } from 'react';
import { Bar, Pie, Line } from 'react-chartjs-2';

const MemeSarcasm = ({ data, yearlyData, yearlyStressDistribution }) => {
  const [chartType, setChartType] = useState('bar');
  const [yearChartType, setYearChartType] = useState('stress');

  console.log('MemeSarcasm received data:', data);
  console.log('MemeSarcasm received yearlyData:', yearlyData);
  console.log('MemeSarcasm received yearlyStressDistribution:', yearlyStressDistribution);

  if (!data || data.meme_count === 0) {
    return (
      <div style={styles.container}>
        <div style={styles.header}>
          <h2 style={styles.title}>😂 Meme Stress & Sarcasm Analysis</h2>
        </div>
        <div style={styles.noData}>
          <p>No meme data available for this exam.</p>
        </div>
      </div>
    );
  }

  const {
    meme_count = 0,
    avg_stress = 0,
    avg_sarcasm = 0,
    sarcastic_count = 0,
    nonsarcastic_count = 0,
    sarcastic_pct = 0,
    nonsarcastic_pct = 0,
    high_stress = 0,
    medium_stress = 0,
    low_stress = 0,
    high_stress_pct = 0,
    medium_stress_pct = 0,
    low_stress_pct = 0
  } = data;

  // Yearly data from year_summary (for line graph)
  const yearData = Array.isArray(yearlyData) ? yearlyData : [];
  const years = yearData.map(item => item?.year?.toString() || 'N/A');
  const stressValues = yearData.map(item => parseFloat(item?.stress) || 0);
  const totalCounts = yearData.map(item => parseInt(item?.total_count) || 0);

  // Yearly stress distribution data (for stacked bar graph)
  const distributionData = Array.isArray(yearlyStressDistribution) ? yearlyStressDistribution : [];
  const distYears = distributionData.map(item => item.year);
  const highStressData = distributionData.map(item => item.high_stress);
  const mediumStressData = distributionData.map(item => item.medium_stress);
  const lowStressData = distributionData.map(item => item.low_stress);

  // LINE CHART - Year-wise Stress Trend
  const lineData = {
    labels: years,
    datasets: [
      {
        label: 'Average Stress (%)',
        data: stressValues,
        borderColor: '#4285F4',
        backgroundColor: 'rgba(66, 133, 244, 0.1)',
        tension: 0.4,
        fill: true,
        pointBackgroundColor: stressValues.map(value => {
          if (value >= 70) return '#EA4335';
          if (value >= 40) return '#FBBC05';
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

  // STACKED BAR CHART - Year-wise Meme Count with Stress Distribution
  const stackedBarData = {
    labels: distYears,
    datasets: [
      {
        label: 'High Stress',
        data: highStressData,
        backgroundColor: '#EA4335',
        borderRadius: 8,
        borderWidth: 0
      },
      {
        label: 'Medium Stress',
        data: mediumStressData,
        backgroundColor: '#FBBC05',
        borderRadius: 8,
        borderWidth: 0
      },
      {
        label: 'Low Stress',
        data: lowStressData,
        backgroundColor: '#34A853',
        borderRadius: 8,
        borderWidth: 0
      }
    ]
  };

  // BAR CHART - Overall Stress Distribution
  const stressBarData = {
    labels: ['High Stress', 'Medium Stress', 'Low Stress'],
    datasets: [
      {
        label: 'Meme Count',
        data: [high_stress, medium_stress, low_stress],
        backgroundColor: ['#EA4335', '#FBBC05', '#34A853'],
        borderRadius: 8,
        borderWidth: 0
      }
    ]
  };

  // PIE CHART - Sarcasm Distribution
  const sarcasmPieData = {
    labels: ['Sarcastic', 'Non-Sarcastic'],
    datasets: [
      {
        data: [sarcastic_count, nonsarcastic_count],
        backgroundColor: ['#EA4335', '#34A853'],
        borderWidth: 0
      }
    ]
  };

  // PIE CHART - Stress Percentage Distribution
  const stressPieData = {
    labels: ['High Stress', 'Medium Stress', 'Low Stress'],
    datasets: [
      {
        data: [high_stress_pct, medium_stress_pct, low_stress_pct],
        backgroundColor: ['#EA4335', '#FBBC05', '#34A853'],
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
        bodyFont: { size: 12, family: "'Poppins', sans-serif" },
        callbacks: {
          label: function(context) {
            let label = context.dataset.label || '';
            let value = context.raw;
            if (context.dataset.label.includes('Stress') || context.dataset.label.includes('Sarcasm')) {
              return `${label}: ${value.toFixed(1)}%`;
            }
            return `${label}: ${value}`;
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: { color: '#3c4043' },
        ticks: { color: '#9aa0a6', font: { size: 11, family: "'Poppins', sans-serif" } },
        title: {
          display: true,
          text: 'Count',
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

  const stackedBarOptions = {
    ...options,
    scales: {
      ...options.scales,
      x: {
        ...options.scales.x,
        stacked: true
      },
      y: {
        ...options.scales.y,
        stacked: true,
        beginAtZero: true
      }
    }
  };

  const lineOptions = {
    ...options,
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        grid: { color: '#3c4043' },
        ticks: { 
          color: '#9aa0a6', 
          font: { size: 11, family: "'Poppins', sans-serif" },
          callback: value => value + '%' 
        },
        title: {
          display: true,
          text: 'Stress Level (%)',
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
        <h2 style={styles.title}>😂 Meme Stress & Sarcasm Analysis</h2>
        <p style={styles.subtitle}>Comprehensive analysis of meme stress levels and sarcasm patterns</p>
      </div>
      
      {/* Stats Cards */}
      <div style={styles.statsGrid}>
        <div style={styles.statCard}>
          <p style={styles.statLabel}>Total Memes</p>
          <h3 style={styles.statValue}>{meme_count}</h3>
          <p style={styles.statTrend}>All time</p>
        </div>
        <div style={styles.statCard}>
          <p style={styles.statLabel}>Avg Stress</p>
          <h3 style={{...styles.statValue, color: avg_stress >= 70 ? '#EA4335' : avg_stress >= 40 ? '#FBBC05' : '#34A853'}}>
            {avg_stress.toFixed(1)}%
          </h3>
          <p style={styles.statTrend}>Overall</p>
        </div>
        <div style={styles.statCard}>
          <p style={styles.statLabel}>Sarcastic</p>
          <h3 style={{...styles.statValue, color: '#EA4335'}}>{sarcastic_count}</h3>
          <p style={styles.statTrend}>{sarcastic_pct.toFixed(1)}%</p>
        </div>
        <div style={styles.statCard}>
          <p style={styles.statLabel}>Sarcasm Score</p>
          <h3 style={{...styles.statValue, color: avg_sarcasm >= 50 ? '#EA4335' : '#34A853'}}>
            {avg_sarcasm.toFixed(1)}%
          </h3>
          <p style={styles.statTrend}>Average</p>
        </div>
      </div>

      {/* Info Box */}
      <div style={styles.infoBox}>
        <h4 style={styles.infoTitle}>😂 Meme Analysis Overview</h4>
        <p style={{ margin: 0, color: '#9aa0a6', fontSize: 13 }}>Comprehensive analysis of meme stress levels and sarcasm patterns.</p>
        <div style={styles.infoStats}>
          <div style={styles.infoItem}>
            <div style={{...styles.infoDot, background: '#4285F4'}} />
            <span>📊 Avg Stress: {avg_stress.toFixed(1)}%</span>
          </div>
          <div style={styles.infoItem}>
            <div style={{...styles.infoDot, background: '#EA4335'}} />
            <span>😏 Sarcasm Rate: {sarcastic_pct.toFixed(1)}%</span>
          </div>
          <div style={styles.infoItem}>
            <div style={{...styles.infoDot, background: '#34A853'}} />
            <span>😐 Non-Sarcastic: {nonsarcastic_pct.toFixed(1)}%</span>
          </div>
          <div style={styles.infoItem}>
            <div style={{...styles.infoDot, background: '#EA4335'}} />
            <span>📈 High Stress: {high_stress_pct.toFixed(1)}%</span>
          </div>
        </div>
      </div>

      {/* Main Chart Type Selector */}
      <div style={styles.chartTypeSelector}>
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
          Sarcasm Split
        </button>
      </div>

      {/* Charts Grid - First Row */}
      <div style={styles.chartGrid}>
        <div style={styles.chartCard}>
          <h5 style={styles.chartTitle}>
            {chartType === 'bar' ? 'Stress Level Distribution' : 'Stress Percentage Distribution'}
          </h5>
          <div style={{ height: 250 }}>
            {chartType === 'bar' ? (
              <Bar data={stressBarData} options={options} />
            ) : (
              <Pie data={stressPieData} options={options} />
            )}
          </div>
        </div>
        <div style={styles.chartCard}>
          <h5 style={styles.chartTitle}>Sarcasm Distribution</h5>
          <div style={{ height: 250 }}>
            <Pie data={sarcasmPieData} options={options} />
          </div>
        </div>
      </div>

      {/* Year-wise Analysis Section */}
      {(yearData.length > 0 || distributionData.length > 0) && (
        <>
          <div style={styles.infoBox}>
            <h4 style={styles.infoTitle}>📅 Year-wise Meme Analysis (2023-2026)</h4>
            <p style={{ margin: 0, color: '#9aa0a6', fontSize: 13 }}>Trend analysis of memes across different years.</p>
          </div>

          {/* Year Chart Type Selector */}
          <div style={styles.chartTypeSelector}>
            <button 
              style={{
                ...styles.chartTypeBtn,
                ...(yearChartType === 'stress' ? styles.chartTypeBtnActive : {})
              }}
              onClick={() => setYearChartType('stress')}
            >
              <span>📈</span>
              Stress Trend Line
            </button>
            <button 
              style={{
                ...styles.chartTypeBtn,
                ...(yearChartType === 'distribution' ? styles.chartTypeBtnActive : {})
              }}
              onClick={() => setYearChartType('distribution')}
            >
              <span>📊</span>
              Stress Distribution by Year
            </button>
          </div>

          {/* Year Chart */}
          <div style={styles.chartWrapper}>
            <h5 style={{...styles.chartTitle, marginBottom: 16}}>
              {yearChartType === 'stress' ? 'Year-wise Stress Trend' : 'Year-wise Meme Count by Stress Level'}
            </h5>
            <div style={{ height: 300 }}>
              {yearChartType === 'stress' ? (
                <Line data={lineData} options={lineOptions} />
              ) : (
                <Bar data={stackedBarData} options={stackedBarOptions} />
              )}
            </div>
          </div>

          {/* Year-wise Table Summary */}
          <div style={styles.tableContainer}>
            <h4 style={styles.tableTitle}>📅 Year-wise Meme Analysis Details</h4>
            <div style={{ overflowX: 'auto' }}>
              <table style={styles.table}>
                <thead>
                  <tr>
                    <th style={styles.th}>Year</th>
                    <th style={styles.th}>Total Memes</th>
                    <th style={styles.th}>High Stress</th>
                    <th style={styles.th}>Medium Stress</th>
                    <th style={styles.th}>Low Stress</th>
                    <th style={styles.th}>Avg Stress (%)</th>
                    <th style={styles.th}>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {distributionData.map((item, index) => {
                    const yearItem = yearData.find(y => y.year === item.year) || {};
                    const stress = yearItem.stress || 0;
                    const total = item.high_stress + item.medium_stress + item.low_stress;
                    
                    let statusColor = '#34A853';
                    let statusText = '🟢 Good';
                    if (stress >= 70) {
                      statusColor = '#EA4335';
                      statusText = '🔴 Critical';
                    } else if (stress >= 40) {
                      statusColor = '#FBBC05';
                      statusText = '🟠 Medium';
                    }
                    
                    return (
                      <tr key={index} style={index % 2 === 0 ? styles.rowEven : styles.rowOdd}>
                        <td style={styles.td}><strong>{item.year}</strong></td>
                        <td style={styles.td}>{total}</td>
                        <td style={{...styles.td, color: '#EA4335', fontWeight: 500}}>{item.high_stress}</td>
                        <td style={{...styles.td, color: '#FBBC05', fontWeight: 500}}>{item.medium_stress}</td>
                        <td style={{...styles.td, color: '#34A853', fontWeight: 500}}>{item.low_stress}</td>
                        <td style={styles.td}>{stress.toFixed(1)}%</td>
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
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}

      {/* Meme Summary Section */}
      <div style={styles.tableContainer}>
        <h4 style={styles.tableTitle}>📊 Meme Analysis Summary</h4>
        <div style={{ overflowX: 'auto' }}>
          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.th}>Category</th>
                <th style={styles.th}>Count</th>
                <th style={styles.th}>Percentage</th>
                <th style={styles.th}>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr style={styles.rowEven}>
                <td style={styles.td}>High Stress Memes</td>
                <td style={styles.td}>{high_stress}</td>
                <td style={styles.td}>{high_stress_pct.toFixed(1)}%</td>
                <td style={styles.td}>
                  <span style={{
                    ...styles.badge,
                    backgroundColor: high_stress_pct > 30 ? '#EA433520' : '#34A85320',
                    color: high_stress_pct > 30 ? '#EA4335' : '#34A853',
                    border: `1px solid ${high_stress_pct > 30 ? '#EA4335' : '#34A853'}`
                  }}>
                    {high_stress_pct > 30 ? '⚠️ High' : '✅ Normal'}
                  </span>
                </td>
              </tr>
              <tr style={styles.rowOdd}>
                <td style={styles.td}>Medium Stress Memes</td>
                <td style={styles.td}>{medium_stress}</td>
                <td style={styles.td}>{medium_stress_pct.toFixed(1)}%</td>
                <td style={styles.td}>-</td>
              </tr>
              <tr style={styles.rowEven}>
                <td style={styles.td}>Low Stress Memes</td>
                <td style={styles.td}>{low_stress}</td>
                <td style={styles.td}>{low_stress_pct.toFixed(1)}%</td>
                <td style={styles.td}>
                  <span style={{
                    ...styles.badge,
                    backgroundColor: low_stress_pct > 50 ? '#34A85320' : '#FBBC0520',
                    color: low_stress_pct > 50 ? '#34A853' : '#FBBC05',
                    border: `1px solid ${low_stress_pct > 50 ? '#34A853' : '#FBBC05'}`
                  }}>
                    {low_stress_pct > 50 ? '✅ Good' : '📊 Moderate'}
                  </span>
                </td>
              </tr>
              <tr style={styles.rowOdd}>
                <td style={styles.td}>Sarcastic Memes</td>
                <td style={styles.td}>{sarcastic_count}</td>
                <td style={styles.td}>{sarcastic_pct.toFixed(1)}%</td>
                <td style={styles.td}>
                  <span style={{
                    ...styles.badge,
                    backgroundColor: sarcastic_pct > 50 ? '#EA433520' : '#34A85320',
                    color: sarcastic_pct > 50 ? '#EA4335' : '#34A853',
                    border: `1px solid ${sarcastic_pct > 50 ? '#EA4335' : '#34A853'}`
                  }}>
                    {sarcastic_pct > 50 ? '🔴 High' : '🟢 Low'}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default MemeSarcasm;