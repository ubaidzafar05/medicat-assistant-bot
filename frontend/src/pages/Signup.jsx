import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { register } from '../api/client';
import { User, Lock, Chrome as GoogleIcon } from 'lucide-react';
import { motion } from 'framer-motion';

export default function Signup() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        try {
            const data = await register(username, password);
            localStorage.setItem('username', data.username);
            navigate('/chat');
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleGoogleSignup = () => {
        setLoading(true);
        window.location.href = 'http://localhost:8000/auth/google';
    };

    return (
        <div className="flex flex-col items-center justify-center min-h-screen p-4">
            <div className="w-full max-w-md p-8 space-y-8 glass-card rounded-2xl animate-fade-in relative z-10">
                <div className="text-center">
                    <h2 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary via-accent to-secondary mb-2 animate-pulse-slow">Join NeuralFlow</h2>
                    <p className="text-slate-300">Create your secure medical profile</p>
                </div>

                {error && <div className="p-3 text-sm text-red-200 bg-red-900/40 border border-red-500/30 rounded-lg backdrop-blur-sm">{error}</div>}

                {/* Google Sign Up Button */}
                <button
                    onClick={handleGoogleSignup}
                    disabled={loading}
                    className="w-full flex items-center justify-center gap-3 py-3 px-4 bg-white/10 hover:bg-white/20 border border-white/10 text-white font-medium rounded-lg transition-all duration-300 backdrop-blur-sm shadow-lg hover:shadow-cyan-500/20 disabled:opacity-50 group"
                >
                    <GoogleIcon />
                    {loading ? 'Connecting...' : 'Sign up with Google'}
                </button>

                <div className="relative">
                    <div className="absolute inset-0 flex items-center">
                        <div className="w-full border-t border-slate-700/50"></div>
                    </div>
                    <div className="relative flex justify-center text-sm">
                        <span className="px-2 text-slate-400">or sign up with email</span>
                    </div>
                </div>

                <form onSubmit={handleSubmit} className="space-y-5">
                    <div className="relative group">
                        <User className="absolute left-3 top-3 text-slate-400 group-focus-within:text-primary transition-colors w-5 h-5" />
                        <input
                            type="text"
                            placeholder="Choose a Username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            className="w-full pl-10 pr-4 py-3 glass-input rounded-xl text-white placeholder-slate-500 outline-none"
                        />
                    </div>
                    <div className="relative group">
                        <Lock className="absolute left-3 top-3 text-slate-400 group-focus-within:text-primary transition-colors w-5 h-5" />
                        <input
                            type="password"
                            placeholder="Choose a Password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="w-full pl-10 pr-4 py-3 glass-input rounded-xl text-white placeholder-slate-500 outline-none"
                        />
                    </div>
                    <button type="submit" className="w-full py-3 font-bold text-white bg-gradient-to-r from-primary to-primary-hover rounded-xl hover:shadow-[0_0_20px_rgba(14,165,233,0.4)] transition-all duration-300 transform hover:-translate-y-0.5">
                        Sign Up
                    </button>
                </form>

                <div className="text-center text-sm text-slate-400">
                    Already have an account? <Link to="/login" className="text-primary hover:text-white transition-colors">Login here</Link>
                </div>
            </div>
        </div>
    );
}
