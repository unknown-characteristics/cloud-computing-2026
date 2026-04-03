/**
 * Interactive star rating component.
 * Props:
 *   value       - current value (0-5)
 *   onChange    - (val) => void  (omit to make read-only)
 *   size        - 'sm' | 'md' | 'lg'
 *   showNumber  - show numeric value next to stars
 */
import { useState } from 'react'
import { Star } from 'lucide-react'
import { motion } from 'framer-motion'

const sizes = {
  sm: 14,
  md: 18,
  lg: 24,
}

export default function StarRating({ value = 0, onChange, size = 'md', showNumber = false }) {
  const [hovered, setHovered] = useState(null)
  const isInteractive = !!onChange
  const display = hovered ?? value

  return (
    <div className="flex items-center gap-1">
      {[1, 2, 3, 4, 5].map((star) => {
        const filled = star <= display
        return (
          <motion.button
            key={star}
            type="button"
            disabled={!isInteractive}
            className={`star-btn ${isInteractive ? 'cursor-pointer' : 'cursor-default'}`}
            whileHover={isInteractive ? { scale: 1.25 } : {}}
            whileTap={isInteractive ? { scale: 0.9 } : {}}
            onMouseEnter={() => isInteractive && setHovered(star)}
            onMouseLeave={() => isInteractive && setHovered(null)}
            onClick={() => isInteractive && onChange(star)}
          >
            <Star
              size={sizes[size]}
              className={`transition-colors duration-100 ${
                filled
                  ? 'fill-amber-400 text-amber-400'
                  : 'fill-transparent text-slate-600'
              }`}
            />
          </motion.button>
        )
      })}
      {showNumber && (
        <span className="ml-1 text-sm font-mono text-slate-400">
          {value > 0 ? value.toFixed(1) : '—'}
        </span>
      )}
    </div>
  )
}
