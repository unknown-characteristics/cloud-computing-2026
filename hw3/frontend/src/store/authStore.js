/**
 * Zustand store for authentication state.
 * Persists token + user to localStorage so sessions survive page refresh.
 */
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export const useAuthStore = create(
  persist(
    (set) => ({
      /** @type {string|null} */
      token: null,
      /** @type {{ id: number, name: string, email: string, credibility_score: number }|null} */
      user: null,

      /** Called after successful login/register */
      setAuth: (token, user) => set({ token, user }),

      /** Called after profile updates */
      setUser: (user) => set({ user }),

      /** Clears everything on logout or 401 */
      logout: () => set({ token: null, user: null }),

      /** Derived helper */
      isLoggedIn: () => {
        const state = useAuthStore.getState()
        return !!state.token && !!state.user
      },
    }),
    {
      name: 'comparena-auth',
      // Only persist these keys
      partialize: (state) => ({ token: state.token, user: state.user }),
    }
  )
)
