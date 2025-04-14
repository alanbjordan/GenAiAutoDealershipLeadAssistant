import './App.css';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Chat from './components/Chat';
import Analytics from './components/Analytics';

function App() {
  return (
    <BrowserRouter>
      <div className="App">
        <Routes>
          <Route path="/" element={<Chat />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;