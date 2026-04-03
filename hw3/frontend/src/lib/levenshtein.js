/**
 * Fuzzy search utility using Levenshtein distance.
 *
 * Given a query string and a list of items, returns items sorted by how
 * closely they match the query. Items with distance ≤ threshold are returned.
 *
 * @template T
 * @param {string} query - The search string
 * @param {T[]} items - The array to search
 * @param {(item: T) => string[]} getFields - Returns an array of searchable strings per item
 * @param {object} [options]
 * @param {number} [options.threshold=0.5] - 0..1 similarity threshold (1 = exact)
 * @returns {T[]} Filtered + sorted array
 */
import levenshtein from 'fast-levenshtein'

export function fuzzySearch(query, items, getFields, options = {}) {
  if (!query || query.trim() === '') return items

  const q = query.toLowerCase().trim()
  const { threshold = 0.45 } = options

  const scored = items.map((item) => {
    const fields = getFields(item).map((f) => (f || '').toLowerCase())

    // Check for substring match first (highest priority)
    const hasSubstring = fields.some((f) => f.includes(q))
    if (hasSubstring) return { item, score: 1 }

    // Compute the best Levenshtein similarity across all words in all fields
    let bestSim = 0
    for (const field of fields) {
      // Compare against the full field
      const dist = levenshtein.get(q, field)
      const maxLen = Math.max(q.length, field.length) || 1
      const sim = 1 - dist / maxLen
      if (sim > bestSim) bestSim = sim

      // Also compare against each word in the field
      const words = field.split(/\s+/)
      for (const word of words) {
        const wDist = levenshtein.get(q, word)
        const wMax = Math.max(q.length, word.length) || 1
        const wSim = 1 - wDist / wMax
        if (wSim > bestSim) bestSim = wSim
      }
    }

    return { item, score: bestSim }
  })

  return scored
    .filter(({ score }) => score >= threshold)
    .sort((a, b) => b.score - a.score)
    .map(({ item }) => item)
}
