import React, { useState, useEffect } from 'react';
import AnalyticsSummary from './AnalyticsSummary';
import AnalyticsTable from './AnalyticsTable';
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

  useEffect(() => {
    // TODO: Fetch analytics data from backend
    // This will be implemented when we add the backend endpoint
  }, []);

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
