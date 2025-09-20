import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { 
  Brain, 
  Target, 
  TrendingUp, 
  Shield, 
  Globe, 
  Eye,
  AlertTriangle,
  CheckCircle,
  BarChart3,
  Lightbulb,
  Users,
  Award
} from 'lucide-react';
import { advancedFeaturesAPI } from '../services/api';
import toast from 'react-hot-toast';

const EnhancedCandidateAnalysis = ({ candidateId, jobId }) => {
  const [selectedTab, setSelectedTab] = useState('overview');
  const queryClient = useQueryClient();

  const { data: candidateData, isLoading } = useQuery(
    ['candidate-analysis', candidateId, jobId],
    () => advancedFeaturesAPI.getEnhancedCandidateAnalysis(candidateId, jobId)
  );

  const { data: biasAnalysis, isLoading: biasLoading } = useQuery(
    ['bias-analysis', candidateId],
    () => advancedFeaturesAPI.analyzeCandidateBias(candidateId),
    { enabled: !!candidateId }
  );

  const tabs = [
    { id: 'overview', name: 'Overview', icon: BarChart3 },
    { id: 'ai-analysis', name: 'AI Analysis', icon: Brain },
    { id: 'bias-detection', name: 'Bias Detection', icon: Shield },
    { id: 'ontology', name: 'Skill Ontology', icon: Target },
    { id: 'multilingual', name: 'Language', icon: Globe }
  ];

  if (isLoading || biasLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const renderOverview = () => (
    <div className="space-y-6">
      {/* Overall Score */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-gray-900">Overall Assessment</h3>
        </div>
        <div className="card-content">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Enhanced AI Score</p>
              <p className="text-3xl font-bold text-gray-900">
                {candidateData?.overall_score || 0}%
              </p>
            </div>
            <div className="text-right">
              <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                (candidateData?.overall_score || 0) >= 80 
                  ? 'bg-green-100 text-green-800' 
                  : (candidateData?.overall_score || 0) >= 60
                  ? 'bg-yellow-100 text-yellow-800'
                  : 'bg-red-100 text-red-800'
              }`}>
                {(candidateData?.overall_score || 0) >= 80 ? 'Excellent' : 
                 (candidateData?.overall_score || 0) >= 60 ? 'Good' : 'Needs Review'}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Individual Scores */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-gray-900">Scoring Breakdown</h3>
        </div>
        <div className="card-content">
          <div className="space-y-4">
            {candidateData?.individual_scores && Object.entries(candidateData.individual_scores).map(([method, score]) => (
              <div key={method} className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-primary-600 rounded-full mr-3"></div>
                  <span className="text-sm font-medium text-gray-900 capitalize">
                    {method.replace('_', ' ')}
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-32 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-primary-600 h-2 rounded-full" 
                      style={{ width: `${score.overall_score || 0}%` }}
                    ></div>
                  </div>
                  <span className="text-sm font-medium text-gray-900 w-12">
                    {score.overall_score || 0}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Features Used */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-gray-900">Analysis Features</h3>
        </div>
        <div className="card-content">
          <div className="flex flex-wrap gap-2">
            {candidateData?.features_used?.map((feature) => (
              <span key={feature} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                {feature.replace('_', ' ')}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  const renderAIAnalysis = () => (
    <div className="space-y-6">
      {/* LLM Analysis */}
      {candidateData?.llm_analysis && (
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900">AI-Powered Analysis</h3>
          </div>
          <div className="card-content">
            {candidateData.llm_analysis.contextual_analysis && (
              <div className="space-y-4">
                <div>
                  <h4 className="text-sm font-medium text-gray-900">Overall Assessment</h4>
                  <p className="text-sm text-gray-700 mt-1">
                    {candidateData.llm_analysis.contextual_analysis.overall_assessment}
                  </p>
                </div>
                
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <div>
                    <h4 className="text-sm font-medium text-gray-900">Strengths</h4>
                    <ul className="mt-2 space-y-1">
                      {candidateData.llm_analysis.contextual_analysis.strengths?.map((strength, index) => (
                        <li key={index} className="flex items-start">
                          <CheckCircle className="h-4 w-4 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                          <span className="text-sm text-gray-700">{strength}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  <div>
                    <h4 className="text-sm font-medium text-gray-900">Areas for Improvement</h4>
                    <ul className="mt-2 space-y-1">
                      {candidateData.llm_analysis.contextual_analysis.weaknesses?.map((weakness, index) => (
                        <li key={index} className="flex items-start">
                          <AlertTriangle className="h-4 w-4 text-orange-500 mr-2 mt-0.5 flex-shrink-0" />
                          <span className="text-sm text-gray-700">{weakness}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                {candidateData.llm_analysis.contextual_analysis.interview_questions && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-900">Suggested Interview Questions</h4>
                    <ul className="mt-2 space-y-1">
                      {candidateData.llm_analysis.contextual_analysis.interview_questions.map((question, index) => (
                        <li key={index} className="flex items-start">
                          <Lightbulb className="h-4 w-4 text-blue-500 mr-2 mt-0.5 flex-shrink-0" />
                          <span className="text-sm text-gray-700">{question}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );

  const renderBiasDetection = () => (
    <div className="space-y-6">
      {biasAnalysis?.bias_detected ? (
        <div className="card bg-red-50 border-red-200">
          <div className="card-header">
            <h3 className="text-lg font-medium text-red-900">Bias Indicators Detected</h3>
          </div>
          <div className="card-content">
            <div className="space-y-4">
              {Object.entries(biasAnalysis.bias_indicators).map(([biasType, indicator]) => (
                <div key={biasType} className="flex items-center justify-between p-3 bg-white rounded-lg border border-red-200">
                  <div className="flex items-center">
                    <AlertTriangle className="h-5 w-5 text-red-500 mr-3" />
                    <div>
                      <h4 className="text-sm font-medium text-gray-900 capitalize">{biasType} Bias</h4>
                      <p className="text-sm text-gray-500">Confidence: {(indicator.confidence * 100).toFixed(1)}%</p>
                    </div>
                  </div>
                  <span className="text-sm font-medium text-red-600">Detected</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <div className="card bg-green-50 border-green-200">
          <div className="card-content">
            <div className="flex items-center">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <div className="ml-3">
                <h3 className="text-sm font-medium text-green-900">No Bias Detected</h3>
                <p className="text-sm text-green-800">This candidate evaluation appears to be free of bias indicators.</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {biasAnalysis?.recommendations && biasAnalysis.recommendations.length > 0 && (
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900">Bias Mitigation Recommendations</h3>
          </div>
          <div className="card-content">
            <ul className="space-y-2">
              {biasAnalysis.recommendations.map((recommendation, index) => (
                <li key={index} className="flex items-start">
                  <div className="flex-shrink-0">
                    <div className="w-2 h-2 bg-primary-600 rounded-full mt-2"></div>
                  </div>
                  <p className="ml-3 text-sm text-gray-700">{recommendation}</p>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );

  const renderOntology = () => (
    <div className="space-y-6">
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-gray-900">Skill Ontology Analysis</h3>
        </div>
        <div className="card-content">
          <p className="text-sm text-gray-600 mb-4">
            Advanced semantic analysis of candidate skills using knowledge graph technology.
          </p>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-900">Ontology Score</span>
              <span className="text-sm font-medium text-gray-900">
                {candidateData?.individual_scores?.ontology?.ontology_score || 0}%
              </span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-900">Semantic Matches</span>
              <span className="text-sm font-medium text-gray-900">
                {candidateData?.individual_scores?.ontology?.semantic_matches?.length || 0}
              </span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-900">Skill Gaps</span>
              <span className="text-sm font-medium text-gray-900">
                {candidateData?.individual_scores?.ontology?.skill_gaps?.length || 0}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderMultilingual = () => (
    <div className="space-y-6">
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-gray-900">Multilingual Analysis</h3>
        </div>
        <div className="card-content">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-900">Detected Language</span>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                {candidateData?.detected_language || 'en'}
              </span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-900">Translation Applied</span>
              <span className="text-sm text-gray-600">
                {candidateData?.detected_language !== 'en' ? 'Yes' : 'No'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Enhanced Candidate Analysis</h1>
        <p className="text-gray-600">Comprehensive AI-powered candidate evaluation with advanced features</p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setSelectedTab(tab.id)}
                className={`flex items-center py-2 px-1 border-b-2 font-medium text-sm ${
                  selectedTab === tab.id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="h-4 w-4 mr-2" />
                {tab.name}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div>
        {selectedTab === 'overview' && renderOverview()}
        {selectedTab === 'ai-analysis' && renderAIAnalysis()}
        {selectedTab === 'bias-detection' && renderBiasDetection()}
        {selectedTab === 'ontology' && renderOntology()}
        {selectedTab === 'multilingual' && renderMultilingual()}
      </div>
    </div>
  );
};

export default EnhancedCandidateAnalysis;
