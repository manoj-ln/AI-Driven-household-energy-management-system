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
  const messagesEndRef = useRef(null);
  const sessionIdRef = useRef(window.localStorage.getItem("smart-ai-chat-session") || `session-${Date.now()}`);

  const activeSuggestions = messages[messages.length - 1]?.suggestions || starterSuggestions;

  useEffect(() => {
    window.localStorage.setItem("smart-ai-chat-session", sessionIdRef.current);
  }, []);

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
        sessionId: sessionIdRef.current,
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
          <div className="chatbot-header">
            <h3>Help Bot</h3>
            <div className="chatbot-controls">
              <button onClick={() => setMessages([starterMessage])} title="Clear Chat">Clear</button>
              <button onClick={() => setIsOpen(false)} title="Close">x</button>
            </div>
          </div>

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
