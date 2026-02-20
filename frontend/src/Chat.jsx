import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Send, Paperclip, X, Loader2, MessageSquare } from 'lucide-react';
import './Chat.css';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);

    const formData = new FormData();
    formData.append('question', input);
    if (file) formData.append('pdf_file', file);

    try {
      const response = await axios.post('http://localhost:8000/api/chat', formData);
      
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: response.data.answer 
      }]);
      
    } catch (error) {
      setMessages(prev => [...prev, { role: 'assistant', content: "Connection Error." }]);
    } finally {
      setLoading(false);
      setInput("");
    }
  };

  return (
    <div className="chat-container">
      <header className="chat-header">
        <h1><MessageSquare size={22} /> AI Assistant</h1>
        {file && (
          <div className="attached-file-badge">
            <Paperclip size={14} /> {file.name.slice(0,15)}...
            <X size={14} onClick={() => setFile(null)} className="clear-file" />
          </div>
        )}
      </header>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="welcome-screen">
            <h2>How can I help you today?</h2>
            <p>Chat normally or attach a PDF to ask specific questions.</p>
          </div>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`message-wrapper ${msg.role}`}>
            <div className="message-bubble">{msg.content}</div>
          </div>
        ))}
        {loading && <Loader2 className="spinner center" />}
        <div ref={scrollRef} />
      </div>

      <footer className="chat-footer">
        <form onSubmit={handleSendMessage} className="question-form">
          <label className="attach-btn">
            <Paperclip size={20} />
            <input 
              type="file" 
              accept=".pdf" 
              hidden 
              onChange={(e) => setFile(e.target.files[0])} 
            />
          </label>
          <input 
            className="question-input"
            placeholder="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
          <button className="send-button" type="submit" disabled={loading || !input.trim()}>
            <Send size={18} />
          </button>
        </form>
      </footer>
    </div>
  );
};

export default ChatInterface;