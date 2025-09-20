import React from 'react';
import { useQuery } from 'react-query';
import { 
  AlertTriangle, 
  Users, 
  TrendingUp, 
  Shield, 
  BarChart3,
  Eye,
  CheckCircle,
  XCircle
} from 'lucide-react';
import { advancedFeaturesAPI } from '../services/api';

const BiasDashboard = () => {
  const { data: biasReport, isLoading } = useQuery(
    'bias-report',
    () => advancedFeaturesAPI.getBiasReport(30)
  );

  const { data: biasDashboard, isLoading: dashboardLoading } = useQuery(
    'bias-dashboard',
    () => advancedFeaturesAPI.getBiasDashboard()
  );

  if (isLoading || dashboardLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const getBiasLevel = (rate) => {
    if (rate < 0.05) return { level: 'Low', color: 'text-green-600 bg-green-100' };
    if (rate < 0.15) return { level: 'Medium', color: 'text-yellow-600 bg-yellow-100' };
    return { level: 'High', color: 'text-red-600 bg-red-100' };
  };

  const biasLevel = getBiasLevel(biasReport?.bias_detection_rate || 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Bias Detection Dashboard</h1>
          <p className="text-gray-600">Monitor and analyze potential bias in candidate evaluation</p>
        </div>
        <div className="flex items-center space-x-2">
          <Shield className="h-6 w-6 text-primary-600" />
          <span className="text-sm font-medium text-gray-700">Ethical AI Monitoring</span>
        </div>
      </div>

      {/* Bias Alert */}
      {biasReport?.requires_attention && (
        <div className="card bg-red-50 border-red-200">
          <div className="card-content">
            <div className="flex items-center">
              <AlertTriangle className="h-5 w-5 text-red-600" />
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-900">Bias Alert</h3>
                <p className="text-sm text-red-800">
                  High bias detection rate detected. Review evaluation criteria and consider implementing bias mitigation measures.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Key Metrics */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <div className="card">
          <div className="card-content">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Users className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Candidates</p>
                <p className="text-2xl font-semibold text-gray-900">{biasReport?.total_candidates || 0}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-content">
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <TrendingUp className="h-6 w-6 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Bias Detection Rate</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {((biasReport?.bias_detection_rate || 0) * 100).toFixed(1)}%
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-content">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                <BarChart3 className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Average Bias Score</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {((biasReport?.average_bias_score || 0) * 100).toFixed(1)}%
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-content">
            <div className="flex items-center">
              <div className={`p-2 rounded-lg ${biasLevel.color}`}>
                <Shield className="h-6 w-6" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Bias Level</p>
                <p className="text-2xl font-semibold text-gray-900">{biasLevel.level}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Bias Types Analysis */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-gray-900">Bias Types Analysis</h3>
        </div>
        <div className="card-content">
          {biasReport?.bias_types && Object.keys(biasReport.bias_types).length > 0 ? (
            <div className="space-y-4">
              {Object.entries(biasReport.bias_types).map(([biasType, count]) => (
                <div key={biasType} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                  <div className="flex items-center">
                    <AlertTriangle className="h-5 w-5 text-orange-500 mr-3" />
                    <div>
                      <h4 className="text-sm font-medium text-gray-900 capitalize">{biasType} Bias</h4>
                      <p className="text-sm text-gray-500">{count} instances detected</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="text-sm font-medium text-gray-900">
                      {((count / (biasReport.total_candidates || 1)) * 100).toFixed(1)}%
                    </span>
                    <p className="text-xs text-gray-500">of candidates</p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <CheckCircle className="h-12 w-12 text-green-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Bias Detected</h3>
              <p className="text-gray-500">Great job! No significant bias patterns detected in recent evaluations.</p>
            </div>
          )}
        </div>
      </div>

      {/* Recommendations */}
      {biasReport?.recommendations && biasReport.recommendations.length > 0 && (
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900">Bias Mitigation Recommendations</h3>
          </div>
          <div className="card-content">
            <div className="space-y-3">
              {biasReport.recommendations.map((recommendation, index) => (
                <div key={index} className="flex items-start">
                  <div className="flex-shrink-0">
                    <div className="w-2 h-2 bg-primary-600 rounded-full mt-2"></div>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm text-gray-700">{recommendation}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Historical Trends */}
      {biasDashboard?.bias_reports && (
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900">Historical Bias Trends</h3>
          </div>
          <div className="card-content">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
              {biasDashboard.bias_reports.map((report, index) => (
                <div key={index} className="p-4 border border-gray-200 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="text-sm font-medium text-gray-900">{report.period_days} Days</h4>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      report.report.bias_detection_rate > 0.15 
                        ? 'bg-red-100 text-red-800' 
                        : report.report.bias_detection_rate > 0.05
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-green-100 text-green-800'
                    }`}>
                      {((report.report.bias_detection_rate || 0) * 100).toFixed(1)}%
                    </span>
                  </div>
                  <p className="text-sm text-gray-600">
                    {report.report.total_candidates || 0} candidates analyzed
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    Avg Score: {((report.report.average_bias_score || 0) * 100).toFixed(1)}%
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="card bg-blue-50 border-blue-200">
        <div className="card-content">
          <h3 className="text-lg font-medium text-blue-900 mb-2">Bias Mitigation Actions</h3>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div className="flex items-center">
              <Eye className="h-5 w-5 text-blue-600 mr-3" />
              <div>
                <h4 className="text-sm font-medium text-blue-900">Blind Resume Screening</h4>
                <p className="text-sm text-blue-800">Remove names and demographic indicators from initial screening</p>
              </div>
            </div>
            <div className="flex items-center">
              <CheckCircle className="h-5 w-5 text-blue-600 mr-3" />
              <div>
                <h4 className="text-sm font-medium text-blue-900">Structured Evaluation</h4>
                <p className="text-sm text-blue-800">Use standardized criteria for all candidate evaluations</p>
              </div>
            </div>
            <div className="flex items-center">
              <Users className="h-5 w-5 text-blue-600 mr-3" />
              <div>
                <h4 className="text-sm font-medium text-blue-900">Diverse Review Panels</h4>
                <p className="text-sm text-blue-800">Include diverse perspectives in evaluation panels</p>
              </div>
            </div>
            <div className="flex items-center">
              <Shield className="h-5 w-5 text-blue-600 mr-3" />
              <div>
                <h4 className="text-sm font-medium text-blue-900">Regular Audits</h4>
                <p className="text-sm text-blue-800">Conduct regular bias audits and training sessions</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BiasDashboard;
