import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  BarChart3, 
  Users, 
  Eye, 
  TrendingUp, 
  MapPin, 
  Briefcase,
  ArrowLeft,
  Calendar,
  Target
} from 'lucide-react';
import { jobsAPI } from '../services/api';

const JobAnalytics = () => {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const [analytics, setAnalytics] = useState(null);
  const [job, setJob] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        // Fetch job details and analytics
        const [jobResponse, analyticsResponse] = await Promise.all([
          jobsAPI.getJob(jobId),
          jobsAPI.getJobAnalytics(jobId)
        ]);
        
        setJob(jobResponse.data);
        setAnalytics(analyticsResponse.data);
      } catch (err) {
        console.error('Error fetching analytics:', err);
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    if (jobId) {
      fetchData();
    }
  }, [jobId]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <h2 className="text-2xl font-bold text-gray-900">Error loading analytics</h2>
        <p className="text-gray-600">{error}</p>
        <button 
          onClick={() => window.location.reload()}
          className="mt-4 px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!analytics || !job) {
    return (
      <div className="text-center py-8">
        <h2 className="text-2xl font-bold text-gray-900">Analytics not found</h2>
        <p className="text-gray-600">The analytics for this job could not be found.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate(-1)}
            className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors duration-200"
          >
            <ArrowLeft className="h-5 w-5" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Job Analytics</h1>
            <p className="text-gray-600">{job.title} at {job.company}</p>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <div className="card">
          <div className="card-content p-6">
            <div className="flex items-center">
              <div className="p-3 bg-blue-100 rounded-lg">
                <Users className="h-8 w-8 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Applications</p>
                <p className="text-2xl font-bold text-gray-900">{analytics.total_applications}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-content p-6">
            <div className="flex items-center">
              <div className="p-3 bg-green-100 rounded-lg">
                <Eye className="h-8 w-8 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Unique Views</p>
                <p className="text-2xl font-bold text-gray-900">{analytics.unique_views}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-content p-6">
            <div className="flex items-center">
              <div className="p-3 bg-purple-100 rounded-lg">
                <TrendingUp className="h-8 w-8 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Application Rate</p>
                <p className="text-2xl font-bold text-gray-900">{(analytics.application_rate * 100).toFixed(1)}%</p>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-content p-6">
            <div className="flex items-center">
              <div className="p-3 bg-orange-100 rounded-lg">
                <BarChart3 className="h-8 w-8 text-orange-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">HR Views</p>
                <p className="text-2xl font-bold text-gray-900">{analytics.hr_views}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Analytics Charts */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Application Status Distribution */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900">Application Status</h3>
          </div>
          <div className="card-content">
            <div className="space-y-4">
              {Object.entries(analytics.status_distribution).map(([status, count]) => (
                <div key={status} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className={`w-3 h-3 rounded-full mr-3 ${
                      status === 'pending' ? 'bg-yellow-400' :
                      status === 'reviewed' ? 'bg-blue-400' :
                      status === 'shortlisted' ? 'bg-green-400' :
                      status === 'rejected' ? 'bg-red-400' :
                      'bg-gray-400'
                    }`}></div>
                    <span className="text-sm font-medium text-gray-700 capitalize">{status}</span>
                  </div>
                  <span className="text-sm font-bold text-gray-900">{count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Experience Level Distribution */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900">Experience Levels</h3>
          </div>
          <div className="card-content">
            <div className="space-y-4">
              {Object.entries(analytics.experience_distribution).map(([level, count]) => (
                <div key={level} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <Briefcase className="h-4 w-4 text-gray-400 mr-3" />
                    <span className="text-sm font-medium text-gray-700 capitalize">{level}</span>
                  </div>
                  <span className="text-sm font-bold text-gray-900">{count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Location Distribution */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900">Applicant Locations</h3>
          </div>
          <div className="card-content">
            <div className="space-y-4">
              {Object.entries(analytics.location_distribution).map(([location, count]) => (
                <div key={location} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <MapPin className="h-4 w-4 text-gray-400 mr-3" />
                    <span className="text-sm font-medium text-gray-700">{location}</span>
                  </div>
                  <span className="text-sm font-bold text-gray-900">{count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Top Skills */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900">Top Skills</h3>
          </div>
          <div className="card-content">
            <div className="flex flex-wrap gap-2">
              {analytics.top_skills.map((skill, index) => (
                <span 
                  key={index}
                  className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-primary-100 text-primary-800"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Job Timeline */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-gray-900">Job Timeline</h3>
        </div>
        <div className="card-content">
          <div className="space-y-4">
            <div className="flex items-center">
              <Calendar className="h-5 w-5 text-gray-400 mr-3" />
              <div>
                <p className="text-sm font-medium text-gray-900">Posted</p>
                <p className="text-sm text-gray-600">{new Date(job.created_at).toLocaleDateString()}</p>
              </div>
            </div>
            {job.completion_date && (
              <div className="flex items-center">
                <Target className="h-5 w-5 text-gray-400 mr-3" />
                <div>
                  <p className="text-sm font-medium text-gray-900">Auto-completion Date</p>
                  <p className="text-sm text-gray-600">{new Date(job.completion_date).toLocaleDateString()}</p>
                </div>
              </div>
            )}
            {job.completed_at && (
              <div className="flex items-center">
                <Target className="h-5 w-5 text-gray-400 mr-3" />
                <div>
                  <p className="text-sm font-medium text-gray-900">Completed</p>
                  <p className="text-sm text-gray-600">{new Date(job.completed_at).toLocaleDateString()}</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default JobAnalytics;
