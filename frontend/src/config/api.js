// src/config/api.js
const API_BASE_URL = 'http://localhost:5000';

export const API_ENDPOINTS = {
  // Courses and dropdowns
  courses: `${API_BASE_URL}/api/courses`,
  majors: `${API_BASE_URL}/api/majors`,
  tnpscGroups: `${API_BASE_URL}/api/tnpsc-groups`,
  
  // Student endpoints
  studentRegister: `${API_BASE_URL}/api/student/register`,
  studentDashboard: (exam) => `${API_BASE_URL}/api/student/dashboard/${exam}`,
  
  // Teacher endpoints
  teacherRegister: `${API_BASE_URL}/api/teacher/register`,
  teacherDashboard: `${API_BASE_URL}/api/teacher/dashboard`,
  
  // Knowledge Graph
  knowledgeGraphNodes: `${API_BASE_URL}/api/knowledge-graph/nodes`,
  knowledgeGraphEdges: `${API_BASE_URL}/api/knowledge-graph/edges`,
  knowledgeGraphStats: `${API_BASE_URL}/api/knowledge-graph/stats`,
  
  // Debug
  debugExams: `${API_BASE_URL}/api/debug/exams`,
  health: `${API_BASE_URL}/api/health`
};

export default API_BASE_URL;