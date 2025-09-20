import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { useForm } from 'react-hook-form';
import { 
  Plus, 
  Edit, 
  Trash2, 
  Eye, 
  Users,
  Calendar,
  DollarSign,
  MapPin,
  Building2
} from 'lucide-react';
import { jobsAPI } from '../services/api';
import toast from 'react-hot-toast';

const JobPosting = () => {
  const [showForm, setShowForm] = useState(false);
  const [editingJob, setEditingJob] = useState(null);
  const queryClient = useQueryClient();

  const { data: jobs, isLoading } = useQuery('hr-jobs', jobsAPI.getHRJobs);

  const { register, handleSubmit, reset, setValue, watch } = useForm({
    defaultValues: {
      title: '',
      description: '',
      company: '',
      location: '',
      job_type: 'full_time',
      experience_level: 'mid',
      salary_min: '',
      salary_max: '',
      required_skills: [],
      preferred_skills: [],
      benefits: [],
      requirements: [],
      responsibilities: []
    }
  });

  const createMutation = useMutation(jobsAPI.createJob, {
    onSuccess: () => {
      toast.success('Job posted successfully!');
      queryClient.invalidateQueries('hr-jobs');
      setShowForm(false);
      reset();
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Failed to create job');
    }
  });

  const updateMutation = useMutation(
    ({ jobId, data }) => jobsAPI.updateJob(jobId, data),
    {
      onSuccess: () => {
        toast.success('Job updated successfully!');
        queryClient.invalidateQueries('hr-jobs');
        setShowForm(false);
        setEditingJob(null);
        reset();
      },
      onError: (error) => {
        toast.error(error.response?.data?.detail || 'Failed to update job');
      }
    }
  );

  const deleteMutation = useMutation(jobsAPI.deleteJob, {
    onSuccess: () => {
      toast.success('Job deleted successfully!');
      queryClient.invalidateQueries('hr-jobs');
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Failed to delete job');
    }
  });

  const onSubmit = (data) => {
    // Convert string inputs to arrays for skills, benefits, etc.
    const processedData = {
      ...data,
      required_skills: data.required_skills.split(',').map(s => s.trim()).filter(s => s),
      preferred_skills: data.preferred_skills.split(',').map(s => s.trim()).filter(s => s),
      benefits: data.benefits.split(',').map(s => s.trim()).filter(s => s),
      requirements: data.requirements.split(',').map(s => s.trim()).filter(s => s),
      responsibilities: data.responsibilities.split(',').map(s => s.trim()).filter(s => s),
      salary_min: data.salary_min ? parseInt(data.salary_min) : null,
      salary_max: data.salary_max ? parseInt(data.salary_max) : null
    };

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

  const handleCancel = () => {
    setShowForm(false);
    setEditingJob(null);
    reset();
  };

  if (isLoading) {
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
          <h1 className="text-2xl font-bold text-gray-900">Job Postings</h1>
          <p className="text-gray-600">Manage your job postings and applications</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="btn btn-primary"
        >
          <Plus className="h-4 w-4 mr-2" />
          Post New Job
        </button>
      </div>

      {/* Job Form */}
      {showForm && (
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
                  <label className="block text-sm font-medium text-gray-700">Job Title</label>
                  <input
                    {...register('title', { required: true })}
                    className="input mt-1"
                    placeholder="e.g., Senior Software Engineer"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Company</label>
                  <input
                    {...register('company', { required: true })}
                    className="input mt-1"
                    placeholder="e.g., Tech Corp"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Location</label>
                  <input
                    {...register('location', { required: true })}
                    className="input mt-1"
                    placeholder="e.g., San Francisco, CA"
                  />
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
                <label className="block text-sm font-medium text-gray-700">Job Description</label>
                <textarea
                  {...register('description', { required: true })}
                  rows={4}
                  className="input mt-1"
                  placeholder="Describe the role, responsibilities, and requirements..."
                />
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

              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={handleCancel}
                  className="btn btn-secondary"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={createMutation.isLoading || updateMutation.isLoading}
                  className="btn btn-primary"
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
      )}

      {/* Jobs List */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-gray-900">Your Job Postings</h3>
        </div>
        <div className="card-content">
          {jobs && jobs.length > 0 ? (
            <div className="space-y-4">
              {jobs.map((job) => (
                <div key={job.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3">
                      <Building2 className="h-5 w-5 text-gray-400" />
                      <div>
                        <h4 className="text-sm font-medium text-gray-900">{job.title}</h4>
                        <p className="text-sm text-gray-500">{job.company} • {job.location}</p>
                        <div className="flex items-center space-x-4 mt-1">
                          <span className="text-xs text-gray-500">{job.job_type}</span>
                          <span className="text-xs text-gray-500">{job.experience_level}</span>
                          {job.salary_min && job.salary_max && (
                            <span className="text-xs text-gray-500">
                              ${job.salary_min.toLocaleString()} - ${job.salary_max.toLocaleString()}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="text-right">
                      <p className="text-sm font-medium text-gray-900">{job.application_count} applications</p>
                      <p className="text-sm text-gray-500">{job.view_count} views</p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        job.status === 'active' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {job.status}
                      </span>
                      <button
                        onClick={() => handleEdit(job)}
                        className="text-primary-600 hover:text-primary-500"
                      >
                        <Edit className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(job.id)}
                        className="text-red-600 hover:text-red-500"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Building2 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No jobs posted yet</h3>
              <p className="text-gray-500 mb-4">Get started by posting your first job opening.</p>
              <button
                onClick={() => setShowForm(true)}
                className="btn btn-primary"
              >
                <Plus className="h-4 w-4 mr-2" />
                Post Your First Job
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default JobPosting;
