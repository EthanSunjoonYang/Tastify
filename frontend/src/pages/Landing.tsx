import { Navigate } from 'react-router-dom'
import { loginUrl } from '../api/client'
import { getMyUserId } from '../session'

export function Landing() {
  if (getMyUserId()) {
    return <Navigate to="/profile" replace />
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-6 px-6 text-center">
      <p className="text-sm font-medium tracking-wide text-emerald-400 uppercase">
        Taste Comparator
      </p>
      <h1 className="max-w-2xl text-4xl font-bold text-white sm:text-5xl">
        Spotify Blend tells you the number.
        <br />
        This tells you the story.
      </h1>
      <p className="max-w-xl text-neutral-400">
        See exactly why you and a friend are compatible: era-by-era listening breakdowns, shared
        artists, taste gaps, and a playlist built from what you actually have in common.
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
