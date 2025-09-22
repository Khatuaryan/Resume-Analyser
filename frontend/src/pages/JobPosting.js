import React, { useState, useEffect } from 'react';
import { useMutation, useQueryClient } from 'react-query';
import { useForm } from 'react-hook-form';
import { useLocation } from 'react-router-dom';
import { 
  Plus, 
  Edit, 
  Trash2, 
  Building2,
  BarChart3,
  Users,
  Pause,
  Play,
  CheckCircle,
  Eye
} from 'lucide-react';
import { jobsAPI } from '../services/api';
import toast from 'react-hot-toast';

const JobPosting = () => {
  const location = useLocation();
  const [showForm, setShowForm] = useState(false);
  const [editingJob, setEditingJob] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const queryClient = useQueryClient();

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

  // Check for create query parameter and automatically show form
  useEffect(() => {
    const urlParams = new URLSearchParams(location.search);
    if (urlParams.get('create') === 'true') {
      setShowForm(true);
    }
  }, [location.search]);

  // Ensure jobs is always an array
  const jobsArray = Array.isArray(jobs) ? jobs : [];


  const { register, handleSubmit, reset, setValue, formState: { errors } } = useForm({
    defaultValues: {
      title: '',
      description: '',
      company: '',
      location: '',
      job_type: 'full_time',
      experience_level: 'mid',
      salary_min: '',
      salary_max: '',
      required_skills: '',
      preferred_skills: '',
      benefits: '',
      requirements: '',
      responsibilities: '',
      auto_complete_days: 15
    }
  });

  const createMutation = useMutation(jobsAPI.createJob, {
    onSuccess: () => {
      toast.success('Job posted successfully!');
      fetchJobs(); // Refetch jobs after creation
      setShowForm(false);
      reset();
    },
    onError: (error) => {
      console.error('Job creation error:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to create job';
      toast.error(typeof errorMessage === 'string' ? errorMessage : 'Failed to create job');
    }
  });

  const updateMutation = useMutation(
    ({ jobId, data }) => jobsAPI.updateJob(jobId, data),
    {
      onSuccess: () => {
        toast.success('Job updated successfully!');
        fetchJobs(); // Refetch jobs after update
        setShowForm(false);
        setEditingJob(null);
        reset();
      },
      onError: (error) => {
        console.error('Job update error:', error);
        const errorMessage = error.response?.data?.detail || error.message || 'Failed to update job';
        toast.error(typeof errorMessage === 'string' ? errorMessage : 'Failed to update job');
      }
    }
  );

  const deleteMutation = useMutation(jobsAPI.deleteJob, {
    onSuccess: () => {
      toast.success('Job deleted successfully!');
      fetchJobs(); // Refetch jobs after deletion
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Failed to delete job');
    }
  });

  const onSubmit = (data) => {
    console.log('Form data received:', data);
    
    // Convert string inputs to arrays for skills, benefits, etc.
    const processedData = {
      ...data,
      required_skills: data.required_skills ? data.required_skills.split(',').map(s => s.trim()).filter(s => s) : [],
      preferred_skills: data.preferred_skills ? data.preferred_skills.split(',').map(s => s.trim()).filter(s => s) : [],
      benefits: data.benefits ? data.benefits.split(',').map(s => s.trim()).filter(s => s) : [],
      requirements: data.requirements ? data.requirements.split(',').map(s => s.trim()).filter(s => s) : [],
      responsibilities: data.responsibilities ? data.responsibilities.split(',').map(s => s.trim()).filter(s => s) : [],
      salary_min: data.salary_min ? parseInt(data.salary_min) : null,
      salary_max: data.salary_max ? parseInt(data.salary_max) : null
    };

    console.log('Processed data:', processedData);

    if (editingJob) {
      updateMutation.mutate({ jobId: editingJob.id, data: processedData });
    } else {
      createMutation.mutate(processedData);
    }
  };

  const handleEdit = (job) => {
    setEditingJob(job);
    setValue('title', job.title);
    setValue('description', job.description);
    setValue('company', job.company);
    setValue('location', job.location);
    setValue('job_type', job.job_type);
    setValue('experience_level', job.experience_level);
    setValue('salary_min', job.salary_min || '');
    setValue('salary_max', job.salary_max || '');
    setValue('required_skills', job.required_skills.join(', '));
    setValue('preferred_skills', job.preferred_skills.join(', '));
    setValue('benefits', job.benefits.join(', '));
    setValue('requirements', job.requirements.join(', '));
    setValue('responsibilities', job.responsibilities.join(', '));
    setShowForm(true);
  };


  const handleDelete = (jobId) => {
    if (window.confirm('Are you sure you want to delete this job?')) {
      deleteMutation.mutate(jobId);
    }
  };

  const handleStatusUpdate = async (jobId, newStatus) => {
    try {
      await jobsAPI.updateJobStatus(jobId, { status: newStatus });
      toast.success(`Job status updated to ${newStatus}`);
      fetchJobs(); // Refetch jobs after status update
    } catch (error) {
      toast.error('Failed to update job status');
      console.error('Status update error:', error);
    }
  };

  const handleViewAnalytics = (jobId) => {
    // Navigate to analytics page or open modal
    window.open(`/hr/jobs/${jobId}/analytics`, '_blank');
  };

  const handleViewCandidates = (jobId) => {
    // Navigate to candidates page or open modal
    window.open(`/hr/jobs/${jobId}/candidates`, '_blank');
  };

  const handleCancel = () => {
    setShowForm(false);
    setEditingJob(null);
    reset();
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600 mb-4">Loading jobs...</p>
          <button 
            onClick={fetchJobs}
            className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <h3 className="text-lg font-medium text-gray-900 mb-2">Error loading jobs</h3>
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
          <h1 className="text-2xl font-bold text-gray-900">Job Postings</h1>
          <p className="text-gray-600">Manage your job postings and applications</p>
        </div>
        {jobsArray.length > 0 && (
          <button
            onClick={() => setShowForm(true)}
            className="inline-flex items-center px-4 py-2 bg-primary-600 text-white font-medium rounded-lg hover:bg-primary-700 transition-colors duration-200 shadow-sm hover:shadow-md"
          >
            <Plus className="h-4 w-4 mr-2" />
            Post New Job
          </button>
        )}
      </div>

      {/* Main Content - Form or Jobs List */}
      {showForm ? (
        /* Job Form */
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900">
              {editingJob ? 'Edit Job' : 'Create New Job'}
            </h3>
          </div>
          <div className="card-content">
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Job Title *</label>
                  <input
                    {...register('title', { 
                      required: 'Job title is required',
                      minLength: { value: 3, message: 'Title must be at least 3 characters' },
                      maxLength: { value: 200, message: 'Title must be less than 200 characters' }
                    })}
                    className="input mt-1"
                    placeholder="e.g., Senior Software Engineer"
                  />
                  {errors.title && <p className="text-red-500 text-sm mt-1">{errors.title.message}</p>}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Company *</label>
                  <input
                    {...register('company', { 
                      required: 'Company name is required',
                      minLength: { value: 2, message: 'Company name must be at least 2 characters' },
                      maxLength: { value: 100, message: 'Company name must be less than 100 characters' }
                    })}
                    className="input mt-1"
                    placeholder="e.g., Tech Corp"
                  />
                  {errors.company && <p className="text-red-500 text-sm mt-1">{errors.company.message}</p>}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Location *</label>
                  <input
                    {...register('location', { 
                      required: 'Location is required',
                      minLength: { value: 2, message: 'Location must be at least 2 characters' },
                      maxLength: { value: 100, message: 'Location must be less than 100 characters' }
                    })}
                    className="input mt-1"
                    placeholder="e.g., San Francisco, CA"
                  />
                  {errors.location && <p className="text-red-500 text-sm mt-1">{errors.location.message}</p>}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Job Type</label>
                  <select {...register('job_type')} className="input mt-1">
                    <option value="full_time">Full Time</option>
                    <option value="part_time">Part Time</option>
                    <option value="contract">Contract</option>
                    <option value="internship">Internship</option>
                    <option value="remote">Remote</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Experience Level</label>
                  <select {...register('experience_level')} className="input mt-1">
                    <option value="entry">Entry Level</option>
                    <option value="junior">Junior</option>
                    <option value="mid">Mid Level</option>
                    <option value="senior">Senior</option>
                    <option value="lead">Lead</option>
                    <option value="executive">Executive</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Salary Range (Optional)</label>
                  <div className="flex space-x-2 mt-1">
                    <input
                      {...register('salary_min')}
                      type="number"
                      className="input"
                      placeholder="Min"
                    />
                    <input
                      {...register('salary_max')}
                      type="number"
                      className="input"
                      placeholder="Max"
                    />
                  </div>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Job Description *</label>
                <textarea
                  {...register('description', { 
                    required: 'Job description is required',
                    minLength: { value: 50, message: 'Description must be at least 50 characters' },
                    maxLength: { value: 5000, message: 'Description must be less than 5000 characters' }
                  })}
                  rows={4}
                  className="input mt-1"
                  placeholder="Describe the role, responsibilities, and requirements... (minimum 50 characters)"
                />
                {errors.description && <p className="text-red-500 text-sm mt-1">{errors.description.message}</p>}
                <p className="text-sm text-gray-500 mt-1">Minimum 50 characters required</p>
              </div>

              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Required Skills</label>
                  <input
                    {...register('required_skills')}
                    className="input mt-1"
                    placeholder="Python, JavaScript, React (comma-separated)"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Preferred Skills</label>
                  <input
                    {...register('preferred_skills')}
                    className="input mt-1"
                    placeholder="AWS, Docker, Kubernetes (comma-separated)"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Benefits</label>
                  <input
                    {...register('benefits')}
                    className="input mt-1"
                    placeholder="Health insurance, 401k, Flexible hours (comma-separated)"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Requirements</label>
                  <input
                    {...register('requirements')}
                    className="input mt-1"
                    placeholder="Bachelor's degree, 3+ years experience (comma-separated)"
                  />
                </div>
              </div>

                     <div>
                       <label className="block text-sm font-medium text-gray-700">Responsibilities</label>
                       <input
                         {...register('responsibilities')}
                         className="input mt-1"
                         placeholder="Develop features, Code reviews, Team collaboration (comma-separated)"
                       />
                     </div>

                     <div>
                       <label className="block text-sm font-medium text-gray-700">Auto-complete after (days)</label>
                       <input
                         {...register('auto_complete_days', {
                           required: 'Auto-complete days is required',
                           min: { value: 1, message: 'Must be at least 1 day' },
                           max: { value: 365, message: 'Cannot exceed 365 days' }
                         })}
                         type="number"
                         min="1"
                         max="365"
                         className="input mt-1"
                         placeholder="15"
                       />
                       {errors.auto_complete_days && <p className="text-red-500 text-sm mt-1">{errors.auto_complete_days.message}</p>}
                       <p className="text-sm text-gray-500 mt-1">Job will automatically be marked as completed after this many days</p>
                     </div>

              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={handleCancel}
                  className="px-4 py-2 text-gray-700 bg-gray-100 border border-gray-300 rounded-lg hover:bg-gray-200 transition-colors duration-200 font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={createMutation.isLoading || updateMutation.isLoading}
                  className="px-6 py-2 bg-primary-600 text-white font-medium rounded-lg hover:bg-primary-700 transition-colors duration-200 shadow-sm hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {createMutation.isLoading || updateMutation.isLoading ? (
                    <div className="flex items-center">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      {editingJob ? 'Updating...' : 'Creating...'}
                    </div>
                  ) : (
                    editingJob ? 'Update Job' : 'Create Job'
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      ) : (
        /* Jobs List */
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900">Your Job Postings</h3>
          </div>
          <div className="card-content">
            {jobsArray.length > 0 ? (
              <div className="space-y-4">
                {jobsArray.map((job) => (
                  <div key={job.id} className="flex items-center justify-between p-6 border border-gray-200 rounded-lg hover:shadow-md transition-shadow duration-200 bg-white">
                    <div className="flex-1">
                      <div className="flex items-center space-x-4">
                        <div className="p-2 bg-primary-100 rounded-lg">
                          <Building2 className="h-6 w-6 text-primary-600" />
                        </div>
                        <div className="flex-1">
                          <h4 className="text-lg font-semibold text-gray-900 mb-1">{job.title}</h4>
                          <p className="text-sm text-gray-600 mb-2">{job.company} • {job.location}</p>
                          <div className="flex items-center space-x-4 flex-wrap">
                            <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                              {job.job_type.replace('_', ' ')}
                            </span>
                            <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                              {job.experience_level.replace('_', ' ')}
                            </span>
                            {job.salary_min && job.salary_max && (
                              <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                ${job.salary_min.toLocaleString()} - ${job.salary_max.toLocaleString()}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-6">
                      <div className="text-right">
                        <p className="text-sm font-semibold text-gray-900">{job.application_count} applications</p>
                        <p className="text-sm text-gray-500">{job.unique_view_count || 0} unique views</p>
                        {job.completion_date && (
                          <p className="text-xs text-gray-400">
                            Auto-completes: {new Date(job.completion_date).toLocaleDateString()}
                          </p>
                        )}
                      </div>
                      <div className="flex items-center space-x-3">
                        <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${
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
                        <div className="flex items-center space-x-2">
                          {/* Status Management Buttons */}
                          {job.status === 'active' && (
                            <button
                              onClick={() => handleStatusUpdate(job.id, 'inactive')}
                              className="p-2 text-yellow-600 hover:text-yellow-700 hover:bg-yellow-50 rounded-lg transition-colors duration-200"
                              title="Pause job"
                            >
                              <Pause className="h-4 w-4" />
                            </button>
                          )}
                          {job.status === 'inactive' && (
                            <button
                              onClick={() => handleStatusUpdate(job.id, 'active')}
                              className="p-2 text-green-600 hover:text-green-700 hover:bg-green-50 rounded-lg transition-colors duration-200"
                              title="Resume job"
                            >
                              <Play className="h-4 w-4" />
                            </button>
                          )}
                          {job.status !== 'completed' && (
                            <button
                              onClick={() => handleStatusUpdate(job.id, 'completed')}
                              className="p-2 text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-colors duration-200"
                              title="Mark as completed"
                            >
                              <CheckCircle className="h-4 w-4" />
                            </button>
                          )}
                          
                          {/* Analytics and Candidates Buttons */}
                          <button
                            onClick={() => handleViewAnalytics(job.id)}
                            className="p-2 text-purple-600 hover:text-purple-700 hover:bg-purple-50 rounded-lg transition-colors duration-200"
                            title="View analytics"
                          >
                            <BarChart3 className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => handleViewCandidates(job.id)}
                            className="p-2 text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50 rounded-lg transition-colors duration-200"
                            title="View candidates"
                          >
                            <Users className="h-4 w-4" />
                          </button>
                          
                          {/* Edit and Delete Buttons */}
                          <button
                            onClick={() => handleEdit(job)}
                            className="p-2 text-primary-600 hover:text-primary-700 hover:bg-primary-50 rounded-lg transition-colors duration-200"
                            title="Edit job"
                          >
                            <Edit className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => handleDelete(job.id)}
                            className="p-2 text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors duration-200"
                            title="Delete job"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12 px-6">
                <Building2 className="h-16 w-16 text-gray-400 mx-auto mb-6" />
                <h3 className="text-xl font-semibold text-gray-900 mb-3">No jobs posted yet</h3>
                <p className="text-gray-500 mb-8 max-w-md mx-auto">Get started by posting your first job opening and begin attracting top talent to your organization.</p>
                <button
                  onClick={() => setShowForm(true)}
                  className="inline-flex items-center px-6 py-3 bg-primary-600 text-white font-medium rounded-lg hover:bg-primary-700 transition-colors duration-200 shadow-sm hover:shadow-md"
                >
                  <Plus className="h-5 w-5 mr-2" />
                  Post Your First Job
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default JobPosting;
