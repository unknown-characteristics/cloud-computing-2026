/**
 * React Query hooks for the Ratings microservice.
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../lib/axios'
import toast from 'react-hot-toast'

// ── Get all ratings for a submission ────────────────────────────────────────
export function useRatings(subId) {
  return useQuery({
    queryKey: ['ratings', subId],
    queryFn: async () => {
      const { data } = await api.get(`/ratings/submission/${subId}`)
      return data
    },
    enabled: !!subId,
  })
}

// ── Create rating ────────────────────────────────────────────────────────────
export function useCreateRating() {
  const qc = useQueryClient()
  return useMutation({
    // Schimbăm aici ca să destructurăm ce primește din componentă
    mutationFn: async ({ submission_id, assignment_id, comment, score }) => {
      // Trimitem către backend exact numele cerut de Pydantic: "submission_id"
      const { data } = await api.post('/ratings/', {
        submission_id: submission_id,
        assignment_id: assignment_id,
        comment: comment,
        score: score
      })
      return data
    },
    onSuccess: (_, vars) => {
      qc.invalidateQueries({ queryKey: ['ratings', vars.submissionId] })
      toast.success('Rating submitted!')
    },
    onError: (err) => {
      toast.error(err.response?.data?.message || 'Failed to submit rating')
    },
  })
}

// ── Update rating ────────────────────────────────────────────────────────────
export function useUpdateRating() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ ratingId, subId, ...payload }) => {
      const { data } = await api.patch(`/ratings/${ratingId}`, payload)
      return { data, subId }
    },
    onSuccess: ({ subId }) => {
      qc.invalidateQueries({ queryKey: ['ratings', subId] })
      toast.success('Rating updated!')
    },
    onError: (err) => {
      toast.error(err.response?.data?.message || 'Failed to update rating')
    },
  })
}

// ── Delete rating ────────────────────────────────────────────────────────────
export function useDeleteRating() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ ratingId, subId }) => {
      await api.delete(`/ratings/${ratingId}`)
      return { subId }
    },
    onSuccess: ({ subId }) => {
      qc.invalidateQueries({ queryKey: ['ratings', subId] })
      toast.success('Rating deleted')
    },
    onError: (err) => {
      toast.error(err.response?.data?.message || 'Failed to delete rating')
    },
  })
}
