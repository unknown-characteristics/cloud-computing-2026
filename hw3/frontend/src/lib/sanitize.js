/**
 * XSS sanitization using DOMPurify.
 * Call sanitize() before rendering any user-generated HTML content.
 */
import DOMPurify from 'dompurify'

/** Sanitizes an HTML string, stripping dangerous tags/attributes */
export function sanitize(dirty) {
  return DOMPurify.sanitize(dirty, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'br', 'p', 'ul', 'ol', 'li'],
    ALLOWED_ATTR: ['href', 'target', 'rel'],
  })
}

/** Strips ALL HTML (plain text only) */
export function sanitizeText(dirty) {
  return DOMPurify.sanitize(dirty, { ALLOWED_TAGS: [], ALLOWED_ATTR: [] })
}
