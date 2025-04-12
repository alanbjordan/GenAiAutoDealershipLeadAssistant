import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { motion, AnimatePresence } from 'framer-motion';
import { format } from 'date-fns';
import apiClient from '../utils/api';
import './Chat.css';

// A simple function to generate a unique ID.
const generateUniqueId = () => {
  return `${Date.now()}-${Math.floor(Math.random() * 10000)}`;
};

const TypingIndicator = () => (
  <div className="typing-indicator">
    <span></span>
    <span></span>
    <span></span>
  </div>
);

const Chat = () => {
  const [messages, setMessages] = useState([
    { 
      id: generateUniqueId(), 
      sender: 'bot', 
      text: 'Hello! How can I help you today?',
      timestamp: new Date()
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationHistory, setConversationHistory] = useState([]);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (!loading && inputRef.current) {
      inputRef.current.focus();
    }
  }, [loading]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!inputText.trim()) return;

    const userMessage = { 
      id: generateUniqueId(), 
      sender: 'user', 
      text: inputText,
      timestamp: new Date()
    };
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

      const botMessage = { 
        id: generateUniqueId(), 
        sender: 'bot', 
        text: chat_response,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error("Error sending message:", error);
      const errorMessage = { 
        id: generateUniqueId(), 
        sender: 'bot', 
        text: 'Sorry, something went wrong. Please try again later.',
        timestamp: new Date()
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
        <AnimatePresence>
          {messages.map(msg => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className={`chat-message ${msg.sender === 'user' ? 'user' : 'bot'}`}
            >
              <div className="message-content">
                <ReactMarkdown>{msg.text}</ReactMarkdown>
              </div>
              <div className="message-timestamp">
                {format(msg.timestamp, 'h:mm a')}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        {loading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="chat-message bot"
          >
            <TypingIndicator />
          </motion.div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <form className="chat-input-container" onSubmit={handleSend}>
        <input
          ref={inputRef}
          type="text"
          placeholder="Type your message here..."
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          disabled={loading}
          className="chat-input"
        />
        <button 
          type="submit" 
          disabled={loading || !inputText.trim()} 
          className={`chat-send-button ${loading ? 'loading' : ''}`}
        >
          {loading ? 'Sending...' : 'Send'}
        </button>
      </form>
    </div>
  );
};

export default Chat;
