import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';

// Context
import { AuthProvider } from './contexts/AuthContext';

// Pages
import Login from './pages/Login';
import Register from './pages/Register';
import HRDashboard from './pages/HRDashboard';
import CandidateDashboard from './pages/CandidateDashboard';
import JobPosting from './pages/JobPosting';
import JobDetails from './pages/JobDetails';
import JobAnalytics from './pages/JobAnalytics';
import JobCandidates from './pages/JobCandidates';
import CandidateRanking from './pages/CandidateRanking';
import ResumeUpload from './pages/ResumeUpload';
import SkillSuggestions from './pages/SkillSuggestions';
import SkillsAnalysis from './pages/SkillsAnalysis';
import Profile from './pages/Profile';

// Components
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/Layout';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      refetchOnWindowFocus: false,
      staleTime: 0,
      cacheTime: 0,
      refetchOnMount: true,
      refetchOnReconnect: true,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Router>
          <div className="min-h-screen bg-gray-50">
            <Routes>
              {/* Public routes */}
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              
              {/* Protected routes */}
              <Route path="/" element={
                <ProtectedRoute>
                  <Layout />
                </ProtectedRoute>
              }>
                {/* HR Routes */}
                <Route path="/hr" element={<HRDashboard />} />
                <Route path="/hr/jobs" element={<JobPosting />} />
                <Route path="/hr/jobs/:jobId" element={<JobDetails />} />
                <Route path="/hr/jobs/:jobId/analytics" element={<JobAnalytics />} />
                <Route path="/hr/jobs/:jobId/candidates" element={<JobCandidates />} />
                <Route path="/hr/candidates/:jobId" element={<CandidateRanking />} />
                
                {/* Candidate Routes */}
                <Route path="/candidate" element={<CandidateDashboard />} />
                <Route path="/candidate/resume" element={<ResumeUpload />} />
                <Route path="/candidate/resume/:resumeId/skills" element={<SkillsAnalysis />} />
                <Route path="/candidate/skills" element={<SkillSuggestions />} />
                
                {/* Common Routes */}
                <Route path="/profile" element={<Profile />} />
                
                {/* Default redirect */}
                <Route path="/" element={<Navigate to="/login" replace />} />
              </Route>
            </Routes>
            
            {/* Toast notifications */}
            <Toaster
              position="top-right"
              toastOptions={{
                duration: 4000,
                style: {
                  background: '#363636',
                  color: '#fff',
                },
                success: {
                  duration: 3000,
                  iconTheme: {
                    primary: '#4ade80',
                    secondary: '#fff',
                  },
                },
                error: {
                  duration: 5000,
                  iconTheme: {
                    primary: '#ef4444',
                    secondary: '#fff',
                  },
                },
              }}
            />
          </div>
        </Router>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
