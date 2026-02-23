"use client";

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { getCookie } from '@/lib/api/cookies';
import { authAPI, RegisterData, RegisterResponse } from '@/lib/api/auth';
import { useRouter } from 'next/navigation';

interface User {
  id: string;
  role: 'patient' | 'nurse' | 'admin';
  name?: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (credentials: any) => Promise<void>;
  register: (data: RegisterData) => Promise<RegisterResponse>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  isLoading: true,
  login: async () => {},
  register: async () => ({ user: {} as any, tokens: { access: '', refresh: '' } }),
  logout: () => {},
  isAuthenticated: false,
});

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  // Extract user info from JWT
  const setUserFromToken = useCallback((accessToken: string) => {
    const userInfo = authAPI.getUserFromToken(accessToken);
    if (userInfo) {
      setUser(userInfo);
    }
  }, []);

  useEffect(() => {
    const initAuth = async () => {
      const accessToken = getCookie('access_token');
      if (accessToken) {
        try {
          setUserFromToken(accessToken);
        } catch {
          authAPI.logout();
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, [setUserFromToken]);

  const login = async (credentials: any) => {
    setIsLoading(true);
    try {
      const res = await authAPI.login(credentials);
      if (res.access) {
        setUserFromToken(res.access);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (data: RegisterData): Promise<RegisterResponse> => {
    setIsLoading(true);
    try {
      const res = await authAPI.register(data);
      if (res.tokens?.access) {
        setUserFromToken(res.tokens.access);
      }
      return res;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    authAPI.logout();
    setUser(null);
    router.push('/login');
  };

  return (
    <AuthContext.Provider value={{
      user,
      isLoading,
      login,
      register,
      logout,
      isAuthenticated: !!user,
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
