/**
 * App.jsx — Root component.
 * Sets up React Router, global layout (Navbar), AuthModal, and page transitions.
 */
import { useState } from 'react'
import { Routes, Route, useLocation } from 'react-router-dom'
import { AnimatePresence } from 'framer-motion'
import Navbar from './components/Navbar'
import AuthModal from './components/AuthModal'
import PageTransition from './components/PageTransition'
import ProtectedRoute from './components/ProtectedRoute'
import Dashboard from './pages/Dashboard'
import AssignmentDetails from './pages/AssignmentDetails'
import Profile from './pages/Profile'

export default function App() {
  const [authOpen, setAuthOpen] = useState(false)
  const location = useLocation()

  return (
    <>
      {/* ── Global Navbar ─────────────────────────────────────────────── */}
      <Navbar onOpenAuth={() => setAuthOpen(true)} />

      {/* ── Auth Modal ────────────────────────────────────────────────── */}
      <AuthModal isOpen={authOpen} onClose={() => setAuthOpen(false)} />

      {/* ── Pages with animated transitions ──────────────────────────── */}
      <AnimatePresence mode="wait">
        <Routes location={location} key={location.pathname}>

          {/* Dashboard */}
          <Route
            path="/"
            element={
              <PageTransition>
                <Dashboard />
              </PageTransition>
            }
          />

          {/* Assignment Details */}
          <Route
            path="/assignment/:id"
            element={
              <PageTransition>
                <AssignmentDetails />
              </PageTransition>
            }
          />

          {/* Profile (protected) */}
          <Route
            path="/profile"
            element={
              <PageTransition>
                <ProtectedRoute onOpenAuth={() => setAuthOpen(true)}>
                  <Profile />
                </ProtectedRoute>
              </PageTransition>
            }
          />

          {/* 404 */}
          <Route
            path="*"
            element={
              <PageTransition>
                <div className="flex flex-col items-center justify-center min-h-screen gap-4">
                  <p className="font-display text-6xl font-bold text-surface-4">404</p>
                  <p className="text-slate-500">Page not found.</p>
                  <a href="/" className="btn-cyan">Go Home</a>
                </div>
              </PageTransition>
            }
          />
        </Routes>
      </AnimatePresence>
    </>
  )
}
