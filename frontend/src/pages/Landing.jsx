import React from 'react'
import { Link } from 'react-router-dom'
import '../App.css'

function Landing() {
  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Background decoration */}
      <div style={{
        position: 'absolute',
        top: '-50%',
        right: '-50%',
        width: '100%',
        height: '200%',
        background: 'radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%)',
        animation: 'pulse 20s ease-in-out infinite'
      }} />
      
      <div style={{
        position: 'relative',
        zIndex: 1,
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '2rem'
      }}>
        {/* Header */}
        <header style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '2rem 0',
          marginBottom: '4rem'
        }}>
          <div style={{
            fontSize: '2rem',
            fontWeight: 'bold',
            color: 'white'
          }}>
            MP Cost Pulse
          </div>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <Link
              to="/login"
              style={{
                padding: '0.75rem 1.5rem',
                background: 'rgba(255,255,255,0.2)',
                border: '1px solid rgba(255,255,255,0.3)',
                color: 'white',
                borderRadius: '8px',
                textDecoration: 'none',
                fontWeight: '500',
                transition: 'all 0.3s',
                backdropFilter: 'blur(10px)'
              }}
              onMouseEnter={(e) => {
                e.target.style.background = 'rgba(255,255,255,0.3)'
              }}
              onMouseLeave={(e) => {
                e.target.style.background = 'rgba(255,255,255,0.2)'
              }}
            >
              Login
            </Link>
            <Link
              to="/login"
              style={{
                padding: '0.75rem 1.5rem',
                background: 'white',
                color: '#667eea',
                borderRadius: '8px',
                textDecoration: 'none',
                fontWeight: '600',
                transition: 'all 0.3s',
                boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
              }}
              onMouseEnter={(e) => {
                e.target.style.transform = 'translateY(-2px)'
                e.target.style.boxShadow = '0 6px 16px rgba(0,0,0,0.2)'
              }}
              onMouseLeave={(e) => {
                e.target.style.transform = 'translateY(0)'
                e.target.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)'
              }}
            >
              Get Started
            </Link>
          </div>
        </header>

        {/* Hero Section */}
        <section style={{
          textAlign: 'center',
          color: 'white',
          marginBottom: '6rem',
          padding: '2rem 0'
        }}>
          <h1 style={{
            fontSize: 'clamp(2.5rem, 5vw, 4rem)',
            fontWeight: '800',
            marginBottom: '1.5rem',
            lineHeight: '1.2',
            textShadow: '0 2px 20px rgba(0,0,0,0.2)'
          }}>
            Find Your Perfect City
            <br />
            <span style={{ color: '#ffd700' }}>Predict Your Cost of Living</span>
          </h1>
          <p style={{
            fontSize: 'clamp(1.1rem, 2vw, 1.5rem)',
            marginBottom: '2.5rem',
            opacity: 0.95,
            maxWidth: '700px',
            margin: '0 auto 2.5rem',
            lineHeight: '1.6'
          }}>
            Make informed decisions about where to live. Compare costs across cities,
            predict your expenses, and discover which location offers the best value for your lifestyle.
          </p>
          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
            <Link
              to="/login"
              style={{
                padding: '1rem 2.5rem',
                background: 'white',
                color: '#667eea',
                borderRadius: '12px',
                textDecoration: 'none',
                fontWeight: '700',
                fontSize: '1.1rem',
                transition: 'all 0.3s',
                boxShadow: '0 6px 20px rgba(0,0,0,0.2)',
                display: 'inline-block'
              }}
              onMouseEnter={(e) => {
                e.target.style.transform = 'translateY(-3px) scale(1.05)'
                e.target.style.boxShadow = '0 8px 25px rgba(0,0,0,0.3)'
              }}
              onMouseLeave={(e) => {
                e.target.style.transform = 'translateY(0) scale(1)'
                e.target.style.boxShadow = '0 6px 20px rgba(0,0,0,0.2)'
              }}
            >
              Start Exploring →
            </Link>
          </div>
        </section>

        {/* Features Section */}
        <section style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '2rem',
          marginBottom: '4rem'
        }}>
          <div style={{
            background: 'rgba(255,255,255,0.15)',
            backdropFilter: 'blur(10px)',
            borderRadius: '16px',
            padding: '2rem',
            border: '1px solid rgba(255,255,255,0.2)',
            transition: 'all 0.3s'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateY(-5px)'
            e.currentTarget.style.background = 'rgba(255,255,255,0.2)'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateY(0)'
            e.currentTarget.style.background = 'rgba(255,255,255,0.15)'
          }}
          >
            <div style={{
              fontSize: '3rem',
              marginBottom: '1rem'
            }}>🏙️</div>
            <h3 style={{
              fontSize: '1.5rem',
              fontWeight: '700',
              marginBottom: '1rem',
              color: 'white'
            }}>
              City Comparison
            </h3>
            <p style={{
              color: 'rgba(255,255,255,0.9)',
              lineHeight: '1.6',
              fontSize: '1rem'
            }}>
              Compare cost of living across multiple cities side-by-side. See rent prices,
              grocery costs, transportation expenses, and more.
            </p>
          </div>

          <div style={{
            background: 'rgba(255,255,255,0.15)',
            backdropFilter: 'blur(10px)',
            borderRadius: '16px',
            padding: '2rem',
            border: '1px solid rgba(255,255,255,0.2)',
            transition: 'all 0.3s'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateY(-5px)'
            e.currentTarget.style.background = 'rgba(255,255,255,0.2)'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateY(0)'
            e.currentTarget.style.background = 'rgba(255,255,255,0.15)'
          }}
          >
            <div style={{
              fontSize: '3rem',
              marginBottom: '1rem'
            }}>🔮</div>
            <h3 style={{
              fontSize: '1.5rem',
              fontWeight: '700',
              marginBottom: '1rem',
              color: 'white'
            }}>
              AI-Powered Predictions
            </h3>
            <p style={{
              color: 'rgba(255,255,255,0.9)',
              lineHeight: '1.6',
              fontSize: '1rem'
            }}>
              Get personalized cost predictions based on your lifestyle, income, and preferences.
              Our ML models help you plan your budget accurately.
            </p>
          </div>

          <div style={{
            background: 'rgba(255,255,255,0.15)',
            backdropFilter: 'blur(10px)',
            borderRadius: '16px',
            padding: '2rem',
            border: '1px solid rgba(255,255,255,0.2)',
            transition: 'all 0.3s'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateY(-5px)'
            e.currentTarget.style.background = 'rgba(255,255,255,0.2)'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateY(0)'
            e.currentTarget.style.background = 'rgba(255,255,255,0.15)'
          }}
          >
            <div style={{
              fontSize: '3rem',
              marginBottom: '1rem'
            }}>📊</div>
            <h3 style={{
              fontSize: '1.5rem',
              fontWeight: '700',
              marginBottom: '1rem',
              color: 'white'
            }}>
              Cost Burden Analysis
            </h3>
            <p style={{
              color: 'rgba(255,255,255,0.9)',
              lineHeight: '1.6',
              fontSize: '1rem'
            }}>
              Understand your cost burden index and see how affordable different localities are
              for your income level. Make data-driven relocation decisions.
            </p>
          </div>
        </section>

        {/* How It Works Section */}
        <section style={{
          background: 'rgba(255,255,255,0.1)',
          backdropFilter: 'blur(10px)',
          borderRadius: '20px',
          padding: '3rem',
          marginBottom: '4rem',
          border: '1px solid rgba(255,255,255,0.2)'
        }}>
          <h2 style={{
            fontSize: '2.5rem',
            fontWeight: '700',
            textAlign: 'center',
            marginBottom: '3rem',
            color: 'white'
          }}>
            How It Works
          </h2>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: '2rem'
          }}>
            {[
              { step: '1', title: 'Sign Up', desc: 'Create your account and set up your profile' },
              { step: '2', title: 'Explore Cities', desc: 'Browse and compare different cities and localities' },
              { step: '3', title: 'Get Predictions', desc: 'Receive AI-powered cost predictions tailored to you' },
              { step: '4', title: 'Make Decisions', desc: 'Use insights to choose the best city for your lifestyle' }
            ].map((item, idx) => (
              <div key={idx} style={{
                textAlign: 'center',
                padding: '1.5rem'
              }}>
                <div style={{
                  width: '60px',
                  height: '60px',
                  borderRadius: '50%',
                  background: 'white',
                  color: '#667eea',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '1.5rem',
                  fontWeight: 'bold',
                  margin: '0 auto 1rem',
                  boxShadow: '0 4px 12px rgba(0,0,0,0.2)'
                }}>
                  {item.step}
                </div>
                <h3 style={{
                  fontSize: '1.25rem',
                  fontWeight: '600',
                  marginBottom: '0.5rem',
                  color: 'white'
                }}>
                  {item.title}
                </h3>
                <p style={{
                  color: 'rgba(255,255,255,0.85)',
                  fontSize: '0.95rem',
                  lineHeight: '1.5'
                }}>
                  {item.desc}
                </p>
              </div>
            ))}
          </div>
        </section>

        {/* CTA Section */}
        <section style={{
          textAlign: 'center',
          padding: '4rem 2rem',
          background: 'rgba(255,255,255,0.1)',
          backdropFilter: 'blur(10px)',
          borderRadius: '20px',
          border: '1px solid rgba(255,255,255,0.2)',
          marginBottom: '2rem'
        }}>
          <h2 style={{
            fontSize: '2.5rem',
            fontWeight: '700',
            marginBottom: '1rem',
            color: 'white'
          }}>
            Ready to Find Your Perfect City?
          </h2>
          <p style={{
            fontSize: '1.2rem',
            marginBottom: '2rem',
            color: 'rgba(255,255,255,0.9)'
          }}>
            Join thousands of users making smarter relocation decisions
          </p>
          <Link
            to="/login"
            style={{
              padding: '1.2rem 3rem',
              background: 'white',
              color: '#667eea',
              borderRadius: '12px',
              textDecoration: 'none',
              fontWeight: '700',
              fontSize: '1.2rem',
              transition: 'all 0.3s',
              boxShadow: '0 6px 20px rgba(0,0,0,0.2)',
              display: 'inline-block'
            }}
            onMouseEnter={(e) => {
              e.target.style.transform = 'translateY(-3px) scale(1.05)'
              e.target.style.boxShadow = '0 8px 25px rgba(0,0,0,0.3)'
            }}
            onMouseLeave={(e) => {
              e.target.style.transform = 'translateY(0) scale(1)'
              e.target.style.boxShadow = '0 6px 20px rgba(0,0,0,0.2)'
            }}
          >
            Get Started Free →
          </Link>
        </section>

        {/* Footer */}
        <footer style={{
          textAlign: 'center',
          padding: '2rem',
          color: 'rgba(255,255,255,0.8)',
          fontSize: '0.9rem'
        }}>
          <p>© 2024 MP Cost Pulse. Helping you make informed relocation decisions.</p>
        </footer>
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 0.5; transform: scale(1); }
          50% { opacity: 0.8; transform: scale(1.1); }
        }
      `}</style>
    </div>
  )
}

export default Landing

