/**
 * Mutations for User auth operations: login + register.
 */
import { useMutation } from '@tanstack/react-query'
import api from '../lib/axios'
import { useAuthStore } from '../store/authStore'
import toast from 'react-hot-toast'

export function useLogin() {
  const setAuth = useAuthStore((s) => s.setAuth)
  return useMutation({
    mutationFn: async ({ email, password }) => {
      const { data } = await api.post('/users/login', { email, password })
      return data
    },
    onSuccess: (data) => {
      // Backend may return { token, user } or set HTTP-only cookie
      const token = data.token || data.access_token || ''
      const user = data.user || {
        id: data.id,
        name: data.name,
        email: data.email,
        credibility_score: data.credibility_score,
      }
      setAuth(token, user)
      toast.success(`Welcome back, ${user.name}!`)
    },
    onError: (err) => {
      toast.error(err.response?.data?.message || 'Login failed')
    },
  })
}

export function useRegister() {
  const setAuth = useAuthStore((s) => s.setAuth)
  return useMutation({
    mutationFn: async ({ name, email, password }) => {
      const { data } = await api.post('/users/register', { name, email, password })
      return data
    },
    onSuccess: (data) => {
      const token = data.token || data.access_token || ''
      const user = {
        id: data.id,
        name: data.name,
        email: data.email,
        credibility_score: data.credibility_score ?? 0,
      }
      setAuth(token, user)
      toast.success(`Account created! Welcome, ${user.name}!`)
    },
    onError: (err) => {
      toast.error(err.response?.data?.message || 'Registration failed')
    },
  })
}
