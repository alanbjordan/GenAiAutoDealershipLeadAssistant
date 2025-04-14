// client/src/components/Analytics/index.jsx

import React, { useState, useEffect, useRef } from 'react';
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
  const lastDataRef = useRef(null);

  // Function to fetch analytics data
  const fetchAnalyticsData = async () => {
    try {
      const response = await apiClient.get('/analytics/summary');
      const newData = response.data;
      setAnalyticsData(newData);
      lastDataRef.current = newData;
      setError(null);
    } catch (err) {
      console.error('Error fetching analytics data:', err);
      setError('Failed to load analytics data. Please try again later.');
    }
  };

  const handleReset = async () => {
    try {
      // Immediately clear the data
      const emptyData = {
        totalCost: 0,
        totalRequests: 0,
        averageCostPerRequest: 0,
        totalSentTokens: 0,
        totalReceivedTokens: 0,
        requestsByDate: [],
        costByModel: {}
      };
      
      // Update the UI immediately with empty data
      setAnalyticsData(emptyData);
      lastDataRef.current = emptyData;
      setShowResetConfirm(false);
      
      // Then make the API call in the background
      const response = await apiClient.post('/analytics/reset');
      
      // Update with the actual reset data from the server
      if (response.data && response.data.analytics) {
        setAnalyticsData(response.data.analytics);
        lastDataRef.current = response.data.analytics;
      }
    } catch (err) {
      console.error('Error resetting analytics data:', err);
      setError('Failed to reset analytics data. Please try again later.');
    }
  };

  // Initial fetch
  useEffect(() => {
    fetchAnalyticsData();
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
        <h2>Model Analytics</h2>
        <div className="header-buttons">
          <button 
            className="fetch-button"
            onClick={fetchAnalyticsData}
          >
            Fetch Data
          </button>
          <button 
            className="reset-button"
            onClick={() => setShowResetConfirm(true)}
          >
            Reset Data
          </button>
        </div>
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
