import { useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { loginUrl } from '../api/client'
import { getMyUserId, setPendingCompareWith } from '../session'

export function Compare() {
  const { shareUserId } = useParams<{ shareUserId: string }>()
  const navigate = useNavigate()
  const myUserId = getMyUserId()

  useEffect(() => {
    if (!shareUserId) return
    if (myUserId) {
      navigate(`/results/${shareUserId}`, { replace: true })
    } else {
      setPendingCompareWith(shareUserId)
    }
  }, [myUserId, shareUserId, navigate])

  if (myUserId || !shareUserId) {
    return null
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-6 px-6 text-center">
      <p className="text-sm font-medium tracking-wide text-emerald-400 uppercase">
        Taste Comparator
      </p>
      <h1 className="max-w-xl text-3xl font-bold text-white sm:text-4xl">
        Someone wants to compare music taste with you
      </h1>
      <p className="max-w-md text-neutral-400">
        Log in with Spotify to see your compatibility score, shared artists, and taste gaps.
      </p>
      <a
        href={loginUrl()}
        className="mt-4 rounded-full bg-emerald-500 px-8 py-3 font-semibold text-black transition hover:bg-emerald-400"
      >
        Log in with Spotify
      </a>
    </div>
  )
}
