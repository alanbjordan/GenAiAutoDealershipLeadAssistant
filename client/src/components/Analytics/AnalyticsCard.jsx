import React from 'react';

const AnalyticsCard = ({ title, value, subtitle }) => {
  return (
    <div className="analytics-card">
      <h4>{title}</h4>
      <p className="analytics-value">{value}</p>
      {subtitle && <small>{subtitle}</small>}
    </div>
  );
};

export default AnalyticsCard;
