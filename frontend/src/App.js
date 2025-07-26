import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Auth Context
const AuthContext = React.createContext();

const useAuth = () => {
  const context = React.useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [sessionToken, setSessionToken] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for stored session
    const stored_token = localStorage.getItem('session_token');
    if (stored_token) {
      setSessionToken(stored_token);
      fetchUserInfo(stored_token);
    } else {
      setLoading(false);
    }
  }, []);

  const fetchUserInfo = async (token) => {
    try {
      const response = await axios.get(`${API}/auth/me?session_token=${token}`);
      setUser(response.data);
    } catch (error) {
      console.error('Failed to fetch user info:', error);
      localStorage.removeItem('session_token');
      setSessionToken(null);
    } finally {
      setLoading(false);
    }
  };

  const login = () => {
    const previewUrl = window.location.origin;
    const authUrl = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(previewUrl)}`;
    window.location.href = authUrl;
  };

  const logout = () => {
    localStorage.removeItem('session_token');
    setUser(null);
    setSessionToken(null);
  };

  const handleAuthCallback = async (sessionId) => {
    try {
      const response = await axios.post(`${API}/auth/profile`, {
        session_id: sessionId
      });
      
      const { user, session_token } = response.data;
      localStorage.setItem('session_token', session_token);
      setSessionToken(session_token);
      setUser(user);
      
      // Clean URL
      window.history.replaceState({}, document.title, window.location.pathname);
    } catch (error) {
      console.error('Authentication failed:', error);
    }
  };

  return (
    <AuthContext.Provider value={{
      user,
      sessionToken,
      loading,
      login,
      logout,
      handleAuthCallback
    }}>
      {children}
    </AuthContext.Provider>
  );
};

// Main App Component
const VaultLinksApp = () => {
  const { user, sessionToken, login, logout } = useAuth();
  const [links, setLinks] = useState([]);
  const [formData, setFormData] = useState({
    url: '',
    name: '',
    access_level: 'Restricted'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (user && sessionToken) {
      fetchLinks();
    }
  }, [user, sessionToken]);

  const fetchLinks = async () => {
    try {
      const response = await axios.get(`${API}/vault-links?session_token=${sessionToken}`);
      setLinks(response.data);
    } catch (error) {
      console.error('Failed to fetch links:', error);
      setError('Failed to load links');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Basic validation
    if (!formData.url.trim() || !formData.name.trim()) {
      setError('URL and Name are required');
      setLoading(false);
      return;
    }

    if (!formData.url.startsWith('http')) {
      setError('URL must start with http:// or https://');
      setLoading(false);
      return;
    }

    try {
      await axios.post(`${API}/vault-links?session_token=${sessionToken}`, formData);
      
      // Reset form
      setFormData({
        url: '',
        name: '',
        access_level: 'Restricted'
      });
      
      // Refresh links
      fetchLinks();
    } catch (error) {
      console.error('Failed to create link:', error);
      setError('Failed to save link');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (linkId) => {
    if (!window.confirm('Are you sure you want to delete this link?')) {
      return;
    }

    try {
      await axios.delete(`${API}/vault-links/${linkId}?session_token=${sessionToken}`);
      fetchLinks();
    } catch (error) {
      console.error('Failed to delete link:', error);
      setError('Failed to delete link');
    }
  };

  const openLink = (url) => {
    window.open(url, '_blank', 'noopener,noreferrer');
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full text-center">
          <div className="mb-6">
            <div className="w-16 h-16 bg-indigo-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"></path>
              </svg>
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">VaultLinks</h1>
            <p className="text-gray-600">Organize and manage your Google Drive links</p>
          </div>
          
          <button
            onClick={login}
            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200 transform hover:scale-105"
          >
            Sign In to Continue
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"></path>
              </svg>
            </div>
            <h1 className="text-xl font-bold text-gray-900">VaultLinks</h1>
          </div>
          
          <div className="flex items-center space-x-3">
            {user.picture && (
              <img 
                src={user.picture} 
                alt={user.name}
                className="w-8 h-8 rounded-full"
              />
            )}
            <span className="text-sm text-gray-700 hidden sm:block">{user.name}</span>
            <button
              onClick={logout}
              className="text-sm text-gray-500 hover:text-gray-700"
            >
              Sign Out
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-6 space-y-6">
        {/* Add Link Form */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Add New Link</h2>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Google Drive URL *
              </label>
              <input
                type="url"
                value={formData.url}
                onChange={(e) => setFormData({...formData, url: e.target.value})}
                placeholder="https://drive.google.com/..."
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition duration-200"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Name / Description *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                placeholder="e.g., Project Documents, Meeting Notes..."
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition duration-200"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Access Level
              </label>
              <select
                value={formData.access_level}
                onChange={(e) => setFormData({...formData, access_level: e.target.value})}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition duration-200"
              >
                <option value="Restricted">Restricted</option>
                <option value="Anyone with link">Anyone with link</option>
                <option value="Public">Public</option>
              </select>
            </div>

            {error && (
              <div className="text-red-600 text-sm bg-red-50 p-3 rounded-lg">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 text-white font-semibold py-3 px-6 rounded-lg transition duration-200 transform hover:scale-[1.02] disabled:transform-none"
            >
              {loading ? 'Adding Link...' : 'Add Link'}
            </button>
          </form>
        </div>

        {/* Links List */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Your Links ({links.length})
          </h2>

          {links.length === 0 ? (
            <div className="text-center py-12">
              <svg className="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"></path>
              </svg>
              <p className="text-gray-600">No links added yet. Add your first Google Drive link above!</p>
            </div>
          ) : (
            <div className="space-y-3">
              {links.map((link) => (
                <div key={link.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition duration-200">
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-3">
                        <button
                          onClick={() => openLink(link.url)}
                          className="text-indigo-600 hover:text-indigo-800 font-medium text-left truncate max-w-xs sm:max-w-md"
                        >
                          {link.name}
                        </button>
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          link.access_level === 'Public' ? 'bg-green-100 text-green-800' :
                          link.access_level === 'Anyone with link' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {link.access_level}
                        </span>
                      </div>
                      <p className="text-sm text-gray-500 truncate mt-1">
                        {link.url}
                      </p>
                    </div>
                    
                    <button
                      onClick={() => handleDelete(link.id)}
                      className="ml-4 text-red-500 hover:text-red-700 p-2 rounded-full hover:bg-red-50 transition duration-200"
                      title="Delete link"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                      </svg>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

// Auth callback handler
const AuthCallbackHandler = () => {
  const { handleAuthCallback } = useAuth();

  useEffect(() => {
    // Check for session_id in URL fragment
    const fragment = window.location.hash.substring(1);
    const params = new URLSearchParams(fragment);
    const sessionId = params.get('session_id');

    if (sessionId) {
      handleAuthCallback(sessionId);
    }
  }, [handleAuthCallback]);

  return null;
};

function App() {
  return (
    <div className="App">
      <AuthProvider>
        <AuthCallbackHandler />
        <VaultLinksApp />
      </AuthProvider>
    </div>
  );
}

export default App;