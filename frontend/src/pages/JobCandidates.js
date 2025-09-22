import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Users, 
  Mail, 
  Calendar, 
  FileText, 
  Star,
  ArrowLeft,
  Filter,
  Search,
  CheckCircle,
  XCircle,
  Clock
} from 'lucide-react';
import { jobsAPI } from '../services/api';
import toast from 'react-hot-toast';

const JobCandidates = () => {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const [candidates, setCandidates] = useState([]);
  const [job, setJob] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        // Fetch job details and candidates
        const [jobResponse, candidatesResponse] = await Promise.all([
          jobsAPI.getJob(jobId),
          jobsAPI.getJobCandidates(jobId)
        ]);
        
        setJob(jobResponse.data);
        setCandidates(candidatesResponse.data);
      } catch (err) {
        console.error('Error fetching candidates:', err);
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    if (jobId) {
      fetchData();
    }
  }, [jobId]);

  const handleStatusUpdate = async (candidateId, newStatus) => {
    try {
      await jobsAPI.updateCandidateStatus(jobId, candidateId, newStatus);
      toast.success(`Candidate status updated to ${newStatus}`);
      
      // Update local state
      setCandidates(prev => prev.map(candidate => 
        candidate.candidate_id === candidateId 
          ? { ...candidate, status: newStatus }
          : candidate
      ));
    } catch (error) {
      toast.error('Failed to update candidate status');
      console.error('Status update error:', error);
    }
  };

  const filteredCandidates = candidates.filter(candidate => {
    const matchesSearch = candidate.candidate_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         candidate.candidate_email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || candidate.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'reviewed': return 'bg-blue-100 text-blue-800';
      case 'shortlisted': return 'bg-green-100 text-green-800';
      case 'rejected': return 'bg-red-100 text-red-800';
      case 'hired': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending': return <Clock className="h-4 w-4" />;
      case 'reviewed': return <FileText className="h-4 w-4" />;
      case 'shortlisted': return <Star className="h-4 w-4" />;
      case 'rejected': return <XCircle className="h-4 w-4" />;
      case 'hired': return <CheckCircle className="h-4 w-4" />;
      default: return <Clock className="h-4 w-4" />;
    }
  };

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
        <h2 className="text-2xl font-bold text-gray-900">Error loading candidates</h2>
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

  if (!job) {
    return (
      <div className="text-center py-8">
        <h2 className="text-2xl font-bold text-gray-900">Job not found</h2>
        <p className="text-gray-600">The job could not be found.</p>
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
            <h1 className="text-2xl font-bold text-gray-900">Job Candidates</h1>
            <p className="text-gray-600">{job.title} at {job.company}</p>
            <p className="text-sm text-gray-500">{candidates.length} candidates applied</p>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="card-content p-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search candidates..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="input pl-10"
                />
              </div>
            </div>
            <div className="sm:w-48">
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="input"
              >
                <option value="all">All Status</option>
                <option value="pending">Pending</option>
                <option value="reviewed">Reviewed</option>
                <option value="shortlisted">Shortlisted</option>
                <option value="rejected">Rejected</option>
                <option value="hired">Hired</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Candidates List */}
      <div className="space-y-4">
        {filteredCandidates.length > 0 ? (
          filteredCandidates.map((candidate) => (
            <div key={candidate.id} className="card">
              <div className="card-content p-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="p-3 bg-primary-100 rounded-lg">
                      <Users className="h-6 w-6 text-primary-600" />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900">{candidate.candidate_name}</h3>
                      <div className="flex items-center space-x-4 mt-1">
                        <div className="flex items-center text-sm text-gray-600">
                          <Mail className="h-4 w-4 mr-1" />
                          {candidate.candidate_email}
                        </div>
                        <div className="flex items-center text-sm text-gray-600">
                          <Calendar className="h-4 w-4 mr-1" />
                          {new Date(candidate.application_date).toLocaleDateString()}
                        </div>
                        {candidate.match_score && (
                          <div className="flex items-center text-sm text-gray-600">
                            <Star className="h-4 w-4 mr-1" />
                            {Math.round(candidate.match_score * 100)}% match
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-4">
                    <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(candidate.status)}`}>
                      {getStatusIcon(candidate.status)}
                      <span className="ml-1 capitalize">{candidate.status}</span>
                    </span>
                    
                    <div className="flex items-center space-x-2">
                      {candidate.status === 'pending' && (
                        <>
                          <button
                            onClick={() => handleStatusUpdate(candidate.candidate_id, 'reviewed')}
                            className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors duration-200"
                          >
                            Mark Reviewed
                          </button>
                          <button
                            onClick={() => handleStatusUpdate(candidate.candidate_id, 'shortlisted')}
                            className="px-3 py-1 text-sm bg-green-100 text-green-700 rounded hover:bg-green-200 transition-colors duration-200"
                          >
                            Shortlist
                          </button>
                          <button
                            onClick={() => handleStatusUpdate(candidate.candidate_id, 'rejected')}
                            className="px-3 py-1 text-sm bg-red-100 text-red-700 rounded hover:bg-red-200 transition-colors duration-200"
                          >
                            Reject
                          </button>
                        </>
                      )}
                      {candidate.status === 'reviewed' && (
                        <>
                          <button
                            onClick={() => handleStatusUpdate(candidate.candidate_id, 'shortlisted')}
                            className="px-3 py-1 text-sm bg-green-100 text-green-700 rounded hover:bg-green-200 transition-colors duration-200"
                          >
                            Shortlist
                          </button>
                          <button
                            onClick={() => handleStatusUpdate(candidate.candidate_id, 'rejected')}
                            className="px-3 py-1 text-sm bg-red-100 text-red-700 rounded hover:bg-red-200 transition-colors duration-200"
                          >
                            Reject
                          </button>
                        </>
                      )}
                      {candidate.status === 'shortlisted' && (
                        <>
                          <button
                            onClick={() => handleStatusUpdate(candidate.candidate_id, 'hired')}
                            className="px-3 py-1 text-sm bg-purple-100 text-purple-700 rounded hover:bg-purple-200 transition-colors duration-200"
                          >
                            Hire
                          </button>
                          <button
                            onClick={() => handleStatusUpdate(candidate.candidate_id, 'rejected')}
                            className="px-3 py-1 text-sm bg-red-100 text-red-700 rounded hover:bg-red-200 transition-colors duration-200"
                          >
                            Reject
                          </button>
                        </>
                      )}
                    </div>
                  </div>
                </div>
                
                {candidate.cover_letter && (
                  <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                    <h4 className="text-sm font-medium text-gray-900 mb-2">Cover Letter</h4>
                    <p className="text-sm text-gray-700 whitespace-pre-wrap">{candidate.cover_letter}</p>
                  </div>
                )}
              </div>
            </div>
          ))
        ) : (
          <div className="text-center py-12">
            <Users className="h-16 w-16 text-gray-400 mx-auto mb-6" />
            <h3 className="text-xl font-semibold text-gray-900 mb-3">No candidates found</h3>
            <p className="text-gray-500">
              {candidates.length === 0 
                ? "No candidates have applied to this job yet."
                : "No candidates match your current filters."
              }
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default JobCandidates;
