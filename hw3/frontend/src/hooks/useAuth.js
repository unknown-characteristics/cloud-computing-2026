import { useMutation } from '@tanstack/react-query'
import api from '../lib/axios'
import { useAuthStore } from '../store/authStore'
import toast from 'react-hot-toast'
import { jwtDecode } from 'jwt-decode' // Nu uita să rulezi: npm install jwt-decode

export function useLogin() {
  const setAuth = useAuthStore((s) => s.setAuth)
  
  return useMutation({
    mutationFn: async ({ email, password }) => {
      const { data } = await api.post('/users/login', { email, password })
      return data
    },
    onSuccess: (data) => {
      const token = data.token || data.access_token || ''
      
      if (token) {
        try {
          // Decodăm token-ul și parsăm string-ul JSON din interior
          const decoded = jwtDecode(token)
          const userObj = JSON.parse(decoded.sub)
          
          // Salvăm în store (asigură-te că ordinea parametrilor e cea corectă pentru store-ul tău)
          setAuth(token, userObj) 
          toast.success(`Welcome back, ${userObj.name}!`)
        } catch (error) {
          console.error("Eroare la parsarea JWT:", error)
          toast.error("Eroare la procesarea datelor de utilizator.")
        }
      }
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
      
      // Dacă backend-ul returnează token și la register, îl decodăm la fel ca la login
      if (token) {
        try {
          const decoded = jwtDecode(token)
          const userObj = JSON.parse(decoded.sub)
          
          setAuth(token, userObj)
          toast.success(`Account created! Welcome, ${userObj.name}!`)
        } catch (error) {
          console.error("Eroare la parsarea JWT:", error)
        }
      } else {
        // Dacă backend-ul NU returnează token la register, utilizatorul va trebui să dea login manual
        toast.success(`Account created! Please log in.`)
      }
    },
    onError: (err) => {
      toast.error(err.response?.data?.message || 'Registration failed')
    },
  })
}