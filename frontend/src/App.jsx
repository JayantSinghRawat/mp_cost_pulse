import React from 'react'
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import Landing from './pages/Landing'
import Dashboard from './pages/Dashboard'
import LocalityComparison from './pages/LocalityComparison'
import CostBurdenIndex from './pages/CostBurdenIndex'
import UserProfile from './pages/UserProfile'
import ScrapedData from './pages/ScrapedData'
import Login from './pages/Login'
import NeighborhoodRecommendations from './pages/NeighborhoodRecommendations'
import './App.css'

function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth()
  
  if (loading) {
    return <div className="loading">Loading...</div>
  }
  
  if (isAuthenticated) {
    return children
  }
  return <Navigate to="/login" replace />
}

function Navbar() {
  const { user, logout, isAuthenticated } = useAuth()
  
  if (!isAuthenticated) {
    return null
  }
  
  return (
    <nav className="navbar">
      <div className="nav-container">
        <Link to="/" className="nav-logo">
          MP Cost Pulse
        </Link>
        <div style={{ display: 'flex', alignItems: 'center', gap: '2rem' }}>
          <div className="nav-links">
            <Link to="/dashboard" className="nav-link">Dashboard</Link>
            <Link to="/recommendations" className="nav-link">Find Neighborhood</Link>
            <Link to="/comparison" className="nav-link">Locality Comparison</Link>
            <Link to="/cost-burden" className="nav-link">Cost Burden Index</Link>
            <Link to="/profile" className="nav-link">Cost Prediction</Link>
            <Link to="/scraped-data" className="nav-link">Scraped Data</Link>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <span style={{ color: 'white', fontSize: '0.9rem' }}>
              {user?.full_name || user?.username}
            </span>
            <button
              onClick={logout}
              style={{
                background: 'rgba(255,255,255,0.2)',
                border: '1px solid rgba(255,255,255,0.3)',
                color: 'white',
                padding: '0.5rem 1rem',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '0.9rem'
              }}
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  )
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="app">
          <Navbar />
          <main className="main-content">
            <Routes>
              <Route path="/landing" element={<Landing />} />
              <Route path="/login" element={<Login />} />
              <Route 
                path="/dashboard" 
                element={
                  <ProtectedRoute>
                    <Dashboard />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/" 
                element={<Navigate to="/landing" replace />}
              />
              <Route 
                path="/comparison" 
                element={
                  <ProtectedRoute>
                    <LocalityComparison />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/cost-burden" 
                element={
                  <ProtectedRoute>
                    <CostBurdenIndex />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/profile" 
                element={
                  <ProtectedRoute>
                    <UserProfile />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/recommendations" 
                element={
                  <ProtectedRoute>
                    <NeighborhoodRecommendations />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/scraped-data" 
                element={
                  <ProtectedRoute>
                    <ScrapedData />
                  </ProtectedRoute>
                } 
              />
            </Routes>
          </main>
        </div>
      </Router>
    </AuthProvider>
  )
}

export default App

