import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { register } from '../api/client';
import { Lock, User } from 'lucide-react';

export default function Signup() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await register(username, password);
            // Auto-redirect to login
            navigate('/login');
        } catch (err) {
            setError('Registration failed. Username might be taken.');
        }
    };

    return (
        <div className="flex flex-col items-center justify-center min-h-screen p-4 bg-gradient-to-b from-slate-900 to-slate-800">
            <div className="w-full max-w-md p-8 space-y-6 bg-slate-800 rounded-xl shadow-2xl border border-slate-700">
                <h2 className="text-3xl font-bold text-center text-accent">Join NeuralFlow</h2>
                <p className="text-center text-slate-400">Create your secure medical profile</p>

                {error && <div className="p-3 text-sm text-red-200 bg-red-900/50 rounded-lg">{error}</div>}

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="relative">
                        <User className="absolute left-3 top-3 text-slate-500 w-5 h-5" />
                        <input
                            type="text"
                            placeholder="Choose a Username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            className="w-full pl-10 pr-4 py-2 bg-slate-900 border border-slate-700 rounded-lg focus:ring-2 focus:ring-accent focus:outline-none"
                        />
                    </div>
                    <div className="relative">
                        <Lock className="absolute left-3 top-3 text-slate-500 w-5 h-5" />
                        <input
                            type="password"
                            placeholder="Choose a Password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="w-full pl-10 pr-4 py-2 bg-slate-900 border border-slate-700 rounded-lg focus:ring-2 focus:ring-accent focus:outline-none"
                        />
                    </div>
                    <button type="submit" className="w-full py-2 font-bold text-slate-900 bg-accent rounded-lg hover:bg-sky-400 transition-colors">
                        Sign Up
                    </button>
                </form>

                <div className="text-center text-sm text-slate-500">
                    Already have an account? <Link to="/login" className="text-accent hover:underline">Login here</Link>
                </div>
            </div>
        </div>
    );
}
