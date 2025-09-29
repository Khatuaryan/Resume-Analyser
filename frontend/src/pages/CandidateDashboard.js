import React, { useEffect, useState } from 'react';
import { useQuery } from 'react-query';
import { Link } from 'react-router-dom';
import { 
  FileText, 
  TrendingUp, 
  Briefcase, 
  Upload,
  CheckCircle,
  AlertCircle,
  Target,
  RefreshCw,
  X
} from 'lucide-react';
import { resumesAPI, jobsAPI } from '../services/api';

const CandidateDashboard = () => {
  // Fallback state for direct API calls
  const [fallbackResumes, setFallbackResumes] = useState([]);
  const [fallbackJobs, setFallbackJobs] = useState([]);
  const [fallbackLoading, setFallbackLoading] = useState(false);
  const [useFallback, setUseFallback] = useState(false);
  
  // Notification state
  const [showNotification, setShowNotification] = useState(false);

  const { data: resumes, isLoading: resumesLoading, error: resumesError, refetch: refetchResumes } = useQuery({
    queryKey: ['resumes'],
    queryFn: async () => {
      console.log('🔍 Executing resumes query...');
      try {
        const result = await resumesAPI.getResumes();
        console.log('📄 Resumes query result:', result);
        return result;
      } catch (error) {
        console.error('❌ Resumes query failed:', error);
        throw error;
      }
    },
    retry: 2,
    refetchOnWindowFocus: false,
    staleTime: 0,
    cacheTime: 0,
    enabled: true,
    refetchOnMount: true,
    refetchOnReconnect: true
  });
  
  const { data: jobs, isLoading: jobsLoading, error: jobsError, refetch: refetchJobs } = useQuery({
    queryKey: ['jobs'],
    queryFn: async () => {
      console.log('🔍 Executing jobs query...');
      try {
        const result = await jobsAPI.getJobs({ limit: 5 });
        console.log('💼 Jobs query result:', result);
        return result;
      } catch (error) {
        console.error('❌ Jobs query failed:', error);
        throw error;
      }
    },
    retry: 2,
    refetchOnWindowFocus: false,
    staleTime: 0,
    cacheTime: 0,
    enabled: true,
    refetchOnMount: true,
    refetchOnReconnect: true
  });

  // Use fallback data if React Query fails
  const finalResumes = useFallback ? fallbackResumes : resumes;
  const finalJobs = useFallback ? fallbackJobs : jobs;
  const finalLoading = useFallback ? fallbackLoading : (resumesLoading || jobsLoading);
  
  // Ensure resumes is always an array
  const resumesArray = Array.isArray(finalResumes) ? finalResumes : [];
  
  // Calculate derived values
  const latestResume = resumesArray[0];
  const hasResume = resumesArray.length > 0;
  const processedResume = resumesArray.find(r => r.status === 'processed');
  
  // Use fallback by default since React Query is not working reliably
  useEffect(() => {
    console.log('🚀 Component mounted, using fallback by default...');
    
    // Check authentication first
    const token = localStorage.getItem('token');
    console.log('🔑 Auth token:', token ? 'Present' : 'Missing');
    
    if (!token) {
      console.log('❌ No auth token, redirecting to login...');
      // You might want to redirect to login here
      return;
    }
    
    // Use fallback immediately since React Query is not working
    console.log('🔄 Using fallback mechanism for reliable data fetching...');
    setUseFallback(true);
    fetchDataDirectly();
  }, []);

  // Show notification temporarily when resume is processed
  useEffect(() => {
    if (hasResume && processedResume) {
      setShowNotification(true);
      const timer = setTimeout(() => {
        setShowNotification(false);
      }, 5000); // Hide after 5 seconds
      return () => clearTimeout(timer);
    }
  }, [hasResume, processedResume]);

  // Direct API calls as fallback
  const fetchDataDirectly = async () => {
    try {
      setFallbackLoading(true);
      console.log('🔄 Fetching data directly...');
      
      const token = localStorage.getItem('token');
      if (!token) {
        console.error('❌ No auth token found');
        return;
      }

      // Fetch resumes directly
      const resumesResponse = await fetch('http://localhost:8000/api/resumes/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (resumesResponse.ok) {
        const resumesData = await resumesResponse.json();
        console.log('📄 Direct resumes result:', resumesData);
        setFallbackResumes(resumesData);
      }

      // Fetch jobs directly
      const jobsResponse = await fetch('http://localhost:8000/api/jobs/?limit=5', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (jobsResponse.ok) {
        const jobsData = await jobsResponse.json();
        console.log('💼 Direct jobs result:', jobsData);
        setFallbackJobs(jobsData);
      }
      
    } catch (error) {
      console.error('❌ Direct API call failed:', error);
    } finally {
      setFallbackLoading(false);
    }
  };

  // Debug logging
  console.log('=== CANDIDATE DASHBOARD DEBUG ===');
  console.log('Using fallback:', useFallback);
  console.log('Resumes loading:', resumesLoading);
  console.log('Resumes error:', resumesError);
  console.log('Resumes data:', resumes);
  console.log('Jobs loading:', jobsLoading);
  console.log('Jobs error:', jobsError);
  console.log('Jobs data:', jobs);
  console.log('Final resumes:', finalResumes);
  console.log('Final jobs:', finalJobs);
  console.log('Resumes array length:', resumesArray.length);
  console.log('Has resume:', hasResume);
  console.log('Processed resume:', processedResume);
  console.log('================================');

  // Test function to manually test API calls
  const testAPICalls = async () => {
    console.log('=== TESTING API CALLS ===');
    try {
      const resumesResponse = await resumesAPI.getResumes();
      console.log('Resumes API Response:', resumesResponse.data);
      
      const jobsResponse = await jobsAPI.getJobs({ limit: 5 });
      console.log('Jobs API Response:', jobsResponse.data);
    } catch (error) {
      console.error('API Test Error:', error);
    }
    console.log('========================');
  };

  const stats = [
    {
      name: 'Resumes Uploaded',
      value: resumesArray.length,
      icon: FileText,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100'
    },
    {
      name: 'Jobs Applied',
      value: 0, // This would come from applications API
      icon: Briefcase,
      color: 'text-green-600',
      bgColor: 'bg-green-100'
    },
    {
      name: 'Profile Score',
      value: processedResume?.analysis_score || 0,
      icon: Target,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100'
    },
    {
      name: 'Job Matches',
      value: finalJobs ? finalJobs.length : 0,
      icon: TrendingUp,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100'
    }
  ];

  if (resumesLoading || jobsLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (resumesError || jobsError) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Error Loading Data</h3>
          <p className="text-gray-500">There was an error loading your dashboard data. Please try refreshing the page.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Candidate Dashboard</h1>
          <p className="text-gray-600">Manage your profile and job applications</p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => {
              console.log('🔄 Refreshing data...');
              fetchDataDirectly();
            }}
            className="text-gray-400 hover:text-gray-600 transition-colors"
            disabled={finalLoading}
            title="Refresh Data"
          >
            <RefreshCw className={`h-4 w-4 ${finalLoading ? 'animate-spin' : ''}`} />
          </button>
        <Link
          to="/candidate/resume"
            className="btn btn-primary px-6 py-3"
        >
          <Upload className="h-4 w-4 mr-2" />
          Upload Resume
        </Link>
        </div>
      </div>

          {/* Temporary Notification */}
          {showNotification && (
            <div className="fixed top-4 right-4 bg-green-50 border border-green-200 rounded-lg p-4 shadow-lg z-50 max-w-sm">
          <div className="flex items-center">
              <CheckCircle className="h-5 w-5 text-green-600" />
            <div className="ml-3">
                  <h3 className="text-sm font-medium text-green-800">Resume processed successfully!</h3>
                  <p className="text-sm text-green-700">Your resume has been analyzed and is ready for job matching.</p>
            </div>
                <button
                  onClick={() => setShowNotification(false)}
                  className="ml-4 text-green-400 hover:text-green-600"
                >
                  <X className="h-4 w-4" />
                </button>
          </div>
        </div>
      )}


      {/* Stats */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 p-6">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.name} className="card">
              <div className="card-content p-6">
                <div className="flex items-center">
                  <div className={`p-2 rounded-lg ${stat.bgColor}`}>
                    <Icon className={`h-6 w-6 ${stat.color}`} />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                    <p className="text-2xl font-semibold text-gray-900">{stat.value}</p>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Resume Status */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-gray-900">Resume Status</h3>
        </div>
        <div className="card-content">
          {hasResume ? (
            <div className="space-y-4">
              {resumesArray.map((resume) => (
                <div key={resume.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <FileText className="h-5 w-5 text-gray-400" />
                    <div>
                      <h4 className="text-sm font-medium text-gray-900">{resume.filename}</h4>
                      <p className="text-sm text-gray-500">
                        Uploaded {new Date(resume.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      resume.status === 'processed' 
                        ? 'bg-green-100 text-green-800' 
                        : resume.status === 'processing'
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {resume.status}
                    </span>
                    {resume.status === 'processed' && (
                          <div className="flex items-center space-x-2">
                            <Link
                              to={`/candidate/resume/${resume.id}/skills`}
                              className="inline-flex items-center px-3 py-1.5 bg-purple-100 text-purple-700 text-xs font-medium rounded-md hover:bg-purple-200 transition-colors"
                            >
                              <TrendingUp className="h-3 w-3 mr-1" />
                              View Skills
                            </Link>
                      <Link
                        to={`/candidate/resume/${resume.id}`}
                        className="text-primary-600 hover:text-primary-500 text-sm font-medium"
                      >
                        View Analysis
                      </Link>
                          </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No resume uploaded</h3>
              <p className="text-gray-500 mb-4">Upload your resume to get started with job matching.</p>
              <Link
                to="/candidate/resume"
                className="btn btn-primary px-6 py-3"
              >
                <Upload className="h-4 w-4 mr-2" />
                Upload Resume
              </Link>
            </div>
          )}
        </div>
      </div>

      {/* Recent Jobs */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-gray-900">Recent Job Opportunities</h3>
        </div>
        <div className="card-content">
          {finalJobs && finalJobs.length > 0 ? (
            <div className="space-y-4">
              {finalJobs.map((job) => (
                <div key={job.id} className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between">
                  <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                      <Briefcase className="h-5 w-5 text-gray-400" />
                      <div>
                        <h4 className="text-sm font-medium text-gray-900">{job.title}</h4>
                        <p className="text-sm text-gray-500">{job.company} • {job.location}</p>
                      </div>
                    </div>
                      {job.description && (
                        <p className="text-sm text-gray-600 mt-2 line-clamp-2">
                          {job.description.length > 150 
                            ? `${job.description.substring(0, 150)}...` 
                            : job.description
                          }
                        </p>
                      )}
                  </div>
                    <div className="flex flex-col items-end space-y-2 ml-4">
                    <Link
                      to={`/candidate/jobs/${job.id}`}
                      className="text-primary-600 hover:text-primary-500 text-sm font-medium"
                    >
                        View Details
                    </Link>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Briefcase className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No jobs available</h3>
              <p className="text-gray-500">Check back later for new job opportunities.</p>
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 p-6">
        <Link
          to="/candidate/resume"
          className="card hover:shadow-md transition-shadow cursor-pointer"
        >
          <div className="card-content p-6">
            <div className="flex items-center">
              <FileText className="h-8 w-8 text-primary-600" />
              <div className="ml-4">
                <h3 className="text-lg font-medium text-gray-900">Manage Resume</h3>
                <p className="text-sm text-gray-500">Upload and analyze your resume</p>
              </div>
            </div>
          </div>
        </Link>

        <Link
          to="/candidate/skills"
          className="card hover:shadow-md transition-shadow cursor-pointer"
        >
          <div className="card-content p-6">
            <div className="flex items-center">
              <TrendingUp className="h-8 w-8 text-primary-600" />
              <div className="ml-4">
                <h3 className="text-lg font-medium text-gray-900">Skill Suggestions</h3>
                <p className="text-sm text-gray-500">Get personalized skill recommendations</p>
              </div>
            </div>
          </div>
        </Link>

        <Link
          to="/jobs"
          className="card hover:shadow-md transition-shadow cursor-pointer"
        >
          <div className="card-content p-6">
            <div className="flex items-center">
              <Briefcase className="h-8 w-8 text-primary-600" />
              <div className="ml-4">
                <h3 className="text-lg font-medium text-gray-900">Browse Jobs</h3>
                <p className="text-sm text-gray-500">Find your next opportunity</p>
              </div>
            </div>
          </div>
        </Link>
      </div>
    </div>
  );
};

export default CandidateDashboard;
