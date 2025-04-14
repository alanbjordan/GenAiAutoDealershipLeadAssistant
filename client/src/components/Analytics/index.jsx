import React, { useState, useEffect } from 'react';
import AnalyticsSummary from './AnalyticsSummary';
import AnalyticsTable from './AnalyticsTable';
import apiClient from '../../utils/apiClient';
import './Analytics.css';

const Analytics = () => {
  const [analyticsData, setAnalyticsData] = useState({
    totalCost: 0,
    totalRequests: 0,
    averageCostPerRequest: 0,
    totalSentTokens: 0,
    totalReceivedTokens: 0,
    requestsByDate: [],
    costByModel: {}
  });
  const [error, setError] = useState(null);
  const [showResetConfirm, setShowResetConfirm] = useState(false);

  const fetchAnalyticsData = async () => {
    try {
      const response = await apiClient.get('/analytics/summary');
      setAnalyticsData(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching analytics data:', err);
      setError('Failed to load analytics data. Please try again later.');
    }
  };

  const handleReset = async () => {
    try {
      await apiClient.post('/analytics/reset');
      // Reset the local state
      setAnalyticsData({
        totalCost: 0,
        totalRequests: 0,
        averageCostPerRequest: 0,
        totalSentTokens: 0,
        totalReceivedTokens: 0,
        requestsByDate: [],
        costByModel: {}
      });
      setShowResetConfirm(false);
    } catch (err) {
      console.error('Error resetting analytics data:', err);
      setError('Failed to reset analytics data. Please try again later.');
    }
  };

  useEffect(() => {
    // Initial fetch
    fetchAnalyticsData();
    
    // Set up polling interval (every 30 seconds)
    const interval = setInterval(fetchAnalyticsData, 30000);
    
    // Cleanup interval on component unmount
    return () => clearInterval(interval);
  }, []);

  if (error) {
    return (
      <div className="analytics-container">
        <h2>LLM Analytics</h2>
        <div className="error">{error}</div>
      </div>
    );
  }

  return (
    <div className="analytics-container">
      <div className="analytics-header">
        <h2>LLM Analytics</h2>
        <button 
          className="reset-button"
          onClick={() => setShowResetConfirm(true)}
        >
          Reset Data
        </button>
      </div>

      {showResetConfirm && (
        <div className="reset-confirm-dialog">
          <div className="reset-confirm-content">
            <h3>Reset Analytics Data</h3>
            <p>Are you sure you want to reset all analytics data? This action cannot be undone.</p>
            <div className="reset-confirm-buttons">
              <button 
                className="cancel-button"
                onClick={() => setShowResetConfirm(false)}
              >
                Cancel
              </button>
              <button 
                className="confirm-button"
                onClick={handleReset}
              >
                Reset Data
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="analytics-content">
        <AnalyticsSummary data={analyticsData} />
        <AnalyticsTable requests={analyticsData.requestsByDate} />
      </div>
    </div>
  );
};

export default Analytics;
