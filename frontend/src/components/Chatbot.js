import React, { useEffect, useRef, useState } from "react";
import "./Chatbot.css";
import { sendChatMessage } from "../services/apiService";

const starterSuggestions = [
  "Hi",
  "How many datasets are there?",
  "List available datasets",
  "Which dataset mode is active?",
  "What does the graph show?",
  "Which model is active?",
];

const starterMessage = {
  id: 1,
  text: "Hello! What help do you need with Smart AI? You can ask about datasets, charts, device status, predictions, model selection, or cost optimization.",
  sender: "bot",
  timestamp: new Date(),
  suggestions: starterSuggestions,
};

const Chatbot = () => {
  const [messages, setMessages] = useState([starterMessage]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const messagesEndRef = useRef(null);
  
  const initialSession = window.localStorage.getItem("smart-ai-chat-session") || `session-${Date.now()}`;
  const [currentSessionId, setCurrentSessionId] = useState(initialSession);
  
  const [savedSessions, setSavedSessions] = useState(() => {
    try {
      const stored = window.localStorage.getItem("smart-ai-saved-sessions");
      return stored ? JSON.parse(stored) : [initialSession];
    } catch (e) {
      return [initialSession];
    }
  });

  const activeSuggestions = messages[messages.length - 1]?.suggestions || starterSuggestions;

  useEffect(() => {
    window.localStorage.setItem("smart-ai-chat-session", currentSessionId);
    if (!savedSessions.includes(currentSessionId)) {
      const updated = [currentSessionId, ...savedSessions].slice(0, 10);
      setSavedSessions(updated);
      window.localStorage.setItem("smart-ai-saved-sessions", JSON.stringify(updated));
    }
  }, [currentSessionId, savedSessions]);

  const startNewChat = () => {
    const newSession = `session-${Date.now()}`;
    setCurrentSessionId(newSession);
    setMessages([starterMessage]);
    setShowHistory(false);
  };

  const loadSession = (sid) => {
    setCurrentSessionId(sid);
    setMessages([starterMessage]); // Note: In a full app, we'd fetch the history from backend here. But starting fresh locally visually is fine for a demo, or the backend will still retain context!
    setShowHistory(false);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const renderMessage = (text) => {
    const lines = String(text || "").split("\n");
    return lines.map((line, index) => {
      const trimmed = line.trim();
      if (!trimmed) {
        return <div key={index} className="message-spacer" />;
      }
      if (trimmed.startsWith("- ")) {
        return (
          <div key={index} className="message-bullet">
            <span className="message-bullet-mark">•</span>
            <span>{trimmed.slice(2)}</span>
          </div>
        );
      }
      if (trimmed.endsWith(":")) {
        return (
          <div key={index} className="message-heading">
            {trimmed}
          </div>
        );
      }
      return (
        <div key={index} className="message-line">
          {trimmed}
        </div>
      );
    });
  };

  const pushMessage = (text, sender, suggestions = undefined) => {
    setMessages((prev) => [
      ...prev,
      {
        id: prev.length + 1,
        text,
        sender,
        timestamp: new Date(),
        suggestions,
      },
    ]);
  };

  const sendMessage = async (e, overrideMessage = null) => {
    if (e && typeof e.preventDefault === "function") {
      e.preventDefault();
    }
    const trimmed = (overrideMessage ?? inputMessage).trim();
    if (!trimmed || trimmed.length > 300) {
      return;
    }

    pushMessage(trimmed, "user");
    setInputMessage("");
    setIsLoading(true);

    try {
      const savedProfile = window.localStorage.getItem("smart-ai-profile");
      const profile = savedProfile ? JSON.parse(savedProfile) : null;
      const data = await sendChatMessage(trimmed, {
        sessionId: currentSessionId,
        userName: profile?.name || "",
      });
      pushMessage(
        data?.response || "I could not generate a reply right now.",
        "bot",
        data?.suggestions || starterSuggestions
      );
    } catch (error) {
      pushMessage(`Sorry, I encountered an error: ${error.message}.`, "bot", starterSuggestions);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <button className="chatbot-toggle" onClick={() => setIsOpen(!isOpen)} title="Help Bot">
        {isOpen ? "x" : "Chat"}
      </button>

      {isOpen && (
        <div className="chatbot-container">
          <div className="chatbot-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <button onClick={() => setShowHistory(!showHistory)} style={{ background: 'none', border: 'none', color: 'white', cursor: 'pointer', fontSize: '1.2rem', padding: '0' }} title="Chat History">≡</button>
              <h3 style={{ margin: 0 }}>Help Bot</h3>
            </div>
            <div className="chatbot-controls" style={{ display: 'flex', gap: '8px' }}>
              <button onClick={startNewChat} style={{ background: 'rgba(255,255,255,0.2)', border: 'none', color: 'white', borderRadius: '4px', padding: '4px 8px', cursor: 'pointer', fontSize: '0.8rem' }} title="New Chat">+ New</button>
              <button onClick={() => setMessages([starterMessage])} style={{ background: 'transparent', border: 'none', color: 'white', cursor: 'pointer' }} title="Clear Chat">Clear</button>
              <button onClick={() => setIsOpen(false)} style={{ background: 'transparent', border: 'none', color: 'white', cursor: 'pointer', fontWeight: 'bold' }} title="Close">X</button>
            </div>
          </div>

          {showHistory && (
            <div style={{ position: 'absolute', top: '50px', left: 0, width: '200px', bottom: 0, background: '#f8fafc', borderRight: '1px solid #e2e8f0', zIndex: 10, padding: '10px', overflowY: 'auto' }}>
              <h4 style={{ margin: '0 0 10px 0', color: '#0f4c81', fontSize: '0.9rem' }}>Recent Chats</h4>
              {savedSessions.map(sid => (
                <div key={sid} onClick={() => loadSession(sid)} style={{ padding: '8px', margin: '4px 0', background: sid === currentSessionId ? '#e0f2fe' : 'white', border: '1px solid #bae6fd', borderRadius: '6px', cursor: 'pointer', fontSize: '0.8rem', color: '#334155' }}>
                  Chat {new Date(parseInt(sid.split('-')[1])).toLocaleDateString()}
                </div>
              ))}
            </div>
          )}

          <div className="chatbot-messages">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`message ${message.sender === "user" ? "user-message" : "bot-message"}`}
              >
                <div className="message-content">
                  {renderMessage(message.text)}
                </div>
                <div className="message-timestamp">{message.timestamp.toLocaleTimeString()}</div>
              </div>
            ))}

            {isLoading && (
              <div className="message bot-message">
                <div className="message-content">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          <form className="chatbot-input-form" onSubmit={sendMessage}>
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Ask Help Bot about your energy project..."
              disabled={isLoading}
              className="chatbot-input"
              maxLength={300}
            />
            <button
              type="submit"
              disabled={isLoading || !inputMessage.trim()}
              className="chatbot-send-button"
            >
              {isLoading ? "..." : "Send"}
            </button>
          </form>

          <div className="chatbot-suggestions">
            <p>Try asking:</p>
            <div className="suggestion-buttons">
              {activeSuggestions.map((suggestion) => (
                <button
                  key={suggestion}
                  type="button"
                  onClick={() => {
                    setInputMessage(suggestion);
                    sendMessage(null, suggestion);
                  }}
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default Chatbot;
