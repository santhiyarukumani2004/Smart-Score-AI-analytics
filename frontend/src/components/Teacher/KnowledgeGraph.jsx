import React, { useState, useEffect, useRef, useCallback, useMemo } from "react";
import ReactECharts from "echarts-for-react";
import { Pie, Bar } from "react-chartjs-2";
import * as XLSX from "xlsx";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Filler
} from "chart.js";

// Register ChartJS components
ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Filler
);

const KnowledgeGraph = ({
  kgStats = {},
  edgeData = [],
  topicSummary = [],
  selectedExam = "all"
}) => {
  
  // ========== ADVANCED STATE MANAGEMENT ==========
  const [state, setState] = useState({
    graphData: { nodes: [], links: [], categories: [] },
    metrics: {
      totalNodes: 0,
      totalEdges: 0,
      avgOverallScore: 0,
      density: 0,
      avgDifficulty: 0,
      subjectCount: 0,
      topicCount: 0
    },
    topics: {
      hardest: [],
      easiest: [],
      distribution: [],
      bySubject: []
    },
    tableData: [],
    isLoading: true,
    error: null,
    lastUpdated: null
  });

  // ========== REFS FOR STABILITY ==========
  const chartRef = useRef(null);
  const neoChartRef = useRef(null);
  const isMounted = useRef(true);
  const animationFrameRef = useRef(null);

  // ========== CLEANUP ==========
  useEffect(() => {
    isMounted.current = true;
    
    return () => {
      isMounted.current = false;
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      if (chartRef.current) {
        try {
          chartRef.current.dispose();
        } catch (e) {}
      }
      if (neoChartRef.current) {
        try {
          neoChartRef.current.dispose();
        } catch (e) {}
      }
    };
  }, []);

  // ========== HELPER FUNCTION TO NORMALIZE SCORES TO 0-6 SCALE ==========
  const normalizeScore = (score, defaultValue = 3.0) => {
    if (score === null || score === undefined) return defaultValue;
    
    let numScore = parseFloat(score);
    if (isNaN(numScore)) return defaultValue;
    
    // If score is on 0-100 scale (typical for percentages)
    if (numScore > 6) {
      // Convert from 0-100 to 0-6 scale
      numScore = (numScore / 100) * 6;
    }
    
    // If score is on 0-10 scale
    if (numScore > 6 && numScore <= 10) {
      numScore = (numScore / 10) * 6;
    }
    
    // Ensure score is within 0-6 range
    return Math.min(6, Math.max(0, numScore));
  };

  // ========== UPDATED THRESHOLDS ==========
  // Hard: ≥ 3.00
  // Medium: 1.5 - 2.90
  // Easy: < 1.5
  
  const getDifficultyColor = (score) => {
    const numScore = normalizeScore(score);
    if (numScore >= 3.0) return '#EA4335'; // Google Red - Hard
    if (numScore >= 1.5) return '#FBBC05'; // Google Yellow - Medium
    return '#34A853'; // Google Green - Easy
  };

  const getDifficultyLabel = (score) => {
    const numScore = normalizeScore(score);
    if (numScore >= 3.0) return 'Hard';
    if (numScore >= 1.5) return 'Medium';
    return 'Easy';
  };

  // ========== NEO4J-INSPIRED GRAPH PROCESSING ==========
  const processGraphData = useCallback((edges) => {
    if (!edges || edges.length === 0) {
      return {
        nodes: [],
        relationships: [],
        metrics: {
          totalNodes: 0,
          totalEdges: 0,
          avgOverallScore: 0,
          density: 0,
          avgDifficulty: 0,
          subjectCount: 0,
          topicCount: 0
        },
        topics: {
          hardest: [],
          easiest: [],
          distribution: [],
          bySubject: []
        },
        tableData: []
      };
    }

    const startTime = performance.now();
    
    // Create Neo4j-like graph structure
    const graph = {
      nodes: new Map(),
      relationships: [],
      labels: new Set()
    };

    // First pass: Create nodes with properties
    edges.slice(0, 150).forEach((edge) => {
      if (!edge?.source || !edge?.target) return;

      // Add source node (Subject)
      if (!graph.nodes.has(edge.source)) {
        graph.nodes.set(edge.source, {
          id: edge.source,
          label: 'Subject',
          properties: {
            name: edge.source,
            type: 'subject',
            overallScore: 0,
            occurrences: 0,
            color: '#4285F4', // Google Blue
            symbolSize: 40
          }
        });
        graph.labels.add('Subject');
      }

      // Add target node (Topic) with normalized score
      if (!graph.nodes.has(edge.target)) {
        // Normalize the score to 0-6 scale
        const overallScore = normalizeScore(edge.weight, 3.0);
        
        graph.nodes.set(edge.target, {
          id: edge.target,
          label: 'Topic',
          properties: {
            name: edge.target,
            type: 'topic',
            overallScore: overallScore,
            occurrences: edge.occurrences || 1,
            color: getDifficultyColor(overallScore),
            symbolSize: 30
          }
        });
        graph.labels.add('Topic');
      }

      // Add relationship with normalized score
      const relationshipScore = normalizeScore(edge.weight, 3.0);
      
      const relationship = {
        source: edge.source,
        target: edge.target,
        type: 'HAS_TOPIC',
        properties: {
          overallScore: relationshipScore,
          occurrences: edge.occurrences || 1
        }
      };
      graph.relationships.push(relationship);

      // Update overallScore and occurrences for source
      if (graph.nodes.has(edge.source)) {
        const sourceNode = graph.nodes.get(edge.source);
        sourceNode.properties.overallScore += relationshipScore;
        sourceNode.properties.occurrences += 1;
      }

      // Update occurrences for target
      if (graph.nodes.has(edge.target)) {
        const targetNode = graph.nodes.get(edge.target);
        targetNode.properties.occurrences += edge.occurrences || 1;
      }
    });

    // Calculate averages and other metrics
    const nodeArray = Array.from(graph.nodes.values());
    const totalNodes = nodeArray.length;
    const totalEdges = graph.relationships.length;
    
    // Calculate average overallScore for subjects (normalized)
    nodeArray.forEach(node => {
      if (node.label === 'Subject' && node.properties.occurrences > 0) {
        node.properties.avgOverallScore = 
          node.properties.overallScore / node.properties.occurrences;
        // Ensure subject average is normalized
        node.properties.avgOverallScore = normalizeScore(node.properties.avgOverallScore);
      }
    });

    // Calculate graph density
    const density = totalNodes > 1 ? (2 * totalEdges) / (totalNodes * (totalNodes - 1)) : 0;

    // Process topics for analysis (all scores normalized)
    const topics = nodeArray
      .filter(n => n?.label === 'Topic')
      .map(n => ({
        name: n.id,
        overallScore: normalizeScore(n.properties?.overallScore, 3.0),
        occurrences: n.properties?.occurrences || 1,
        subject: graph.relationships.find(r => r.target === n.id)?.source || 'Unknown',
        difficultyLevel: getDifficultyLabel(n.properties?.overallScore)
      }));

    // Find hardest/easiest topics based on overallScore
    const sortedTopics = [...topics].sort((a, b) => b.overallScore - a.overallScore);
    const hardest = sortedTopics.slice(0, 5);
    const easiest = sortedTopics.slice(-5).reverse();

    // Process subjects (averages normalized)
    const subjects = nodeArray
      .filter(n => n?.label === 'Subject')
      .map(s => {
        const relatedTopics = topics.filter(t => 
          graph.relationships.some(r => r.source === s.id && r.target === t.name)
        );
        const avgOverallScore = relatedTopics.length > 0
          ? relatedTopics.reduce((sum, t) => sum + t.overallScore, 0) / relatedTopics.length
          : 0;
        
        return {
          name: s.id,
          topicCount: relatedTopics.length,
          avgOverallScore: normalizeScore(avgOverallScore),
          totalOccurrences: s.properties?.occurrences || 0
        };
      });

    console.log(`Graph processed in ${performance.now() - startTime}ms`);
    console.log('Sample normalized scores:', topics.slice(0, 3));

    return {
      nodes: nodeArray,
      relationships: graph.relationships,
      metrics: {
        totalNodes,
        totalEdges,
        avgOverallScore: topics.length > 0 
          ? normalizeScore(topics.reduce((sum, t) => sum + t.overallScore, 0) / topics.length)
          : 0,
        density,
        avgDifficulty: topics.length > 0 
          ? normalizeScore(topics.reduce((sum, t) => sum + t.overallScore, 0) / topics.length)
          : 0,
        subjectCount: subjects.length,
        topicCount: topics.length
      },
      topics: {
        hardest,
        easiest,
        distribution: [],
        bySubject: subjects
      },
      tableData: sortedTopics.slice(0, 20).map(t => ({
        subject: t.subject,
        topic: t.name,
        overallScore: t.overallScore.toFixed(2),
        occurrences: t.occurrences,
        connections: graph.relationships.filter(r => r.target === t.name).length,
        difficultyLevel: t.difficultyLevel
      }))
    };
  }, []);

  // ========== DATA PROCESSING EFFECT ==========
  useEffect(() => {
    if (!isMounted.current) return;

    const processor = setTimeout(() => {
      try {
        setState(prev => ({ ...prev, isLoading: true, error: null }));

        const processed = processGraphData(edgeData);
        
        if (processed && isMounted.current) {
          setState({
            graphData: {
              nodes: processed.nodes || [],
              links: processed.relationships || [],
              categories: [
                { name: 'Subject', itemStyle: { color: '#4285F4' } },
                { name: 'Topic', itemStyle: { color: '#34A853' } }
              ]
            },
            metrics: processed.metrics || {
              totalNodes: 0,
              totalEdges: 0,
              avgOverallScore: 0,
              density: 0,
              avgDifficulty: 0,
              subjectCount: 0,
              topicCount: 0
            },
            topics: processed.topics || {
              hardest: [],
              easiest: [],
              distribution: [],
              bySubject: []
            },
            tableData: processed.tableData || [],
            isLoading: false,
            error: null,
            lastUpdated: new Date().toISOString()
          });
        }
      } catch (error) {
        console.error("Processing error:", error);
        if (isMounted.current) {
          setState(prev => ({ 
            ...prev, 
            isLoading: false, 
            error: error.message 
          }));
        }
      }
    }, 100);

    return () => clearTimeout(processor);
  }, [edgeData, processGraphData]);

  // ========== ADVANCED ECHARTS CONFIG ==========
  const getNeo4jGraphOption = useMemo(() => {
    if (!state.graphData.nodes || state.graphData.nodes.length === 0) {
      return {
        title: {
          text: 'No Graph Data Available',
          left: 'center',
          top: 'center',
          textStyle: { color: '#9aa0a6', fontSize: 16 }
        },
        series: []
      };
    }

    return {
      title: {
        text: 'Knowledge Graph - Neo4j Style',
        left: 'center',
        top: 10,
        textStyle: { color: '#fff', fontSize: 16, fontWeight: 'normal' }
      },
      tooltip: {
        trigger: 'item',
        triggerOn: 'mousemove',
        formatter: (params) => {
          if (params.dataType === 'node') {
            const node = params.data;
            const score = normalizeScore(node.properties?.overallScore);
            const difficultyLevel = getDifficultyLabel(score);
            return `
              <div style="background: #202124; padding: 8px; border-radius: 4px;">
                <strong style="color: #fff;">${node.name || node.id}</strong><br/>
                <span style="color: #9aa0a6;">Type: ${node.label || 'Unknown'}</span><br/>
                <span style="color: #9aa0a6;">Overall Score: ${score.toFixed(2)}/6</span><br/>
                <span style="color: #9aa0a6;">Level: ${difficultyLevel}</span><br/>
                <span style="color: #9aa0a6;">Occurrences: ${node.properties?.occurrences || 0}</span>
              </div>
            `;
          } else {
            const score = normalizeScore(params.data.properties?.overallScore);
            return `
              <div style="background: #202124; padding: 8px; border-radius: 4px;">
                <strong style="color: #fff;">${params.data.source || ''} → ${params.data.target || ''}</strong><br/>
                <span style="color: #9aa0a6;">Overall Score: ${score.toFixed(2)}/6</span><br/>
                <span style="color: #9aa0a6;">Occurrences: ${params.data.properties?.occurrences || 0}</span>
              </div>
            `;
          }
        }
      },
      series: [{
        type: 'graph',
        layout: 'force',
        animation: false,
        roam: true,
        draggable: true,
        focusNodeAdjacency: true,
        edgeSymbol: ['none', 'arrow'],
        edgeLabel: {
          show: false
        },
        data: (state.graphData.nodes || []).map(n => ({
          name: n.id,
          id: n.id,
          value: normalizeScore(n.properties?.overallScore),
          category: n.label === 'Subject' ? 0 : 1,
          symbolSize: n.properties?.symbolSize || 30,
          itemStyle: { color: n.properties?.color || getDifficultyColor(n.properties?.overallScore) },
          properties: {
            ...n.properties,
            overallScore: normalizeScore(n.properties?.overallScore)
          },
          label: {
            show: true,
            position: 'right',
            fontSize: 11,
            color: '#e8eaed',
            formatter: '{b}'
          }
        })),
        links: (state.graphData.links || []).map(r => ({
          source: r.source,
          target: r.target,
          value: normalizeScore(r.properties?.overallScore),
          properties: {
            ...r.properties,
            overallScore: normalizeScore(r.properties?.overallScore)
          },
          lineStyle: {
            color: getDifficultyColor(r.properties?.overallScore),
            width: Math.max(1, (r.properties?.occurrences || 1) / 10),
            curveness: 0.2,
            opacity: 0.7
          }
        })),
        categories: [
          { name: 'Subject', itemStyle: { color: '#4285F4' } },
          { name: 'Topic', itemStyle: { color: '#34A853' } }
        ],
        force: {
          repulsion: 1000,
          edgeLength: 200,
          gravity: 0.3,
          friction: 0.5,
          layoutAnimation: false
        },
        lineStyle: {
          color: 'source',
          width: 2,
          opacity: 0.7
        },
        emphasis: {
          focus: 'adjacency',
          lineStyle: { width: 3 }
        }
      }]
    };
  }, [state.graphData]);

  // ========== CHART.JS CONFIGS ==========
  const chartConfigs = useMemo(() => {
    // Safely access data with defaults
    const hardest = state.topics?.hardest || [];
    const easiest = state.topics?.easiest || [];
    const bySubject = state.topics?.bySubject || [];
    
    // Hardest Topics Pie - Show top 5 hardest with their scores (normalized)
    const hardestPieData = {
      labels: hardest.map(t => t?.name || 'Unknown'),
      datasets: [{
        data: hardest.map(t => normalizeScore(t?.overallScore, 3.0)),
        backgroundColor: ['#EA4335', '#FBBC05', '#4285F4', '#34A853', '#9AA0A6'],
        borderWidth: 0
      }]
    };

    // Easiest Topics Pie - Show top 5 easiest with their scores (normalized)
    const easiestPieData = {
      labels: easiest.map(t => t?.name || 'Unknown'),
      datasets: [{
        data: easiest.map(t => normalizeScore(t?.overallScore, 3.0)),
        backgroundColor: ['#34A853', '#4285F4', '#FBBC05', '#9AA0A6', '#EA4335'].slice(0, easiest.length),
        borderWidth: 0
      }]
    };

    // Subject Performance Bar (averages normalized)
    const subjectData = {
      labels: (bySubject.slice(0, 8) || []).map(s => s?.name || 'Unknown'),
      datasets: [{
        label: 'Avg Overall Score',
        data: (bySubject.slice(0, 8) || []).map(s => normalizeScore(s?.avgOverallScore, 3.0)),
        backgroundColor: '#4285F4',
        borderRadius: 4
      }]
    };

    const chartOptions = {
      responsive: true,
      maintainAspectRatio: true,
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
          callbacks: {
            label: (context) => {
              const value = context.raw;
              const difficultyLevel = getDifficultyLabel(value);
              return `Overall Score: ${value.toFixed(2)}/6 (${difficultyLevel})`;
            }
          }
        }
      },
      layout: {
        padding: {
          top: 20,
          bottom: 20,
          left: 20,
          right: 20
        }
      }
    };

    return {
      hardestPie: { data: hardestPieData, options: chartOptions },
      easiestPie: { data: easiestPieData, options: chartOptions },
      subjectPerf: { 
        data: subjectData, 
        options: {
          ...chartOptions,
          scales: {
            y: { 
              beginAtZero: true, 
              max: 6,
              grid: { color: '#3c4043' },
              ticks: { 
                color: '#9aa0a6', 
                stepSize: 1,
                callback: (value) => value.toFixed(1)
              },
              title: {
                display: true,
                text: 'Score (0-6 scale)',
                color: '#9aa0a6'
              }
            },
            x: { 
              ticks: { color: '#9aa0a6', maxRotation: 45 },
              grid: { display: false }
            }
          }
        }
      }
    };
  }, [state.topics]);

  // ========== CHART READY HANDLER ==========
  const onChartReady = useCallback((chart) => {
    if (!isMounted.current) return;
    
    chartRef.current = chart;
    
    animationFrameRef.current = requestAnimationFrame(() => {
      if (chartRef.current && isMounted.current) {
        try {
          chartRef.current.dispatchAction({ type: 'forceLayoutStop' });
        } catch (e) {}
      }
    });
  }, []);

  // ========== EXPORT FUNCTION ==========
  const exportData = useCallback(() => {
    const wb = XLSX.utils.book_new();
    
    // Metrics sheet with normalized values
    const exportMetrics = {
      ...state.metrics,
      avgOverallScore: normalizeScore(state.metrics?.avgOverallScore).toFixed(2),
      avgDifficulty: normalizeScore(state.metrics?.avgDifficulty).toFixed(2)
    };
    
    XLSX.utils.book_append_sheet(wb, 
      XLSX.utils.json_to_sheet([exportMetrics]), 
      "Metrics"
    );
    
    // Topics sheet with normalized scores
    if (state.tableData && state.tableData.length > 0) {
      const exportTableData = state.tableData.map(row => ({
        ...row,
        overallScore: normalizeScore(parseFloat(row.overallScore)).toFixed(2),
        difficultyLevel: getDifficultyLabel(row.overallScore)
      }));
      XLSX.utils.book_append_sheet(wb, 
        XLSX.utils.json_to_sheet(exportTableData), 
        "Topics"
      );
    }
    
    // Graph sheet with normalized scores
    if (state.graphData?.links && state.graphData.links.length > 0) {
      const exportLinks = state.graphData.links.map(link => ({
        source: link.source,
        target: link.target,
        overallScore: normalizeScore(link.properties?.overallScore).toFixed(2),
        occurrences: link.properties?.occurrences || 0
      }));
      XLSX.utils.book_append_sheet(wb, 
        XLSX.utils.json_to_sheet(exportLinks), 
        "Relationships"
      );
    }
    
    XLSX.writeFile(wb, `knowledge_graph_${selectedExam}_${Date.now()}.xlsx`);
  }, [state, selectedExam]);

  // ========== RENDER ==========
  return (
    <div style={styles.container}>
      {/* Google AI Dashboard Header */}
      <div style={styles.header}>
        <div>
          <h1 style={styles.title}>Knowledge Graph Analytics</h1>
          <p style={styles.subtitle}>
            {selectedExam !== 'all' ? selectedExam : 'All Exams'} • 
            Last updated: {state.lastUpdated ? new Date(state.lastUpdated).toLocaleString() : 'Loading...'}
          </p>
        </div>
        <button 
          onClick={exportData}
          style={styles.exportButton}
          disabled={state.isLoading}
        >
          <span style={styles.buttonIcon}>📊</span>
          Export Analysis
        </button>
      </div>

      {/* Metrics Cards - Google AI Style */}
      <div style={styles.metricsGrid}>
        {[
          { label: 'Total Nodes', value: state.metrics?.totalNodes || 0, icon: '🔷' },
          { label: 'Relationships', value: state.metrics?.totalEdges || 0, icon: '🔗' },
          { label: 'Avg Score', value: normalizeScore(state.metrics?.avgOverallScore || 0).toFixed(2), icon: '📊' },
          { label: 'Density', value: (state.metrics?.density || 0).toFixed(3), icon: '🌐' },
          { label: 'Avg Difficulty', value: normalizeScore(state.metrics?.avgDifficulty || 0).toFixed(2), icon: '📈' },
          { label: 'Subjects', value: state.metrics?.subjectCount || 0, icon: '📚' },
          { label: 'Topics', value: state.metrics?.topicCount || 0, icon: '🎯' },
          { label: 'Connections', value: state.metrics?.totalEdges || 0, icon: '🔄' }
        ].map((metric, i) => (
          <div key={i} style={styles.metricCard}>
            <span style={styles.metricIcon}>{metric.icon}</span>
            <div>
              <h3 style={styles.metricValue}>{metric.value}</h3>
              <p style={styles.metricLabel}>{metric.label}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Neo4j-Style Graph */}
      {!state.isLoading && state.graphData?.nodes && state.graphData.nodes.length > 0 && (
        <div style={styles.graphCard}>
          <div style={styles.cardHeader}>
            <h2 style={styles.cardTitle}>Graph Visualization</h2>
            <div style={styles.legend}>
              <span style={styles.legendItem}><span style={{...styles.legendDot, background: '#4285F4'}} /> Subjects</span>
              <span style={styles.legendItem}><span style={{...styles.legendDot, background: '#34A853'}} /> Easy (&lt;1.5)</span>
              <span style={styles.legendItem}><span style={{...styles.legendDot, background: '#FBBC05'}} /> Medium (1.5-2.90)</span>
              <span style={styles.legendItem}><span style={{...styles.legendDot, background: '#EA4335'}} /> Hard (≥3.0)</span>
            </div>
          </div>
          <div style={styles.graphContainer}>
            <ReactECharts
              option={getNeo4jGraphOption}
              style={{ height: '100%', width: '100%' }}
              theme="dark"
              onChartReady={onChartReady}
            />
          </div>
        </div>
      )}

      {/* Analytics Dashboard - Google AI Style */}
      <div style={styles.analyticsGrid}>
        {/* Hardest Topics */}
        <div style={styles.analyticsCard}>
          <h3 style={styles.cardTitle}>🔥 Hardest Topics (≥3.0)</h3>
          <div style={styles.pieChartContainer}>
            {state.topics?.hardest && state.topics.hardest.length > 0 ? (
              <>
                <div style={styles.pieWrapper}>
                  <Pie data={chartConfigs.hardestPie.data} options={chartConfigs.hardestPie.options} />
                </div>
                <div style={styles.topicList}>
                  {state.topics.hardest.map((t, i) => {
                    const score = normalizeScore(t?.overallScore);
                    return (
                      <div key={i} style={styles.topicItem}>
                        <span style={styles.topicRank}>#{i + 1}</span>
                        <span style={styles.topicName}>{t?.name || 'Unknown'}</span>
                        <span style={{...styles.topicScore, color: getDifficultyColor(score)}}>
                          {score.toFixed(2)}
                        </span>
                        <span style={styles.topicOccurrences}>occ: {t?.occurrences || 0}</span>
                        <span style={{
                          ...styles.difficultyBadge,
                          backgroundColor: getDifficultyColor(score) + '20',
                          color: getDifficultyColor(score),
                          border: `1px solid ${getDifficultyColor(score)}`
                        }}>
                          {getDifficultyLabel(score)}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </>
            ) : (
              <p style={styles.noData}>No data available</p>
            )}
          </div>
        </div>

        {/* Easiest Topics */}
        <div style={styles.analyticsCard}>
          <h3 style={styles.cardTitle}>✅ Easiest Topics (&lt;1.5)</h3>
          <div style={styles.pieChartContainer}>
            {state.topics?.easiest && state.topics.easiest.length > 0 ? (
              <>
                <div style={styles.pieWrapper}>
                  <Pie data={chartConfigs.easiestPie.data} options={chartConfigs.easiestPie.options} />
                </div>
                <div style={styles.topicList}>
                  {state.topics.easiest.map((t, i) => {
                    const score = normalizeScore(t?.overallScore);
                    return (
                      <div key={i} style={styles.topicItem}>
                        <span style={styles.topicRank}>#{i + 1}</span>
                        <span style={styles.topicName}>{t?.name || 'Unknown'}</span>
                        <span style={{...styles.topicScore, color: getDifficultyColor(score)}}>
                          {score.toFixed(2)}
                        </span>
                        <span style={styles.topicOccurrences}>occ: {t?.occurrences || 0}</span>
                        <span style={{
                          ...styles.difficultyBadge,
                          backgroundColor: getDifficultyColor(score) + '20',
                          color: getDifficultyColor(score),
                          border: `1px solid ${getDifficultyColor(score)}`
                        }}>
                          {getDifficultyLabel(score)}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </>
            ) : (
              <p style={styles.noData}>No data available</p>
            )}
          </div>
        </div>

        {/* Subject Performance */}
        <div style={styles.analyticsCard}>
          <h3 style={styles.cardTitle}>📊 Subject Performance (Avg Score)</h3>
          <div style={{ height: 300 }}>
            {state.topics?.bySubject && state.topics.bySubject.length > 0 ? (
              <Bar data={chartConfigs.subjectPerf.data} options={chartConfigs.subjectPerf.options} />
            ) : (
              <p style={styles.noData}>No subject data</p>
            )}
          </div>
        </div>

        {/* Score Distribution Guide */}
        <div style={styles.analyticsCard}>
          <h3 style={styles.cardTitle}>📈 Score Interpretation Guide</h3>
          <div style={{ height: 300, padding: 20 }}>
            <div style={styles.guideItem}>
              <div style={{...styles.guideDot, background: '#EA4335'}} />
              <div>
                <strong style={{ color: '#EA4335' }}>Hard (≥ 3.0)</strong>
                <p style={styles.guideText}>High difficulty topics requiring more focus</p>
              </div>
            </div>
            <div style={styles.guideItem}>
              <div style={{...styles.guideDot, background: '#FBBC05'}} />
              <div>
                <strong style={{ color: '#FBBC05' }}>Medium (1.5 - 2.90)</strong>
                <p style={styles.guideText}>Moderate difficulty topics</p>
              </div>
            </div>
            <div style={styles.guideItem}>
              <div style={{...styles.guideDot, background: '#34A853'}} />
              <div>
                <strong style={{ color: '#34A853' }}>Easy (&lt; 1.5)</strong>
                <p style={styles.guideText}>Lower difficulty topics</p>
              </div>
            </div>
            <div style={styles.guideNote}>
              <p>All scores normalized to 0-6 scale for consistency across all analysis pages</p>
            </div>
          </div>
        </div>
      </div>

      {/* Topics Table */}
      {state.tableData && state.tableData.length > 0 && (
        <div style={styles.tableCard}>
          <h3 style={styles.cardTitle}>📋 Topic Analysis (Normalized to 0-6 scale)</h3>
          <div style={styles.tableWrapper}>
            <table style={styles.table}>
              <thead>
                <tr>
                  <th style={styles.th}>Subject</th>
                  <th style={styles.th}>Topic</th>
                  <th style={styles.th}>Overall Score</th>
                  <th style={styles.th}>Level</th>
                  <th style={styles.th}>Occurrences</th>
                  <th style={styles.th}>Connections</th>
                </tr>
              </thead>
              <tbody>
                {state.tableData.map((row, i) => {
                  const score = parseFloat(row.overallScore) || 0;
                  const normalizedScore = normalizeScore(score);
                  const color = getDifficultyColor(normalizedScore);
                  const level = getDifficultyLabel(normalizedScore);
                  
                  return (
                    <tr key={i} style={i % 2 === 0 ? styles.rowEven : styles.rowOdd}>
                      <td style={styles.td}>{row.subject || 'N/A'}</td>
                      <td style={styles.td}>{row.topic || 'N/A'}</td>
                      <td style={styles.td}>
                        <div style={styles.scoreCell}>
                          <span style={{ color, fontWeight: 600 }}>
                            {normalizedScore.toFixed(2)}
                          </span>
                          <div style={styles.progressBar}>
                            <div style={{
                              width: `${(normalizedScore / 6) * 100}%`,
                              height: '100%',
                              backgroundColor: color,
                              borderRadius: 2
                            }} />
                          </div>
                        </div>
                      </td>
                      <td style={styles.td}>
                        <span style={{
                          ...styles.levelBadge,
                          backgroundColor: color + '20',
                          color: color,
                          border: `1px solid ${color}`
                        }}>
                          {level}
                        </span>
                      </td>
                      <td style={styles.td}>{row.occurrences || 0}</td>
                      <td style={styles.td}>{row.connections || 0}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

// ========== GOOGLE AI DASHBOARD STYLES ==========
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
  exportButton: {
    padding: '10px 24px',
    background: '#4285F4',
    color: 'white',
    border: 'none',
    borderRadius: 100,
    cursor: 'pointer',
    fontWeight: 500,
    fontSize: 14,
    display: 'flex',
    alignItems: 'center',
    gap: 8,
    transition: 'all 0.2s',
    ':hover': {
      background: '#5a95f5',
      transform: 'translateY(-1px)',
      boxShadow: '0 4px 8px rgba(66,133,244,0.3)'
    },
    ':disabled': {
      opacity: 0.5,
      cursor: 'not-allowed'
    }
  },
  buttonIcon: {
    fontSize: 18
  },
  metricsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(8, 1fr)',
    gap: 16,
    marginBottom: 32
  },
  metricCard: {
    background: '#2d2e30',
    padding: 16,
    borderRadius: 12,
    display: 'flex',
    alignItems: 'center',
    gap: 12,
    border: '1px solid #3c4043',
    transition: 'all 0.2s',
    ':hover': {
      background: '#35363a',
      transform: 'translateY(-2px)',
      boxShadow: '0 4px 12px rgba(0,0,0,0.3)'
    }
  },
  metricIcon: {
    fontSize: 24,
    opacity: 0.8
  },
  metricValue: {
    margin: 0,
    fontSize: 20,
    fontWeight: 500,
    color: '#e8eaed'
  },
  metricLabel: {
    margin: '4px 0 0',
    fontSize: 12,
    color: '#9aa0a6'
  },
  graphCard: {
    background: '#2d2e30',
    borderRadius: 16,
    padding: 24,
    marginBottom: 32,
    border: '1px solid #3c4043'
  },
  cardHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20
  },
  cardTitle: {
    margin: 0,
    fontSize: 18,
    fontWeight: 500,
    color: '#e8eaed'
  },
  legend: {
    display: 'flex',
    gap: 16,
    flexWrap: 'wrap'
  },
  legendItem: {
    display: 'flex',
    alignItems: 'center',
    gap: 6,
    fontSize: 13,
    color: '#9aa0a6'
  },
  legendDot: {
    width: 10,
    height: 10,
    borderRadius: '50%'
  },
  graphContainer: {
    height: 500,
    width: '100%',
    background: '#1e1f21',
    borderRadius: 12,
    overflow: 'hidden'
  },
  analyticsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(2, 1fr)',
    gap: 20,
    marginBottom: 32
  },
  analyticsCard: {
    background: '#2d2e30',
    borderRadius: 16,
    padding: 20,
    border: '1px solid #3c4043'
  },
  pieChartContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    width: '100%'
  },
  pieWrapper: {
    width: '100%',
    height: 250,
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16
  },
  topicList: {
    width: '100%',
    display: 'flex',
    flexDirection: 'column',
    gap: 8,
    marginTop: 8
  },
  topicItem: {
    display: 'flex',
    alignItems: 'center',
    gap: 12,
    padding: '8px 12px',
    background: '#35363a',
    borderRadius: 8,
    fontSize: 13
  },
  topicRank: {
    color: '#9aa0a6',
    fontWeight: 500,
    minWidth: 30
  },
  topicName: {
    flex: 1,
    color: '#e8eaed'
  },
  topicScore: {
    fontWeight: 600,
    minWidth: 45
  },
  topicOccurrences: {
    color: '#9aa0a6',
    fontSize: 11,
    minWidth: 50
  },
  difficultyBadge: {
    padding: '2px 8px',
    borderRadius: 100,
    fontSize: 10,
    fontWeight: 500
  },
  tableCard: {
    background: '#2d2e30',
    borderRadius: 16,
    padding: 24,
    border: '1px solid #3c4043'
  },
  tableWrapper: {
    overflowX: 'auto',
    marginTop: 16
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
    minWidth: 900,
    fontSize: 14
  },
  th: {
    background: '#35363a',
    color: '#9aa0a6',
    padding: '12px 16px',
    textAlign: 'left',
    fontWeight: 500,
    fontSize: 13
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
  scoreCell: {
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
  levelBadge: {
    padding: '4px 12px',
    borderRadius: 100,
    fontSize: 11,
    fontWeight: 500,
    display: 'inline-block'
  },
  guideItem: {
    display: 'flex',
    gap: 16,
    marginBottom: 20,
    alignItems: 'flex-start'
  },
  guideDot: {
    width: 16,
    height: 16,
    borderRadius: '50%',
    marginTop: 2
  },
  guideText: {
    margin: '4px 0 0',
    fontSize: 12,
    color: '#9aa0a6'
  },
  guideNote: {
    marginTop: 20,
    padding: 12,
    background: '#35363a',
    borderRadius: 8,
    fontSize: 12,
    color: '#9aa0a6',
    textAlign: 'center'
  },
  noData: {
    textAlign: 'center',
    color: '#9aa0a6',
    padding: 40
  }
};

export default KnowledgeGraph;