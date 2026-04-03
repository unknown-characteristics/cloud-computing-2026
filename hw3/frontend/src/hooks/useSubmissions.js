/**
 * React Query hooks for the Submissions microservice.
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../lib/axios'
import toast from 'react-hot-toast'

// ── Get all submissions for an assignment ────────────────────────────────────
export function useSubmissions(assignmentId) {
  return useQuery({
    queryKey: ['submissions', assignmentId],
    queryFn: async () => {
      const { data } = await api.get(`/submissions/assignment/${assignmentId}`)
      return data
    },
    enabled: !!assignmentId,
  })
}

// ── Upload submission (multipart) ────────────────────────────────────────────
export function useUploadSubmission() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ assignmentId, file }) => {
      const form = new FormData()
      form.append('assignment_id', assignmentId)
      form.append('file', file)
      const { data } = await api.post('/submissions/', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      return data
    },
    onSuccess: (_, vars) => {
      qc.invalidateQueries({ queryKey: ['submissions', vars.assignmentId] })
      toast.success('Submission uploaded!')
    },
    onError: (err) => {
      toast.error(err.response?.data?.message || 'Upload failed')
    },
  })
}

// ── Edit submission (multipart) ──────────────────────────────────────────────
export function useUpdateSubmission() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ subId, assignmentId, file }) => {
      const form = new FormData()
      form.append('file', file)
      const { data } = await api.patch(`/submissions/${subId}`, form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      return data
    },
    onSuccess: (_, vars) => {
      qc.invalidateQueries({ queryKey: ['submissions', vars.assignmentId] })
      toast.success('Submission updated!')
    },
    onError: (err) => {
      toast.error(err.response?.data?.message || 'Update failed')
    },
  })
}

// ── Delete submission ────────────────────────────────────────────────────────
export function useDeleteSubmission() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ subId, assignmentId }) => {
      await api.delete(`/submissions/${subId}`)
      return { assignmentId }
    },
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ['submissions', data.assignmentId] })
      toast.success('Submission removed')
    },
    onError: (err) => {
      toast.error(err.response?.data?.message || 'Delete failed')
    },
  })
}

// ── Download submission file URL ─────────────────────────────────────────────
export function getFileDownloadUrl(subId) {
  return `${import.meta.env.VITE_API_URL || '/api'}/submissions/${subId}/file`
}
