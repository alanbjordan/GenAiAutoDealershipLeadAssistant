import React from 'react';
import AnalyticsCard from './AnalyticsCard';

const AnalyticsSummary = ({ data }) => {
  return (
    <div className="analytics-summary">
      <AnalyticsCard 
        title="Cost" 
        value={`$${data.totalCost.toFixed(4)}`} 
        subtitle={`Avg: $${data.averageCostPerRequest.toFixed(4)}/req`} 
      />
      <AnalyticsCard 
        title="Requests" 
        value={data.totalRequests} 
      />
      <AnalyticsCard 
        title="Sent Tokens" 
        value={data.totalSentTokens.toLocaleString()} 
      />
      <AnalyticsCard 
        title="Received Tokens" 
        value={data.totalReceivedTokens.toLocaleString()} 
      />
    </div>
  );
};

export default AnalyticsSummary;
