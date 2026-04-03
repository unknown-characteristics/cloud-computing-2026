/**
 * ProtectedRoute — redirects to '/' if user is not authenticated.
 * Shows the auth modal instead of navigating away, to keep UX smooth.
 */
import { useEffect } from 'react'
import { useAuthStore } from '../store/authStore'
import toast from 'react-hot-toast'

export default function ProtectedRoute({ children, onOpenAuth }) {
  const user = useAuthStore((s) => s.user)

  useEffect(() => {
    if (!user) {
      toast.error('Sign in to access this page')
      onOpenAuth?.()
    }
  }, [user, onOpenAuth])

  if (!user) return null
  return children
}
