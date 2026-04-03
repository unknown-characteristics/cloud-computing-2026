/**
 * AssignmentCard — displays one assignment in the feed.
 * Clicking navigates to /assignment/:id
 */
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Clock, Users, ArrowRight, Calendar, Trophy } from 'lucide-react'
import { format, isPast, isFuture } from 'date-fns'

function StatusBadge({ assignment }) {
  const now = new Date()
  const stop = new Date(assignment.stop_submit_time)
  const start = new Date(assignment.start_time)

  if (isFuture(start)) {
    return <span className="badge-amber">Upcoming</span>
  }
  if (isPast(stop)) {
    return <span className="badge badge-rose bg-rose-500/10 text-rose-400 border border-rose-500/20">Closed</span>
  }
  return <span className="badge-emerald">Active</span>
}

function TypeBadge({ type }) {
  return (
    <span className="badge-cyan">
      {type}
    </span>
  )
}

export default function AssignmentCard({ assignment, index = 0 }) {
  const deadline = new Date(assignment.stop_submit_time)

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.06, duration: 0.4, ease: 'easeOut' }}
    >
      <Link to={`/assignment/${assignment.id}`} className="block assignment-card">
        {/* Top row: badges */}
        <div className="flex items-center gap-2 mb-3">
          <StatusBadge assignment={assignment} />
          {assignment.type && <TypeBadge type={assignment.type} />}
        </div>

        {/* Title */}
        <h3 className="font-display font-semibold text-white text-base leading-snug mb-2 group-hover:text-cyan-300 transition-colors line-clamp-2">
          {assignment.name}
        </h3>

        {/* Description snippet */}
        <p className="text-sm text-slate-400 line-clamp-2 leading-relaxed mb-4">
          {assignment.description}
        </p>

        {/* Meta row */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3 text-xs text-slate-500">
            <span className="flex items-center gap-1">
              <Calendar size={12} className="text-cyan-600" />
              {format(deadline, 'MMM d, yyyy')}
            </span>
          </div>

          <div className="flex items-center gap-1 text-xs text-cyan-500 font-display font-medium opacity-0 group-hover:opacity-100 transition-opacity">
            View <ArrowRight size={12} />
          </div>
        </div>

        {/* Hover glow bar at bottom */}
        <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-cyan-500/40 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
      </Link>
    </motion.div>
  )
}
