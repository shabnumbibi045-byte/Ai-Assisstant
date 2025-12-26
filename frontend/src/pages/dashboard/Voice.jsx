import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import {
  HiMicrophone,
  HiStop,
  HiCog,
  HiVolumeUp,
  HiTranslate,
  HiClock,
  HiSparkles,
  HiChat,
} from 'react-icons/hi';

const Voice = () => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [aiResponse, setAiResponse] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [selectedVoice, setSelectedVoice] = useState('alloy');
  const [selectedLanguage, setSelectedLanguage] = useState('en');
  const [volume, setVolume] = useState(80);
  const [history, setHistory] = useState([
    { id: 1, type: 'user', text: 'What are my banking balances?', time: '10:30 AM' },
    { id: 2, type: 'ai', text: 'Your total balance across all accounts is $140,920.50. TD Canada Trust has $15,420.50...', time: '10:30 AM' },
    { id: 3, type: 'user', text: 'Send an email to John about the meeting', time: '10:35 AM' },
    { id: 4, type: 'ai', text: 'I\'ve drafted an email to John Smith regarding the meeting. Would you like me to send it?', time: '10:35 AM' },
  ]);

  const canvasRef = useRef(null);
  const animationRef = useRef(null);

  const voices = [
    { id: 'alloy', name: 'Alloy', description: 'Neutral & balanced' },
    { id: 'echo', name: 'Echo', description: 'Deep & resonant' },
    { id: 'fable', name: 'Fable', description: 'British accent' },
    { id: 'onyx', name: 'Onyx', description: 'Deep & authoritative' },
    { id: 'nova', name: 'Nova', description: 'Warm & friendly' },
    { id: 'shimmer', name: 'Shimmer', description: 'Clear & expressive' },
  ];

  const languages = [
    { code: 'en', name: 'English' },
    { code: 'es', name: 'Spanish' },
    { code: 'fr', name: 'French' },
    { code: 'de', name: 'German' },
    { code: 'sw', name: 'Swahili' },
  ];

  // Audio visualization
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    const animate = () => {
      ctx.clearRect(0, 0, width, height);

      if (isListening || isSpeaking) {
        const bars = 40;
        const barWidth = width / bars - 2;

        for (let i = 0; i < bars; i++) {
          const barHeight = isListening
            ? Math.random() * height * 0.8 + height * 0.1
            : (Math.sin(Date.now() / 100 + i) + 1) * height * 0.3 + height * 0.2;

          const gradient = ctx.createLinearGradient(0, height - barHeight, 0, height);
          gradient.addColorStop(0, '#7c3aed');
          gradient.addColorStop(1, '#06b6d4');

          ctx.fillStyle = gradient;
          ctx.fillRect(i * (barWidth + 2), height - barHeight, barWidth, barHeight);
        }
      } else {
        // Idle wave
        ctx.beginPath();
        ctx.moveTo(0, height / 2);
        for (let i = 0; i < width; i++) {
          const y = height / 2 + Math.sin(i / 30 + Date.now() / 1000) * 10;
          ctx.lineTo(i, y);
        }
        ctx.strokeStyle = '#475569';
        ctx.lineWidth = 2;
        ctx.stroke();
      }

      animationRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isListening, isSpeaking]);

  const handleStartListening = () => {
    setIsListening(true);
    setTranscript('');
    toast.success('Listening...');

    // Simulate speech recognition
    setTimeout(() => {
      setTranscript('Check my TD Canada Trust account balance');
    }, 2000);

    setTimeout(() => {
      handleStopListening();
    }, 3000);
  };

  const handleStopListening = async () => {
    setIsListening(false);
    setIsProcessing(true);

    // Simulate AI processing
    await new Promise(r => setTimeout(r, 1500));

    const response = 'Your TD Canada Trust checking account has a balance of $15,420.50 CAD. The account is up 2.3% this month.';
    setAiResponse(response);
    setIsProcessing(false);

    // Add to history
    setHistory(prev => [
      ...prev,
      { id: Date.now(), type: 'user', text: transcript || 'Check my TD Canada Trust account balance', time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) },
      { id: Date.now() + 1, type: 'ai', text: response, time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) },
    ]);

    // Simulate text-to-speech
    setIsSpeaking(true);
    setTimeout(() => {
      setIsSpeaking(false);
    }, 4000);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-display font-bold text-white">Voice Assistant</h1>
          <p className="text-slate-400">Interact with your AI assistant using voice commands</p>
        </div>
        <div className="flex items-center gap-3">
          <button className="btn-ghost flex items-center gap-2 border border-slate-700">
            <HiClock className="w-5 h-5" />
            History
          </button>
          <button className="btn-ghost flex items-center gap-2 border border-slate-700">
            <HiCog className="w-5 h-5" />
            Settings
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Voice Interface */}
        <div className="lg:col-span-2 space-y-6">
          {/* Voice Control Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="card bg-gradient-to-br from-slate-800/80 to-slate-900/80"
          >
            {/* Visualization */}
            <div className="relative h-40 mb-6 rounded-xl overflow-hidden bg-slate-900/50">
              <canvas
                ref={canvasRef}
                width={600}
                height={160}
                className="w-full h-full"
              />
              <AnimatePresence>
                {isProcessing && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="absolute inset-0 flex items-center justify-center bg-slate-900/80"
                  >
                    <div className="flex items-center gap-3">
                      <HiSparkles className="w-6 h-6 text-primary-400 animate-pulse" />
                      <span className="text-white">Processing...</span>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Microphone Button */}
            <div className="flex justify-center mb-6">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={isListening ? handleStopListening : handleStartListening}
                className={`w-24 h-24 rounded-full flex items-center justify-center transition-all ${
                  isListening
                    ? 'bg-red-500 shadow-lg shadow-red-500/30'
                    : 'bg-gradient-to-br from-primary-500 to-secondary-500 shadow-lg shadow-primary-500/30'
                }`}
              >
                {isListening ? (
                  <HiStop className="w-10 h-10 text-white" />
                ) : (
                  <HiMicrophone className="w-10 h-10 text-white" />
                )}
              </motion.button>
            </div>

            <p className="text-center text-slate-400 mb-6">
              {isListening ? 'Listening... Click to stop' : 'Click to start speaking'}
            </p>

            {/* Transcript */}
            {transcript && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="p-4 rounded-xl bg-slate-800/50 mb-4"
              >
                <p className="text-xs text-slate-500 mb-1">You said:</p>
                <p className="text-white">{transcript}</p>
              </motion.div>
            )}

            {/* AI Response */}
            {aiResponse && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="p-4 rounded-xl bg-primary-500/10 border border-primary-500/20"
              >
                <div className="flex items-center gap-2 mb-2">
                  <HiSparkles className="w-4 h-4 text-primary-400" />
                  <p className="text-xs text-primary-400">AI Response:</p>
                  {isSpeaking && (
                    <HiVolumeUp className="w-4 h-4 text-primary-400 animate-pulse ml-auto" />
                  )}
                </div>
                <p className="text-white">{aiResponse}</p>
              </motion.div>
            )}
          </motion.div>

          {/* Quick Commands */}
          <div className="card">
            <h3 className="text-lg font-semibold text-white mb-4">Quick Commands</h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              {[
                { text: 'Check my balances', icon: '💰' },
                { text: 'Send an email', icon: '✉️' },
                { text: 'Stock portfolio', icon: '📈' },
                { text: 'Search flights', icon: '✈️' },
                { text: 'Legal research', icon: '⚖️' },
                { text: 'Query documents', icon: '📄' },
              ].map((cmd, index) => (
                <motion.button
                  key={index}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => {
                    setTranscript(cmd.text);
                    toast.success(`Command: "${cmd.text}"`);
                  }}
                  className="flex items-center gap-3 p-3 rounded-xl bg-slate-800/50 hover:bg-slate-800 transition-colors text-left"
                >
                  <span className="text-2xl">{cmd.icon}</span>
                  <span className="text-white text-sm">{cmd.text}</span>
                </motion.button>
              ))}
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Voice Settings */}
          <div className="card">
            <h3 className="text-lg font-semibold text-white mb-4">Voice Settings</h3>

            {/* Voice Selection */}
            <div className="mb-4">
              <label className="text-sm text-slate-400 block mb-2">AI Voice</label>
              <div className="grid grid-cols-2 gap-2">
                {voices.slice(0, 4).map((voice) => (
                  <button
                    key={voice.id}
                    onClick={() => setSelectedVoice(voice.id)}
                    className={`p-2 rounded-lg text-sm transition-all ${
                      selectedVoice === voice.id
                        ? 'bg-primary-500 text-white'
                        : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                    }`}
                  >
                    {voice.name}
                  </button>
                ))}
              </div>
            </div>

            {/* Language Selection */}
            <div className="mb-4">
              <label className="text-sm text-slate-400 block mb-2">Language</label>
              <select
                value={selectedLanguage}
                onChange={(e) => setSelectedLanguage(e.target.value)}
                className="input"
              >
                {languages.map((lang) => (
                  <option key={lang.code} value={lang.code}>{lang.name}</option>
                ))}
              </select>
            </div>

            {/* Volume Control */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm text-slate-400">Volume</label>
                <span className="text-sm text-white">{volume}%</span>
              </div>
              <div className="flex items-center gap-3">
                <HiVolumeUp className="w-5 h-5 text-slate-400" />
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={volume}
                  onChange={(e) => setVolume(e.target.value)}
                  className="flex-1 h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-primary-500"
                />
              </div>
            </div>
          </div>

          {/* Conversation History */}
          <div className="card">
            <h3 className="text-lg font-semibold text-white mb-4">Recent Conversations</h3>
            <div className="space-y-3 max-h-80 overflow-y-auto">
              {history.slice(-6).map((item) => (
                <motion.div
                  key={item.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className={`p-3 rounded-xl ${
                    item.type === 'user'
                      ? 'bg-slate-800/50'
                      : 'bg-primary-500/10 border border-primary-500/20'
                  }`}
                >
                  <div className="flex items-center gap-2 mb-1">
                    {item.type === 'user' ? (
                      <HiMicrophone className="w-4 h-4 text-slate-400" />
                    ) : (
                      <HiSparkles className="w-4 h-4 text-primary-400" />
                    )}
                    <span className="text-xs text-slate-500">{item.time}</span>
                  </div>
                  <p className="text-sm text-slate-300 line-clamp-2">{item.text}</p>
                </motion.div>
              ))}
            </div>
          </div>

          {/* Stats */}
          <div className="card">
            <h3 className="text-lg font-semibold text-white mb-4">Voice Stats</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-slate-400">Commands Today</span>
                <span className="font-semibold text-white">24</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-400">Avg Response Time</span>
                <span className="font-semibold text-white">1.2s</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-400">Recognition Rate</span>
                <span className="font-semibold text-emerald-400">98%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Voice;
