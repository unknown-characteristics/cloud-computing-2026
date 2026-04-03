/**
 * Profile Page — /profile
 * Displays user info, credibility score, created assignments (with edit/delete),
 * and recent submissions.
 */
import { useState } from 'react'
import { motion } from 'framer-motion'
import { Link, useNavigate } from 'react-router-dom'
import {
  User, Mail, Trophy, Zap, Pencil, Trash2, Loader2,
  ChevronRight, FileText, BarChart2, Star
} from 'lucide-react'
import { useAuthStore } from '../store/authStore'
import { useAssignments, useDeleteAssignment } from '../hooks/useAssignments'
import AssignmentFormModal from '../components/AssignmentFormModal'
import { format } from 'date-fns'

// ── Stat card ────────────────────────────────────────────────────────────────
function StatCard({ icon: Icon, label, value, color = 'cyan' }) {
  const colors = {
    cyan:   'text-cyan-400   bg-cyan-500/10   border-cyan-500/20',
    amber:  'text-amber-400  bg-amber-500/10  border-amber-500/20',
    emerald:'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
  }
  return (
    <div className={`glass rounded-2xl p-5 flex items-center gap-4 border ${colors[color]}`}>
      <div className={`p-3 rounded-xl ${colors[color].split(' ').slice(1).join(' ')}`}>
        <Icon size={20} className={colors[color].split(' ')[0]} />
      </div>
      <div>
        <p className="text-2xl font-display font-bold text-white">{value ?? '—'}</p>
        <p className="text-xs text-slate-400 mt-0.5">{label}</p>
      </div>
    </div>
  )
}

export default function Profile() {
  const { user } = useAuthStore()
  const navigate = useNavigate()
  const [editTarget, setEditTarget] = useState(null)

  const { data: allAssignments = [], isLoading } = useAssignments()
  const { mutate: deleteAssignment, isPending: isDeleting } = useDeleteAssignment()

  // Filter assignments created by current user
  const myAssignments = allAssignments.filter((a) => a.creator_id === user?.id)

  if (!user) {
    navigate('/')
    return null
  }

  const handleDelete = (id) => {
    if (!confirm('Delete this assignment?')) return
    deleteAssignment(id)
  }

  return (
    <div className="max-w-4xl mx-auto px-6 pt-24 pb-24">
      {/* ── Profile header ───────────────────────────────────────────────── */}
      <motion.div
        className="glass-strong rounded-2xl p-6 mb-8"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <div className="flex items-start gap-5">
          {/* Avatar */}
          <div className="relative shrink-0">
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-cyan-400 to-cyan-700 flex items-center justify-center shadow-cyan-md">
              <span className="font-display font-bold text-3xl text-surface-0">
                {user.name[0].toUpperCase()}
              </span>
            </div>
            {/* Online dot */}
            <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-emerald-400 rounded-full border-2 border-surface-2" />
          </div>

          {/* Info */}
          <div className="flex-1 min-w-0">
            <h1 className="font-display font-bold text-2xl text-white">{user.name}</h1>
            <div className="flex items-center gap-2 mt-1 text-sm text-slate-400">
              <Mail size={13} className="text-cyan-600" />
              {user.email}
            </div>
          </div>
        </div>

        {/* Stats row */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-6">
          <StatCard
            icon={Trophy}
            label="Credibility Score"
            value={user.credibility_score ?? 0}
            color="amber"
          />
          <StatCard
            icon={Zap}
            label="Assignments Created"
            value={isLoading ? '…' : myAssignments.length}
            color="cyan"
          />
          <StatCard
            icon={Star}
            label="Average Rating"
            value="—"
            color="emerald"
          />
        </div>
      </motion.div>

      {/* ── My Assignments ───────────────────────────────────────────────── */}
      <motion.div
        className="glass rounded-2xl p-6 mb-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <h2 className="font-display font-semibold text-white mb-4 flex items-center gap-2">
          <BarChart2 size={16} className="text-cyan-400" />
          My Assignments
        </h2>

        {isLoading ? (
          <div className="space-y-2">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="h-14 skeleton rounded-xl" />
            ))}
          </div>
        ) : myAssignments.length === 0 ? (
          <p className="text-slate-500 text-sm text-center py-8">
            You haven't created any assignments yet.
          </p>
        ) : (
          <div className="space-y-0">
            {myAssignments.map((a, i) => (
              <motion.div
                key={a.id}
                className="flex items-center justify-between py-3.5 border-b border-cyan-900/20 last:border-b-0 group"
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.05 }}
              >
                <div className="flex-1 min-w-0">
                  <Link
                    to={`/assignment/${a.id}`}
                    className="text-sm font-display font-medium text-slate-200 hover:text-cyan-300 transition-colors flex items-center gap-1 group-hover:gap-2"
                  >
                    {a.name}
                    <ChevronRight size={13} className="text-slate-600 group-hover:text-cyan-500 transition-all" />
                  </Link>
                  <p className="text-xs text-slate-500 mt-0.5 font-mono">
                    Deadline: {format(new Date(a.stop_submit_time), 'MMM d, yyyy HH:mm')}
                  </p>
                </div>

                <div className="flex items-center gap-1 ml-3 shrink-0">
                  <button
                    onClick={() => setEditTarget(a)}
                    className="p-1.5 rounded-lg text-slate-500 hover:text-cyan-400 hover:bg-cyan-500/10 transition-colors"
                    title="Edit"
                  >
                    <Pencil size={13} />
                  </button>
                  <button
                    onClick={() => handleDelete(a.id)}
                    disabled={isDeleting}
                    className="p-1.5 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
                    title="Delete"
                  >
                    {isDeleting ? <Loader2 size={13} className="animate-spin" /> : <Trash2 size={13} />}
                  </button>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </motion.div>

      {/* Edit modal */}
      <AssignmentFormModal
        isOpen={!!editTarget}
        onClose={() => setEditTarget(null)}
        existing={editTarget}
      />
    </div>
  )
}
