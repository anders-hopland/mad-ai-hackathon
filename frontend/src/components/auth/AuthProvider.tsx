'use client';

import { ReactNode, useEffect, useState } from 'react';
import { AuthContext, User, getToken, removeToken, setToken } from '@/lib/auth';

interface AuthProviderProps {
  children: ReactNode;
}

export default function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for token in URL (from OAuth callback)
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    
    if (token) {
      setToken(token);
      // Remove token from URL
      window.history.replaceState({}, document.title, window.location.pathname);
    }

    // Try to get user info if we have a token
    fetchUser();
  }, []);

  const fetchUser = async () => {
    const token = getToken();
    if (!token) {
      setIsLoading(false);
      return;
    }

    try {
      const response = await fetch('http://localhost:8000/auth/me', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      } else {
        // Token is invalid
        removeToken();
      }
    } catch (error) {
      console.error('Failed to fetch user:', error);
      removeToken();
    } finally {
      setIsLoading(false);
    }
  };

  const login = () => {
    window.location.href = 'http://localhost:8000/auth/google';
  };

  const logout = () => {
    removeToken();
    setUser(null);
    window.location.href = '/';
  };

  const value = {
    user,
    login,
    logout,
    isLoading,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}