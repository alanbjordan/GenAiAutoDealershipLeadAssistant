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
  const [conversationHistory, setConversationHistory] = useState([]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!inputText.trim()) return;

    const userMessage = { id: generateUniqueId(), sender: 'user', text: inputText };
    setMessages(prev => [...prev, userMessage]);

    const userInput = inputText;
    setInputText('');
    setLoading(true);

    try {
      // Convert messages to the format expected by the backend
      const formattedHistory = messages.map(msg => ({
        role: msg.sender === 'user' ? 'user' : 'assistant',
        content: msg.text
      }));

      // Add the current message to the history
      formattedHistory.push({
        role: 'user',
        content: userInput
      });

      const payload = {
        message: userInput,
        conversation_history: formattedHistory
      };

      const response = await apiClient.post('/chat', payload);
      const { chat_response, conversation_history: updatedHistory } = response.data;

      // Update the conversation history from the server
      setConversationHistory(updatedHistory);

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
