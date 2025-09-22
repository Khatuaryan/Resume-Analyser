import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { 
  Building2, 
  MapPin, 
  Calendar, 
  DollarSign, 
  Users,
  Clock,
  Briefcase,
  Target,
  BarChart3,
  Eye,
  TrendingUp
} from 'lucide-react';
import { jobsAPI } from '../services/api';

const JobDetails = () => {
  const { jobId } = useParams();
  const [job, setJob] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [candidates, setCandidates] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('details');

  // Fetch job details using useEffect
  const fetchJob = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const [jobResponse, analyticsResponse, candidatesResponse] = await Promise.all([
        jobsAPI.getJob(jobId),
        jobsAPI.getJobAnalytics(jobId),
        jobsAPI.getJobCandidates(jobId)
      ]);
      setJob(jobResponse.data);
      setAnalytics(analyticsResponse.data);
      setCandidates(candidatesResponse.data);
    } catch (err) {
      console.error('Error fetching job:', err);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (jobId) {
      fetchJob();
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
        <h2 className="text-2xl font-bold text-gray-900">Error loading job</h2>
        <p className="text-gray-600">{error}</p>
        <button 
          onClick={fetchJob}
          className="mt-4 px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!job) {
    return (
      <div className="text-center py-8">
        <h2 className="text-2xl font-bold text-gray-900">Job not found</h2>
        <p className="text-gray-600">The job you're looking for doesn't exist.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{job.title}</h1>
          <p className="text-gray-600">{job.company} • {job.location}</p>
        </div>
        <div className="flex items-center space-x-2">
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
            job.status === 'active' 
              ? 'bg-green-100 text-green-800' 
              : 'bg-gray-100 text-gray-800'
          }`}>
            {job.status || 'Unknown'}
          </span>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('details')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'details'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Job Details
          </button>
          <button
            onClick={() => setActiveTab('analytics')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'analytics'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Analytics
          </button>
          <button
            onClick={() => setActiveTab('candidates')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'candidates'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Candidates ({candidates.length})
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'details' && (
        <>
          {/* Job Info */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Description */}
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-medium text-gray-900">Job Description</h3>
            </div>
            <div className="card-content">
              <div className="prose max-w-none">
                <p className="text-gray-700 whitespace-pre-wrap">{job.description}</p>
              </div>
            </div>
          </div>

          {/* Requirements */}
          {job.requirements && job.requirements.length > 0 && (
            <div className="card">
              <div className="card-header">
                <h3 className="text-lg font-medium text-gray-900">Requirements</h3>
              </div>
              <div className="card-content">
                <ul className="space-y-2">
                  {job.requirements.map((requirement, index) => (
                    <li key={index} className="flex items-start">
                      <Target className="h-4 w-4 text-gray-400 mr-2 mt-0.5 flex-shrink-0" />
                      <span className="text-gray-700">{requirement}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          {/* Responsibilities */}
          {job.responsibilities && job.responsibilities.length > 0 && (
            <div className="card">
              <div className="card-header">
                <h3 className="text-lg font-medium text-gray-900">Responsibilities</h3>
              </div>
              <div className="card-content">
                <ul className="space-y-2">
                  {job.responsibilities.map((responsibility, index) => (
                    <li key={index} className="flex items-start">
                      <Briefcase className="h-4 w-4 text-gray-400 mr-2 mt-0.5 flex-shrink-0" />
                      <span className="text-gray-700">{responsibility}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          {/* Benefits */}
          {job.benefits && job.benefits.length > 0 && (
            <div className="card">
              <div className="card-header">
                <h3 className="text-lg font-medium text-gray-900">Benefits</h3>
              </div>
              <div className="card-content">
                <ul className="space-y-2">
                  {job.benefits.map((benefit, index) => (
                    <li key={index} className="flex items-start">
                      <span className="h-2 w-2 bg-primary-600 rounded-full mr-3 mt-2 flex-shrink-0"></span>
                      <span className="text-gray-700">{benefit}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Job Details */}
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-medium text-gray-900">Job Details</h3>
            </div>
            <div className="card-content space-y-4">
              <div className="flex items-center">
                <Building2 className="h-5 w-5 text-gray-400 mr-3" />
                <div>
                  <p className="text-sm font-medium text-gray-900">Company</p>
                  <p className="text-sm text-gray-600">{job.company}</p>
                </div>
              </div>
              
              <div className="flex items-center">
                <MapPin className="h-5 w-5 text-gray-400 mr-3" />
                <div>
                  <p className="text-sm font-medium text-gray-900">Location</p>
                  <p className="text-sm text-gray-600">{job.location}</p>
                </div>
              </div>
              
              <div className="flex items-center">
                <Clock className="h-5 w-5 text-gray-400 mr-3" />
                <div>
                  <p className="text-sm font-medium text-gray-900">Job Type</p>
                  <p className="text-sm text-gray-600">{job.job_type ? job.job_type.replace('_', ' ') : 'Not specified'}</p>
                </div>
              </div>
              
              <div className="flex items-center">
                <Target className="h-5 w-5 text-gray-400 mr-3" />
                <div>
                  <p className="text-sm font-medium text-gray-900">Experience Level</p>
                  <p className="text-sm text-gray-600">{job.experience_level || 'Not specified'}</p>
                </div>
              </div>
              
              {(job.salary_min || job.salary_max) && (
                <div className="flex items-center">
                  <DollarSign className="h-5 w-5 text-gray-400 mr-3" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">Salary</p>
                    <p className="text-sm text-gray-600">
                      {job.salary_min && job.salary_max 
                        ? `$${job.salary_min.toLocaleString()} - $${job.salary_max.toLocaleString()}`
                        : job.salary_min 
                        ? `$${job.salary_min.toLocaleString()}+`
                        : `Up to $${job.salary_max.toLocaleString()}`
                      }
                    </p>
                  </div>
                </div>
              )}
              
              <div className="flex items-center">
                <Calendar className="h-5 w-5 text-gray-400 mr-3" />
                <div>
                  <p className="text-sm font-medium text-gray-900">Posted</p>
                  <p className="text-sm text-gray-600">
                    {new Date(job.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Skills */}
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-medium text-gray-900">Required Skills</h3>
            </div>
            <div className="card-content">
              <div className="flex flex-wrap gap-2">
                {job.required_skills?.map((skill, index) => (
                  <span key={index} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                    {skill}
                  </span>
                ))}
              </div>
              
              {job.preferred_skills && job.preferred_skills.length > 0 && (
                <div className="mt-4">
                  <h4 className="text-sm font-medium text-gray-900 mb-2">Preferred Skills</h4>
                  <div className="flex flex-wrap gap-2">
                    {job.preferred_skills.map((skill, index) => (
                      <span key={index} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Stats */}
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-medium text-gray-900">Job Statistics</h3>
            </div>
            <div className="card-content space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <Users className="h-5 w-5 text-gray-400 mr-2" />
                  <span className="text-sm text-gray-600">Applications</span>
                </div>
                <span className="text-sm font-medium text-gray-900">{job.application_count || 0}</span>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <Calendar className="h-5 w-5 text-gray-400 mr-2" />
                  <span className="text-sm text-gray-600">Views</span>
                </div>
                <span className="text-sm font-medium text-gray-900">{job.view_count || 0}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
        </>
      )}

      {/* Analytics Tab */}
      {activeTab === 'analytics' && analytics && (
        <div className="space-y-6">
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
                    <p className="text-sm font-medium text-gray-600">Candidate Views</p>
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
          </div>
        </div>
      )}

      {/* Candidates Tab */}
      {activeTab === 'candidates' && (
        <div className="space-y-6">
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-medium text-gray-900">Job Candidates ({candidates.length})</h3>
            </div>
            <div className="card-content">
              {candidates.length > 0 ? (
                <div className="space-y-4">
                  {candidates.map((candidate) => (
                    <div key={candidate.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                      <div className="flex items-center space-x-4">
                        <div className="p-3 bg-primary-100 rounded-lg">
                          <Users className="h-6 w-6 text-primary-600" />
                        </div>
                        <div className="flex-1">
                          <h3 className="text-lg font-semibold text-gray-900">{candidate.candidate_name}</h3>
                          <div className="flex items-center space-x-4 mt-1">
                            <div className="flex items-center text-sm text-gray-600">
                              <Users className="h-4 w-4 mr-1" />
                              {candidate.candidate_email}
                            </div>
                            <div className="flex items-center text-sm text-gray-600">
                              <Calendar className="h-4 w-4 mr-1" />
                              {new Date(candidate.application_date).toLocaleDateString()}
                            </div>
                            {candidate.match_score && (
                              <div className="flex items-center text-sm text-gray-600">
                                <Target className="h-4 w-4 mr-1" />
                                {Math.round(candidate.match_score * 100)}% match
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-4">
                        <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${
                          candidate.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                          candidate.status === 'reviewed' ? 'bg-blue-100 text-blue-800' :
                          candidate.status === 'shortlisted' ? 'bg-green-100 text-green-800' :
                          candidate.status === 'rejected' ? 'bg-red-100 text-red-800' :
                          candidate.status === 'hired' ? 'bg-purple-100 text-purple-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {candidate.status}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <Users className="h-16 w-16 text-gray-400 mx-auto mb-6" />
                  <h3 className="text-xl font-semibold text-gray-900 mb-3">No candidates yet</h3>
                  <p className="text-gray-500">No candidates have applied to this job yet.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default JobDetails;
