import React from 'react';
import { MessageSquare, Clock } from 'lucide-react';
import { motion } from 'framer-motion';

const ChatHistory = ({ sessions, activeSessionId, onSelectSession, loading }) => {
    const formatDate = (dateStr) => {
        const date = new Date(dateStr);
        const now = new Date();
        const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));

        if (diffDays === 0) return 'Today';
        if (diffDays === 1) return 'Yesterday';
        if (diffDays < 7) return `${diffDays} days ago`;
        return date.toLocaleDateString();
    };

    if (loading) {
        return (
            <div className="space-y-2">
                {[1, 2, 3].map(i => (
                    <div key={i} className="h-16 bg-slate-700/50 rounded-lg animate-pulse" />
                ))}
            </div>
        );
    }

    if (!sessions || sessions.length === 0) {
        return (
            <div className="text-center text-slate-500 py-8 text-sm">
                <MessageSquare className="w-8 h-8 mx-auto mb-2 opacity-50" />
                No conversations yet
            </div>
        );
    }

    return (
        <div className="space-y-2">
            {sessions.map((session, idx) => (
                <motion.button
                    key={session.id}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: idx * 0.05 }}
                    onClick={() => onSelectSession(session.id)}
                    className={`w-full text-left p-3 rounded-lg transition-all duration-200 group relative overflow-hidden backdrop-blur-sm
                        ${activeSessionId === session.id
                            ? 'bg-primary/20 border border-primary/50 text-white'
                            : 'bg-glass-input hover:bg-white/5 border border-transparent'
                        }`}
                >
                    {/* Active Indicator */}
                    {activeSessionId === session.id && (
                        <motion.div
                            layoutId="activeIndicator"
                            className="absolute left-0 top-0 bottom-0 w-1 bg-primary"
                        />
                    )}

                    <div className="flex items-start gap-3 pl-2">
                        <MessageSquare className={`w-4 h-4 mt-1 flex-shrink-0 
                            ${activeSessionId === session.id ? 'text-primary' : 'text-slate-400 group-hover:text-primary transition-colors'}`}
                        />
                        <div className="flex-1 min-w-0">
                            <div className={`text-sm font-medium truncate
                                ${activeSessionId === session.id ? 'text-white' : 'text-slate-300 group-hover:text-white transition-colors'}`}>
                                {session.preview || 'New conversation'}
                            </div>
                            <div className="flex items-center gap-2 mt-1 text-xs text-slate-500 group-hover:text-slate-400">
                                <Clock className="w-3 h-3" />
                                {formatDate(session.last_active)}
                                <span className="text-slate-600">·</span>
                                <span>{session.message_count} msgs</span>
                            </div>
                        </div>
                    </div>
                </motion.button>
            ))}
        </div>
    );
};

export default ChatHistory;
