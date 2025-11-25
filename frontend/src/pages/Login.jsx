import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import '../App.css'

function Login() {
  const [isLogin, setIsLogin] = useState(true)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [email, setEmail] = useState('')
  const [fullName, setFullName] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [showOtp, setShowOtp] = useState(false)
  const [otpCode, setOtpCode] = useState('')
  const [sessionToken, setSessionToken] = useState(null)
  const [otpMessage, setOtpMessage] = useState('')
  
  const { login, verifyOtp, register } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      if (isLogin) {
        if (showOtp) {
          // Step 2: Verify OTP
          const result = await verifyOtp(sessionToken, otpCode)
          if (result.success) {
            navigate('/dashboard')
          } else {
            setError(result.error)
          }
        } else {
          // Step 1: Verify password and get OTP
          const result = await login(username, password)
          if (result.success && result.requiresOtp) {
            setSessionToken(result.sessionToken)
            setOtpMessage(result.message)
            setShowOtp(true)
            setError('')
          } else {
            setError(result.error)
          }
        }
      } else {
        const result = await register({
          username,
          password,
          email,
          full_name: fullName
        })
        if (result.success) {
          if (result.requiresLogin) {
            // Switch to login mode after successful registration
            setIsLogin(true)
            setError('')
            setEmail('')
            setFullName('')
            setPassword('')
            setUsername('')
            // Show success message
            setError(result.message || 'Registration successful. Please login.')
            setTimeout(() => setError(''), 3000)
          } else {
            navigate('/dashboard')
          }
        } else {
          setError(result.error)
        }
      }
    } catch (err) {
      setError('An unexpected error occurred')
    } finally {
      setLoading(false)
    }
  }

  const handleBackToLogin = () => {
    setShowOtp(false)
    setOtpCode('')
    setSessionToken(null)
    setOtpMessage('')
    setError('')
  }

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '2rem'
    }}>
      <div className="card" style={{
        maxWidth: '400px',
        width: '100%',
        padding: '2.5rem'
      }}>
        <h1 style={{
          textAlign: 'center',
          marginBottom: '0.5rem',
          color: '#333',
          fontSize: '2rem'
        }}>
          MP Cost Pulse
        </h1>
        <p style={{
          textAlign: 'center',
          color: '#666',
          marginBottom: '2rem',
          fontSize: '0.9rem'
        }}>
          {isLogin ? 'Sign in to your account' : 'Create a new account'}
        </p>

        <div style={{
          display: 'flex',
          gap: '1rem',
          marginBottom: '2rem',
          borderBottom: '2px solid #eee',
          paddingBottom: '1rem'
        }}>
          <button
            type="button"
            onClick={() => {
              setIsLogin(true)
              setError('')
              setShowOtp(false)
              setOtpCode('')
              setSessionToken(null)
            }}
            style={{
              flex: 1,
              padding: '0.75rem',
              border: 'none',
              background: isLogin ? '#667eea' : 'transparent',
              color: isLogin ? 'white' : '#666',
              borderRadius: '4px',
              cursor: 'pointer',
              fontWeight: '500',
              transition: 'all 0.2s'
            }}
          >
            Login
          </button>
          <button
            type="button"
            onClick={() => {
              setIsLogin(false)
              setError('')
              setShowOtp(false)
              setOtpCode('')
              setSessionToken(null)
            }}
            style={{
              flex: 1,
              padding: '0.75rem',
              border: 'none',
              background: !isLogin ? '#667eea' : 'transparent',
              color: !isLogin ? 'white' : '#666',
              borderRadius: '4px',
              cursor: 'pointer',
              fontWeight: '500',
              transition: 'all 0.2s'
            }}
          >
            Register
          </button>
        </div>

        {error && (
          <div className="error" style={{ marginBottom: '1rem' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {!isLogin && (
            <>
              <div style={{ marginBottom: '1rem' }}>
                <label style={{
                  display: 'block',
                  marginBottom: '0.5rem',
                  color: '#333',
                  fontWeight: '500'
                }}>
                  Full Name
                </label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    fontSize: '1rem',
                    boxSizing: 'border-box'
                  }}
                  placeholder="Enter your full name"
                />
              </div>
              <div style={{ marginBottom: '1rem' }}>
                <label style={{
                  display: 'block',
                  marginBottom: '0.5rem',
                  color: '#333',
                  fontWeight: '500'
                }}>
                  Email
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required={!isLogin}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    fontSize: '1rem',
                    boxSizing: 'border-box'
                  }}
                  placeholder="Enter your email"
                />
              </div>
            </>
          )}

          <div style={{ marginBottom: '1rem' }}>
            <label style={{
              display: 'block',
              marginBottom: '0.5rem',
              color: '#333',
              fontWeight: '500'
            }}>
              Username
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              style={{
                width: '100%',
                padding: '0.75rem',
                border: '1px solid #ddd',
                borderRadius: '4px',
                fontSize: '1rem',
                boxSizing: 'border-box'
              }}
              placeholder="Enter your username"
            />
          </div>

          {!showOtp ? (
            <>
              <div style={{ marginBottom: '1.5rem' }}>
                <label style={{
                  display: 'block',
                  marginBottom: '0.5rem',
                  color: '#333',
                  fontWeight: '500'
                }}>
                  Password
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    fontSize: '1rem',
                    boxSizing: 'border-box'
                  }}
                  placeholder="Enter your password"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  fontSize: '1rem',
                  fontWeight: '600',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  opacity: loading ? 0.7 : 1,
                  transition: 'opacity 0.2s'
                }}
              >
                {loading ? 'Please wait...' : (isLogin ? 'Sign In' : 'Sign Up')}
              </button>
            </>
          ) : (
            <>
              {otpMessage && (
                <div style={{
                  marginBottom: '1rem',
                  padding: '0.75rem',
                  background: '#e3f2fd',
                  border: '1px solid #2196f3',
                  borderRadius: '4px',
                  color: '#1976d2',
                  fontSize: '0.9rem'
                }}>
                  {otpMessage}
                </div>
              )}
              <div style={{ marginBottom: '1.5rem' }}>
                <label style={{
                  display: 'block',
                  marginBottom: '0.5rem',
                  color: '#333',
                  fontWeight: '500'
                }}>
                  Enter Verification Code
                </label>
                <input
                  type="text"
                  value={otpCode}
                  onChange={(e) => setOtpCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                  required
                  maxLength={6}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    fontSize: '1.5rem',
                    letterSpacing: '0.5rem',
                    textAlign: 'center',
                    boxSizing: 'border-box',
                    fontWeight: '600'
                  }}
                  placeholder="000000"
                />
                <p style={{
                  marginTop: '0.5rem',
                  fontSize: '0.85rem',
                  color: '#666',
                  textAlign: 'center'
                }}>
                  Enter the 6-digit code sent to your email
                </p>
              </div>

              <button
                type="submit"
                disabled={loading || otpCode.length !== 6}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  fontSize: '1rem',
                  fontWeight: '600',
                  cursor: (loading || otpCode.length !== 6) ? 'not-allowed' : 'pointer',
                  opacity: (loading || otpCode.length !== 6) ? 0.7 : 1,
                  transition: 'opacity 0.2s',
                  marginBottom: '0.5rem'
                }}
              >
                {loading ? 'Verifying...' : 'Verify Code'}
              </button>

              <button
                type="button"
                onClick={handleBackToLogin}
                disabled={loading}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  background: 'transparent',
                  color: '#667eea',
                  border: '1px solid #667eea',
                  borderRadius: '4px',
                  fontSize: '0.9rem',
                  fontWeight: '500',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  opacity: loading ? 0.7 : 1,
                  transition: 'opacity 0.2s'
                }}
              >
                Back to Login
              </button>
            </>
          )}
        </form>
      </div>
    </div>
  )
}

export default Login

