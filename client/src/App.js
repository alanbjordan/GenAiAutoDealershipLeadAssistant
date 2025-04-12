import logo from './logo.svg';
import './App.css';
import Dashboard from './components/Dashboard'; // Example import; can be removed if not used
import Chat from './components/Chat/Chat';

function App() {
  return (
    <div className="App">
      {/* Render the Chat component */}
      <Chat />
    </div>
  );
}

export default App;
