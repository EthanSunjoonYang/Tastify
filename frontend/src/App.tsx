import { Route, Routes } from 'react-router-dom'
import { AuthSuccess } from './pages/AuthSuccess'
import { Compare } from './pages/Compare'
import { Landing } from './pages/Landing'
import { Profile } from './pages/Profile'
import { Results } from './pages/Results'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/auth/success" element={<AuthSuccess />} />
      <Route path="/profile" element={<Profile />} />
      <Route path="/compare/:shareUserId" element={<Compare />} />
      <Route path="/results/:otherUserId" element={<Results />} />
    </Routes>
  )
}

export default App
