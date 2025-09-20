import React from 'react';
import { useQuery } from 'react-query';
import { Link } from 'react-router-dom';
import { 
  FileText, 
  TrendingUp, 
  Briefcase, 
  Upload,
  CheckCircle,
  AlertCircle,
  User,
  Target
} from 'lucide-react';
import { resumesAPI, jobsAPI } from '../services/api';

const CandidateDashboard = () => {
  const { data: resumes, isLoading: resumesLoading } = useQuery('resumes', resumesAPI.getResumes);
  const { data: jobs, isLoading: jobsLoading } = useQuery('jobs', () => jobsAPI.getJobs({ limit: 5 }));

  const latestResume = resumes?.[0];
  const hasResume = resumes && resumes.length > 0;
  const processedResume = resumes?.find(r => r.status === 'processed');

  const stats = [
    {
      name: 'Resumes Uploaded',
      value: resumes?.length || 0,
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
      name: 'Skills Analyzed',
      value: processedResume?.parsed_data?.skills?.length || 0,
      icon: TrendingUp,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100'
    },
    {
      name: 'Profile Score',
      value: processedResume?.analysis_score || 0,
      icon: Target,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100'
    }
  ];

  if (resumesLoading || jobsLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
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
        <Link
          to="/candidate/resume"
          className="btn btn-primary"
        >
          <Upload className="h-4 w-4 mr-2" />
          Upload Resume
        </Link>
      </div>

      {/* Resume Status Alert */}
      {hasResume && (
        <div className={`rounded-lg p-4 ${
          latestResume?.status === 'processed' 
            ? 'bg-green-50 border border-green-200' 
            : latestResume?.status === 'processing'
            ? 'bg-yellow-50 border border-yellow-200'
            : 'bg-red-50 border border-red-200'
        }`}>
          <div className="flex items-center">
            {latestResume?.status === 'processed' ? (
              <CheckCircle className="h-5 w-5 text-green-600" />
            ) : latestResume?.status === 'processing' ? (
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-yellow-600"></div>
            ) : (
              <AlertCircle className="h-5 w-5 text-red-600" />
            )}
            <div className="ml-3">
              <h3 className="text-sm font-medium">
                {latestResume?.status === 'processed' 
                  ? 'Resume processed successfully!' 
                  : latestResume?.status === 'processing'
                  ? 'Processing your resume...'
                  : 'Resume processing failed'
                }
              </h3>
              <p className="text-sm text-gray-600">
                {latestResume?.status === 'processed' 
                  ? 'Your resume has been analyzed and is ready for job matching.' 
                  : latestResume?.status === 'processing'
                  ? 'Please wait while we analyze your resume.'
                  : 'Please try uploading your resume again.'
                }
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.name} className="card">
              <div className="card-content">
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
              {resumes.map((resume) => (
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
                      <Link
                        to={`/candidate/resume/${resume.id}`}
                        className="text-primary-600 hover:text-primary-500 text-sm font-medium"
                      >
                        View Analysis
                      </Link>
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
                className="btn btn-primary"
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
          {jobs && jobs.length > 0 ? (
            <div className="space-y-4">
              {jobs.map((job) => (
                <div key={job.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3">
                      <Briefcase className="h-5 w-5 text-gray-400" />
                      <div>
                        <h4 className="text-sm font-medium text-gray-900">{job.title}</h4>
                        <p className="text-sm text-gray-500">{job.company} • {job.location}</p>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-gray-500">{job.job_type}</span>
                    <Link
                      to={`/jobs/${job.id}`}
                      className="text-primary-600 hover:text-primary-500 text-sm font-medium"
                    >
                      View Job
                    </Link>
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
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <Link
          to="/candidate/resume"
          className="card hover:shadow-md transition-shadow cursor-pointer"
        >
          <div className="card-content">
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
          <div className="card-content">
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
          <div className="card-content">
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
