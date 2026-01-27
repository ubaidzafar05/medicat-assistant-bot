import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

export default function GoogleCallback({ onLogin }) {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();

    useEffect(() => {
        const token = searchParams.get('token');
        const username = searchParams.get('username');
        const email = searchParams.get('email');

        if (token && username) {
            localStorage.setItem('token', token);
            localStorage.setItem('username', username);
            if (email) localStorage.setItem('email', email);

            onLogin(username);
            navigate('/chat');
        } else {
            navigate('/login?error=auth_failed');
        }
    }, [searchParams, navigate, onLogin]);

    return (
        <div className="flex flex-col items-center justify-center min-h-screen">
            <div className="glass-card p-8 rounded-2xl flex flex-col items-center animate-fade-in">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary mx-auto"></div>
                <h2 className="text-xl font-semibold mt-4 text-white">Authenticating...</h2>
                <p className="text-slate-400 mt-2">Please wait while we log you in.</p>
            </div>
        </div>
    );
}
