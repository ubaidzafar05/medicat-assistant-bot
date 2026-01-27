import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Chat from './pages/Chat';
import GoogleCallback from './pages/GoogleCallback';
import Prescriptions from './pages/Prescriptions';
import DynamicBackground from './components/DynamicBackground';
import { useState } from 'react';

function App() {
  const [user, setUser] = useState(localStorage.getItem('username'));

  const handleLogin = (username) => {
    localStorage.setItem('username', username);
    setUser(username);
  };

  const handleLogout = () => {
    localStorage.removeItem('username');
    localStorage.removeItem('email');
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <Router>
      <DynamicBackground>
        <Routes>
          <Route path="/login" element={!user ? <Login onLogin={handleLogin} /> : <Navigate to="/chat" />} />
          <Route path="/signup" element={!user ? <Signup /> : <Navigate to="/chat" />} />
          <Route path="/auth/google/callback" element={<GoogleCallback onLogin={handleLogin} />} />
          <Route path="/chat" element={user ? <Chat user={user} onLogout={handleLogout} /> : <Navigate to="/login" />} />
          <Route path="/prescriptions" element={user ? <Prescriptions user={user} /> : <Navigate to="/login" />} />
          <Route path="*" element={<Navigate to={user ? "/chat" : "/login"} />} />
        </Routes>
      </DynamicBackground>
    </Router>
  );
}

export default App;
