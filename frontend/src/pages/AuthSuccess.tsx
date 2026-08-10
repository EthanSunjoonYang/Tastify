import { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Spinner } from '../components/Spinner'
import { clearPendingLobbyHost, getPendingLobbyHost, setMyUserId } from '../session'

export function AuthSuccess() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()

  useEffect(() => {
    const userId = searchParams.get('user_id')
    if (!userId) {
      navigate('/', { replace: true })
      return
    }

    setMyUserId(userId)

    const pendingLobbyHost = getPendingLobbyHost()
    if (pendingLobbyHost) {
      clearPendingLobbyHost()
      navigate(`/lobby/${pendingLobbyHost}`, { replace: true })
    } else {
      navigate('/profile', { replace: true })
    }
  }, [searchParams, navigate])

  return <Spinner label="Signing you in..." />
}
