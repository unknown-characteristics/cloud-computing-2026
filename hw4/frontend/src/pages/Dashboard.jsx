/**
 * Dashboard / Home Page
 * - Animated hero with floating 3D-like cyan particles
 * - Fuzzy-search bar with type + status filters
 * - Assignment feed grid
 * - "Create Assignment" FAB (logged-in only)
 */
import { useState, useMemo } from 'react'
import { motion } from 'framer-motion'
import { Search, Plus, SlidersHorizontal, Filter, Trophy, Zap, Users } from 'lucide-react'
import { useAssignments } from '../hooks/useAssignments'
import { useAuthStore } from '../store/authStore'
import AssignmentCard from '../components/AssignmentCard'
import AssignmentFormModal from '../components/AssignmentFormModal'
import { SkeletonCard } from '../components/ui/Skeleton'
import { fuzzySearch } from '../lib/levenshtein'
import { isPast, isFuture } from 'date-fns'

// ── Particle background ──────────────────────────────────────────────────────
function Particles() {
  const particles = [
    { size: 120, x: '10%',  y: '20%', dur: '7s',  del: '0s'   },
    { size: 80,  x: '80%',  y: '15%', dur: '9s',  del: '1s'   },
    { size: 200, x: '60%',  y: '60%', dur: '11s', del: '2s'   },
    { size: 60,  x: '25%',  y: '75%', dur: '8s',  del: '0.5s' },
    { size: 140, x: '88%',  y: '70%', dur: '10s', del: '3s'   },
    { size: 40,  x: '45%',  y: '30%', dur: '6s',  del: '1.5s' },
  ]

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {particles.map((p, i) => (
        <div
          key={i}
          className="particle absolute rounded-full"
          style={{
            left: p.x,
            top: p.y,
            width: p.size,
            height: p.size,
            '--duration': p.dur,
            '--delay':    p.del,
            background: `radial-gradient(circle, rgba(6,182,212,${0.08 + (i % 3) * 0.04}) 0%, transparent 70%)`,
            border: '1px solid rgba(6,182,212,0.08)',
            transform: 'translate(-50%, -50%)',
          }}
        />
      ))}
      {/* Grid overlay */}
      <div
        className="absolute inset-0 bg-grid-cyan bg-grid opacity-40"
        style={{ maskImage: 'radial-gradient(ellipse at center, black 30%, transparent 80%)' }}
      />
    </div>
  )
}

// ── Hero section ─────────────────────────────────────────────────────────────
function Hero({ onCreateClick, isLoggedIn }) {
  return (
    <section className="relative min-h-[420px] flex flex-col items-center justify-center text-center px-6 pt-24 pb-16">
      <Particles />

      <motion.div
        className="relative z-10 max-w-3xl mx-auto"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
      >
        {/* Eyebrow */}
        <motion.div
          className="inline-flex items-center gap-2 px-3 py-1.5 mb-6 badge-cyan"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
        >
          <Zap size={12} />
          <span className="text-xs font-mono">Competitive Programming Platform</span>
        </motion.div>

        {/* Heading */}
        <h1 className="font-display font-extrabold text-4xl sm:text-5xl lg:text-6xl text-white leading-tight mb-5">
          Compete.{' '}
          <span className="text-neon">Learn.</span>
          {' '}Rank.
        </h1>

        {/* Sub-heading */}
        <p className="text-slate-400 text-lg leading-relaxed mb-8 max-w-xl mx-auto">
          Site pentru participat la competiții, etc.
        </p>

        {/* Stats row */}
        <motion.div
          className="flex items-center justify-center gap-8 mb-10"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          {[
            { icon: Trophy,  label: 'Challenges' },
            { icon: Users,   label: 'Participants' },
            { icon: Zap,     label: 'Submissions' },
          ].map(({ icon: Icon, label }) => (
            <div key={label} className="flex flex-col items-center gap-1">
              <Icon size={20} className="text-cyan-500" />
              <span className="text-xs text-slate-500 font-display">{label}</span>
            </div>
          ))}
        </motion.div>

        {/* CTA */}
        {isLoggedIn ? (
          <motion.button
            onClick={onCreateClick}
            className="btn-cyan inline-flex items-center gap-2 px-8 py-3 text-base"
            whileHover={{ scale: 1.04 }}
            whileTap={{ scale: 0.97 }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
          >
            <Plus size={18} />
            Create Assignment
          </motion.button>
        ) : (
          <p className="text-sm text-slate-500">
            Sign in to create and submit assignments
          </p>
        )}
      </motion.div>
    </section>
  )
}

// ── Filter bar ───────────────────────────────────────────────────────────────
const STATUS_OPTIONS = [
  { value: '',       label: 'All'        },
  { value: 'active', label: 'Active'     },
  { value: 'closed', label: 'Closed'     },
  { value: 'future', label: 'Upcoming'   },
]

function getStatus(a) {
  const start = new Date(a.start_time)
  const stop  = new Date(a.stop_submit_time)
  if (isFuture(start))  return 'future'
  if (isPast(stop))     return 'closed'
  return 'active'
}

function FilterBar({ query, setQuery, typeFilter, setTypeFilter, statusFilter, setStatusFilter, types }) {
  return (
    <div className="flex flex-col sm:flex-row gap-3 mb-8">
      {/* Search */}
      <div className="relative flex-1">
        <Search size={15} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search assignments (fuzzy)…"
          className="input-field pl-10"
        />
      </div>

      {/* Status filter */}
      <div className="relative">
        <Filter size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none" />
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="input-field pl-8 pr-8 appearance-none cursor-pointer w-full sm:w-auto"
        >
          {STATUS_OPTIONS.map((o) => (
            <option key={o.value} value={o.value} className="bg-surface-2">{o.label}</option>
          ))}
        </select>
      </div>

      {/* Type filter */}
      {types.length > 0 && (
        <div className="relative">
          <SlidersHorizontal size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none" />
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="input-field pl-8 pr-8 appearance-none cursor-pointer w-full sm:w-auto"
          >
            <option value="" className="bg-surface-2">All Types</option>
            {types.map((t) => (
              <option key={t} value={t} className="bg-surface-2 capitalize">{t}</option>
            ))}
          </select>
        </div>
      )}
    </div>
  )
}

// ── Page ─────────────────────────────────────────────────────────────────────
export default function Dashboard() {
  const { user } = useAuthStore()
  const isLoggedIn = !!user

  const [createOpen, setCreateOpen] = useState(false)
  const [query, setQuery]           = useState('')
  const [typeFilter, setTypeFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')

  const { data: assignments = [], isLoading, isError } = useAssignments()

  // Collect unique types for filter dropdown
  const types = useMemo(
    () => [...new Set(assignments.map((a) => a.type).filter(Boolean))],
    [assignments]
  )

  // Apply status + type filters, then fuzzy search
  const filtered = useMemo(() => {
    let list = assignments

    if (statusFilter) {
      list = list.filter((a) => getStatus(a) === statusFilter)
    }
    if (typeFilter) {
      list = list.filter((a) => a.type === typeFilter)
    }

    return fuzzySearch(
      query,
      list,
      (a) => [a.name, a.description],
      { threshold: 0.4 }
    )
  }, [assignments, query, typeFilter, statusFilter])

  return (
    <div className="page-wrapper">
      {/* Hero */}
      <Hero onCreateClick={() => setCreateOpen(true)} isLoggedIn={isLoggedIn} />

      {/* Feed */}
      <main className="max-w-6xl mx-auto px-6 pb-24">
        {/* Filter bar */}
        <FilterBar
          query={query} setQuery={setQuery}
          typeFilter={typeFilter} setTypeFilter={setTypeFilter}
          statusFilter={statusFilter} setStatusFilter={setStatusFilter}
          types={types}
        />

        {/* Loading skeletons */}
        {isLoading && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {Array.from({ length: 6 }).map((_, i) => <SkeletonCard key={i} />)}
          </div>
        )}

        {/* Error */}
        {isError && (
          <div className="text-center py-20 text-rose-400">
            Failed to load assignments. Check your connection.
          </div>
        )}

        {/* Empty state */}
        {!isLoading && !isError && filtered.length === 0 && (
          <motion.div
            className="text-center py-20"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            <Search size={40} className="text-slate-700 mx-auto mb-4" />
            <p className="text-slate-500 font-display">
              {query ? `No results for "${query}"` : 'No assignments yet'}
            </p>
          </motion.div>
        )}

        {/* Grid */}
        {!isLoading && filtered.length > 0 && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {filtered.map((a, i) => (
              <AssignmentCard key={a.id} assignment={a} index={i} />
            ))}
          </div>
        )}
      </main>

      {/* Floating create button (mobile) */}
      {isLoggedIn && (
        <motion.button
          onClick={() => setCreateOpen(true)}
          className="fixed bottom-6 right-6 z-30 w-14 h-14 rounded-full btn-cyan flex items-center justify-center shadow-cyan-md sm:hidden"
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.93 }}
        >
          <Plus size={22} />
        </motion.button>
      )}

      {/* Create modal */}
      <AssignmentFormModal
        isOpen={createOpen}
        onClose={() => setCreateOpen(false)}
      />
    </div>
  )
}
