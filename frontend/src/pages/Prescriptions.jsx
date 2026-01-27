import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Pill, Clock, Trash2, ArrowLeft, Plus, Bell } from 'lucide-react';
import client from '../api/client';

export default function Prescriptions({ user }) {
    const [prescriptions, setPrescriptions] = useState([]);
    const [reminders, setReminders] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        loadData();
    }, [user]);

    const loadData = async () => {
        setLoading(true);
        try {
            // Fetch prescriptions
            const presData = await client.get(`/prescriptions?username=${user}`);
            setPrescriptions(presData);

            // Fetch upcoming reminders
            const remData = await client.get(`/reminders?username=${user}&limit=5`);
            setReminders(remData);
        } catch (err) {
            setError('Failed to load prescriptions');
        } finally {
            setLoading(false);
        }
    };

    const cancelPrescription = async (id, medicineName) => {
        if (!confirm(`Cancel reminders for ${medicineName}?`)) return;

        try {
            await client.delete(`/prescriptions/${id}?username=${user}`);
            // Refresh data
            loadData();
        } catch (err) {
            setError('Failed to cancel prescription');
        }
    };

    const formatTime = (timeStr) => {
        if (!timeStr) return '';
        try {
            const date = new Date(timeStr);
            return date.toLocaleString('en-US', { hour: 'numeric', minute: 'numeric', hour12: true });
        } catch {
            return timeStr;
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
            </div>
        );
    }

    return (
        <div className="min-h-screen p-6 relative z-10">
            <div className="max-w-4xl mx-auto space-y-8 animate-fade-in">
                {/* Header */}
                <div className="flex items-center justify-between">
                    <button
                        onClick={() => navigate('/chat')}
                        className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors group"
                    >
                        <ArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
                        Back to Chat
                    </button>
                    <h1 className="text-3xl font-bold flex items-center gap-3">
                        <div className="p-2 bg-primary/10 rounded-lg">
                            <Pill className="w-8 h-8 text-primary" />
                        </div>
                        <span className="text-gradient">My Prescriptions</span>
                    </h1>
                </div>

                {error && (
                    <div className="glass-card bg-red-900/20 border-red-500/30 text-red-200 p-4 rounded-xl backdrop-blur-sm">{error}</div>
                )}

                {/* Upcoming Reminders */}
                {reminders.length > 0 && (
                    <div className="glass-card rounded-2xl p-6 border-l-4 border-l-yellow-400">
                        <h2 className="text-lg font-semibold text-white flex items-center gap-2 mb-4">
                            <Bell className="w-5 h-5 text-yellow-400 animate-pulse" />
                            Upcoming Reminders
                        </h2>
                        <div className="space-y-3">
                            {reminders.map((r, idx) => (
                                <div key={idx} className="flex items-center justify-between bg-white/5 rounded-xl p-3 border border-white/5 hover:bg-white/10 transition-colors">
                                    <span className="text-white font-medium">{r.medicine_name}</span>
                                    <span className="text-slate-300 text-sm font-mono bg-black/20 px-2 py-1 rounded-md">{formatTime(r.scheduled_time)}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Active Prescriptions */}
                <div className="glass-card rounded-2xl p-8">
                    <div className="flex items-center justify-between mb-8">
                        <h2 className="text-xl font-semibold text-white">Active Prescriptions</h2>
                        <button
                            onClick={() => navigate('/chat')}
                            className="flex items-center gap-2 px-4 py-2 bg-primary/10 text-primary rounded-lg hover:bg-primary hover:text-white transition-all duration-300 font-medium"
                        >
                            <Plus className="w-4 h-4" />
                            Add New
                        </button>
                    </div>

                    {prescriptions.length === 0 ? (
                        <div className="text-center py-12 border-2 border-dashed border-slate-700/50 rounded-xl">
                            <div className="w-16 h-16 bg-slate-800/50 rounded-full flex items-center justify-center mx-auto mb-4">
                                <Pill className="w-8 h-8 text-slate-500" />
                            </div>
                            <p className="text-slate-400 text-lg">No prescriptions yet</p>
                            <p className="text-slate-500 text-sm mt-2">
                                Go to chat and say "Remind me to take [medicine] at [time]"
                            </p>
                        </div>
                    ) : (
                        <div className="grid gap-4">
                            {prescriptions.map((p) => (
                                <div
                                    key={p.id}
                                    className="group relative bg-white/5 hover:bg-white/10 rounded-xl p-6 border border-white/5 hover:border-primary/30 transition-all duration-300"
                                >
                                    <div className="flex items-start justify-between">
                                        <div>
                                            <h3 className="text-xl font-bold text-white group-hover:text-primary transition-colors">
                                                {p.medicine_name}
                                                {p.dosage && <span className="text-slate-400 font-normal text-base ml-2">({p.dosage})</span>}
                                            </h3>
                                            <div className="flex items-center gap-3 mt-3 text-slate-300">
                                                <div className="flex items-center gap-1.5 bg-black/20 px-2 py-1 rounded-md text-sm">
                                                    <Clock className="w-3.5 h-3.5 text-primary" />
                                                    {p.times && p.times.length > 0
                                                        ? p.times.join(', ')
                                                        : p.frequency || 'No schedule set'
                                                    }
                                                </div>
                                            </div>
                                            {p.instructions && (
                                                <p className="text-slate-400 text-sm mt-3 pl-3 border-l-2 border-slate-700 italic">{p.instructions}</p>
                                            )}
                                        </div>
                                        <button
                                            onClick={() => cancelPrescription(p.id, p.medicine_name)}
                                            className="text-slate-500 hover:text-red-400 hover:bg-red-400/10 p-2 rounded-lg transition-colors opacity-0 group-hover:opacity-100"
                                            title="Cancel prescription"
                                        >
                                            <Trash2 className="w-5 h-5" />
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
