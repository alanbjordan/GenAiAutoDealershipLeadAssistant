import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import apiClient from '../utils/api'; // Adjust the import path as necessary
import './Chat.css';

const Chat = () => {
  // The initial state contains an initial greeting from the bot.
  const [messages, setMessages] = useState([
    { id: 1, sender: 'bot', text: 'Hello! How can I help you today?' }
  ]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);

  // Function to send a message to the server and update chat with the bot response
  const handleSend = async (e) => {
    e.preventDefault();
    
    // Do nothing if the input field is empty or just whitespace.
    if (!inputText.trim()) return;

    // Append the user message to the chat state
    const userMessage = { id: messages.length + 1, sender: 'user', text: inputText };
    setMessages(prevMessages => [...prevMessages, userMessage]);

    // Preserve the current user input and reset the input field
    const userInput = inputText;
    setInputText('');
    setLoading(true);

    try {
      // Call the chat endpoint on your server, sending the user's message in the body
      const response = await apiClient.post('/chat', { message_content: userInput });
      
      // Extract the chat response from the server response (ensure your server's response contains this property)
      const botMessageText = response.data.chat_response;
      
      // Append the bot's response to the chat messages
      const botMessage = { id: messages.length + 2, sender: 'bot', text: botMessageText };
      setMessages(prevMessages => [...prevMessages, botMessage]);
    } catch (error) {
      console.error("Error sending message:", error);
      // Provide an error message in the chat if the request fails
      const errorMessage = { id: messages.length + 2, sender: 'bot', text: 'Sorry, something went wrong. Please try again later.' };
      setMessages(prevMessages => [...prevMessages, errorMessage]);
    } finally {
      // Reset the loading state
      setLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h2>Nissan of Hendersonville Chat</h2>
      </div>
      <div className="chat-messages">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`chat-message ${msg.sender === 'user' ? 'user' : 'bot'}`}
          >
            {/* Render message text as Markdown */}
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
          className="chat-input"
          disabled={loading}
        />
        <button type="submit" className="chat-send-button" disabled={loading}>
          {loading ? 'Sending...' : 'Send'}
        </button>
      </form>
    </div>
  );
};

export default Chat;
