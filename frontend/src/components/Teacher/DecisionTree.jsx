import React, { useState, useEffect } from 'react';
import './TeacherDashboard.css';

const DecisionTree = ({ data = null }) => {
  const [expandedNodes, setExpandedNodes] = useState(new Set());
  const [hoveredNode, setHoveredNode] = useState(null);

  console.log('DecisionTree received:', data);

  useEffect(() => {
    if (data?.children) {
      const initialExpanded = new Set();
      data.children.forEach((_, index) => {
        initialExpanded.add(`root-${index}`);
      });
      setExpandedNodes(initialExpanded);
    }
  }, [data]);

  if (!data) {
    return (
      <div style={styles.container}>
        <div style={styles.header}>
          <h1 style={styles.title}>🌳 Decision Tree</h1>
        </div>
        <div style={styles.noData}>
          <p>No tree data available</p>
        </div>
      </div>
    );
  }

  const toggleNode = (path) => {
    const newExpanded = new Set(expandedNodes);
    if (newExpanded.has(path)) {
      newExpanded.delete(path);
    } else {
      newExpanded.add(path);
    }
    setExpandedNodes(newExpanded);
  };

  // Google colors for difficulty thresholds
  const getDifficultyColor = (score) => {
    const numScore = parseFloat(score) || 0;
    if (numScore >= 2.91) return '#EA4335'; // Google Red
    if (numScore >= 2.01) return '#FBBC05'; // Google Yellow
    return '#34A853'; // Google Green
  };

  const getDifficultyLabel = (score) => {
    const numScore = parseFloat(score) || 0;
    if (numScore >= 2.91) return 'Hard';
    if (numScore >= 2.01) return 'Medium';
    return 'Low';
  };

  const renderNode = (node, level = 0, path = 'root') => {
    if (!node) return null;
    
    const isExpanded = expandedNodes.has(path);
    const isHovered = hoveredNode === path;
    const hasChildren = node.children && node.children.length > 0;
    
    let nodeColor = '#4285F4'; // Google Blue for exams
    if (node.type === 'subject') nodeColor = '#9AA0A6'; // Google Gray for subjects
    else if (node.type === 'topic') {
      const score = node.overall_score || 0;
      nodeColor = getDifficultyColor(score);
    }

    // Get difficulty label for topic nodes
    const difficultyLabel = node.type === 'topic' ? getDifficultyLabel(node.overall_score) : '';

    return (
      <div key={path} style={styles.nodeWrapper}>
        <div style={{ marginLeft: level * 40 }}>
          <div 
            style={{
              ...styles.node,
              backgroundColor: nodeColor,
              opacity: hoveredNode && hoveredNode !== path ? 0.7 : 1,
              transform: isHovered ? 'translateX(4px)' : 'none',
              cursor: hasChildren ? 'pointer' : 'default',
              boxShadow: isHovered ? '0 4px 12px rgba(0,0,0,0.3)' : 'none'
            }}
            onClick={() => hasChildren && toggleNode(path)}
            onMouseEnter={() => setHoveredNode(path)}
            onMouseLeave={() => setHoveredNode(null)}
          >
            <span style={styles.nodeName} title={node.name}>
              {node.name && node.name.length > 25 ? node.name.substring(0, 25) + '...' : node.name || 'Unknown'}
            </span>
            
            {node.overall_score !== undefined && (
              <span style={{
                ...styles.nodeScore,
                backgroundColor: 'rgba(255,255,255,0.2)'
              }}>
                {node.overall_score.toFixed(2)}
              </span>
            )}
            
            {difficultyLabel && (
              <span style={{
                ...styles.difficultyBadge,
                backgroundColor: nodeColor,
                border: '1px solid rgba(255,255,255,0.3)'
              }}>
                {difficultyLabel}
              </span>
            )}
            
            {hasChildren && (
              <span style={styles.expandIcon}>
                {isExpanded ? '−' : '+'}
              </span>
            )}
          </div>
          
          {node.topic_count > 0 && node.type !== 'topic' && (
            <div style={styles.nodeCount}>
              <span style={styles.countDot} /> {node.topic_count} topics
            </div>
          )}
        </div>

        {isExpanded && hasChildren && (
          <div style={styles.childrenContainer}>
            {node.children.map((child, index) => 
              renderNode(child, level + 1, `${path}-${index}`)
            )}
          </div>
        )}
      </div>
    );
  };

  const totalExams = data.children?.length || 0;
  const totalSubjects = data.children?.reduce((acc, exam) => acc + (exam.children?.length || 0), 0) || 0;
  const totalTopics = data.children?.reduce((acc, exam) => 
    acc + (exam.children?.reduce((subAcc, subj) => 
      subAcc + (subj.children?.length || 0), 0) || 0), 0) || 0;

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
    legendContainer: {
      display: 'flex',
      gap: 24,
      marginBottom: 24,
      padding: 16,
      background: '#2d2e30',
      borderRadius: 12,
      border: '1px solid #3c4043',
      flexWrap: 'wrap'
    },
    legendItem: {
      display: 'flex',
      alignItems: 'center',
      gap: 8
    },
    legendDot: {
      width: 12,
      height: 12,
      borderRadius: '50%'
    },
    legendText: {
      fontSize: 13,
      color: '#9aa0a6'
    },
    controls: {
      display: 'flex',
      gap: 12,
      marginBottom: 24
    },
    button: {
      padding: '10px 24px',
      background: '#35363a',
      border: '1px solid #3c4043',
      borderRadius: 100,
      color: '#e8eaed',
      fontSize: 13,
      fontWeight: 500,
      cursor: 'pointer',
      transition: 'all 0.2s',
      ':hover': {
        background: '#404144'
      }
    },
    treeContainer: {
      background: '#2d2e30',
      borderRadius: 16,
      padding: 32,
      border: '1px solid #3c4043',
      overflowX: 'auto'
    },
    nodeWrapper: {
      marginBottom: 8
    },
    node: {
      display: 'inline-flex',
      alignItems: 'center',
      gap: 8,
      padding: '8px 16px',
      borderRadius: 100,
      fontSize: 13,
      color: 'white',
      transition: 'all 0.2s ease',
      position: 'relative',
      minWidth: 200
    },
    nodeName: {
      fontWeight: 500,
      flex: 1
    },
    nodeScore: {
      padding: '2px 8px',
      borderRadius: 100,
      fontSize: 11,
      fontWeight: 500
    },
    difficultyBadge: {
      padding: '2px 8px',
      borderRadius: 100,
      fontSize: 10,
      fontWeight: 500,
      textTransform: 'uppercase',
      letterSpacing: '0.5px'
    },
    expandIcon: {
      width: 20,
      height: 20,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      borderRadius: '50%',
      background: 'rgba(255,255,255,0.2)',
      fontSize: 14,
      fontWeight: 'bold'
    },
    nodeCount: {
      marginLeft: 16,
      marginTop: 4,
      fontSize: 11,
      color: '#9aa0a6',
      display: 'flex',
      alignItems: 'center',
      gap: 6
    },
    countDot: {
      width: 6,
      height: 6,
      borderRadius: '50%',
      background: '#9aa0a6'
    },
    childrenContainer: {
      marginTop: 8,
      borderLeft: '2px solid #3c4043',
      paddingLeft: 20
    },
    statsCard: {
      marginTop: 24,
      padding: 20,
      background: '#2d2e30',
      borderRadius: 12,
      border: '1px solid #3c4043'
    },
    statsText: {
      margin: 0,
      fontSize: 14,
      color: '#e8eaed'
    },
    statsHighlight: {
      color: '#4285F4',
      fontWeight: 500
    },
    infoBox: {
      marginTop: 24,
      padding: 20,
      background: '#2d2e30',
      borderRadius: 12,
      border: '1px solid #3c4043'
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
          <h1 style={styles.title}>🌳 Knowledge Graph Decision Tree</h1>
          <p style={styles.subtitle}>
            {totalExams} exams • {totalSubjects} subjects • {totalTopics} topics
          </p>
        </div>
      </div>

      {/* Legend */}
      <div style={styles.legendContainer}>
        <div style={styles.legendItem}>
          <div style={{...styles.legendDot, background: '#4285F4'}} />
          <span style={styles.legendText}>Exam</span>
        </div>
        <div style={styles.legendItem}>
          <div style={{...styles.legendDot, background: '#9AA0A6'}} />
          <span style={styles.legendText}>Subject</span>
        </div>
        <div style={styles.legendItem}>
          <div style={{...styles.legendDot, background: '#EA4335'}} />
          <span style={styles.legendText}>Hard Topic (2.91 - 5.0)</span>
        </div>
        <div style={styles.legendItem}>
          <div style={{...styles.legendDot, background: '#FBBC05'}} />
          <span style={styles.legendText}>Medium Topic (2.01 - 2.90)</span>
        </div>
        <div style={styles.legendItem}>
          <div style={{...styles.legendDot, background: '#34A853'}} />
          <span style={styles.legendText}>Low Topic (1.0 - 2.0)</span>
        </div>
      </div>

      {/* Controls */}
      <div style={styles.controls}>
        <button style={styles.button} onClick={() => {
          const allPaths = new Set();
          const addPaths = (node, path = 'root') => {
            if (node.children) {
              node.children.forEach((child, index) => {
                const childPath = `${path}-${index}`;
                allPaths.add(childPath);
                if (child.children) {
                  addPaths(child, childPath);
                }
              });
            }
          };
          addPaths(data);
          setExpandedNodes(allPaths);
        }}>
          Expand All
        </button>
        <button style={styles.button} onClick={() => {
          const initialExpanded = new Set();
          if (data.children) {
            data.children.forEach((_, index) => {
              initialExpanded.add(`root-${index}`);
            });
          }
          setExpandedNodes(initialExpanded);
        }}>
          Collapse All
        </button>
      </div>

      {/* Tree Visualization */}
      <div style={styles.treeContainer}>
        {renderNode(data)}
      </div>

      {/* Stats */}
      <div style={styles.statsCard}>
        <p style={styles.statsText}>
          <span style={styles.statsHighlight}>Total Exams:</span> {totalExams} • 
          <span style={styles.statsHighlight}> Total Subjects:</span> {totalSubjects} • 
          <span style={styles.statsHighlight}> Total Topics:</span> {totalTopics}
        </p>
      </div>

      {/* Threshold Info */}
      <div style={styles.infoBox}>
        <h3 style={styles.infoTitle}>📊 Difficulty Thresholds</h3>
        <div style={styles.infoStats}>
          <div style={styles.infoItem}>
            <div style={{...styles.infoDot, background: '#EA4335'}} />
            <span>Hard: 2.91 - 5.0</span>
          </div>
          <div style={styles.infoItem}>
            <div style={{...styles.infoDot, background: '#FBBC05'}} />
            <span>Medium: 2.01 - 2.90</span>
          </div>
          <div style={styles.infoItem}>
            <div style={{...styles.infoDot, background: '#34A853'}} />
            <span>Low: 1.0 - 2.0</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DecisionTree;