# CompArena — Frontend

> Competitive Programming / Assignment Platform built with React, Vite, Tailwind CSS, Framer Motion, and React Query.

## Stack

| Layer         | Library                        |
|---------------|-------------------------------|
| Framework     | React 18 + Vite               |
| Routing       | React Router v6               |
| Styling       | Tailwind CSS (Cyan dark theme)|
| Animations    | Framer Motion                 |
| State         | Zustand (persisted)           |
| Data fetching | TanStack React Query v5       |
| Forms         | react-hook-form + zod         |
| HTTP          | Axios (JWT interceptors)      |
| File upload   | react-dropzone                |
| Notifications | react-hot-toast               |
| Sanitization  | DOMPurify                     |
| Fuzzy search  | fast-levenshtein              |

## Setup

```bash
# 1. Install dependencies
npm install

# 2. Configure your backend URL
cp .env.example .env.local
# Edit VITE_API_URL in .env.local

# 3. Start dev server
npm run dev

# 4. Build for production
npm run build
```

## Project Structure

```
src/
├── components/
│   ├── ui/             # Modal, StarRating, Skeleton
│   ├── Navbar.jsx
│   ├── AuthModal.jsx
│   ├── AssignmentCard.jsx
│   ├── AssignmentFormModal.jsx
│   ├── FileDropzone.jsx
│   ├── RatingModal.jsx
│   ├── PageTransition.jsx
│   └── ProtectedRoute.jsx
├── hooks/
│   ├── useAssignments.js
│   ├── useSubmissions.js
│   ├── useRatings.js
│   └── useAuth.js
├── lib/
│   ├── axios.js        # Axios instance with JWT interceptors
│   ├── levenshtein.js  # Fuzzy search utility
│   └── sanitize.js     # XSS sanitization
├── pages/
│   ├── Dashboard.jsx
│   ├── AssignmentDetails.jsx
│   └── Profile.jsx
├── store/
│   └── authStore.js    # Zustand auth store
├── App.jsx
├── main.jsx
└── index.css
```

## Backend Integration

The frontend proxies all `/api/*` requests to `VITE_API_URL` (default: `http://localhost:8080`).

JWT token is stored in Zustand (localStorage-persisted) and automatically injected by the Axios interceptor.

On 401 responses, the user is automatically logged out.

## Key Features

- **Fuzzy search** with Levenshtein distance on assignment name + description
- **Framer Motion** page transitions, card animations, modal pop-ins
- **Drag-and-drop** file upload with client-side size/type validation
- **XSS sanitization** via DOMPurify on all user-generated content
- **Zod + react-hook-form** with strict time ordering validation
- **React Query** caching + background refetching
- **Glassmorphism** dark UI with cyan accents and particle hero
