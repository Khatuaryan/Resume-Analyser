import React from 'react';
import { useQuery } from 'react-query';
import { 
  TrendingUp, 
  Target, 
  BookOpen, 
  ExternalLink,
  CheckCircle,
  AlertCircle,
  Lightbulb,
  BarChart3
} from 'lucide-react';
import { skillsAPI } from '../services/api';

const SkillSuggestions = () => {
  const { data: recommendations, isLoading: recommendationsLoading } = useQuery(
    'skill-recommendations',
    skillsAPI.getSkillRecommendations,
    {
      retry: false,
      onError: (error) => {
        console.error('Failed to load recommendations:', error);
      }
    }
  );

  const { data: marketTrends, isLoading: trendsLoading } = useQuery(
    'market-trends',
    skillsAPI.getMarketTrends
  );

  const { data: gapAnalysis, isLoading: gapLoading } = useQuery(
    'skill-gap-analysis',
    skillsAPI.getSkillGapAnalysis
  );

  if (recommendationsLoading || trendsLoading || gapLoading) {
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
        <h1 className="text-2xl font-bold text-gray-900">Skill Development</h1>
        <p className="text-gray-600">Get personalized skill recommendations and learning paths</p>
      </div>

      {/* Skill Recommendations */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-gray-900">Personalized Recommendations</h3>
        </div>
        <div className="card-content">
          {recommendations ? (
            <div className="space-y-6">
              {/* Recommended Skills */}
              <div>
                <h4 className="text-md font-medium text-gray-900 mb-3">Recommended Skills</h4>
                <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
                  {recommendations.recommended_skills?.slice(0, 9).map((skill, index) => (
                    <div key={skill} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                      <div className="flex items-center">
                        <Target className="h-4 w-4 text-primary-600 mr-2" />
                        <span className="text-sm font-medium text-gray-900">{skill}</span>
                      </div>
                      <span className="text-xs text-gray-500">
                        #{index + 1}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Reasoning */}
              {recommendations.reasoning && recommendations.reasoning.length > 0 && (
                <div>
                  <h4 className="text-md font-medium text-gray-900 mb-3">Why These Skills?</h4>
                  <div className="space-y-2">
                    {recommendations.reasoning.map((reason, index) => (
                      <div key={index} className="flex items-start">
                        <Lightbulb className="h-4 w-4 text-yellow-500 mr-2 mt-0.5 flex-shrink-0" />
                        <p className="text-sm text-gray-700">{reason}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Learning Resources */}
              {recommendations.learning_resources && Object.keys(recommendations.learning_resources).length > 0 && (
                <div>
                  <h4 className="text-md font-medium text-gray-900 mb-3">Learning Resources</h4>
                  <div className="space-y-4">
                    {Object.entries(recommendations.learning_resources).slice(0, 3).map(([skill, resources]) => (
                      <div key={skill} className="border border-gray-200 rounded-lg p-4">
                        <h5 className="text-sm font-medium text-gray-900 mb-2">{skill}</h5>
                        <ul className="space-y-1">
                          {resources.slice(0, 3).map((resource, index) => (
                            <li key={index} className="flex items-start">
                              <BookOpen className="h-3 w-3 text-gray-400 mr-2 mt-1 flex-shrink-0" />
                              <span className="text-xs text-gray-600">{resource}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-8">
              <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No recommendations available</h3>
              <p className="text-gray-500">Upload and process your resume to get personalized skill recommendations.</p>
            </div>
          )}
        </div>
      </div>

      {/* Market Trends */}
      {marketTrends && (
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900">Market Trends</h3>
          </div>
          <div className="card-content">
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
              {/* Top Skills */}
              <div>
                <h4 className="text-md font-medium text-gray-900 mb-3">Most In-Demand Skills</h4>
                <div className="space-y-2">
                  {marketTrends.top_skills?.slice(0, 5).map((skill, index) => (
                    <div key={skill.skill} className="flex items-center justify-between">
                      <span className="text-sm text-gray-700">{skill.skill}</span>
                      <span className="text-xs text-gray-500">{skill.count} jobs</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Top Locations */}
              <div>
                <h4 className="text-md font-medium text-gray-900 mb-3">Popular Locations</h4>
                <div className="space-y-2">
                  {marketTrends.top_locations?.slice(0, 5).map((location, index) => (
                    <div key={location.location} className="flex items-center justify-between">
                      <span className="text-sm text-gray-700">{location.location}</span>
                      <span className="text-xs text-gray-500">{location.count} jobs</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Job Types */}
              <div>
                <h4 className="text-md font-medium text-gray-900 mb-3">Job Types</h4>
                <div className="space-y-2">
                  {marketTrends.top_job_types?.slice(0, 5).map((jobType, index) => (
                    <div key={jobType.job_type} className="flex items-center justify-between">
                      <span className="text-sm text-gray-700">{jobType.job_type.replace('_', ' ')}</span>
                      <span className="text-xs text-gray-500">{jobType.count} jobs</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Skill Gap Analysis */}
      {gapAnalysis && (
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900">Skill Gap Analysis</h3>
          </div>
          <div className="card-content">
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
              {/* Current Skills */}
              <div>
                <h4 className="text-md font-medium text-gray-900 mb-3">Your Current Skills</h4>
                <div className="flex flex-wrap gap-2">
                  {gapAnalysis.current_skills?.map((skill, index) => (
                    <span key={index} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      <CheckCircle className="h-3 w-3 mr-1" />
                      {skill}
                    </span>
                  ))}
                </div>
              </div>

              {/* Missing Skills */}
              <div>
                <h4 className="text-md font-medium text-gray-900 mb-3">Skills to Develop</h4>
                <div className="space-y-2">
                  {gapAnalysis.missing_skills?.slice(0, 10).map((skill, index) => (
                    <div key={skill.skill} className="flex items-center justify-between p-2 border border-gray-200 rounded">
                      <span className="text-sm text-gray-700">{skill.skill}</span>
                      <span className="text-xs text-gray-500">{skill.frequency} jobs</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Learning Paths */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-gray-900">Learning Paths</h3>
        </div>
        <div className="card-content">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {['Python', 'JavaScript', 'SQL', 'Git', 'Communication'].map((skill) => (
              <div key={skill} className="border border-gray-200 rounded-lg p-4">
                <h4 className="text-sm font-medium text-gray-900 mb-2">{skill}</h4>
                <div className="space-y-2">
                  <div className="text-xs text-gray-600">
                    <span className="font-medium">Beginner:</span> Learn basics and fundamentals
                  </div>
                  <div className="text-xs text-gray-600">
                    <span className="font-medium">Intermediate:</span> Build projects and practice
                  </div>
                  <div className="text-xs text-gray-600">
                    <span className="font-medium">Advanced:</span> Master concepts and teach others
                  </div>
                </div>
                <button className="mt-3 text-xs text-primary-600 hover:text-primary-500 font-medium">
                  View Learning Path →
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Tips */}
      <div className="card bg-blue-50 border-blue-200">
        <div className="card-content">
          <h3 className="text-lg font-medium text-blue-900 mb-2">Skill Development Tips</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Focus on 2-3 skills at a time to avoid overwhelm</li>
            <li>• Practice regularly with real projects</li>
            <li>• Join online communities and forums</li>
            <li>• Consider getting certifications for in-demand skills</li>
            <li>• Update your resume as you learn new skills</li>
            <li>• Network with professionals in your field</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default SkillSuggestions;
