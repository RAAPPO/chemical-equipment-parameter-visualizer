import { createContext, useState, useContext, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in on mount
    const token = localStorage.getItem('access_token');
    if (token) {
      setUser({ username: localStorage.getItem('username') || 'User' });
    }
    setLoading(false);
  }, []);

  const login = async (username, password) => {
    try {
      const response = await authAPI.login(username, password);

      /**
       * FIXED: Support for both nested and flat response structures.
       * Your authAPI.login returns response.data directly, so tokens 
       * are usually found at response.access. This check handles both 
       * local and production variations safely.
       */
      const accessToken = response.access || response.data?.access;
      const refreshToken = response.refresh || response.data?.refresh;

      if (!accessToken) {
        throw new Error('Authentication failed: No access token received from server.');
      }

      // Save credentials to local storage
      localStorage.setItem('access_token', accessToken);
      localStorage.setItem('refresh_token', refreshToken);
      localStorage.setItem('username', username);

      setUser({ username });
      return { success: true };
    } catch (error) {
      // Provide specific error messages for better debugging
      let errorMessage = 'Login failed';

      if (error.response?.status === 401) {
        errorMessage = 'Invalid username or password.';
      } else if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.message) {
        errorMessage = error.message;
      }

      return {
        success: false,
        error: errorMessage
      };
    }
  };

  const logout = () => {
    authAPI.logout();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};