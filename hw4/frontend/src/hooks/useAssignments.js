/**
 * React Query hooks for the Assignments microservice.
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../lib/axios'
import toast from 'react-hot-toast'

// ── Fetch all assignments ────────────────────────────────────────────────────
export function useAssignments() {
  return useQuery({
    queryKey: ['assignments'],
    queryFn: async () => {
      const { data } = await api.get('/assignments/')
      return data
    },
  })
}

// ── Fetch single assignment ──────────────────────────────────────────────────
export const useAssignment = (id) => {
  return useQuery({
    queryKey: ['assignment', id],
    queryFn: async () => {
      const response = await api.get(`/assignments/${id}`);
      return response.data;
    },
    // Regula enabled împiedică React Query să facă request-ul dacă nu avem încă ID-ul în URL
    enabled: !!id,
  });
};

// ── Fetch leaderboard ────────────────────────────────────────────────────────
export function useLeaderboard() {
  return useQuery({
    queryKey: ['assignments', 'leaderboard'],
    queryFn: async () => {
      const { data } = await api.get('/assignments/leaderboard')
      return data
    },
  })
}

// ── Create assignment ────────────────────────────────────────────────────────
export function useCreateAssignment() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload) => {
      const { data } = await api.post('/assignments/', payload)
      return data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['assignments'] })
      toast.success('Assignment created!')
    },
    onError: (err) => {
      toast.error(err.response?.data?.message || 'Failed to create assignment')
    },
  })
}

// ── Update assignment ────────────────────────────────────────────────────────
export function useUpdateAssignment() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, ...payload }) => {
      const { data } = await api.patch(`/assignments/${id}`, payload)
      return data
    },
    onSuccess: (_, vars) => {
      qc.invalidateQueries({ queryKey: ['assignments'] })
      qc.invalidateQueries({ queryKey: ['assignment', vars.id] })
      toast.success('Assignment updated!')
    },
    onError: (err) => {
      toast.error(err.response?.data?.message || 'Failed to update assignment')
    },
  })
}

// ── Delete assignment ────────────────────────────────────────────────────────
export function useDeleteAssignment() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id) => {
      await api.delete(`/assignments/${id}`)
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['assignments'] })
      toast.success('Assignment deleted')
    },
    onError: (err) => {
      toast.error(err.response?.data?.message || 'Failed to delete assignment')
    },
  })
}
