import './App.css';
import { BrowserRouter } from 'react-router-dom';
import AppLayout from './components/AppLayout';

function App() {
  return (
    <BrowserRouter>
      <div className="App">
        <AppLayout />
      </div>
    </BrowserRouter>
  );
}

export default App;