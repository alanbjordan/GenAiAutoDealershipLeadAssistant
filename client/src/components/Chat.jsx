import React, { useState } from 'react';
import './Chat.css';

const Chat = () => {
  // Sample initial message from the bot
  const [messages, setMessages] = useState([
    { id: 1, sender: 'bot', text: 'Hello! How can I help you today?' }
  ]);
  const [inputText, setInputText] = useState('');

  // Handle sending a new message
  const handleSend = (e) => {
    e.preventDefault();
    if (!inputText.trim()) return;

    // Append new user message
    const newMessage = {
      id: messages.length + 1,
      sender: 'user',
      text: inputText
    };
    setMessages([...messages, newMessage]);
    setInputText('');

    // (Optional) Simulate a bot response after a slight delay
    setTimeout(() => {
      setMessages((msgs) => [
        ...msgs,
        { id: msgs.length + 1, sender: 'bot', text: 'Thanks for your message!' }
      ]);
    }, 500);
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
            <p>{msg.text}</p>
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
        />
        <button type="submit" className="chat-send-button">
          Send
        </button>
      </form>
    </div>
  );
};

export default Chat;
