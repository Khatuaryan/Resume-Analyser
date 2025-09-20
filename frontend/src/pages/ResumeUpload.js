import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { useNavigate } from 'react-router-dom';
import { 
  Upload, 
  FileText, 
  CheckCircle, 
  AlertCircle, 
  Trash2,
  Download,
  Eye
} from 'lucide-react';
import { resumesAPI } from '../services/api';
import toast from 'react-hot-toast';

const ResumeUpload = () => {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { data: resumes, isLoading } = useQuery('resumes', resumesAPI.getResumes);

  const uploadMutation = useMutation(resumesAPI.uploadResume, {
    onSuccess: () => {
      toast.success('Resume uploaded successfully! Processing...');
      queryClient.invalidateQueries('resumes');
      setSelectedFile(null);
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Upload failed');
    }
  });

  const deleteMutation = useMutation(resumesAPI.deleteResume, {
    onSuccess: () => {
      toast.success('Resume deleted successfully');
      queryClient.invalidateQueries('resumes');
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Delete failed');
    }
  });

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleFile = (file) => {
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
    const maxSize = 10 * 1024 * 1024; // 10MB

    if (!allowedTypes.includes(file.type)) {
      toast.error('Invalid file type. Please upload PDF, DOCX, or TXT files only.');
      return;
    }

    if (file.size > maxSize) {
      toast.error('File size too large. Maximum size is 10MB.');
      return;
    }

    setSelectedFile(file);
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleUpload = () => {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append('file', selectedFile);

    uploadMutation.mutate(formData);
  };

  const handleDelete = (resumeId) => {
    if (window.confirm('Are you sure you want to delete this resume?')) {
      deleteMutation.mutate(resumeId);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'processed':
        return 'text-green-600 bg-green-100';
      case 'processing':
        return 'text-yellow-600 bg-yellow-100';
      case 'failed':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'processed':
        return <CheckCircle className="h-4 w-4" />;
      case 'processing':
        return <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-yellow-600" />;
      case 'failed':
        return <AlertCircle className="h-4 w-4" />;
      default:
        return <FileText className="h-4 w-4" />;
    }
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
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Resume Management</h1>
        <p className="text-gray-600">Upload and manage your resumes</p>
      </div>

      {/* Upload Section */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-gray-900">Upload New Resume</h3>
        </div>
        <div className="card-content">
          <div
            className={`relative border-2 border-dashed rounded-lg p-6 ${
              dragActive 
                ? 'border-primary-500 bg-primary-50' 
                : 'border-gray-300'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <div className="text-center">
              <Upload className="mx-auto h-12 w-12 text-gray-400" />
              <div className="mt-4">
                <label htmlFor="file-upload" className="cursor-pointer">
                  <span className="mt-2 block text-sm font-medium text-gray-900">
                    {selectedFile ? selectedFile.name : 'Drop your resume here, or click to browse'}
                  </span>
                  <input
                    id="file-upload"
                    name="file-upload"
                    type="file"
                    className="sr-only"
                    accept=".pdf,.docx,.txt"
                    onChange={handleFileInput}
                  />
                </label>
                <p className="mt-1 text-sm text-gray-500">
                  PDF, DOCX, or TXT files up to 10MB
                </p>
              </div>
            </div>
          </div>

          {selectedFile && (
            <div className="mt-4 flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center">
                <FileText className="h-5 w-5 text-gray-400 mr-2" />
                <span className="text-sm font-medium text-gray-900">{selectedFile.name}</span>
                <span className="ml-2 text-sm text-gray-500">
                  ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
                </span>
              </div>
              <button
                onClick={handleUpload}
                disabled={uploadMutation.isLoading}
                className="btn btn-primary btn-sm"
              >
                {uploadMutation.isLoading ? (
                  <div className="flex items-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Uploading...
                  </div>
                ) : (
                  'Upload Resume'
                )}
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Existing Resumes */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-gray-900">Your Resumes</h3>
        </div>
        <div className="card-content">
          {resumes && resumes.length > 0 ? (
            <div className="space-y-4">
              {resumes.map((resume) => (
                <div key={resume.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <FileText className="h-5 w-5 text-gray-400" />
                    <div>
                      <h4 className="text-sm font-medium text-gray-900">{resume.filename}</h4>
                      <p className="text-sm text-gray-500">
                        Uploaded {new Date(resume.created_at).toLocaleDateString()} • 
                        {(resume.file_size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(resume.status)}`}>
                      {getStatusIcon(resume.status)}
                      <span className="ml-1">{resume.status}</span>
                    </span>
                    {resume.status === 'processed' && (
                      <button
                        onClick={() => navigate(`/candidate/resume/${resume.id}`)}
                        className="text-primary-600 hover:text-primary-500 text-sm font-medium"
                      >
                        <Eye className="h-4 w-4" />
                      </button>
                    )}
                    <button
                      onClick={() => handleDelete(resume.id)}
                      className="text-red-600 hover:text-red-500 text-sm font-medium"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No resumes uploaded</h3>
              <p className="text-gray-500">Upload your first resume to get started.</p>
            </div>
          )}
        </div>
      </div>

      {/* Tips */}
      <div className="card bg-blue-50 border-blue-200">
        <div className="card-content">
          <h3 className="text-lg font-medium text-blue-900 mb-2">Tips for Better Results</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Use a clear, well-formatted resume</li>
            <li>• Include relevant keywords and skills</li>
            <li>• Make sure your contact information is up to date</li>
            <li>• Include your work experience and education</li>
            <li>• Save your resume as a PDF for best compatibility</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default ResumeUpload;
