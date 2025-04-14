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
      <div className="analytics-header">
        <h1>LLM Analytics Dashboard</h1>
      </div>
      
      <div className="analytics-content">
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

        <div className="analytics-table">
          <h2>Recent Requests</h2>
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Model</th>
                <th>Tokens</th>
                <th>Cost</th>
              </tr>
            </thead>
            <tbody>
              {analyticsData.requestsByDate.slice(0, 10).map((request, index) => (
                <tr key={index}>
                  <td>{request.date}</td>
                  <td>{request.model}</td>
                  <td>{request.tokens}</td>
                  <td>${request.cost.toFixed(4)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Analytics; 