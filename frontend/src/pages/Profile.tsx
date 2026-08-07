import { useEffect, useState } from 'react'
import { Navigate } from 'react-router-dom'
import { ApiError, getProfile } from '../api/client'
import { ArtistGrid } from '../components/ArtistGrid'
import { ErrorState } from '../components/ErrorState'
import { EraChart } from '../components/EraChart'
import { Spinner } from '../components/Spinner'
import { getMyUserId } from '../session'
import type { TasteProfile } from '../types'

const TOP_ARTISTS_DISPLAY_LIMIT = 15

function decadeSortKey(decade: string): number {
  return parseInt(decade, 10)
}

export function Profile() {
  const myUserId = getMyUserId()
  const [profile, setProfile] = useState<TasteProfile | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)

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

  const shareUrl = `${window.location.origin}/compare/${myUserId}`

  function copyShareLink() {
    navigator.clipboard.writeText(shareUrl).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    })
  }

  return (
    <div className="mx-auto max-w-4xl px-6 py-12">
      <h1 className="text-2xl font-bold text-white">Your taste profile</h1>

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

      <section className="mt-10 rounded-xl border border-neutral-800 bg-neutral-900/50 p-6">
        <h2 className="text-sm font-semibold tracking-wide text-neutral-400 uppercase">
          Compare with a friend
        </h2>
        <p className="mt-2 text-sm text-neutral-400">
          Share this link -- when they log in, you'll both see your compatibility breakdown.
        </p>
        <div className="mt-4 flex gap-2">
          <input
            readOnly
            value={shareUrl}
            className="flex-1 rounded-lg border border-neutral-700 bg-neutral-950 px-3 py-2 text-sm text-neutral-300"
          />
          <button
            onClick={copyShareLink}
            className="rounded-lg bg-emerald-500 px-4 py-2 text-sm font-semibold text-black transition hover:bg-emerald-400"
          >
            {copied ? 'Copied!' : 'Copy'}
          </button>
        </div>
      </section>
    </div>
  )
}
