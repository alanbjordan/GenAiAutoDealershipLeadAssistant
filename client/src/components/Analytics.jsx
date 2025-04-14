import React, { useState, useEffect } from 'react';
import './Analytics.css';

const Analytics = () => {
  const [analyticsData, setAnalyticsData] = useState({
    totalCost: 0,
    totalRequests: 0,
    averageCostPerRequest: 0,
    requestsByDate: [],
    costByModel: {}
  });

  useEffect(() => {
    // TODO: Fetch analytics data from backend
    // This will be implemented when we add the backend endpoint
  }, []);

  return (
    <div className="analytics-container">
      <h1>LLM Analytics Dashboard</h1>
      
      <div className="analytics-summary">
        <div className="analytics-card">
          <h3>Total Cost</h3>
          <p className="analytics-value">${analyticsData.totalCost.toFixed(4)}</p>
        </div>
        <div className="analytics-card">
          <h3>Total Requests</h3>
          <p className="analytics-value">{analyticsData.totalRequests}</p>
        </div>
        <div className="analytics-card">
          <h3>Average Cost/Request</h3>
          <p className="analytics-value">${analyticsData.averageCostPerRequest.toFixed(4)}</p>
        </div>
      </div>

      <div className="analytics-details">
        <div className="analytics-section">
          <h2>Cost by Date</h2>
          <div className="analytics-chart">
            {/* TODO: Add chart component */}
            <p>Chart will be implemented here</p>
          </div>
        </div>

        <div className="analytics-section">
          <h2>Cost by Model</h2>
          <div className="analytics-chart">
            {/* TODO: Add chart component */}
            <p>Chart will be implemented here</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics; 