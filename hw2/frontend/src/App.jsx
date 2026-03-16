import Navbar from './components/Navbar'
import { Route, Routes } from 'react-router-dom'
import { Home } from './pages/Home'
import { ProtectedRoute } from './components/ProtectedRoute'
import { Login } from './pages/Login'
import { Register } from './pages/Register'
import { Box } from "@mui/material"
import { ProfilePage } from './pages/ProfilePage'
import { Users } from './pages/Users'
import { Contestants } from './pages/Contestants'
import { ContestantPage } from './pages/ContestantPage'
import { Unauthorized } from './pages/Unauthorized'
import { Contests } from './pages/Contests'
import { ContestPage } from './pages/ContestPage'
import { CreateContest } from './pages/ContestCreate'
import { CreatePrize } from './pages/PrizeCreate'
import { ParticipationPage } from './pages/ParticipationPage'
import { PrizePage } from './pages/PrizePage'
import { Footer } from './components/Footer'
import "./global.css"

export function App()
{
  return (
    <div style={{display: 'flex', flexDirection: "column", height: "100%"}}>
      <Navbar />
      <Box sx={{marginTop: 2}}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/unauthorized" element={<Unauthorized />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/users/:id" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
          <Route path="/users" element={<ProtectedRoute role="admin"><Users /></ProtectedRoute>} />
          <Route path="/contestants" element={<ProtectedRoute><Contestants /></ProtectedRoute>} />
          <Route path="/contestants/:id" element={<ProtectedRoute><ContestantPage /></ProtectedRoute>} />
          <Route path="/contests" element={<ProtectedRoute><Contests /></ProtectedRoute>} />
          <Route path="/contests/create" element={<ProtectedRoute role="admin"><CreateContest /></ProtectedRoute>} />
          <Route path="/contests/:id" element={<ProtectedRoute><ContestPage /></ProtectedRoute>} />
          <Route path="/contests/:contest_id/participations/:contestant_id" element={<ProtectedRoute><ParticipationPage /></ProtectedRoute>} />
          <Route path="/contestants/:contestant_id/participations/:contest_id" element={<ProtectedRoute><ParticipationPage /></ProtectedRoute>} />
          <Route path="/contests/:contest_id/prizes/create" element={<ProtectedRoute role="admin"><CreatePrize /></ProtectedRoute>} />
          <Route path="/contests/:contest_id/prizes/:prize_id" element={<ProtectedRoute><PrizePage /></ProtectedRoute>} />
        </Routes>
      </Box>
      <Footer />
    </div>
  )
}
