/** Generic skeleton loader blocks */
export function SkeletonCard() {
  return (
    <div className="glass rounded-2xl p-5 space-y-3">
      <div className="skeleton h-4 w-2/3 rounded-lg" />
      <div className="skeleton h-3 w-full rounded-lg" />
      <div className="skeleton h-3 w-4/5 rounded-lg" />
      <div className="flex gap-2 pt-1">
        <div className="skeleton h-5 w-16 rounded-full" />
        <div className="skeleton h-5 w-20 rounded-full" />
      </div>
    </div>
  )
}

export function SkeletonLine({ w = 'full', h = 4 }) {
  return <div className={`skeleton h-${h} w-${w} rounded-lg`} />
}

export function SkeletonTable({ rows = 5 }) {
  return (
    <div className="space-y-2">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex gap-4 py-2">
          <div className="skeleton h-4 w-1/4 rounded" />
          <div className="skeleton h-4 w-1/3 rounded" />
          <div className="skeleton h-4 w-1/5 rounded" />
        </div>
      ))}
    </div>
  )
}
