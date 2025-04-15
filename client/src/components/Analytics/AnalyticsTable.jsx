import React from 'react';

const AnalyticsTable = ({ requests }) => {
  return (
    <div className="analytics-table">
      <h3>Recent Requests</h3>
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Model</th>
            <th>Sent</th>
            <th>Recv</th>
            <th>Total</th>
            <th>Cost</th>
          </tr>
        </thead>
        <tbody>
          {requests.slice(0, 10).map((request, index) => {
            // Ensure cost is a number
            const cost = typeof request.cost === 'number' ? request.cost : 0;
            
            return (
              <tr key={index}>
                <td>{request.date}</td>
                <td>{request.model}</td>
                <td>{request.sentTokens.toLocaleString()}</td>
                <td>{request.receivedTokens.toLocaleString()}</td>
                <td>{(request.sentTokens + request.receivedTokens).toLocaleString()}</td>
                <td>${cost.toFixed(4)}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

export default AnalyticsTable;
