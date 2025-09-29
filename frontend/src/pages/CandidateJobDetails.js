import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Building2, 
  MapPin, 
  Calendar, 
  DollarSign, 
  Users,
  Clock,
  Briefcase,
  Target,
  ArrowLeft,
  Send,
  CheckCircle,
  Star,
  Globe,
  Phone,
  Mail,
  ExternalLink
} from 'lucide-react';
import { jobsAPI } from '../services/api';
import toast from 'react-hot-toast';

const CandidateJobDetails = () => {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const [job, setJob] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isApplying, setIsApplying] = useState(false);
  const [hasApplied, setHasApplied] = useState(false);
  const [applicationStatus, setApplicationStatus] = useState('unknown'); // 'unknown', 'applied', 'not_applied'

  // Check if user has already applied to this job
  const checkApplicationStatus = async () => {
    try {
      // Try to get job applications to check if current user has applied
      const response = await jobsAPI.getJobApplications(jobId);
      const applications = response.data || [];
      
      // Get current user info from localStorage or context
      const token = localStorage.getItem('token');
      if (token) {
        // Decode token to get user info (simple approach)
        const payload = JSON.parse(atob(token.split('.')[1]));
        const currentUserId = payload.sub;
        
        // Check if current user has applied
        const userApplication = applications.find(app => app.candidate_id === currentUserId);
        if (userApplication) {
          setApplicationStatus('applied');
          setHasApplied(true);
        } else {
          setApplicationStatus('not_applied');
          setHasApplied(false);
        }
      }
    } catch (err) {
      console.error('Error checking application status:', err);
      // If we can't check, assume not applied
      setApplicationStatus('not_applied');
      setHasApplied(false);
    }
  };

  // Fetch job details
  const fetchJob = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await jobsAPI.getJob(jobId);
      setJob(response.data);
      
      // Check application status after loading job
      await checkApplicationStatus();
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

  // Handle job application
  const handleApply = async () => {
    // Prevent applying if already applied
    if (hasApplied || applicationStatus === 'applied') {
      toast.error('You have already applied to this job.');
      return;
    }

    try {
      setIsApplying(true);
      const response = await jobsAPI.applyToJob(jobId, {
        cover_letter: '', // Optional cover letter
        additional_info: '' // Optional additional information
      });
      
      setHasApplied(true);
      setApplicationStatus('applied');
      toast.success('Application submitted successfully!');
    } catch (err) {
      console.error('Error applying to job:', err);
      
      // Handle specific error cases
      if (err.response?.status === 409) {
        // Conflict - user already applied
        setHasApplied(true);
        setApplicationStatus('applied');
        toast.error('You have already applied to this job.');
      } else if (err.response?.status === 400) {
        // Bad request - might be duplicate
        const errorMessage = err.response?.data?.detail || 'You may have already applied to this job.';
        toast.error(errorMessage);
      } else {
        // Other errors
        const errorMessage = err.response?.data?.detail || 'Failed to submit application. Please try again.';
        toast.error(errorMessage);
      }
    } finally {
      setIsApplying(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading job details...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Error loading job</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <div className="space-x-4">
            <button 
              onClick={fetchJob}
              className="btn btn-primary"
            >
              Retry
            </button>
            <button 
              onClick={() => navigate('/candidate')}
              className="btn btn-secondary"
            >
              Back to Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!job) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Job not found</h2>
          <p className="text-gray-600 mb-6">The job you're looking for doesn't exist.</p>
          <button 
            onClick={() => navigate('/candidate')}
            className="btn btn-primary"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/candidate')}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <ArrowLeft className="h-6 w-6" />
              </button>
              <div>
                <h1 className="text-xl font-semibold text-gray-900">{job.title}</h1>
                <p className="text-sm text-gray-500">{job.company} • {job.location}</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              {hasApplied || applicationStatus === 'applied' ? (
                <div className="flex items-center space-x-2 text-green-600">
                  <CheckCircle className="h-5 w-5" />
                  <span className="text-sm font-medium">Applied</span>
                </div>
              ) : (
                <button
                  onClick={handleApply}
                  disabled={isApplying || applicationStatus === 'unknown'}
                  className="btn btn-primary flex items-center space-x-2 px-6 py-3 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isApplying ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      <span>Applying...</span>
                    </>
                  ) : applicationStatus === 'unknown' ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      <span>Checking...</span>
                    </>
                  ) : (
                    <>
                      <Send className="h-4 w-4" />
                      <span>Apply Now</span>
                    </>
                  )}
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Job Description */}
            <div className="card">
              <div className="card-header">
                <h2 className="text-xl font-semibold text-gray-900">Job Description</h2>
              </div>
              <div className="card-content">
                <div className="prose max-w-none">
                  <p className="text-gray-700 whitespace-pre-wrap leading-relaxed">
                    {job.description}
                  </p>
                </div>
              </div>
            </div>

            {/* Requirements */}
            {job.requirements && job.requirements.length > 0 && (
              <div className="card">
                <div className="card-header">
                  <h3 className="text-lg font-semibold text-gray-900">Requirements</h3>
                </div>
                <div className="card-content">
                  <ul className="space-y-3">
                    {job.requirements.map((requirement, index) => (
                      <li key={index} className="flex items-start">
                        <Target className="h-5 w-5 text-primary-600 mr-3 mt-0.5 flex-shrink-0" />
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
                  <h3 className="text-lg font-semibold text-gray-900">Key Responsibilities</h3>
                </div>
                <div className="card-content">
                  <ul className="space-y-3">
                    {job.responsibilities.map((responsibility, index) => (
                      <li key={index} className="flex items-start">
                        <Briefcase className="h-5 w-5 text-primary-600 mr-3 mt-0.5 flex-shrink-0" />
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
                  <h3 className="text-lg font-semibold text-gray-900">Benefits & Perks</h3>
                </div>
                <div className="card-content">
                  <ul className="space-y-3">
                    {job.benefits.map((benefit, index) => (
                      <li key={index} className="flex items-start">
                        <Star className="h-5 w-5 text-yellow-500 mr-3 mt-0.5 flex-shrink-0" />
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
            {/* Company Info */}
            <div className="card">
              <div className="card-header">
                <h3 className="text-lg font-semibold text-gray-900">Company Information</h3>
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
                
                {job.company_website && (
                  <div className="flex items-center">
                    <Globe className="h-5 w-5 text-gray-400 mr-3" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">Website</p>
                      <a 
                        href={job.company_website} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-sm text-primary-600 hover:text-primary-500 flex items-center"
                      >
                        Visit Website
                        <ExternalLink className="h-3 w-3 ml-1" />
                      </a>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Job Details */}
            <div className="card">
              <div className="card-header">
                <h3 className="text-lg font-semibold text-gray-900">Job Details</h3>
              </div>
              <div className="card-content space-y-4">
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
                      <p className="text-sm font-medium text-gray-900">Salary Range</p>
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

            {/* Required Skills */}
            {job.required_skills && job.required_skills.length > 0 && (
              <div className="card">
                <div className="card-header">
                  <h3 className="text-lg font-semibold text-gray-900">Required Skills</h3>
                </div>
                <div className="card-content">
                  <div className="flex flex-wrap gap-2">
                    {job.required_skills.map((skill, index) => (
                      <span key={index} className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-primary-100 text-primary-800">
                        {skill}
                      </span>
                    ))}
                  </div>
                  
                  {job.preferred_skills && job.preferred_skills.length > 0 && (
                    <div className="mt-4">
                      <h4 className="text-sm font-medium text-gray-900 mb-2">Preferred Skills</h4>
                      <div className="flex flex-wrap gap-2">
                        {job.preferred_skills.map((skill, index) => (
                          <span key={index} className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-800">
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Application Stats */}
            <div className="card">
              <div className="card-header">
                <h3 className="text-lg font-semibold text-gray-900">Job Statistics</h3>
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
      </div>
    </div>
  );
};

export default CandidateJobDetails;
