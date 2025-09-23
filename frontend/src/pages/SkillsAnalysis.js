import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  Star, 
  TrendingUp, 
  Target,
  CheckCircle,
  AlertCircle,
  X,
  Award,
  BookOpen,
  Code,
  Users,
  Lightbulb,
  BarChart3,
  Zap,
  Shield,
  Rocket
} from 'lucide-react';
import { resumesAPI } from '../services/api';

const SkillsAnalysis = () => {
  const { resumeId } = useParams();
  const navigate = useNavigate();
  const [resume, setResume] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchResume = async () => {
      try {
        setLoading(true);
        const response = await resumesAPI.getResume(resumeId);
        setResume(response.data);
      } catch (err) {
        console.error('Error fetching resume:', err);
        setError('Failed to load resume data');
      } finally {
        setLoading(false);
      }
    };

    if (resumeId) {
      fetchResume();
    }
  }, [resumeId]);

  // Skill categorization and analysis
  const categorizeSkills = (skills) => {
    const categories = {
      technical: [],
      soft: [],
      tools: [],
      languages: [],
      frameworks: [],
      databases: []
    };

    const skillKeywords = {
      technical: ['programming', 'development', 'coding', 'algorithm', 'data structure', 'software engineering'],
      soft: ['leadership', 'communication', 'teamwork', 'management', 'problem solving', 'creativity'],
      tools: ['git', 'docker', 'kubernetes', 'jenkins', 'aws', 'azure', 'gcp'],
      languages: ['python', 'javascript', 'java', 'c++', 'c#', 'go', 'rust', 'php', 'ruby'],
      frameworks: ['react', 'angular', 'vue', 'django', 'flask', 'spring', 'express', 'laravel'],
      databases: ['mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'sqlite']
    };

    skills.forEach(skill => {
      const skillName = typeof skill === 'string' ? skill.toLowerCase() : (skill.name || skill.skill || '').toLowerCase();
      let categorized = false;

      for (const [category, keywords] of Object.entries(skillKeywords)) {
        if (keywords.some(keyword => skillName.includes(keyword))) {
          categories[category].push(skill);
          categorized = true;
          break;
        }
      }

      if (!categorized) {
        // Default to technical if not categorized
        categories.technical.push(skill);
      }
    });

    return categories;
  };

  const getSkillLevel = (skill) => {
    if (typeof skill === 'string') return 'Intermediate';
    if (skill.confidence > 0.8) return 'Expert';
    if (skill.confidence > 0.6) return 'Advanced';
    if (skill.confidence > 0.4) return 'Intermediate';
    return 'Beginner';
  };

  const getSkillColor = (level) => {
    switch (level) {
      case 'Expert': return 'bg-green-100 text-green-800 border-green-200';
      case 'Advanced': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'Intermediate': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'Beginner': return 'bg-gray-100 text-gray-800 border-gray-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getSkillIcon = (level) => {
    switch (level) {
      case 'Expert': return <Star className="h-4 w-4" />;
      case 'Advanced': return <TrendingUp className="h-4 w-4" />;
      case 'Intermediate': return <Target className="h-4 w-4" />;
      case 'Beginner': return <CheckCircle className="h-4 w-4" />;
      default: return <CheckCircle className="h-4 w-4" />;
    }
  };

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'technical': return <Code className="h-5 w-5" />;
      case 'soft': return <Users className="h-5 w-5" />;
      case 'tools': return <Zap className="h-5 w-5" />;
      case 'languages': return <BookOpen className="h-5 w-5" />;
      case 'frameworks': return <Rocket className="h-5 w-5" />;
      case 'databases': return <Shield className="h-5 w-5" />;
      default: return <Target className="h-5 w-5" />;
    }
  };

  const getCategoryColor = (category) => {
    switch (category) {
      case 'technical': return 'bg-blue-50 border-blue-200 text-blue-800';
      case 'soft': return 'bg-green-50 border-green-200 text-green-800';
      case 'tools': return 'bg-purple-50 border-purple-200 text-purple-800';
      case 'languages': return 'bg-orange-50 border-orange-200 text-orange-800';
      case 'frameworks': return 'bg-pink-50 border-pink-200 text-pink-800';
      case 'databases': return 'bg-indigo-50 border-indigo-200 text-indigo-800';
      default: return 'bg-gray-50 border-gray-200 text-gray-800';
    }
  };

  const getSkillRecommendations = (skills) => {
    const recommendations = [];
    const skillNames = skills.map(s => typeof s === 'string' ? s.toLowerCase() : (s.name || s.skill || '').toLowerCase());
    
    // Check for missing popular skills
    const popularSkills = {
      'Python': !skillNames.some(s => s.includes('python')),
      'JavaScript': !skillNames.some(s => s.includes('javascript') || s.includes('js')),
      'React': !skillNames.some(s => s.includes('react')),
      'Node.js': !skillNames.some(s => s.includes('node')),
      'Git': !skillNames.some(s => s.includes('git')),
      'Docker': !skillNames.some(s => s.includes('docker')),
      'AWS': !skillNames.some(s => s.includes('aws')),
      'SQL': !skillNames.some(s => s.includes('sql')),
      'Leadership': !skillNames.some(s => s.includes('leadership')),
      'Communication': !skillNames.some(s => s.includes('communication'))
    };

    Object.entries(popularSkills).forEach(([skill, isMissing]) => {
      if (isMissing) {
        recommendations.push({
          skill,
          reason: 'High demand in current job market',
          priority: 'High',
          category: skill === 'Leadership' || skill === 'Communication' ? 'soft' : 'technical'
        });
      }
    });

    return recommendations.slice(0, 5); // Top 5 recommendations
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error || !resume) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Error Loading Resume</h3>
          <p className="text-gray-500 mb-4">{error || 'Resume not found'}</p>
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

  const skills = resume.parsed_data?.skills || [];
  const analysisScore = resume.analysis_score || 0;
  const categorizedSkills = categorizeSkills(skills);
  const recommendations = getSkillRecommendations(skills);

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
                <h1 className="text-xl font-semibold text-gray-900">Skills Analysis</h1>
                <p className="text-sm text-gray-500">{resume.filename}</p>
              </div>
            </div>
            <button
              onClick={() => navigate('/candidate')}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="h-6 w-6" />
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Resume Overview */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-lg font-medium text-gray-900">Resume Overview</h2>
              <p className="text-sm text-gray-500">Analysis completed on {new Date(resume.updated_at).toLocaleDateString()}</p>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-primary-600">{analysisScore.toFixed(1)}%</div>
              <div className="text-sm text-gray-500">Overall Score</div>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="text-2xl font-bold text-gray-900">{skills.length}</div>
              <div className="text-sm text-gray-500">Total Skills</div>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="text-2xl font-bold text-gray-900">
                {skills.filter(skill => getSkillLevel(skill) === 'Expert').length}
              </div>
              <div className="text-sm text-gray-500">Expert Level</div>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="text-2xl font-bold text-gray-900">
                {Object.keys(categorizedSkills).filter(cat => categorizedSkills[cat].length > 0).length}
              </div>
              <div className="text-sm text-gray-500">Skill Categories</div>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="text-2xl font-bold text-gray-900">{recommendations.length}</div>
              <div className="text-sm text-gray-500">Recommendations</div>
            </div>
          </div>
        </div>

        {/* Skills by Category */}
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6 mb-8">
          {Object.entries(categorizedSkills).map(([category, categorySkills]) => {
            if (categorySkills.length === 0) return null;
            
            return (
              <div key={category} className="bg-white rounded-lg shadow-sm border h-80 flex flex-col">
                <div className={`p-4 border-b ${getCategoryColor(category)} flex-shrink-0`}>
                  <div className="flex items-center space-x-2">
                    {getCategoryIcon(category)}
                    <h3 className="text-lg font-medium capitalize">{category} Skills</h3>
                    <span className="bg-white bg-opacity-50 px-2 py-1 rounded-full text-xs font-medium">
                      {categorySkills.length}
                    </span>
                  </div>
                </div>
                
                <div className="flex-1 overflow-hidden relative">
                  <div className="h-full overflow-y-auto p-4 space-y-3 scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100">
                    {categorySkills.map((skill, index) => {
                      const level = getSkillLevel(skill);
                      const colorClass = getSkillColor(level);
                      const icon = getSkillIcon(level);
                      
                      return (
                        <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg flex-shrink-0">
                          <div className="flex items-center space-x-3 min-w-0 flex-1">
                            <div className={`p-1.5 rounded ${colorClass} flex-shrink-0`}>
                              {icon}
                            </div>
                            <div className="min-w-0 flex-1">
                              <h4 className="text-sm font-medium text-gray-900 capitalize truncate">
                                {typeof skill === 'string' ? skill : skill.name || skill.skill}
                              </h4>
                            </div>
                          </div>
                          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${colorClass} flex-shrink-0 ml-2`}>
                            {level}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                  
                  {/* Scroll indicator */}
                  {categorySkills.length > 3 && (
                    <div className="absolute bottom-2 right-2 bg-gray-800 bg-opacity-75 text-white text-xs px-2 py-1 rounded-full">
                      {categorySkills.length} skills
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Skill Recommendations */}
        {recommendations.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm border mb-8">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center space-x-2">
                <Lightbulb className="h-5 w-5 text-yellow-600" />
                <h3 className="text-lg font-medium text-gray-900">Skill Recommendations</h3>
              </div>
              <p className="text-sm text-gray-500 mt-1">Skills that could boost your profile</p>
            </div>
            
            <div className="p-6">
              <div className="space-y-4">
                {recommendations.map((rec, index) => (
                  <div key={index} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className="p-2 bg-yellow-100 rounded-lg">
                        <Award className="h-4 w-4 text-yellow-600" />
                      </div>
                      <div>
                        <h4 className="text-sm font-medium text-gray-900">{rec.skill}</h4>
                        <p className="text-xs text-gray-500">{rec.reason}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                        {rec.priority} Priority
                      </span>
                      <span className="text-xs text-gray-500 capitalize">{rec.category}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Skills Strength Analysis */}
        <div className="bg-white rounded-lg shadow-sm border mb-8">
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center space-x-2">
              <BarChart3 className="h-5 w-5 text-blue-600" />
              <h3 className="text-lg font-medium text-gray-900">Skills Strength Analysis</h3>
            </div>
            <p className="text-sm text-gray-500 mt-1">Your skill distribution and areas of expertise</p>
          </div>
          
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="text-sm font-medium text-gray-900 mb-3">Skill Level Distribution</h4>
                <div className="space-y-2">
                  {['Expert', 'Advanced', 'Intermediate', 'Beginner'].map(level => {
                    const count = skills.filter(skill => getSkillLevel(skill) === level).length;
                    const percentage = skills.length > 0 ? (count / skills.length) * 100 : 0;
                    
                    return (
                      <div key={level} className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">{level}</span>
                        <div className="flex items-center space-x-2">
                          <div className="w-24 bg-gray-200 rounded-full h-2">
                            <div 
                              className={`h-2 rounded-full ${getSkillColor(level).split(' ')[0]}`}
                              style={{ width: `${percentage}%` }}
                            ></div>
                          </div>
                          <span className="text-xs text-gray-500 w-8">{count}</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
              
              <div>
                <h4 className="text-sm font-medium text-gray-900 mb-3">Category Breakdown</h4>
                <div className="space-y-2">
                  {Object.entries(categorizedSkills).map(([category, categorySkills]) => {
                    if (categorySkills.length === 0) return null;
                    const percentage = skills.length > 0 ? (categorySkills.length / skills.length) * 100 : 0;
                    
                    return (
                      <div key={category} className="flex items-center justify-between">
                        <span className="text-sm text-gray-600 capitalize">{category}</span>
                        <div className="flex items-center space-x-2">
                          <div className="w-24 bg-gray-200 rounded-full h-2">
                            <div 
                              className={`h-2 rounded-full ${getCategoryColor(category).split(' ')[0]}`}
                              style={{ width: `${percentage}%` }}
                            ></div>
                          </div>
                          <span className="text-xs text-gray-500 w-8">{categorySkills.length}</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-center space-x-4">
          <button
            onClick={() => navigate('/candidate')}
            className="btn btn-secondary"
          >
            Back to Dashboard
          </button>
          <button
            onClick={() => navigate('/candidate/skills')}
            className="btn btn-primary"
          >
            Get Skill Suggestions
          </button>
        </div>
      </div>
    </div>
  );
};

export default SkillsAnalysis;
