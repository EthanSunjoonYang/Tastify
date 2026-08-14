import { useEffect, useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { ApiError, getProfile } from '../api/client'
import { ArtistGrid } from '../components/ArtistGrid'
import { ErrorState } from '../components/ErrorState'
import { EraChart } from '../components/EraChart'
import { Spinner } from '../components/Spinner'
import { clearMyUserId, getMyUserId } from '../session'
import type { TasteProfile } from '../types'

const TOP_ARTISTS_DISPLAY_LIMIT = 15

function decadeSortKey(decade: string): number {
  return parseInt(decade, 10)
}

export function Profile() {
  const myUserId = getMyUserId()
  const navigate = useNavigate()
  const [profile, setProfile] = useState<TasteProfile | null>(null)
  const [error, setError] = useState<string | null>(null)

  function signOut() {
    clearMyUserId()
    navigate('/', { replace: true })
  }

  useEffect(() => {
    if (!myUserId) return
    getProfile(myUserId)
      .then(setProfile)
      .catch((err: unknown) => {
        setError(err instanceof ApiError ? err.message : 'Failed to load your profile.')
      })
  }, [myUserId])

  if (!myUserId) {
    return <Navigate to="/" replace />
  }

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center px-6">
        <ErrorState message={error} />
      </div>
    )
  }

  if (!profile) {
    return <Spinner label="Loading your taste profile..." />
  }

  const eraData = Object.entries(profile.era_vector)
    .sort(([a], [b]) => decadeSortKey(a) - decadeSortKey(b))
    .map(([decade, value]) => ({ decade, value }))

  const topArtists = Object.entries(profile.top_artist_ids)
    .sort(([, a], [, b]) => b - a)
    .slice(0, TOP_ARTISTS_DISPLAY_LIMIT)
    .map(([artistId]) => ({
      artist_id: artistId,
      name: profile.artist_names[artistId] ?? '',
      image_url: profile.artist_images[artistId] ?? '',
    }))

  return (
    <div className="mx-auto max-w-4xl px-6 py-12">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white">Your taste profile</h1>
        <button
          onClick={signOut}
          className="rounded-full border border-neutral-700 px-4 py-2 text-sm text-neutral-400 transition hover:border-neutral-500 hover:text-white"
        >
          Sign out
        </button>
      </div>

      <section className="mt-8">
        <h2 className="mb-3 text-sm font-semibold tracking-wide text-neutral-400 uppercase">
          Listening era
        </h2>
        <EraChart
          data={eraData}
          series={[{ key: 'value', name: 'Share of listening', color: '#34d399' }]}
        />
      </section>

      <section className="mt-10">
        <h2 className="mb-3 text-sm font-semibold tracking-wide text-neutral-400 uppercase">
          Top artists
        </h2>
        <ArtistGrid artists={topArtists} />
      </section>

      <section className="mt-10 rounded-xl border border-neutral-800 bg-neutral-900/50 p-6 text-center">
        <h2 className="text-sm font-semibold tracking-wide text-neutral-400 uppercase">
          Compare with a friend
        </h2>
        <p className="mt-2 text-sm text-neutral-400">
          Head to your lobby to invite someone and blend your taste together.
        </p>
        <Link
          to="/lobby"
          className="mt-4 inline-block rounded-full bg-emerald-500 px-8 py-3 font-semibold text-black transition hover:bg-emerald-400"
        >
          Go to your lobby
        </Link>
      </section>
    </div>
  )
}
