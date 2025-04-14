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
      <h2>LLM Analytics</h2>
      <div className="analytics-content">
        <AnalyticsSummary data={analyticsData} />
        <AnalyticsTable requests={analyticsData.requestsByDate} />
      </div>
    </div>
  );
};

export default Analytics;
