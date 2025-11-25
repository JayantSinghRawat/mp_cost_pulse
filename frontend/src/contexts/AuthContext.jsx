import React, { createContext, useState, useContext, useEffect } from 'react'
import { authAPI } from '../services/api'

const AuthContext = createContext(null)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(localStorage.getItem('token'))
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check if user is logged in on mount
    if (token) {
      fetchCurrentUser()
    } else {
      setLoading(false)
    }
  }, [token])

  const fetchCurrentUser = async () => {
    try {
      const response = await authAPI.getCurrentUser()
      setUser(response.data)
    } catch (error) {
      // Token is invalid, clear it
      logout()
    } finally {
      setLoading(false)
    }
  }

  const login = async (username, password) => {
    try {
      const response = await authAPI.login(username, password)
      // Step 1: Password verified, OTP sent - return session token
      return { 
        success: true, 
        requiresOtp: true,
        sessionToken: response.data.session_token,
        message: response.data.message
      }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Login failed'
      }
    }
  }

  const verifyOtp = async (sessionToken, otpCode) => {
    try {
      const response = await authAPI.verifyOtp(sessionToken, otpCode)
      const { access_token } = response.data
      localStorage.setItem('token', access_token)
      setToken(access_token)
      await fetchCurrentUser()
      return { success: true }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'OTP verification failed'
      }
    }
  }

  const register = async (userData) => {
    try {
      const response = await authAPI.register(userData)
      // After registration, user needs to login with 2FA
      // Return success but indicate login is required
      return { 
        success: true, 
        user: response.data,
        requiresLogin: true,
        message: 'Registration successful. Please login to continue.'
      }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Registration failed'
      }
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    setToken(null)
    setUser(null)
  }

  const value = {
    user,
    token,
    loading,
    login,
    verifyOtp,
    register,
    logout,
    isAuthenticated: !!token && !!user
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

