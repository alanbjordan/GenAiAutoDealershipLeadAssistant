import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { motion, AnimatePresence } from 'framer-motion';
import { format } from 'date-fns';
import apiClient from '../utils/apiClient';
import VideoModal from './VideoModal';
import InventoryDisplay from './InventoryDisplay';
import './Chat.css';
import { useNavigate } from 'react-router-dom';

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
  const [summary, setSummary] = useState(null);
  const [showSummary, setShowSummary] = useState(false);
  const [isSummaryExpanded, setIsSummaryExpanded] = useState(false);
  const [isVideoModalOpen, setIsVideoModalOpen] = useState(false);
  const [videoResults, setVideoResults] = useState([]);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const navigate = useNavigate();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, summary]);

  useEffect(() => {
    if (!loading && !toolCallInProgress && inputRef.current) {
      inputRef.current.focus();
    }
  }, [loading, toolCallInProgress]);

  // Add new effect to handle delayed summary display
  useEffect(() => {
    if (summary) {
      const timer = setTimeout(() => {
        setShowSummary(true);
      }, 2000); // 2 second delay
      return () => clearTimeout(timer);
    }
  }, [summary]);

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
      const { chat_response, conversation_history: updatedHistory, tool_call_detected, summary: newSummary } = response.data;
      
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
        const { final_response, final_conversation_history, summary: toolCallSummary } = toolCallResponse.data;
        
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
        
        // Check if a summary was generated
        if (toolCallSummary) {
          setSummary(toolCallSummary);
          setShowSummary(true);
        }
      } else {
        // No tool call, just add the response as a message
        const botMessage = { 
          id: generateUniqueId(), 
          sender: 'bot', 
          text: chat_response,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, botMessage]);
        
        // Check if a summary was generated
        if (newSummary) {
          setSummary(newSummary);
          setShowSummary(true);
        }
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

  // Function to handle car review video requests
  const handleCarReviewRequest = async (carMake, carModel, year = null) => {
    try {
      setLoading(true);
      console.log(`Requesting car review videos for ${carMake} ${carModel}${year ? ` ${year}` : ''}`);
      
      const response = await apiClient.post('/car-review-videos', {
        car_make: carMake,
        car_model: carModel,
        year: year
      });
      
      console.log('Car review videos response:', response.data);
      
      if (response.data.videos && response.data.videos.length > 0) {
        console.log(`Found ${response.data.videos.length} videos`);
        setVideoResults(response.data.videos);
        setIsVideoModalOpen(true);
      } else {
        console.log('No videos found in response');
        // Add a message if no videos were found
        const noVideosMessage = { 
          id: generateUniqueId(), 
          sender: 'bot', 
          text: `I couldn't find any review videos for the ${carMake} ${carModel}${year ? ` ${year}` : ''}.${response.data.error ? ` Error: ${response.data.error}` : ''}`,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, noVideosMessage]);
      }
    } catch (error) {
      console.error("Error fetching car review videos:", error);
      const errorMessage = { 
        id: generateUniqueId(), 
        sender: 'bot', 
        text: `Sorry, I encountered an error while searching for car review videos: ${error.message || 'Unknown error'}`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  // Function to render message content with action buttons
  const renderMessageContent = (message) => {
    // Check if the message contains car information that might be of interest
    const carInfoRegex = /(?:interested in|looking at|considering|thinking about|want to see|want to know more about) (?:a|an) (\d{4})? ?([A-Za-z]+) ([A-Za-z0-9]+)/i;
    const match = message.text.match(carInfoRegex);
    
    if (match && message.sender === 'user') {
      const year = match[1] ? parseInt(match[1]) : null;
      const make = match[2];
      const model = match[3];
      
      return (
        <div>
          <ReactMarkdown>{message.text}</ReactMarkdown>
          <div className="action-buttons">
            <button 
              className="action-button"
              onClick={() => handleCarReviewRequest(make, model, year)}
            >
              Watch {make} {model} Review Videos
            </button>
          </div>
        </div>
      );
    }
    
    return <ReactMarkdown>{message.text}</ReactMarkdown>;
  };

  const handleAnalyticsClick = () => {
    navigate('/analytics');
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h2>Nissan of Hendersonville Chat</h2>
        <div className="header-buttons">
          <InventoryDisplay />
          <button 
            className="analytics-button"
            onClick={handleAnalyticsClick}
          >
            View Analytics
          </button>
        </div>
      </div>
      
      {showSummary && summary && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="summary-container"
        >
          <div 
            className="summary-header"
            onClick={() => setIsSummaryExpanded(!isSummaryExpanded)}
          >
            <h3>Conversation Summary</h3>
            <div className={`dropdown-arrow ${isSummaryExpanded ? 'expanded' : ''}`}>
              <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M2 4L6 8L10 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
          </div>
          
          {isSummaryExpanded && (
            <div className="summary-content">
              <div className="summary-section">
                <h4>Sentiment</h4>
                <p className={`sentiment ${summary.sentiment}`}>{summary.sentiment}</p>
              </div>
              
              <div className="summary-section">
                <h4>Keywords</h4>
                <div className="keywords">
                  {summary.keywords.map((keyword, index) => (
                    <span key={index} className="keyword-tag">{keyword}</span>
                  ))}
                </div>
              </div>
              
              <div className="summary-section">
                <h4>Summary</h4>
                <p>{summary.summary}</p>
              </div>
              
              <div className="summary-section">
                <h4>Recommended Department</h4>
                <p className="department">{summary.department}</p>
              </div>
              
              <div className="summary-section">
                <h4>Additional Insights</h4>
                <ul>
                  <li><strong>Urgency:</strong> {summary.insights.urgency}</li>
                  <li><strong>Upsell Opportunity:</strong> {summary.insights.upsell_opportunity ? 'Yes' : 'No'}</li>
                  <li><strong>Customer Interest:</strong> {summary.insights.customer_interest}</li>
                  {summary.insights.additional_notes && (
                    <li><strong>Notes:</strong> {summary.insights.additional_notes}</li>
                  )}
                </ul>
              </div>
            </div>
          )}
        </motion.div>
      )}
      
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
                {renderMessageContent(msg)}
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

      {/* Video Modal */}
      <VideoModal 
        isOpen={isVideoModalOpen}
        onClose={() => setIsVideoModalOpen(false)}
        videos={videoResults}
      />
    </div>
  );
};

export default Chat;
