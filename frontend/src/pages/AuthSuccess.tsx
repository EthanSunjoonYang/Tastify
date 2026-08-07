import { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Spinner } from '../components/Spinner'
import { clearPendingCompareWith, getPendingCompareWith, setMyUserId } from '../session'

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

    const pendingCompareWith = getPendingCompareWith()
    if (pendingCompareWith) {
      clearPendingCompareWith()
      navigate(`/results/${pendingCompareWith}`, { replace: true })
    } else {
      navigate('/profile', { replace: true })
    }
  }, [searchParams, navigate])

  return <Spinner label="Signing you in..." />
}
