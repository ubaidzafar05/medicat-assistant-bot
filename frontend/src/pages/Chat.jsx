import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { streamChat, getHistory, getVitals, getSessions, createNewChat, getSessionHistory } from '../api/client';
import { Send, Activity, LogOut, Plus, History, ChevronLeft, ChevronRight, Pill } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import MedicalResponse from '../components/MedicalResponse';
import ChatHistory from '../components/ChatHistory';
import ConfirmDialog from '../components/ConfirmDialog';

export default function Chat({ user, onLogout }) {
    const navigate = useNavigate();
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const [activeSessionId, setActiveSessionId] = useState(null);
    const [sessions, setSessions] = useState([]);
    const [sessionsLoading, setSessionsLoading] = useState(false);
    const [error, setError] = useState('');
    const [vitals, setVitals] = useState([]);
    const messagesEndRef = useRef(null);
    const [sidebarView, setSidebarView] = useState('history');
    const [showNewChatDialog, setShowNewChatDialog] = useState(false);

    useEffect(() => {
        loadSessions();
        loadVitals();
    }, [user]);

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    const loadSessions = async () => {
        setSessionsLoading(true);
        try {
            const data = await getSessions(user);
            setSessions(data);
            if (data.length > 0) {
                handleSelectSession(data[0].id);
            }
        } catch (err) {
            console.error(err);
        } finally {
            setSessionsLoading(false);
        }
    };

    const loadVitals = async () => {
        try {
            const data = await getVitals(user);
            setVitals(data);
        } catch (err) {
            console.error("Failed to load vitals", err);
        }
    };

    const handleSelectSession = async (sessionId) => {
        setActiveSessionId(sessionId);
        setLoading(true);
        try {
            const history = await getSessionHistory(sessionId, user);
            setMessages(history);
        } catch (err) {
            setError('Failed to load chat history');
        } finally {
            setLoading(false);
        }
    };

    const handleNewChat = async () => {
        setLoading(true);
        try {
            const newSession = await createNewChat(user);
            setSessions([newSession, ...sessions]);
            setActiveSessionId(newSession.id);
            setMessages([]);
            setShowNewChatDialog(false);
        } catch (err) {
            setError('Failed to create new chat');
        } finally {
            setLoading(false);
        }
    };

    const handleSend = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMessage = { role: 'user', content: input };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setLoading(true);
        setError('');

        // Optimistic session creation if none
        let currentSessionId = activeSessionId;
        if (!currentSessionId) {
            try {
                const newSession = await createNewChat(user);
                setSessions([newSession, ...sessions]);
                currentSessionId = newSession.id;
                setActiveSessionId(currentSessionId);
            } catch (err) {
                setError('Failed to start chat');
                setLoading(false);
                return;
            }
        }

        // Placeholder for AI response
        setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

        try {
            let fullResponse = "";
            await streamChat(user, input, currentSessionId, (chunk) => {
                fullResponse += chunk;
                setMessages(prev => {
                    const newMessages = [...prev];
                    newMessages[newMessages.length - 1].content = fullResponse;
                    return newMessages;
                });
            });

            // Refresh sessions to update preview text and message counts
            loadSessions();

        } catch (err) {
            setError('Failed to send message');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex h-screen overflow-hidden relative z-10">

            {/* Sidebar (Glass) */}
            <div className="w-80 bg-slate-900/80 backdrop-blur-xl border-r border-slate-700/50 hidden md:flex flex-col">
                {/* Sidebar Header */}
                <div className="p-4 border-b border-slate-700/50">
                    <h2 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary via-accent to-secondary flex items-center gap-2">
                        <Activity className="w-5 h-5 text-primary" /> Health Monitor
                    </h2>
                    <div className="text-sm text-slate-400 mt-1">Patient: {user}</div>

                    {/* Sidebar Toggle */}
                    <div className="flex gap-2 mt-3 bg-slate-800/50 p-1 rounded-xl">
                        <button
                            onClick={() => setSidebarView('history')}
                            className={`flex-1 py-1.5 px-3 rounded-lg text-xs font-medium transition-all duration-300
                                ${sidebarView === 'history'
                                    ? 'bg-primary/20 text-primary shadow-sm'
                                    : 'text-slate-400 hover:text-white'}`}
                        >
                            <History className="w-3 h-3 inline mr-1" /> Chats
                        </button>
                        <button
                            onClick={() => setSidebarView('vitals')}
                            className={`flex-1 py-1.5 px-3 rounded-lg text-xs font-medium transition-all duration-300
                                ${sidebarView === 'vitals'
                                    ? 'bg-primary/20 text-primary shadow-sm'
                                    : 'text-slate-400 hover:text-white'}`}
                        >
                            <Activity className="w-3 h-3 inline mr-1" /> Vitals
                        </button>
                    </div>
                </div>

                {/* Sidebar Content */}
                <div className="flex-1 overflow-y-auto p-4 custom-scrollbar">
                    {sidebarView === 'history' ? (
                        <ChatHistory
                            sessions={sessions}
                            activeSessionId={activeSessionId}
                            onSelectSession={handleSelectSession}
                            loading={sessionsLoading}
                        />
                    ) : (
                        <div className="space-y-4">
                            <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-widest pl-2">Recent Vitals</h3>
                            {vitals.length === 0 && <div className="text-slate-500 italic text-sm pl-2">No recent data.</div>}
                            {vitals.map((v, i) => (
                                <div key={i} className="glass-card p-3 rounded-xl flex justify-between items-center group hover:bg-white/5 transition-colors">
                                    <div>
                                        <div className="text-slate-300 font-medium group-hover:text-primary transition-colors">{v.vital_type}</div>
                                        <div className="text-xs text-slate-500">{new Date(v.timestamp).toLocaleString()}</div>
                                    </div>
                                    <div className="text-primary font-bold bg-primary/10 px-2 py-1 rounded-lg">
                                        {v.value} <span className="text-xs text-slate-400 font-normal ml-1">{v.unit}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* Sidebar Footer */}
                <div className="p-4 border-t border-slate-700/50 space-y-2">
                    <button
                        onClick={() => navigate('/prescriptions')}
                        className="flex items-center gap-2 text-slate-400 hover:text-primary hover:bg-primary/10 transition-all w-full p-2 rounded-lg"
                    >
                        <Pill className="w-4 h-4" /> My Prescriptions
                    </button>
                    <button onClick={onLogout} className="flex items-center gap-2 text-slate-400 hover:text-white hover:bg-white/5 transition-all w-full p-2 rounded-lg">
                        <LogOut className="w-4 h-4" /> Sign Out
                    </button>
                </div>
            </div>

            {/* Main Chat Area */}
            <div className="flex-1 flex flex-col bg-background/50 backdrop-blur-sm">
                {/* Header with New Chat Button */}
                <div className="p-4 border-b border-slate-700/50 flex justify-between items-center backdrop-blur-md sticky top-0 z-20">
                    <div className="font-bold text-primary flex items-center gap-2">
                        <Activity className="w-5 h-5 md:hidden" />
                        <span className="md:hidden">NeuralFlow</span>
                        <span className="hidden md:inline text-slate-300 font-normal text-sm bg-slate-800/50 px-3 py-1 rounded-full border border-slate-700/50">
                            {sessions.find(s => s.id === activeSessionId)?.preview || 'New Conversation'}
                        </span>
                    </div>
                    <div className="flex items-center gap-2">
                        <button
                            onClick={() => setShowNewChatDialog(true)}
                            className="flex items-center gap-2 px-3 py-2 bg-primary text-white rounded-lg 
                                hover:bg-primary-hover transition-colors text-sm font-bold shadow-lg shadow-primary/20"
                        >
                            <Plus className="w-4 h-4" /> New Chat
                        </button>
                        <button onClick={onLogout} className="md:hidden p-2">
                            <LogOut className="w-5 h-5 text-slate-400" />
                        </button>
                    </div>
                </div>

                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-4 space-y-6 custom-scrollbar">
                    {messages.length === 0 && !loading && (
                        <div className="flex flex-col items-center justify-center h-full text-slate-500 animate-fade-in">
                            <div className="w-20 h-20 bg-slate-800/50 rounded-full flex items-center justify-center mb-6">
                                <Activity className="w-10 h-10 text-slate-600" />
                            </div>
                            <p className="text-xl font-medium text-slate-400">Start a new conversation</p>
                            <p className="text-sm mt-2 text-slate-500">Describe your symptoms or ask a health question</p>
                        </div>
                    )}

                    {messages.map((msg, idx) => (
                        <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            key={idx}
                            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                            {/* Don't render empty assistant bubbles (wait for content) */}
                            {(msg.content || msg.role === 'user') && (
                                <div className={`max-w-[85%] lg:max-w-[75%] p-5 rounded-2xl shadow-sm backdrop-blur-sm ${msg.role === 'user'
                                    ? 'bg-primary text-white font-medium rounded-br-none shadow-primary/20'
                                    : 'bg-surface text-slate-100 border border-slate-700/50 rounded-bl-none'
                                    }`}>
                                    {msg.role === 'user' ? (
                                        <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                                    ) : (
                                        <MedicalResponse content={msg.content} />
                                    )}
                                </div>
                            )}
                        </motion.div>
                    ))}

                    {/* Loading Bubbles */}
                    {loading && messages.length > 0 && messages[messages.length - 1].content === '' && (
                        <div className="flex justify-start">
                            <div className="glass-card p-4 rounded-2xl rounded-bl-none flex gap-1.5 items-center">
                                <div className="w-2 h-2 bg-primary/50 rounded-full animate-bounce" />
                                <div className="w-2 h-2 bg-primary/50 rounded-full animate-bounce [animation-delay:0.2s]" />
                                <div className="w-2 h-2 bg-primary/50 rounded-full animate-bounce [animation-delay:0.4s]" />
                            </div>
                        </div>
                    )}

                    {error && (
                        <div className="text-center p-4 text-red-400 bg-red-900/20 rounded-lg border border-red-500/20">
                            {error}
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                {/* Input Area */}
                <div className="p-4 border-t border-white/5 backdrop-blur-md bg-surface/40">
                    <form onSubmit={handleSend} className="relative max-w-4xl mx-auto">
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Describe your symptoms..."
                            className="w-full pl-6 pr-12 py-4 glass-input rounded-full focus:outline-none text-white placeholder-slate-500 shadow-xl"
                        />
                        <button
                            type="submit"
                            disabled={!input.trim() || loading}
                            className="absolute right-2 top-2 p-2 bg-primary text-white rounded-full hover:bg-primary-hover disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-primary/30"
                        >
                            <Send className="w-5 h-5" />
                        </button>
                    </form>
                    <div className="text-center mt-3 text-xs text-slate-500 font-medium">
                        NeuralFlow AI can make mistakes. Consult a doctor for medical advice.
                    </div>
                </div>

                {/* Modals */}
                <ConfirmDialog
                    isOpen={showNewChatDialog}
                    title="Start New Chat"
                    message="Start a new conversation? This will save your current chat to history."
                    onConfirm={handleNewChat}
                    onCancel={() => setShowNewChatDialog(false)}
                />
            </div>
        </div>
    );
}