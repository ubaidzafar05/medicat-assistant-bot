import axios from 'axios';

const client = axios.create({
    baseURL: 'http://localhost:8000',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add response interceptor to unwrap data
client.interceptors.response.use(
    (response) => response.data,
    (error) => {
        // Optional: specific error handling (e.g., 401 logout) could go here
        return Promise.reject(error);
    }
);

export const register = (username, password) =>
    client.post('/auth/register', { username, password });

export const login = (username, password) =>
    client.post('/auth/login', { username, password });

export const getVitals = (username, limit) =>
    client.get(`/vitals?username=${username}&limit=${limit}`);

export const saveVital = (username, type, value, unit) =>
    client.post('/vitals', { username, type, value, unit });

export const getHistory = (username) =>
    client.get(`/chat/history?username=${username}`);

// Session management
// Session management
export const createNewChat = (username) =>
    client.post('/chat/new', { username });

export const getSessions = (username, limit = 20) =>
    client.get(`/chat/sessions?username=${username}&limit=${limit}`);

export const getSessionHistory = (sessionId, username) =>
    client.get(`/chat/history/${sessionId}?username=${username}`);

export const switchSession = (username, sessionId) =>
    client.post(`/chat/switch/${sessionId}`, { username });

// Streaming chat helper
export const streamChat = async (username, userInput, sessionId, onChunk, onComplete, onError) => {
    try {
        const response = await fetch('http://localhost:8000/chat/message', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username,
                user_input: userInput,
                session_id: sessionId
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let done = false;

        while (!done) {
            const { value, done: doneReading } = await reader.read();
            done = doneReading;
            const chunkValue = decoder.decode(value, { stream: true });
            if (chunkValue) {
                onChunk(chunkValue);
            }
        }
        if (onComplete) onComplete();
    } catch (error) {
        if (onError) onError(error);
        else console.error("Stream error:", error);
    }
};

export default client;

