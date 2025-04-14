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
  const [loading, setLoading] = useState(false);
  const [isPolling, setIsPolling] = useState(false);
  const pollingIntervalRef = useRef(null);
  const lastDataRef = useRef(null);

  // Function to fetch analytics data
  const fetchAnalyticsData = async (isInitialFetch = false) => {
    try {
      if (isInitialFetch) {
        setLoading(true);
      }
      
      const response = await apiClient.get('/analytics/summary');
      const newData = response.data;
      
      // If this is the initial fetch, just set the data
      if (isInitialFetch) {
        setAnalyticsData(newData);
        lastDataRef.current = newData;
        setError(null);
      } else {
        // For polling updates, compare with previous data and update only what changed
        updateAnalyticsDataSmoothly(newData);
      }
    } catch (err) {
      console.error('Error fetching analytics data:', err);
      if (isInitialFetch) {
        setError('Failed to load analytics data. Please try again later.');
      }
    } finally {
      if (isInitialFetch) {
        setLoading(false);
      }
    }
  };

  // Function to smoothly update analytics data
  const updateAnalyticsDataSmoothly = (newData) => {
    if (!lastDataRef.current) {
      setAnalyticsData(newData);
      lastDataRef.current = newData;
      return;
    }

    // Check if there are any changes
    const hasChanges = JSON.stringify(newData) !== JSON.stringify(lastDataRef.current);
    
    if (hasChanges) {
      // Update the data with the new values
      setAnalyticsData(newData);
      lastDataRef.current = newData;
    }
  };

  const handleReset = async () => {
    try {
      // Immediately clear the data without showing loading state
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

  const handleDownload = async () => {
    try {
      // Create a temporary link element
      const link = document.createElement('a');
      link.href = `${process.env.REACT_APP_API_URL || ''}/api/analytics/download`;
      link.setAttribute('download', ''); // This will use the filename from the server
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err) {
      console.error('Error downloading report:', err);
      setError('Failed to download report. Please try again later.');
    }
  };

  // Start polling for updates
  const startPolling = () => {
    if (!isPolling) {
      setIsPolling(true);
      pollingIntervalRef.current = setInterval(() => {
        fetchAnalyticsData(false);
      }, 5000); // Poll every 5 seconds
    }
  };

  // Stop polling
  const stopPolling = () => {
    if (isPolling && pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
      setIsPolling(false);
    }
  };

  // Initial fetch and setup polling
  useEffect(() => {
    // Initial fetch
    fetchAnalyticsData(true);
    
    // Start polling
    startPolling();
    
    // Cleanup on unmount
    return () => {
      stopPolling();
    };
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
            className="download-button"
            onClick={handleDownload}
          >
            Download Report
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
        {loading ? (
          <>
            <div className="analytics-summary skeleton">
              <div className="analytics-card skeleton-card"></div>
              <div className="analytics-card skeleton-card"></div>
              <div className="analytics-card skeleton-card"></div>
              <div className="analytics-card skeleton-card"></div>
            </div>
            <div className="analytics-table skeleton">
              <div className="skeleton-table-header"></div>
              <div className="skeleton-table-row"></div>
              <div className="skeleton-table-row"></div>
              <div className="skeleton-table-row"></div>
              <div className="skeleton-table-row"></div>
            </div>
          </>
        ) : (
          <>
            <AnalyticsSummary data={analyticsData} />
            <AnalyticsTable requests={analyticsData.requestsByDate} />
          </>
        )}
      </div>
    </div>
  );
};

export default Analytics;
