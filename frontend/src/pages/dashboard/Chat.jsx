import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useChatStore } from '../../store/chatStore';
import { chatAPI } from '../../services/api';
import ReactMarkdown from 'react-markdown';
import toast from 'react-hot-toast';
import {
  HiPaperAirplane,
  HiMicrophone,
  HiStop,
  HiPhotograph,
  HiPaperClip,
  HiDotsVertical,
  HiTrash,
  HiRefresh,
  HiLightBulb,
  HiChevronLeft,
  HiPlus,
} from 'react-icons/hi';

const Chat = () => {
  const [input, setInput] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [showSidebar, setShowSidebar] = useState(true);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  
  const {
    messages,
    sessions,
    currentSessionId,
    isTyping,
    addMessage,
    setMessages,
    setTyping,
    setCurrentSession,
    clearMessages,
  } = useChatStore();

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Suggested prompts
  const suggestions = [
    "What are my bank balances today?",
    "Show me my stock portfolio performance",
    "Search flights from Toronto to Dubai next month",
    "Export my weekly transactions for the accountant",
    "Find legal cases about contract disputes in Canada",
  ];

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = {
      role: 'user',
      content: input,
    };

    addMessage(userMessage);
    setInput('');
    setTyping(true);

    try {
      const response = await chatAPI.sendMessage({
        message: input,
        session_id: currentSessionId,
        use_tools: true,
        use_memory: true,
      });

      addMessage({
        role: 'assistant',
        content: response.data.response,
        tool_calls: response.data.tool_calls,
        sources: response.data.sources,
      });
    } catch (error) {
      toast.error('Failed to get response');
      addMessage({
        role: 'assistant',
        content: "I apologize, but I encountered an error. Please try again.",
      });
    } finally {
      setTyping(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setInput(suggestion);
    inputRef.current?.focus();
  };

  const startNewChat = () => {
    clearMessages();
    setCurrentSession(null);
  };

  return (
    <div className="flex h-[calc(100vh-8rem)] -m-4 lg:-m-8">
      {/* Chat Sessions Sidebar */}
      <AnimatePresence>
        {showSidebar && (
          <motion.div
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: 280, opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            className="hidden md:flex flex-col border-r border-slate-800 bg-slate-900/50"
          >
            <div className="p-4 border-b border-slate-800">
              <button
                onClick={startNewChat}
                className="btn-primary w-full flex items-center justify-center gap-2"
              >
                <HiPlus className="w-5 h-5" />
                New Chat
              </button>
            </div>
            <div className="flex-1 overflow-y-auto p-4 space-y-2">
              {sessions.length === 0 ? (
                <p className="text-slate-500 text-sm text-center py-4">
                  No chat history yet
                </p>
              ) : (
                sessions.map((session) => (
                  <button
                    key={session.id}
                    onClick={() => setCurrentSession(session.id)}
                    className={`w-full p-3 rounded-xl text-left transition-colors ${
                      currentSessionId === session.id
                        ? 'bg-primary-500/20 border border-primary-500/30'
                        : 'hover:bg-slate-800'
                    }`}
                  >
                    <p className="text-sm text-slate-200 truncate">{session.title || 'Chat Session'}</p>
                    <p className="text-xs text-slate-500">{session.date}</p>
                  </button>
                ))
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col bg-slate-900/30">
        {/* Chat Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <button
              className="md:hidden text-slate-400 hover:text-white"
              onClick={() => setShowSidebar(!showSidebar)}
            >
              <HiChevronLeft className="w-6 h-6" />
            </button>
            <div>
              <h2 className="text-lg font-semibold text-white">AI Assistant</h2>
              <p className="text-xs text-slate-400">Always here to help</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={startNewChat}
              className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
              title="New chat"
            >
              <HiRefresh className="w-5 h-5" />
            </button>
            <button
              className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
              title="More options"
            >
              <HiDotsVertical className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full">
              <div className="w-20 h-20 mb-6 rounded-2xl bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center">
                <HiLightBulb className="w-10 h-10 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">How can I help you today?</h3>
              <p className="text-slate-400 text-center mb-8 max-w-md">
                I can help with banking, stocks, travel bookings, legal research, and much more.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-2xl">
                {suggestions.map((suggestion, index) => (
                  <button
                    key={index}
                    onClick={() => handleSuggestionClick(suggestion)}
                    className="p-4 text-left rounded-xl border border-slate-700 hover:border-primary-500/50 hover:bg-slate-800/50 transition-all group"
                  >
                    <p className="text-slate-300 group-hover:text-white text-sm">
                      {suggestion}
                    </p>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <>
              {messages.map((message, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={
                      message.role === 'user'
                        ? 'chat-message-user'
                        : 'chat-message-assistant'
                    }
                  >
                    <ReactMarkdown className="prose prose-invert prose-sm max-w-none">
                      {message.content}
                    </ReactMarkdown>
                    
                    {/* Tool calls */}
                    {message.tool_calls && message.tool_calls.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-slate-700">
                        <p className="text-xs text-slate-400 mb-2">Actions taken:</p>
                        {message.tool_calls.map((tool, i) => (
                          <div key={i} className="badge-secondary text-xs mr-2">
                            {tool.tool}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </motion.div>
              ))}
              
              {/* Typing indicator */}
              {isTyping && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex justify-start"
                >
                  <div className="chat-message-assistant">
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                      <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                      <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                    </div>
                  </div>
                </motion.div>
              )}
              
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input Area */}
        <div className="p-4 border-t border-slate-800">
          <div className="flex items-end gap-3 max-w-4xl mx-auto">
            {/* Attachment button */}
            <button className="p-3 text-slate-400 hover:text-white hover:bg-slate-800 rounded-xl transition-colors">
              <HiPaperClip className="w-5 h-5" />
            </button>

            {/* Input */}
            <div className="flex-1 relative">
              <textarea
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask me anything..."
                rows={1}
                className="w-full px-4 py-3 pr-12 bg-slate-800/50 border border-slate-700 rounded-xl text-slate-100 placeholder-slate-400 focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500 resize-none"
                style={{ minHeight: '48px', maxHeight: '120px' }}
              />
            </div>

            {/* Voice button */}
            <button
              onClick={() => setIsRecording(!isRecording)}
              className={`p-3 rounded-xl transition-colors ${
                isRecording
                  ? 'bg-red-500 text-white'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              {isRecording ? <HiStop className="w-5 h-5" /> : <HiMicrophone className="w-5 h-5" />}
            </button>

            {/* Send button */}
            <button
              onClick={handleSend}
              disabled={!input.trim() || isTyping}
              className="p-3 bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-500 hover:to-primary-600 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-xl transition-all"
            >
              <HiPaperAirplane className="w-5 h-5 transform rotate-90" />
            </button>
          </div>
          
          <p className="text-center text-xs text-slate-500 mt-3">
            Salim AI can make mistakes. Consider checking important information.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Chat;
