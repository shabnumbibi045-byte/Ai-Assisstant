import React, { useState, useRef, useEffect, useCallback } from 'react';
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
  HiPaperAirplane,
  HiRefresh,
} from 'react-icons/hi';
import { voiceAPI } from '../../services/api';
import { useAuthStore } from '../../store/authStore';

// Browser Speech Recognition
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

const Voice = () => {
  const { user } = useAuthStore();
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [aiResponse, setAiResponse] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [selectedVoice, setSelectedVoice] = useState('alloy');
  const [selectedLanguage, setSelectedLanguage] = useState('en');
  const [volume, setVolume] = useState(80);
  const [history, setHistory] = useState([]);
  const [recognitionSupported, setRecognitionSupported] = useState(true);

  const canvasRef = useRef(null);
  const animationRef = useRef(null);
  const recognitionRef = useRef(null);
  const audioRef = useRef(null);

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

  // Initialize Speech Recognition
  useEffect(() => {
    if (!SpeechRecognition) {
      setRecognitionSupported(false);
      toast.error('Speech recognition not supported in this browser. Try Chrome or Edge.');
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = selectedLanguage === 'en' ? 'en-US' : selectedLanguage;

    recognition.onresult = (event) => {
      let finalTranscript = '';
      let interimTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcriptPart = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalTranscript += transcriptPart;
        } else {
          interimTranscript += transcriptPart;
        }
      }

      setTranscript(finalTranscript || interimTranscript);
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      if (event.error === 'not-allowed') {
        toast.error('Microphone access denied. Please allow microphone access.');
      } else if (event.error !== 'aborted') {
        toast.error(`Speech recognition error: ${event.error}`);
      }
      setIsListening(false);
    };

    recognition.onend = () => {
      if (isListening) {
        // Auto-restart if still supposed to be listening
        try {
          recognition.start();
        } catch (e) {
          // Ignore - already started
        }
      }
    };

    recognitionRef.current = recognition;

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, [selectedLanguage]);

  // Update recognition language when changed
  useEffect(() => {
    if (recognitionRef.current) {
      recognitionRef.current.lang = selectedLanguage === 'en' ? 'en-US' : selectedLanguage;
    }
  }, [selectedLanguage]);

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

  // Process voice command via backend API
  const processVoiceCommand = useCallback(async (text) => {
    if (!text.trim()) return;

    setIsProcessing(true);
    const currentTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    // Add user message to history
    setHistory(prev => [
      ...prev,
      { id: Date.now(), type: 'user', text: text, time: currentTime }
    ]);

    try {
      // Call backend voice command API
      const response = await voiceAPI.processCommand({
        user_id: user?.user_id || 'demo-user-001',
        text: text
      });

      const aiText = response.data.response_text;
      setAiResponse(aiText);

      // Add AI response to history
      setHistory(prev => [
        ...prev,
        { id: Date.now() + 1, type: 'ai', text: aiText, time: currentTime }
      ]);

      // Text-to-speech for the response
      await speakResponse(aiText);

    } catch (error) {
      console.error('Voice command error:', error);
      const errorMsg = 'Sorry, I encountered an error processing your command.';
      setAiResponse(errorMsg);
      toast.error('Failed to process voice command');
    } finally {
      setIsProcessing(false);
    }
  }, [selectedVoice]);

  // Text-to-Speech using browser API (backup) or backend
  const speakResponse = useCallback(async (text) => {
    setIsSpeaking(true);

    try {
      // Try backend TTS first
      const response = await voiceAPI.textToSpeech(text, selectedVoice);
      
      // If we get an audio URL, we could play it (but mock returns fake URL)
      // For now, use browser's built-in TTS as fallback
      if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.volume = volume / 100;
        utterance.rate = 1;
        utterance.pitch = 1;
        
        utterance.onend = () => {
          setIsSpeaking(false);
        };
        
        utterance.onerror = () => {
          setIsSpeaking(false);
        };

        window.speechSynthesis.speak(utterance);
      } else {
        // No TTS available, just show text
        setTimeout(() => setIsSpeaking(false), 2000);
      }
    } catch (error) {
      console.error('TTS error:', error);
      // Fallback to browser TTS
      if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.volume = volume / 100;
        utterance.onend = () => setIsSpeaking(false);
        window.speechSynthesis.speak(utterance);
      } else {
        setIsSpeaking(false);
      }
    }
  }, [selectedVoice, volume]);

  const handleStartListening = useCallback(() => {
    if (!recognitionSupported) {
      toast.error('Speech recognition not supported');
      return;
    }

    setTranscript('');
    setAiResponse('');
    setIsListening(true);
    toast.success('Listening...');

    try {
      recognitionRef.current?.start();
    } catch (e) {
      // Already started
    }
  }, [recognitionSupported]);

  const handleStopListening = useCallback(async () => {
    setIsListening(false);
    
    try {
      recognitionRef.current?.stop();
    } catch (e) {
      // Already stopped
    }

    // Don't auto-process - let user review and click send button
    if (transcript.trim()) {
      toast.success('Ready to send! Click the green button to submit your command.');
    }
  }, [transcript]);

  // Quick command handler
  const handleQuickCommand = useCallback(async (commandText) => {
    setTranscript(commandText);
    await processVoiceCommand(commandText);
  }, [processVoiceCommand]);

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
            <div className="flex justify-center items-center gap-4 mb-6">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={isListening ? handleStopListening : handleStartListening}
                disabled={isProcessing}
                className={`w-24 h-24 rounded-full flex items-center justify-center transition-all ${
                  isListening
                    ? 'bg-red-500 shadow-lg shadow-red-500/30'
                    : isProcessing
                    ? 'bg-slate-600 cursor-not-allowed'
                    : 'bg-gradient-to-br from-primary-500 to-secondary-500 shadow-lg shadow-primary-500/30'
                }`}
              >
                {isListening ? (
                  <HiStop className="w-10 h-10 text-white" />
                ) : (
                  <HiMicrophone className="w-10 h-10 text-white" />
                )}
              </motion.button>
              
              {/* Send button - visible when there's a transcript */}
              {transcript && !isListening && !isProcessing && (
                <motion.button
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => processVoiceCommand(transcript)}
                  className="w-16 h-16 rounded-full bg-emerald-500 hover:bg-emerald-600 shadow-lg shadow-emerald-500/30 flex items-center justify-center"
                >
                  <HiPaperAirplane className="w-7 h-7 text-white transform rotate-90" />
                </motion.button>
              )}
            </div>

            {/* Status Text with better feedback */}
            <div className="text-center mb-6">
              {isProcessing ? (
                <div className="flex items-center justify-center gap-2 text-primary-400">
                  <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                  <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                  <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  <span className="ml-2">Processing your request...</span>
                </div>
              ) : isListening ? (
                <p className="text-red-400 animate-pulse">🎤 Listening... Click the red button to stop and send</p>
              ) : transcript ? (
                <p className="text-emerald-400">Click the green send button to submit your command</p>
              ) : (
                <p className="text-slate-400">Click the microphone to start speaking</p>
              )}
            </div>

            {/* Transcript */}
            {transcript && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="p-4 rounded-xl bg-slate-800/50 mb-4"
              >
                <div className="flex items-center justify-between mb-1">
                  <p className="text-xs text-slate-500">You said:</p>
                  <button
                    onClick={() => setTranscript('')}
                    className="text-xs text-slate-500 hover:text-slate-300 flex items-center gap-1"
                  >
                    <HiRefresh className="w-3 h-3" />
                    Clear
                  </button>
                </div>
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
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-3 gap-3">
              {[
                { text: 'Check my balances', icon: '💰' },
                { text: 'Send an email', icon: '✉️' },
                { text: 'Stock portfolio', icon: '📈' },
                { text: 'Search flights from Toronto to London', icon: '✈️' },
                { text: 'Find hotels in Dubai for next week', icon: '🏨' },
                { text: 'Rent a car in New York for 5 days', icon: '🚗' },
                { text: 'Set alert for flights from Vancouver to Nairobi', icon: '🔔' },
                { text: 'Summarize my documents', icon: '📝' },
                { text: 'List my uploaded documents', icon: '📂' },
                { text: 'Legal research', icon: '⚖️' },
                { text: 'Query documents', icon: '📄' },
              ].map((cmd, index) => (
                <motion.button
                  key={index}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => handleQuickCommand(cmd.text)}
                  disabled={isProcessing}
                  className={`flex items-center gap-3 p-3 rounded-xl bg-slate-800/50 hover:bg-slate-800 transition-colors text-left ${isProcessing ? 'opacity-50 cursor-not-allowed' : ''}`}
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
