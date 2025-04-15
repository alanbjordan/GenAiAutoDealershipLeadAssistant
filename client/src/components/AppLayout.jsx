import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Chat from './Chat';
import Analytics from './Analytics';

const AppLayout = () => {
  return (
    <Routes>
      <Route path="/" element={<Chat />} />
      <Route path="/analytics" element={<Analytics />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

export default AppLayout; 