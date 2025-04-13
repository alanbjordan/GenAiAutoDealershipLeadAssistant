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

// Function to get current time in EST
const getCurrentTimeInEST = () => {
  try {
    // Create a date object for the current time
    const now = new Date();
    
    // Format the date to EST timezone
    // This uses the browser's timezone conversion capabilities
    const options = { 
      timeZone: 'America/New_York',
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    };
    
    // Format the date according to the options
    const estDate = new Intl.DateTimeFormat('en-US', options).format(now);
    
    // Convert the formatted string to a more readable format
    // The format will be MM/DD/YYYY, HH:MM:SS
    const [datePart, timePart] = estDate.split(', ');
    const [month, day, year] = datePart.split('/');
    
    // Return in the format YYYY-MM-DD HH:MM:SS EST
    return `${year}-${month}-${day} ${timePart} EST`;
  } catch (error) {
    console.error("Error formatting EST time:", error);
    // Fallback to a simpler approach if the Intl API fails
    const now = new Date();
    const estOffset = -5; // EST is UTC-5
    const utc = now.getTime() + (now.getTimezoneOffset() * 60000);
    const est = new Date(utc + (3600000 * estOffset));
    
    return format(est, 'yyyy-MM-dd HH:mm:ss') + ' EST';
  }
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
  const [toolCallInProgress, setToolCallInProgress] = useState(false);
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
    if (!loading && !toolCallInProgress && inputRef.current) {
      inputRef.current.focus();
    }
  }, [loading, toolCallInProgress]);

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
      // Use the stored conversation history if available, otherwise create a new one
      let formattedHistory = conversationHistory.length > 0 
        ? [...conversationHistory] 
        : [];
      
      // Get current time in EST
      const currentTime = getCurrentTimeInEST();
      
      // Add the current time context message
      formattedHistory.push({
        role: "system",
        content: `Current time: ${currentTime}`
      });
      
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
      const { chat_response, conversation_history: updatedHistory, tool_call_detected } = response.data;
      
      // Store the updated conversation history
      setConversationHistory(updatedHistory);

      // Check if a tool call was detected
      if (tool_call_detected) {
        // Set tool call in progress state
        setToolCallInProgress(true);
        
        // Add a message indicating that we're searching inventory
        const searchingMessage = { 
          id: generateUniqueId(), 
          sender: 'bot', 
          text: 'Please wait while I search our inventory.',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, searchingMessage]);
        
        // Wait for the tool call to complete
        const toolCallResponse = await apiClient.post('/tool-call-result', {
          conversation_history: updatedHistory
        });
        
        // Get the final response after the tool call
        const { final_response, final_conversation_history } = toolCallResponse.data;
        
        // Update the conversation history
        setConversationHistory(final_conversation_history);
        
        // Add the final response as a message
        const finalMessage = { 
          id: generateUniqueId(), 
          sender: 'bot', 
          text: final_response,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, finalMessage]);
        
        // Reset the tool call in progress state
        setToolCallInProgress(false);
      } else {
        // No tool call, just add the response as a message
        const botMessage = { 
          id: generateUniqueId(), 
          sender: 'bot', 
          text: chat_response,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, botMessage]);
      }
    } catch (error) {
      console.error("Error sending message:", error);
      const errorMessage = { 
        id: generateUniqueId(), 
        sender: 'bot', 
        text: 'Sorry, something went wrong. Please try again later.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
      setToolCallInProgress(false);
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
        {(loading || toolCallInProgress) && (
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
          disabled={loading || toolCallInProgress}
          className="chat-input"
        />
        <button 
          type="submit" 
          disabled={loading || toolCallInProgress || !inputText.trim()} 
          className={`chat-send-button ${(loading || toolCallInProgress) ? 'loading' : ''}`}
        >
          {loading ? 'Sending...' : toolCallInProgress ? 'Searching...' : 'Send'}
        </button>
      </form>
    </div>
  );
};

export default Chat;
