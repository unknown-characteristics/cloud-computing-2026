/**
 * RatingModal — view all ratings for a submission, add/edit/delete ratings.
 */
import { useState } from 'react'
import { motion } from 'framer-motion'
import { Loader2, Pencil, Trash2, Star, MessageSquare } from 'lucide-react'
import Modal from './ui/Modal'
import StarRating from './ui/StarRating'
import { useRatings, useCreateRating, useUpdateRating, useDeleteRating } from '../hooks/useRatings'
import { useAuthStore } from '../store/authStore'
import { SkeletonTable } from './ui/Skeleton'
import { sanitizeText } from '../lib/sanitize'
import { format } from 'date-fns'

// ── Single rating row ────────────────────────────────────────────────────────
function RatingRow({ rating, currentUserId, subId }) {
  const [editing, setEditing] = useState(false)
  const [editScore, setEditScore] = useState(rating.score)
  const [editComment, setEditComment] = useState(rating.comment || '')

  const { mutate: updateRating, isPending: isUpdating } = useUpdateRating()
  const { mutate: deleteRating, isPending: isDeleting } = useDeleteRating()

  const isOwner = currentUserId && rating.user_id === currentUserId

  const handleSave = () => {
    updateRating(
      { ratingId: rating.id, subId, score: editScore, comment: editComment },
      { onSuccess: () => setEditing(false) }
    )
  }

  return (
    <motion.div
      layout
      className="py-3 border-b border-cyan-900/20 last:border-b-0"
    >
      {editing ? (
        <div className="space-y-2">
          <StarRating value={editScore} onChange={setEditScore} />
          <textarea
            value={editComment}
            onChange={(e) => setEditComment(e.target.value)}
            rows={2}
            className="input-field text-xs resize-none"
            placeholder="Update your comment…"
          />
          <div className="flex gap-2">
            <button
              onClick={handleSave}
              disabled={isUpdating}
              className="btn-cyan text-xs px-3 py-1.5 flex items-center gap-1"
            >
              {isUpdating && <Loader2 size={12} className="animate-spin" />}
              Save
            </button>
            <button onClick={() => setEditing(false)} className="btn-ghost text-xs px-3 py-1.5">
              Cancel
            </button>
          </div>
        </div>
      ) : (
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <StarRating value={rating.score} size="sm" />
              <span className="text-xs text-slate-500 font-mono">
                {rating.created_at ? format(new Date(rating.created_at), 'MMM d') : ''}
              </span>
            </div>
            {rating.comment && (
              <p className="text-sm text-slate-400 leading-relaxed">
                {sanitizeText(rating.comment)}
              </p>
            )}
          </div>
          {isOwner && (
            <div className="flex items-center gap-1 shrink-0">
              <button
                onClick={() => setEditing(true)}
                className="p-1.5 rounded-lg text-slate-500 hover:text-cyan-400 hover:bg-cyan-500/10 transition-colors"
                title="Edit rating"
              >
                <Pencil size={13} />
              </button>
              <button
                onClick={() => deleteRating({ ratingId: rating.id, subId })}
                disabled={isDeleting}
                className="p-1.5 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
                title="Delete rating"
              >
                {isDeleting ? <Loader2 size={13} className="animate-spin" /> : <Trash2 size={13} />}
              </button>
            </div>
          )}
        </div>
      )}
    </motion.div>
  )
}

// ── Add rating form ──────────────────────────────────────────────────────────
function AddRatingForm({ subId, assignmentId }) {
  const [score, setScore]     = useState(0)
  const [comment, setComment] = useState('')
  const { mutate: createRating, isPending } = useCreateRating()

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!score) return
    createRating(
      { submission_id: subId, assignment_id: assignmentId, score, comment },
      { onSuccess: () => { setScore(0); setComment('') } }
    )
  }

  return (
    <form onSubmit={handleSubmit} className="pt-4 border-t border-cyan-900/30 space-y-3">
      <p className="text-xs font-display font-medium text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
        <Star size={12} className="text-amber-400" /> Add Your Rating
      </p>
      <StarRating value={score} onChange={setScore} />
      <textarea
        value={comment}
        onChange={(e) => setComment(e.target.value)}
        rows={3}
        className="input-field text-sm resize-none"
        placeholder="Write a comment (optional)…"
      />
      <button
        type="submit"
        disabled={isPending || !score}
        className="btn-cyan flex items-center gap-2 text-sm"
      >
        {isPending && <Loader2 size={13} className="animate-spin" />}
        Submit Rating
      </button>
    </form>
  )
}

// ── Main modal ───────────────────────────────────────────────────────────────
export default function RatingModal({ isOpen, onClose, submission, assignmentId }) {
  const { user } = useAuthStore()
  const isLoggedIn = !!user
  const subId = submission?.id

  const { data: ratings = [], isLoading } = useRatings(subId)

  const avgScore = ratings.length
    ? (ratings.reduce((s, r) => s + r.score, 0) / ratings.length).toFixed(1)
    : null

  // Check if user already rated
  const myRating = user ? ratings.find((r) => r.user_id === user.id) : null

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Submission Ratings"
      size="md"
    >
      {/* Summary */}
      {avgScore && (
        <div className="flex items-center gap-3 mb-4 px-4 py-3 bg-amber-500/5 border border-amber-500/20 rounded-xl">
          <StarRating value={parseFloat(avgScore)} size="md" />
          <span className="text-2xl font-display font-bold text-white">{avgScore}</span>
          <span className="text-sm text-slate-500">({ratings.length} rating{ratings.length !== 1 ? 's' : ''})</span>
        </div>
      )}

      {/* Rating list */}
      <div className="mb-4">
        {isLoading ? (
          <SkeletonTable rows={3} />
        ) : ratings.length === 0 ? (
          <div className="text-center py-8 text-slate-500 text-sm flex flex-col items-center gap-2">
            <MessageSquare size={28} className="text-slate-700" />
            No ratings yet. Be the first!
          </div>
        ) : (
          ratings.map((r) => (
            <RatingRow
              key={r.id}
              rating={r}
              currentUserId={user?.id}
              subId={subId}
            />
          ))
        )}
      </div>

      {/* Add rating (only if logged in and not already rated) */}
      {isLoggedIn && !myRating && (
        <AddRatingForm subId={subId} assignmentId={assignmentId} />
      )}
      {!isLoggedIn && (
        <p className="text-center text-sm text-slate-500 pt-4 border-t border-cyan-900/30">
          Sign in to leave a rating
        </p>
      )}
    </Modal>
  )
}
