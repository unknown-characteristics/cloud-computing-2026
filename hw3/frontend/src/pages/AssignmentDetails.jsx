/**
 * Assignment Details Page — /assignment/:id
 * Shows full assignment info, submission zone, community submissions + ratings.
 */
import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  ArrowLeft, Calendar, Clock, Trophy, Users,
  Upload, Download, Pencil, Trash2, Loader2,
  Star, ChevronRight, AlertTriangle
} from 'lucide-react'
import { format, isPast, isFuture, formatDistanceToNow } from 'date-fns'
import { useAssignment, useDeleteAssignment } from '../hooks/useAssignments'
import {
  useSubmissions, useUploadSubmission,
  useUpdateSubmission, useDeleteSubmission, downloadSubmissionFile
} from '../hooks/useSubmissions'
import { useRatings } from '../hooks/useRatings'
import { useAuthStore } from '../store/authStore'
import AssignmentFormModal from '../components/AssignmentFormModal'
import FileDropzone from '../components/FileDropzone'
import RatingModal from '../components/RatingModal'
import { SkeletonCard, SkeletonLine } from '../components/ui/Skeleton'
import StarRating from '../components/ui/StarRating'
import { sanitize } from '../lib/sanitize'

// ── Time chip ─────────────────────────────────────────────────────────────────
function TimeChip({ icon: Icon, label, date }) {
  const past = isPast(new Date(date))
  return (
    <div className={`flex items-center gap-2 px-3 py-2 rounded-xl border text-sm ${
      past
        ? 'bg-rose-500/5 border-rose-500/20 text-rose-400'
        : 'bg-surface-3/50 border-cyan-900/30 text-slate-300'
    }`}>
      <Icon size={13} className={past ? 'text-rose-500' : 'text-cyan-500'} />
      <span className="text-xs font-display text-slate-500 mr-1">{label}</span>
      <span className="font-mono text-xs">{format(new Date(date), 'MMM d, HH:mm')}</span>
    </div>
  )
}

function SubmissionRow({ sub, currentUserId, assignmentId, onRate }) {
  const { mutate: deleteSub, isPending: isDeleting } = useDeleteSubmission()
  const { mutate: updateSub, isPending: isUpdating } = useUpdateSubmission()
  const [editFile, setEditFile] = useState(null)
  const [showEdit, setShowEdit] = useState(false)
  const { data: ratings = [] } = useRatings(sub.id)

  const isOwner = currentUserId && sub.user_id === currentUserId
  const avgScore = ratings.length
    ? (ratings.reduce((s, r) => s + r.score, 0) / ratings.length).toFixed(1)
    : null

  const handleUpdate = () => {
    if (!editFile) return
    updateSub(
      { subId: sub.id, assignmentId, file: editFile },
      { onSuccess: () => { setShowEdit(false); setEditFile(null) } }
    )
  }

  return (
    <motion.div layout className="py-3 border-b border-cyan-900/20 last:border-b-0">
      <div className="flex items-center justify-between gap-3">
        <div className="flex-1 min-w-0">
          <p className="text-sm text-slate-200 truncate font-mono">
            {sub.filename || `Submission #${sub.id}`}
            {isOwner && <span className="ml-2 text-[10px] bg-cyan-500/20 text-cyan-400 px-2 py-0.5 rounded-full">Yours</span>}
          </p>
          <div className="flex items-center gap-3 mt-1">
            {avgScore && (
              <span className="flex items-center gap-1 text-xs text-amber-400">
                <Star size={11} className="fill-amber-400" />
                {avgScore} <span className="text-slate-500">({ratings.length})</span>
              </span>
            )}
            <span className="text-xs text-slate-500">
              {/* AICI: Am inlocuit submitted_at cu created_at */}
              {sub.created_at
                ? formatDistanceToNow(new Date(sub.created_at), { addSuffix: true })
                : 'Just now'}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-1 shrink-0">
          <button onClick={() => onRate(sub)} className="flex items-center gap-1 px-2.5 py-1.5 text-xs btn-ghost rounded-lg">
            <Star size={12} /> Rate
          </button>

          <button onClick={() => downloadSubmissionFile(sub.id, sub.filename)} className="p-1.5 rounded-lg text-slate-500 hover:text-cyan-400 hover:bg-cyan-500/10 transition-colors" title="Download">
            <Download size={14} />
          </button>

          {isOwner && (
            <>
              <button onClick={() => setShowEdit(!showEdit)} className="p-1.5 rounded-lg text-slate-500 hover:text-cyan-400 hover:bg-cyan-500/10 transition-colors">
                <Pencil size={14} />
              </button>
              <button onClick={() => deleteSub({ subId: sub.id, assignmentId })} disabled={isDeleting} className="p-1.5 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 transition-colors">
                {isDeleting ? <Loader2 size={14} className="animate-spin" /> : <Trash2 size={14} />}
              </button>
            </>
          )}
        </div>
      </div>

      <AnimatePresence>
        {showEdit && (
          <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }} className="mt-3 overflow-hidden">
            <FileDropzone onFile={setEditFile} currentFile={editFile} label="Choose a new file to replace" />
            <div className="flex gap-2 mt-2">
              <button onClick={handleUpdate} disabled={!editFile || isUpdating} className="btn-cyan text-xs py-1.5 px-3 flex items-center gap-1">
                {isUpdating ? <Loader2 size={12} className="animate-spin" /> : 'Save Changes'}
              </button>
              <button onClick={() => setShowEdit(false)} className="btn-ghost text-xs py-1.5 px-3">Cancel</button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

// ── Main page ────────────────────────────────────────────────────────────────
export default function AssignmentDetails() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user } = useAuthStore()

  // Am pastrat denumirile standard din react-query
  const { data: assignment, isLoading, error } = useAssignment(id)
  const { data: submissions = [], isLoading: loadingSubs } = useSubmissions(id)
  const { mutate: deleteAssignment, isPending: isDeleting } = useDeleteAssignment()
  const { mutate: uploadSub, isPending: isUploading } = useUploadSubmission()

  const [editOpen,  setEditOpen]  = useState(false)
  const [ratingOpen, setRatingOpen] = useState(false)
  const [ratedSub, setRatedSub]   = useState(null)
  const [newFile, setNewFile]     = useState(null)

  // Acum folosim isLoading in loc de loadingAssignment
  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-6 pt-24 space-y-4">
        <SkeletonLine w="48" h="8" />
        <SkeletonCard />
        <SkeletonCard />
      </div>
    )
  }

  // Verificam daca e o eroare si nu s-a returnat niciun assignment
  if (error || !assignment) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen gap-4">
        <AlertTriangle size={40} className="text-slate-600" />
        <p className="text-slate-400">Assignment not found or error loading it.</p>
        <button onClick={() => navigate('/')} className="btn-ghost">← Back</button>
      </div>
    )
  }

  const isCreator = user && assignment.creator_id === user.id
  const canSubmit = user && !isPast(new Date(assignment.stop_submit_time)) && !isFuture(new Date(assignment.start_time))
  const mySubmission = user ? submissions.find((s) => s.user_id === user.id) : null

  const handleDelete = () => {
    if (!confirm('Delete this assignment? This cannot be undone.')) return
    deleteAssignment(assignment.id, { onSuccess: () => navigate('/') })
  }

  const handleUpload = () => {
    if (!newFile) return
    uploadSub({ assignmentId: id, file: newFile }, { onSuccess: () => setNewFile(null) })
  }

  const openRating = (sub) => {
    setRatedSub(sub)
    setRatingOpen(true)
  }

  return (
    <div className="max-w-4xl mx-auto px-6 pt-24 pb-24">
      {/* Back button */}
      <button
        onClick={() => navigate('/')}
        className="flex items-center gap-1.5 text-sm text-slate-500 hover:text-cyan-400 transition-colors mb-6 font-display"
      >
        <ArrowLeft size={15} /> Back to Dashboard
      </button>

      {/* ── Header card ──────────────────────────────────────────────────── */}
      <motion.div
        className="glass-strong rounded-2xl p-6 mb-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        {/* Top row */}
        <div className="flex items-start justify-between gap-4 mb-4">
          <div className="flex-1 min-w-0">
            {assignment.type && (
              <span className="badge-cyan mb-3 inline-flex capitalize">{assignment.type}</span>
            )}
            <h1 className="font-display font-bold text-2xl sm:text-3xl text-white leading-tight">
              {assignment.name}
            </h1>
          </div>

          {/* Creator actions */}
          {isCreator && (
            <div className="flex items-center gap-2 shrink-0">
              <button onClick={() => setEditOpen(true)} className="btn-ghost flex items-center gap-1.5 text-xs">
                <Pencil size={13} /> Edit
              </button>
              <button
                onClick={handleDelete}
                disabled={isDeleting}
                className="btn-danger flex items-center gap-1.5 text-xs"
              >
                {isDeleting ? <Loader2 size={13} className="animate-spin" /> : <Trash2 size={13} />}
                Delete
              </button>
            </div>
          )}
        </div>

        {/* Description */}
        <div
          className="text-slate-400 leading-relaxed mb-5 text-sm prose prose-invert prose-sm max-w-none"
          dangerouslySetInnerHTML={{ __html: sanitize(assignment.description) }}
        />

        {/* Times */}
        <div className="flex flex-wrap gap-2">
          <TimeChip icon={Clock}    label="Starts"    date={assignment.start_time} />
          <TimeChip icon={Calendar} label="Deadline"  date={assignment.stop_submit_time} />
          <TimeChip icon={Trophy}   label="Grading"   date={assignment.stop_grade_time} />
        </div>
      </motion.div>

      {/* ── Submit section ───────────────────────────────────────────────── */}
      {/* ── Submit section ───────────────────────────────────────────────── */}
      {canSubmit && !mySubmission && (
        <motion.div className="glass rounded-2xl p-6 mb-6 border border-cyan-500/30 bg-cyan-950/10">
          <h2 className="font-display font-semibold text-white mb-2 flex items-center gap-2">
            <Upload size={18} className="text-cyan-400" />
            Submit Your Solution
          </h2>
          <p className="text-xs text-slate-400 mb-4">You haven't submitted a solution yet. Upload your file below.</p>

          <FileDropzone onFile={setNewFile} currentFile={newFile} />

          <div className="flex justify-end mt-4">
            <button onClick={handleUpload} disabled={!newFile || isUploading} className="btn-cyan flex items-center gap-2">
              {isUploading ? <Loader2 size={16} className="animate-spin" /> : 'Submit Solution'}
            </button>
          </div>
        </motion.div>
      )}

      {/* Daca are deja o submisie, ii aratam un mesaj dragut (editarea se face direct din lista de mai jos) */}
      {mySubmission && (
         <div className="flex items-center justify-between px-4 py-3 mb-6 bg-emerald-500/10 border border-emerald-500/20 rounded-xl">
           <div className="flex items-center gap-2 text-emerald-400 text-sm">
             <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
             You have already submitted a solution for this assignment.
           </div>
           <span className="text-xs text-slate-400">Edit or delete it from the list below.</span>
         </div>
      )}

      {/* Submission deadline passed banner */}
      {user && isPast(new Date(assignment.stop_submit_time)) && (
        <div className="flex items-center gap-2 px-4 py-3 mb-6 bg-amber-500/10 border border-amber-500/20 rounded-xl text-amber-400 text-sm">
          <AlertTriangle size={15} />
          Submission window has closed.
        </div>
      )}

      {/* ── Community submissions ─────────────────────────────────────────── */}
      <motion.div
        className="glass rounded-2xl p-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <h2 className="font-display font-semibold text-white mb-4 flex items-center gap-2">
          <Users size={16} className="text-cyan-400" />
          Community Submissions
          {submissions.length > 0 && (
            <span className="badge-cyan text-xs ml-1">{submissions.length}</span>
          )}
        </h2>

        {loadingSubs ? (
          <div className="space-y-2">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="h-12 skeleton rounded-xl" />
            ))}
          </div>
        ) : submissions.length === 0 ? (
          <p className="text-slate-500 text-sm text-center py-8">No submissions yet.</p>
        ) : (
          submissions.map((sub) => (
            <SubmissionRow
              key={sub.id}
              sub={sub}
              currentUserId={user?.id}
              assignmentId={id}
              onRate={openRating}
            />
          ))
        )}
      </motion.div>

      {/* Modals */}
      <AssignmentFormModal
        isOpen={editOpen}
        onClose={() => setEditOpen(false)}
        existing={assignment}
      />
      <RatingModal
        isOpen={ratingOpen}
        onClose={() => { setRatingOpen(false); setRatedSub(null) }}
        submission={ratedSub}
        assignmentId={id}
      />
    </div>
  )
}
