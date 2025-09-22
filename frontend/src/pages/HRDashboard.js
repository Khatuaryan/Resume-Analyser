import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Briefcase,
  Users,
  TrendingUp,
  Eye,
  Plus,
  Building2,
  Calendar
} from 'lucide-react';
import { jobsAPI } from '../services/api';

const HRDashboard = () => {
  const [jobs, setJobs] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showTotalJobs, setShowTotalJobs] = useState(false);
  const [showActiveJobs, setShowActiveJobs] = useState(false);
  const [showTrendingJobs, setShowTrendingJobs] = useState(false);
  const [showRecentJobs, setShowRecentJobs] = useState(false);
  const [showAllJobs, setShowAllJobs] = useState(true); // Default to showing all jobs
  const [currentPage, setCurrentPage] = useState(1);
  const [jobsPerPage] = useState(10);

  // Fetch jobs using useEffect
  const fetchJobs = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await jobsAPI.getHRJobs();
      setJobs(response.data || []);
    } catch (err) {
      console.error('Error fetching jobs:', err);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, []);

  // Ensure jobs is always an array
  const jobsArray = Array.isArray(jobs) ? jobs : [];

  // Sorting functions
  const getActiveJobsByDeadline = () => {
    return jobsArray
      .filter(job => job.status === 'active')
      .sort((a, b) => {
        const dateA = new Date(a.completion_date || a.created_at);
        const dateB = new Date(b.completion_date || b.created_at);
        return dateA - dateB; // Nearest deadline first
      });
  };

  const getTrendingJobs = () => {
    return jobsArray
      .filter(job => job.status === 'active')
      .sort((a, b) => {
        const rateA = (a.application_count || 0) / Math.max(a.unique_view_count || 1, 1);
        const rateB = (b.application_count || 0) / Math.max(b.unique_view_count || 1, 1);
        return rateB - rateA; // Highest application rate first
      });
  };

  const getRecentJobs = () => {
    return jobsArray
      .sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
  };

  const getTotalJobs = () => {
    return jobsArray.filter(job => job.status !== 'draft');
  };

  // Get current jobs based on active view
  const getCurrentJobs = () => {
    if (showTotalJobs) return getTotalJobs();
    if (showActiveJobs) return getActiveJobsByDeadline();
    if (showTrendingJobs) return getTrendingJobs();
    if (showRecentJobs) return getRecentJobs();
    if (showAllJobs) return getTotalJobs(); // Default to all jobs
    return getTotalJobs(); // Fallback to all jobs
  };

  // Pagination logic
  const currentJobs = getCurrentJobs();
  const totalPages = Math.ceil(currentJobs.length / jobsPerPage);
  const startIndex = (currentPage - 1) * jobsPerPage;
  const endIndex = startIndex + jobsPerPage;
  const paginatedJobs = currentJobs.slice(startIndex, endIndex);

  const stats = [
    {
      name: 'Total Jobs',
      value: jobsArray.filter(job => job.status !== 'draft').length,
      icon: Briefcase,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100'
    },
    {
      name: 'Active Jobs',
      value: jobsArray.filter(job => job.status === 'active').length,
      icon: Eye,
      color: 'text-green-600',
      bgColor: 'bg-green-100'
    },
    {
      name: 'Trending Jobs',
      value: jobsArray.filter(job => job.status === 'active').length,
      icon: TrendingUp,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100'
    },
    {
      name: 'Recent Jobs',
      value: jobsArray.length,
      icon: Calendar,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100'
    }
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <h3 className="text-lg font-medium text-gray-900 mb-2">Error loading dashboard</h3>
          <p className="text-gray-500 mb-4">Unable to load job data. Please try again.</p>
          <button 
            onClick={() => window.location.reload()} 
            className="btn btn-primary"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">HR Dashboard</h1>
          <p className="text-gray-600">Manage your job postings and candidates</p>
        </div>
        {jobsArray.length > 0 && (
          <Link
            to="/hr/jobs?create=true"
            className="inline-flex items-center px-4 py-2 bg-primary-600 text-white font-medium rounded-lg hover:bg-primary-700 transition-colors duration-200 shadow-sm hover:shadow-md"
          >
            <Plus className="h-4 w-4 mr-2" />
            Post New Job
          </Link>
        )}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          const isClickable = stat.name === 'Total Jobs' || stat.name === 'Active Jobs' || stat.name === 'Trending Jobs' || stat.name === 'Recent Jobs';
          return (
            <div 
              key={stat.name} 
              className={`card ${isClickable ? 'cursor-pointer hover:shadow-lg transition-shadow duration-200' : ''}`}
              onClick={isClickable ? () => {
                if (stat.name === 'Total Jobs') {
                  const newShowTotalJobs = !showTotalJobs;
                  setShowTotalJobs(newShowTotalJobs);
                  setShowActiveJobs(false);
                  setShowTrendingJobs(false);
                  setShowRecentJobs(false);
                  setShowAllJobs(!newShowTotalJobs); // Show all jobs when Total Jobs is unselected
                } else if (stat.name === 'Active Jobs') {
                  const newShowActiveJobs = !showActiveJobs;
                  setShowActiveJobs(newShowActiveJobs);
                  setShowTotalJobs(false);
                  setShowTrendingJobs(false);
                  setShowRecentJobs(false);
                  setShowAllJobs(!newShowActiveJobs); // Show all jobs when Active Jobs is unselected
                } else if (stat.name === 'Trending Jobs') {
                  const newShowTrendingJobs = !showTrendingJobs;
                  setShowTrendingJobs(newShowTrendingJobs);
                  setShowTotalJobs(false);
                  setShowActiveJobs(false);
                  setShowRecentJobs(false);
                  setShowAllJobs(!newShowTrendingJobs); // Show all jobs when Trending Jobs is unselected
                } else if (stat.name === 'Recent Jobs') {
                  const newShowRecentJobs = !showRecentJobs;
                  setShowRecentJobs(newShowRecentJobs);
                  setShowTotalJobs(false);
                  setShowActiveJobs(false);
                  setShowTrendingJobs(false);
                  setShowAllJobs(!newShowRecentJobs); // Show all jobs when Recent Jobs is unselected
                }
                setCurrentPage(1); // Reset to first page when switching views
              } : undefined}
            >
              <div className="card-content p-6">
                <div className="flex items-center">
                  <div className={`p-2 rounded-lg ${stat.bgColor}`}>
                    <Icon className={`h-6 w-6 ${stat.color}`} />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                    <p className="text-2xl font-semibold text-gray-900">{stat.value}</p>
                    {isClickable && (
                      <p className="text-xs text-gray-500 mt-1">Click to view details</p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Job Listings */}
      {(showAllJobs || showTotalJobs || showActiveJobs || showTrendingJobs || showRecentJobs) && (
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900">
              {showAllJobs && 'All Job Postings'}
              {showTotalJobs && 'All Jobs'}
              {showActiveJobs && 'Active Jobs (by Deadline)'}
              {showTrendingJobs && 'Trending Jobs'}
              {showRecentJobs && 'Recent Jobs'}
            </h3>
            <p className="text-sm text-gray-500 mt-1">
              Showing {startIndex + 1}-{Math.min(endIndex, currentJobs.length)} of {currentJobs.length} jobs
            </p>
          </div>
          <div className="card-content">
            <div className="space-y-4">
              {paginatedJobs.map((job) => (
                <Link
                  key={job.id}
                  to={`/hr/jobs/${job.id}`}
                  className="block"
                >
                  <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow duration-200 cursor-pointer">
                    <div className="flex-1">
                      <h4 className="text-lg font-semibold text-gray-900">{job.title} | {job.company}</h4>
                      <p className="text-sm text-gray-600">{job.location}</p>
                      <div className="flex items-center space-x-4 mt-2">
                        <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${
                          job.status === 'active' 
                            ? 'bg-green-100 text-green-800' 
                            : job.status === 'inactive'
                            ? 'bg-yellow-100 text-yellow-800'
                            : job.status === 'completed'
                            ? 'bg-blue-100 text-blue-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {job.status}
                        </span>
                        <span className="text-sm text-gray-500">{job.application_count} applications</span>
                        <span className="text-sm text-gray-500">{job.unique_view_count || 0} candidate views</span>
                        {showActiveJobs && job.completion_date && (
                          <span className="text-sm text-gray-500">
                            Deadline: {new Date(job.completion_date).toLocaleDateString()}
                          </span>
                        )}
                        {showTrendingJobs && (
                          <span className="text-sm text-gray-500">
                            Rate: {((job.application_count || 0) / Math.max(job.unique_view_count || 1, 1) * 100).toFixed(1)}%
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
            
            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between mt-6">
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                    disabled={currentPage === 1}
                    className="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Previous
                  </button>
                  <span className="text-sm text-gray-700">
                    Page {currentPage} of {totalPages}
                  </span>
                  <button
                    onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                    disabled={currentPage === totalPages}
                    className="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Next
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Empty State - Only show when no jobs and no specific view is selected */}
      {jobsArray.length === 0 && !showTotalJobs && !showActiveJobs && !showTrendingJobs && !showRecentJobs && (
        <div className="card">
          <div className="card-content">
            <div className="text-center py-12 px-6">
              <Briefcase className="h-16 w-16 text-gray-400 mx-auto mb-6" />
              <h3 className="text-xl font-semibold text-gray-900 mb-3">No jobs posted yet</h3>
              <p className="text-gray-500 mb-8 max-w-md mx-auto">Get started by posting your first job opening and begin attracting top talent to your organization.</p>
              <Link
                to="/hr/jobs"
                className="inline-flex items-center px-6 py-3 bg-primary-600 text-white font-medium rounded-lg hover:bg-primary-700 transition-colors duration-200 shadow-sm hover:shadow-md"
              >
                <Plus className="h-5 w-5 mr-2" />
                Post Your First Job
              </Link>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

export default HRDashboard;
