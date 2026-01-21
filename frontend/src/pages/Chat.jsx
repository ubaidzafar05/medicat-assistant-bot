import { useState, useEffect, useRef } from 'react';
import { streamChat, getHistory, getVitals, getSessions, createNewChat, getSessionHistory } from '../api/client';
import { Send, Activity, LogOut, Plus, History, ChevronLeft, ChevronRight } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import MedicalResponse from '../components/MedicalResponse';
import ChatHistory from '../components/ChatHistory';
import ConfirmDialog from '../components/ConfirmDialog';

export default function Chat({ user, onLogout }) {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [vitals, setVitals] = useState([]);
    const [sessions, setSessions] = useState([]);
    const [activeSessionId, setActiveSessionId] = useState(null);
    const [sessionsLoading, setSessionsLoading] = useState(true);
    const [showNewChatDialog, setShowNewChatDialog] = useState(false);
    const [sidebarView, setSidebarView] = useState('history'); // 'history' or 'vitals'
    const messagesEndRef = useRef(null);

    // Load initial data
    useEffect(() => {
        const loadData = async () => {
            try {
                // Load sessions
                setSessionsLoading(true);
                const sessionsRes = await getSessions(user);
                setSessions(sessionsRes.data || []);

                // Set active session to most recent
                if (sessionsRes.data && sessionsRes.data.length > 0) {
                    setActiveSessionId(sessionsRes.data[0].id);
                }

                setSessionsLoading(false);

                // Load current history
                const history = await getHistory(user);
                setMessages(history.data || []);

                // Load vitals
                const recentVitals = await getVitals(user, 5);
                setVitals(recentVitals.data || []);
            } catch (err) {
                console.error("Failed to load data:", err);
                setError("Failed to load chat history. Is the server running?");
                setSessionsLoading(false);
            }
        };
        loadData();
    }, [user]);

    // Auto-scroll to bottom
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const handleSelectSession = async (sessionId) => {
        if (sessionId === activeSessionId) return;

        try {
            const historyRes = await getSessionHistory(user, sessionId);
            setMessages(historyRes.data || []);
            setActiveSessionId(sessionId);
        } catch (err) {
            console.error("Failed to load session:", err);
            setError("Failed to load session history.");
        }
    };

    const handleNewChat = async () => {
        try {
            const res = await createNewChat(user);
            const newSessionId = res.data.session_id;

            // Clear messages and set new session
            setMessages([]);
            setActiveSessionId(newSessionId);

            // Refresh sessions list
            const sessionsRes = await getSessions(user);
            setSessions(sessionsRes.data || []);

            setShowNewChatDialog(false);
        } catch (err) {
            console.error("Failed to create new chat:", err);
            setError("Failed to create new chat.");
        }
    };

    const handleSend = async (e) => {
        e.preventDefault();
        if (!input.trim() || loading) return;

        const userMsg = { role: 'user', content: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setLoading(true);
        setError(null);

        let accumulatedContent = '';
        setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

        await streamChat(
            user,
            userMsg.content,
            (chunk) => {
                accumulatedContent += chunk;
                setMessages(prev => {
                    const newMsgs = [...prev];
                    newMsgs[newMsgs.length - 1] = {
                        role: 'assistant',
                        content: accumulatedContent
                    };
                    return newMsgs;
                });
            },
            async () => {
                setLoading(false);
                // Refresh vitals and sessions
                getVitals(user, 5).then(res => setVitals(res.data || []));
                const sessionsRes = await getSessions(user);
                setSessions(sessionsRes.data || []);
            },
            (err) => {
                setLoading(false);
                setError("Failed to send message. Please try again.");
                console.error("Stream error:", err);
            }
        );
    };

    return (
        <div className="flex h-screen bg-slate-900 border-t border-slate-700 overflow-hidden">

            {/* Sidebar */}
            <div className="w-80 bg-slate-800 border-r border-slate-700 hidden md:flex flex-col">
                {/* Sidebar Header */}
                <div className="p-4 border-b border-slate-700">
                    <h2 className="text-xl font-bold text-accent flex items-center gap-2">
                        <Activity className="w-5 h-5" /> Health Monitor
                    </h2>
                    <div className="text-sm text-slate-400 mt-1">Patient: {user}</div>

                    {/* Sidebar Toggle */}
                    <div className="flex gap-2 mt-3">
                        <button
                            onClick={() => setSidebarView('history')}
                            className={`flex-1 py-1.5 px-3 rounded-lg text-xs font-medium transition-colors
                                ${sidebarView === 'history'
                                    ? 'bg-accent/20 text-accent'
                                    : 'text-slate-400 hover:bg-slate-700'}`}
                        >
                            <History className="w-3 h-3 inline mr-1" /> Chats
                        </button>
                        <button
                            onClick={() => setSidebarView('vitals')}
                            className={`flex-1 py-1.5 px-3 rounded-lg text-xs font-medium transition-colors
                                ${sidebarView === 'vitals'
                                    ? 'bg-accent/20 text-accent'
                                    : 'text-slate-400 hover:bg-slate-700'}`}
                        >
                            <Activity className="w-3 h-3 inline mr-1" /> Vitals
                        </button>
                    </div>
                </div>

                {/* Sidebar Content */}
                <div className="flex-1 overflow-y-auto p-4">
                    {sidebarView === 'history' ? (
                        <ChatHistory
                            sessions={sessions}
                            activeSessionId={activeSessionId}
                            onSelectSession={handleSelectSession}
                            loading={sessionsLoading}
                        />
                    ) : (
                        <div className="space-y-4">
                            <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-widest">Recent Vitals</h3>
                            {vitals.length === 0 && <div className="text-slate-500 italic text-sm">No recent data.</div>}
                            {vitals.map((v, i) => (
                                <div key={i} className="bg-slate-900/50 p-3 rounded-lg border border-slate-700 flex justify-between items-center">
                                    <div>
                                        <div className="text-slate-300 font-medium">{v.vital_type}</div>
                                        <div className="text-xs text-slate-500">{new Date(v.timestamp).toLocaleString()}</div>
                                    </div>
                                    <div className="text-accent font-bold">
                                        {v.value} <span className="text-xs text-slate-500 font-normal">{v.unit}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* Sidebar Footer */}
                <div className="p-4 border-t border-slate-700">
                    <button onClick={onLogout} className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors w-full p-2 rounded hover:bg-slate-700">
                        <LogOut className="w-4 h-4" /> Sign Out
                    </button>
                </div>
            </div>

            {/* Main Chat Area */}
            <div className="flex-1 flex flex-col">
                {/* Header with New Chat Button */}
                <div className="p-4 bg-slate-800 border-b border-slate-700 flex justify-between items-center">
                    <div className="font-bold text-accent flex items-center gap-2">
                        <Activity className="w-5 h-5 md:hidden" />
                        <span className="md:hidden">NeuralFlow</span>
                        <span className="hidden md:inline text-slate-300 font-normal text-sm">
                            {sessions.find(s => s.id === activeSessionId)?.preview || 'New Conversation'}
                        </span>
                    </div>
                    <div className="flex items-center gap-2">
                        <button
                            onClick={() => setShowNewChatDialog(true)}
                            className="flex items-center gap-2 px-3 py-2 bg-accent text-slate-900 rounded-lg 
                                hover:bg-sky-400 transition-colors text-sm font-medium"
                        >
                            <Plus className="w-4 h-4" /> New Chat
                        </button>
                        <button onClick={onLogout} className="md:hidden p-2">
                            <LogOut className="w-5 h-5 text-slate-400" />
                        </button>
                    </div>
                </div>

                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-4 space-y-6">
                    {messages.length === 0 && !loading && (
                        <div className="flex flex-col items-center justify-center h-full text-slate-500">
                            <Activity className="w-12 h-12 mb-4 opacity-30" />
                            <p className="text-lg">Start a new conversation</p>
                            <p className="text-sm mt-1">Describe your symptoms or ask a health question</p>
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
                                <div className={`max-w-[85%] lg:max-w-[75%] p-4 rounded-2xl ${msg.role === 'user'
                                    ? 'bg-accent text-slate-900 rounded-br-none'
                                    : 'bg-white text-slate-800 border border-slate-200 shadow-sm rounded-bl-none'
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
                            <div className="bg-white p-4 rounded-2xl rounded-bl-none border border-slate-200 shadow-sm flex gap-1">
                                <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" />
                                <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce [animation-delay:0.2s]" />
                                <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce [animation-delay:0.4s]" />
                            </div>
                        </div>
                    )}

                    {error && (
                        <div className="text-center p-4 text-red-400 bg-red-900/20 rounded-lg">
                            {error}
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                {/* Input Area */}
                <div className="p-4 bg-slate-900 border-t border-slate-700">
                    <form onSubmit={handleSend} className="relative max-w-4xl mx-auto">
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Describe your symptoms..."
                            className="w-full pl-6 pr-12 py-4 bg-slate-800 border border-slate-700 rounded-full focus:ring-2 focus:ring-accent focus:outline-none text-white placeholder-slate-500 shadow-lg"
                        />
                        <button
                            type="submit"
                            disabled={!input.trim() || loading}
                            className="absolute right-3 top-3 p-2 bg-accent text-slate-900 rounded-full hover:bg-sky-400 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        >
                            <Send className="w-5 h-5" />
                        </button>
                    </form>
                    <div className="text-center mt-2 text-xs text-slate-500">
                        NeuralFlow AI can make mistakes. Consult a doctor for medical advice.
                    </div>
                </div>
            </div>

            {/* Confirm Dialog */}
            <ConfirmDialog
                isOpen={showNewChatDialog}
                title="Start New Chat?"
                message="This will create a new conversation. Your current chat will be saved and you can access it from the history."
                confirmText="New Chat"
                onConfirm={handleNewChat}
                onCancel={() => setShowNewChatDialog(false)}
            />
        </div>
    );
}