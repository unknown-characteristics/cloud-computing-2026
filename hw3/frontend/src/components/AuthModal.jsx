/**
 * AuthModal — Login / Register forms with:
 * - react-hook-form + zod validation
 * - Animated tab switching
 * - Loading state + error display
 */
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { motion, AnimatePresence } from 'framer-motion'
import { Eye, EyeOff, Loader2 } from 'lucide-react'
import Modal from './ui/Modal'
import { useLogin, useRegister } from '../hooks/useAuth'

// ── Zod schemas ──────────────────────────────────────────────────────────────
const loginSchema = z.object({
  email:    z.string().email('Invalid email'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
})

const registerSchema = z.object({
  name:     z.string().min(2, 'Name must be at least 2 characters').max(80),
  email:    z.string().email('Invalid email'),
  password: z.string().min(6, 'Min 6 characters')
    .regex(/[A-Z]/, 'Must include an uppercase letter')
    .regex(/[0-9]/, 'Must include a number'),
  confirm:  z.string(),
}).refine((d) => d.password === d.confirm, {
  message: "Passwords don't match",
  path: ['confirm'],
})

// ── Reusable form field ──────────────────────────────────────────────────────
function Field({ label, error, children }) {
  return (
    <div className="space-y-1.5">
      <label className="block text-xs font-display font-medium text-slate-400 uppercase tracking-wider">
        {label}
      </label>
      {children}
      {error && (
        <p className="text-xs text-rose-400 flex items-center gap-1">
          <span>✕</span> {error}
        </p>
      )}
    </div>
  )
}

// ── Password input with show/hide toggle ────────────────────────────────────
function PasswordInput({ registration, placeholder }) {
  const [show, setShow] = useState(false)
  return (
    <div className="relative">
      <input
        {...registration}
        type={show ? 'text' : 'password'}
        placeholder={placeholder}
        className="input-field pr-10"
      />
      <button
        type="button"
        onClick={() => setShow((v) => !v)}
        className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-colors"
      >
        {show ? <EyeOff size={15} /> : <Eye size={15} />}
      </button>
    </div>
  )
}

// ── Login Form ───────────────────────────────────────────────────────────────
function LoginForm({ onSuccess }) {
  const { mutate: login, isPending } = useLogin()
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(loginSchema),
  })

  const onSubmit = (data) => {
    login(data, { onSuccess })
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <Field label="Email" error={errors.email?.message}>
        <input
          {...register('email')}
          type="email"
          placeholder="you@example.com"
          className="input-field"
          autoComplete="email"
        />
      </Field>

      <Field label="Password" error={errors.password?.message}>
        <PasswordInput
          registration={register('password')}
          placeholder="••••••••"
        />
      </Field>

      <button
        type="submit"
        disabled={isPending}
        className="btn-cyan w-full flex items-center justify-center gap-2 mt-2"
      >
        {isPending && <Loader2 size={15} className="animate-spin" />}
        {isPending ? 'Signing in…' : 'Sign In'}
      </button>
    </form>
  )
}

// ── Register Form ────────────────────────────────────────────────────────────
function RegisterForm({ onSuccess }) {
  const { mutate: register_, isPending } = useRegister()
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(registerSchema),
  })

  const onSubmit = (data) => {
    const { confirm, ...payload } = data
    register_(payload, { onSuccess })
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <Field label="Full Name" error={errors.name?.message}>
        <input
          {...register('name')}
          type="text"
          placeholder="Ada Lovelace"
          className="input-field"
          autoComplete="name"
        />
      </Field>

      <Field label="Email" error={errors.email?.message}>
        <input
          {...register('email')}
          type="email"
          placeholder="you@example.com"
          className="input-field"
          autoComplete="email"
        />
      </Field>

      <Field label="Password" error={errors.password?.message}>
        <PasswordInput registration={register('password')} placeholder="Min 6 chars, 1 uppercase, 1 number" />
      </Field>

      <Field label="Confirm Password" error={errors.confirm?.message}>
        <PasswordInput registration={register('confirm')} placeholder="Repeat password" />
      </Field>

      <button
        type="submit"
        disabled={isPending}
        className="btn-cyan w-full flex items-center justify-center gap-2 mt-2"
      >
        {isPending && <Loader2 size={15} className="animate-spin" />}
        {isPending ? 'Creating account…' : 'Create Account'}
      </button>
    </form>
  )
}

// ── Main AuthModal ───────────────────────────────────────────────────────────
export default function AuthModal({ isOpen, onClose }) {
  const [tab, setTab] = useState('login') // 'login' | 'register'

  const tabs = [
    { id: 'login',    label: 'Sign In'  },
    { id: 'register', label: 'Register' },
  ]

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Welcome to CompArena">
      {/* Tab switcher */}
      <div className="flex gap-1 p-1 bg-surface-3/50 rounded-xl mb-6">
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`relative flex-1 py-2 text-sm font-display font-semibold rounded-lg transition-colors ${
              tab === t.id ? 'text-white' : 'text-slate-500 hover:text-slate-300'
            }`}
          >
            {tab === t.id && (
              <motion.div
                layoutId="auth-tab-indicator"
                className="absolute inset-0 bg-cyan-500/20 border border-cyan-500/30 rounded-lg"
              />
            )}
            <span className="relative z-10">{t.label}</span>
          </button>
        ))}
      </div>

      {/* Form */}
      <AnimatePresence mode="wait">
        <motion.div
          key={tab}
          initial={{ opacity: 0, x: tab === 'login' ? -20 : 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{    opacity: 0, x: tab === 'login' ? 20 : -20 }}
          transition={{ duration: 0.2 }}
        >
          {tab === 'login'
            ? <LoginForm    onSuccess={onClose} />
            : <RegisterForm onSuccess={onClose} />
          }
        </motion.div>
      </AnimatePresence>

      {/* Switch link */}
      <p className="mt-5 text-center text-sm text-slate-500">
        {tab === 'login' ? "Don't have an account? " : 'Already have an account? '}
        <button
          onClick={() => setTab(tab === 'login' ? 'register' : 'login')}
          className="text-cyan-400 hover:text-cyan-300 font-medium transition-colors"
        >
          {tab === 'login' ? 'Register' : 'Sign In'}
        </button>
      </p>
    </Modal>
  )
}
