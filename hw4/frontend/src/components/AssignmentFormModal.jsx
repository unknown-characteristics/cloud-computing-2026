/**
 * AssignmentFormModal — Create or Edit an assignment.
 * Uses react-hook-form + zod. Validates time ordering.
 */
import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Loader2 } from 'lucide-react'
import Modal from './ui/Modal'
import { useCreateAssignment, useUpdateAssignment } from '../hooks/useAssignments'
import { useAuthStore } from '../store/authStore'
import { format } from 'date-fns'

// ── Helpers ──────────────────────────────────────────────────────────────────
// datetime-local inputs need "YYYY-MM-DDTHH:MM" format
const toLocal = (iso) => {
  if (!iso) return ''
  return format(new Date(iso), "yyyy-MM-dd'T'HH:mm")
}

// ── Zod schema ───────────────────────────────────────────────────────────────
const schema = z.object({
  name:             z.string().min(3, 'Name too short').max(120),
  description:      z.string().min(10, 'Description too short').max(2000),
  type:             z.string().min(1, 'Select a type'),
  start_time:       z.string().min(1, 'Required'),
  stop_submit_time: z.string().min(1, 'Required'),
  stop_grade_time:  z.string().min(1, 'Required'),
}).refine(
  (d) => new Date(d.stop_submit_time) > new Date(d.start_time),
  { message: 'Submission deadline must be after start time', path: ['stop_submit_time'] }
).refine(
  (d) => new Date(d.stop_grade_time) >= new Date(d.stop_submit_time),
  { message: 'Grading deadline must be ≥ submission deadline', path: ['stop_grade_time'] }
)

const TYPES = ['competitive', 'assignment', 'quiz', 'project', 'hackathon']

function Field({ label, error, children }) {
  return (
    <div className="space-y-1.5">
      <label className="block text-xs font-display font-medium text-slate-400 uppercase tracking-wider">
        {label}
      </label>
      {children}
      {error && <p className="text-xs text-rose-400">✕ {error}</p>}
    </div>
  )
}

export default function AssignmentFormModal({ isOpen, onClose, existing = null }) {
  const { user } = useAuthStore()
  const { mutate: create, isPending: isCreating } = useCreateAssignment()
  const { mutate: update, isPending: isUpdating } = useUpdateAssignment()
  const isPending = isCreating || isUpdating
  const isEdit = !!existing

  const { register, handleSubmit, reset, formState: { errors } } = useForm({
    resolver: zodResolver(schema),
    defaultValues: {
      name:             existing?.name             ?? '',
      description:      existing?.description      ?? '',
      type:             existing?.type             ?? '',
      start_time:       toLocal(existing?.start_time),
      stop_submit_time: toLocal(existing?.stop_submit_time),
      stop_grade_time:  toLocal(existing?.stop_grade_time),
    }
  })

  // Re-populate when `existing` changes (e.g. opening edit for different item)
  useEffect(() => {
    if (isOpen) {
      reset({
        name:             existing?.name             ?? '',
        description:      existing?.description      ?? '',
        type:             existing?.type             ?? '',
        start_time:       toLocal(existing?.start_time),
        stop_submit_time: toLocal(existing?.stop_submit_time),
        stop_grade_time:  toLocal(existing?.stop_grade_time),
      })
    }
  }, [existing, isOpen, reset])

  const onSubmit = (data) => {
    const payload = {
      ...data,
      start_time:       new Date(data.start_time).toISOString(),
      stop_submit_time: new Date(data.stop_submit_time).toISOString(),
      stop_grade_time:  new Date(data.stop_grade_time).toISOString(),
    }
    if (isEdit) {
      update({ id: existing.id, ...payload }, { onSuccess: onClose })
    } else {
      create({ creator_id: user.id, ...payload }, { onSuccess: onClose })
    }
  }

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEdit ? 'Edit Assignment' : 'New Assignment'}
      size="lg"
    >
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        {/* Name */}
        <Field label="Assignment Name" error={errors.name?.message}>
          <input {...register('name')} placeholder="e.g. Graph Algorithms Challenge" className="input-field" />
        </Field>

        {/* Description */}
        <Field label="Description" error={errors.description?.message}>
          <textarea
            {...register('description')}
            rows={4}
            placeholder="Describe the task, rules, and scoring criteria…"
            className="input-field resize-none"
          />
        </Field>

        {/* Type */}
        <Field label="Type" error={errors.type?.message}>
          <select {...register('type')} className="input-field">
            <option value="">Select type…</option>
            {TYPES.map((t) => (
              <option key={t} value={t} className="bg-surface-2 capitalize">{t}</option>
            ))}
          </select>
        </Field>

        {/* Dates grid */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <Field label="Start Time" error={errors.start_time?.message}>
            <input {...register('start_time')} type="datetime-local" className="input-field" />
          </Field>
          <Field label="Submission Deadline" error={errors.stop_submit_time?.message}>
            <input {...register('stop_submit_time')} type="datetime-local" className="input-field" />
          </Field>
          <Field label="Grading Deadline" error={errors.stop_grade_time?.message}>
            <input {...register('stop_grade_time')} type="datetime-local" className="input-field" />
          </Field>
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-3 pt-2">
          <button type="button" onClick={onClose} className="btn-ghost">Cancel</button>
          <button type="submit" disabled={isPending} className="btn-cyan flex items-center gap-2">
            {isPending && <Loader2 size={14} className="animate-spin" />}
            {isEdit ? 'Save Changes' : 'Create Assignment'}
          </button>
        </div>
      </form>
    </Modal>
  )
}
