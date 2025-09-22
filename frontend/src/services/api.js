import axios from 'axios';

// Create axios instance
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (email, password) => api.post('/api/auth/login', { email, password }),
  register: (userData) => api.post('/api/auth/register', userData),
  getProfile: () => api.get('/api/auth/me'),
  updateProfile: (profileData) => api.put('/api/auth/profile', profileData),
  verifyToken: () => api.get('/api/auth/verify-token'),
  logout: () => api.post('/api/auth/logout'),
};

// Jobs API
export const jobsAPI = {
  getJobs: (params = {}) => api.get('/api/jobs', { params }),
  searchJobs: (params = {}) => api.get('/api/jobs/search', { params }),
  getJob: (jobId) => api.get(`/api/jobs/${jobId}`),
  createJob: (jobData) => api.post('/api/jobs', jobData),
  updateJob: (jobId, jobData) => api.put(`/api/jobs/${jobId}`, jobData),
  deleteJob: (jobId) => api.delete(`/api/jobs/${jobId}`),
  getHRJobs: () => api.get('/api/jobs/hr/my-jobs'),
  getJobApplications: (jobId) => api.get(`/api/jobs/${jobId}/applications`),
  applyToJob: (jobId, applicationData) => api.post(`/api/jobs/${jobId}/apply`, applicationData),
  
  // New job management endpoints
  updateJobStatus: (jobId, statusData) => api.patch(`/api/jobs/${jobId}/status`, statusData),
  getJobAnalytics: (jobId) => api.get(`/api/jobs/${jobId}/analytics`),
  getJobCandidates: (jobId) => api.get(`/api/jobs/${jobId}/candidates`),
  updateCandidateStatus: (jobId, candidateId, status) => 
    api.patch(`/api/jobs/${jobId}/candidates/${candidateId}/status`, { status }),
  checkAutoCompleteJobs: () => api.get('/api/jobs/hr/auto-complete-check'),
};

// Resumes API
export const resumesAPI = {
  uploadResume: (formData) => api.post('/api/resumes/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  getResumes: () => api.get('/api/resumes'),
  getResume: (resumeId) => api.get(`/api/resumes/${resumeId}`),
  deleteResume: (resumeId) => api.delete(`/api/resumes/${resumeId}`),
  getResumeAnalysis: (resumeId) => api.get(`/api/resumes/${resumeId}/analysis`),
};

// Candidates API
export const candidatesAPI = {
  getCandidateRankings: (jobId) => api.get(`/api/candidates/job/${jobId}/rankings`),
  getJobApplications: (jobId) => api.get(`/api/candidates/job/${jobId}/applications`),
  updateApplicationStatus: (applicationId, statusData) => 
    api.put(`/api/candidates/applications/${applicationId}/status`, statusData),
  getCandidateProfile: (candidateId) => api.get(`/api/candidates/candidate/${candidateId}/profile`),
  searchCandidates: (params = {}) => api.get('/api/candidates/search', { params }),
};

// Skills API
export const skillsAPI = {
  getSkillRecommendations: () => api.get('/api/skills/recommendations'),
  getMarketTrends: () => api.get('/api/skills/market-trends'),
  getSkillGapAnalysis: (jobId = null) => 
    api.get('/api/skills/skill-gap-analysis', { params: jobId ? { job_id: jobId } : {} }),
  getLearningPaths: (skill) => api.get('/api/skills/learning-paths', { params: { skill } }),
};

// Advanced Features API
export const advancedFeaturesAPI = {
  parseResumeEnhanced: (formData) => api.post('/api/advanced/resumes/parse-enhanced', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  calculateEnhancedScore: (candidateData, jobRequirements) => 
    api.post('/api/advanced/candidates/score-enhanced', { candidate_data: candidateData, job_requirements: jobRequirements }),
  getEnhancedRecommendations: () => api.get('/api/advanced/skills/recommendations-enhanced'),
  getServiceCapabilities: () => api.get('/api/advanced/capabilities'),
  trainMLModels: (trainingData) => api.post('/api/advanced/ml-models/train', trainingData),
  getBiasReport: (timePeriodDays = 30) => api.get('/api/advanced/bias/report', { params: { time_period_days: timePeriodDays } }),
  getBiasDashboard: () => api.get('/api/advanced/bias/dashboard'),
  analyzeCandidateBias: (candidateData, rankingScore, jobRequirements) => 
    api.post('/api/advanced/candidates/bias-analysis', { candidate_data: candidateData, ranking_score: rankingScore, job_requirements: jobRequirements }),
  getOntologyStats: () => api.get('/api/advanced/ontology/stats'),
  getSupportedLanguages: () => api.get('/api/advanced/multilingual/supported-languages'),
  processImageResume: (formData) => api.post('/api/advanced/ocr/process-image', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  getLLMAnalysis: (resumeData, jobRequirements) => 
    api.get('/api/advanced/llm/analysis', { params: { resume_data: resumeData, job_requirements: jobRequirements } })
};

export default api;
