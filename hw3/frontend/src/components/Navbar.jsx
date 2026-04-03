/**
 * Global Navbar:
 * - Left: Logo + App Name
 * - Right: Nav links + Avatar button -> dropdown (Profile / Logout)
 */
import { useState, useRef, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { User, LogOut, LayoutDashboard, ListChecks, Zap, ChevronDown } from 'lucide-react'
import { useAuthStore } from '../store/authStore'

export default function Navbar({ onOpenAuth }) {
  const { user, logout } = useAuthStore()
  const isLoggedIn = !!user
  const navigate = useNavigate()

  const [dropdownOpen, setDropdownOpen] = useState(false)
  const dropRef = useRef(null)

  // Close dropdown on outside click
  useEffect(() => {
    const handler = (e) => {
      if (dropRef.current && !dropRef.current.contains(e.target)) {
        setDropdownOpen(false)
      }
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const handleAvatarClick = () => {
    if (isLoggedIn) setDropdownOpen((v) => !v)
    else onOpenAuth()
  }

  const handleLogout = () => {
    logout()
    setDropdownOpen(false)
    navigate('/')
  }

  return (
    <nav className="fixed top-0 left-0 right-0 z-40 h-16">
      {/* Glassmorphism bar */}
      <div className="h-full glass border-b border-cyan-900/30 px-6 flex items-center justify-between">
        {/* ── Logo ──────────────────────────────── */}
        <Link to="/" className="flex items-center gap-2.5 group">
          <div className="relative w-8 h-8 flex items-center justify-center">
            <div className="absolute inset-0 bg-cyan-500/20 rounded-lg blur-sm group-hover:bg-cyan-500/30 transition-all" />
            <Zap size={18} className="relative text-cyan-400" />
          </div>
          <span className="font-display font-bold text-lg tracking-tight">
            Comp<span className="text-neon">Arena</span>
          </span>
        </Link>

        {/* ── Right side ────────────────────────── */}
        <div className="flex items-center gap-6">
          {/* Nav links (desktop) */}
          <div className="hidden sm:flex items-center gap-5">
            <Link
              to="/"
              className="flex items-center gap-1.5 text-sm text-slate-400 hover:text-cyan-400 transition-colors font-display"
            >
              <LayoutDashboard size={15} />
              Dashboard
            </Link>

            {/* NOU: Link către pagina globală de Submissions */}
            <Link
              to="/submissions"
              className="flex items-center gap-1.5 text-sm text-slate-400 hover:text-cyan-400 transition-colors font-display"
            >
              <ListChecks size={15} />
              Submissions
            </Link>
          </div>

          {/* Avatar button + dropdown */}
          <div className="relative" ref={dropRef}>
            <motion.button
              onClick={handleAvatarClick}
              className="flex items-center gap-2 pl-3 pr-2.5 py-1.5 rounded-xl glass border border-cyan-900/40 hover:border-cyan-500/30 transition-all"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.97 }}
            >
              <div className="w-6 h-6 rounded-full bg-gradient-to-br from-cyan-400 to-cyan-600 flex items-center justify-center">
                <User size={13} className="text-surface-0" />
              </div>
              {isLoggedIn && (
                <>
                  <span className="text-sm font-display text-slate-200 hidden sm:inline max-w-[120px] truncate">
                    {user.name}
                  </span>
                  <ChevronDown
                    size={13}
                    className={`text-slate-400 transition-transform ${dropdownOpen ? 'rotate-180' : ''}`}
                  />
                </>
              )}
              {!isLoggedIn && (
                <span className="text-sm font-display text-slate-300">Sign In</span>
              )}
            </motion.button>

            {/* Dropdown menu */}
            <AnimatePresence>
              {dropdownOpen && isLoggedIn && (
                <motion.div
                  className="absolute right-0 top-full mt-2 w-48 glass-strong rounded-xl overflow-hidden shadow-cyan-md"
                  initial={{ opacity: 0, y: -8, scale: 0.97 }}
                  animate={{ opacity: 1, y: 0,  scale: 1    }}
                  exit={{    opacity: 0, y: -8, scale: 0.97 }}
                  transition={{ duration: 0.15, ease: 'easeOut' }}
                >
                  {/* User info header */}
                  <div className="px-4 py-3 border-b border-cyan-900/30">
                    <p className="text-sm font-display font-medium text-white truncate">{user.name}</p>
                    <p className="text-xs text-slate-500 truncate mt-0.5">{user.email}</p>
                  </div>

                  {/* Menu items */}
                  <div className="py-1">
                    <button
                      onClick={() => { navigate('/profile'); setDropdownOpen(false) }}
                      className="w-full flex items-center gap-2.5 px-4 py-2.5 text-sm text-slate-300 hover:text-white hover:bg-cyan-500/10 transition-colors"
                    >
                      <User size={14} className="text-cyan-400" />
                      My Profile
                    </button>
                    <button
                      onClick={handleLogout}
                      className="w-full flex items-center gap-2.5 px-4 py-2.5 text-sm text-rose-400 hover:text-rose-300 hover:bg-rose-500/10 transition-colors"
                    >
                      <LogOut size={14} />
                      Sign Out
                    </button>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </nav>
  )
}