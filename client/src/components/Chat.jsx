import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import apiClient from '../utils/api';
import './Chat.css';

// A simple function to generate a unique ID.
const generateUniqueId = () => {
  return `${Date.now()}-${Math.floor(Math.random() * 10000)}`;
};

const Chat = () => {
  const [messages, setMessages] = useState([
    { id: generateUniqueId(), sender: 'bot', text: 'Hello! How can I help you today?' }
  ]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  // Store the thread id once received from the server.
  const [threadId, setThreadId] = useState(null);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!inputText.trim()) return;

    const userMessage = { id: generateUniqueId(), sender: 'user', text: inputText };
    setMessages(prev => [...prev, userMessage]);

    const userInput = inputText;
    setInputText('');
    setLoading(true);

    try {
      // Include thread_id if available.
      const payload = threadId 
                      ? { message_content: userInput, thread_id: threadId }
                      : { message_content: userInput };

      const response = await apiClient.post('/chat', payload);
      const { chat_response, thread_id } = response.data;

      // Store the thread_id from the response if available.
      if (thread_id) {
        setThreadId(thread_id);
      }

      const botMessage = { id: generateUniqueId(), sender: 'bot', text: chat_response };
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error("Error sending message:", error);
      const errorMessage = { 
        id: generateUniqueId(), 
        sender: 'bot', 
        text: 'Sorry, something went wrong. Please try again later.' 
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h2>Nissan of Hendersonville Chat</h2>
      </div>
      <div className="chat-messages">
        {messages.map(msg => (
          <div key={msg.id} className={`chat-message ${msg.sender === 'user' ? 'user' : 'bot'}`}>
            <ReactMarkdown>{msg.text}</ReactMarkdown>
          </div>
        ))}
      </div>
      <form className="chat-input-container" onSubmit={handleSend}>
        <input
          type="text"
          placeholder="Type your message here..."
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          disabled={loading}
          className="chat-input"
        />
        <button type="submit" disabled={loading} className="chat-send-button">
          {loading ? 'Sending...' : 'Send'}
        </button>
      </form>
    </div>
  );
};

export default Chat;
