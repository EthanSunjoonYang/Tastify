import { Route, Routes } from 'react-router-dom'
import { AuthSuccess } from './pages/AuthSuccess'
import { Landing } from './pages/Landing'
import { LobbyPage } from './pages/Lobby'
import { Profile } from './pages/Profile'
import { Results } from './pages/Results'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/auth/success" element={<AuthSuccess />} />
      <Route path="/profile" element={<Profile />} />
      <Route path="/lobby" element={<LobbyPage />} />
      <Route path="/lobby/:hostUserId" element={<LobbyPage />} />
      <Route path="/results/:otherUserId" element={<Results />} />
    </Routes>
  )
}

export default App
