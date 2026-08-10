import { useEffect, useState } from 'react'
import { Navigate, useParams } from 'react-router-dom'
import { ApiError, generatePlaylist, getComparison } from '../api/client'
import { ArtistGrid } from '../components/ArtistGrid'
import { ArtistOverlapDonut } from '../components/ArtistOverlapDonut'
import { ErrorState } from '../components/ErrorState'
import { EraChart } from '../components/EraChart'
import { ScoreCard } from '../components/ScoreCard'
import { ScoreRing } from '../components/ScoreRing'
import { Spinner } from '../components/Spinner'
import { getMyUserId } from '../session'
import type { Comparison, PlaylistResult } from '../types'

export function Results() {
  const myUserId = getMyUserId()
  const { otherUserId } = useParams<{ otherUserId: string }>()
  const [comparison, setComparison] = useState<Comparison | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [playlist, setPlaylist] = useState<PlaylistResult | null>(null)
  const [playlistError, setPlaylistError] = useState<string | null>(null)
  const [playlistRetrying, setPlaylistRetrying] = useState(false)

  useEffect(() => {
    if (!myUserId || !otherUserId) return

    Promise.allSettled([
      getComparison(myUserId, otherUserId),
      generatePlaylist(myUserId, otherUserId),
    ]).then(([comparisonResult, playlistResult]) => {
      if (comparisonResult.status === 'fulfilled') {
        setComparison(comparisonResult.value)
      } else {
        const reason = comparisonResult.reason
        setError(reason instanceof ApiError ? reason.message : 'Failed to load comparison.')
      }

      if (playlistResult.status === 'fulfilled') {
        setPlaylist(playlistResult.value)
      } else {
        const reason = playlistResult.reason
        setPlaylistError(reason instanceof ApiError ? reason.message : 'Failed to generate playlist.')
      }
    })
  }, [myUserId, otherUserId])

  if (!myUserId || !otherUserId) {
    return <Navigate to="/" replace />
  }

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center px-6">
        <ErrorState message={error} />
      </div>
    )
  }

  if (!comparison) {
    return <Spinner label="Creating your blend..." />
  }

  const otherLabel = comparison.user_b_display_name ?? 'them'

  function retryPlaylist() {
    if (!myUserId || !otherUserId) return
    setPlaylistRetrying(true)
    setPlaylistError(null)
    generatePlaylist(myUserId, otherUserId)
      .then(setPlaylist)
      .catch((err: unknown) => {
        setPlaylistError(err instanceof ApiError ? err.message : 'Failed to generate playlist.')
      })
      .finally(() => setPlaylistRetrying(false))
  }

  return (
    <div className="mx-auto max-w-4xl px-6 py-12">
      <div className="flex flex-col items-center text-center">
        <p className="mb-4 text-sm text-neutral-400">You and {otherLabel} are</p>
        <ScoreRing percent={comparison.overall_score} label="compatible" />
      </div>

      <div className="mt-10 grid grid-cols-2 gap-4">
        <ScoreCard label="Era similarity" value={comparison.era_score} />
        <ScoreCard label="Artist overlap" value={comparison.artist_score} />
      </div>

      <section className="mt-10">
        <h2 className="mb-3 text-sm font-semibold tracking-wide text-neutral-400 uppercase">
          Listening era, side by side
        </h2>
        <EraChart
          data={comparison.era_breakdown}
          series={[
            { key: 'user_a', name: 'You', color: '#34d399' },
            { key: 'user_b', name: otherLabel, color: '#60a5fa' },
          ]}
        />
      </section>

      <section className="mt-10">
        <h2 className="mb-3 text-sm font-semibold tracking-wide text-neutral-400 uppercase">
          Artist overlap
        </h2>
        <ArtistOverlapDonut
          sharedCount={comparison.shared_artists.length}
          onlyYouCount={comparison.taste_gaps.artists_only_in_a.length}
          onlyThemCount={comparison.taste_gaps.artists_only_in_b.length}
          otherLabel={otherLabel}
        />
      </section>

      <section className="mt-10">
        <h2 className="mb-3 text-sm font-semibold tracking-wide text-neutral-400 uppercase">
          Shared artists
        </h2>
        <ArtistGrid artists={comparison.shared_artists} />
      </section>

      <section className="mt-10">
        <h2 className="mb-3 text-sm font-semibold tracking-wide text-neutral-400 uppercase">
          Taste gaps
        </h2>
        <div className="space-y-2 text-sm text-neutral-300">
          {comparison.taste_gaps.eras_only_in_a.length > 0 && (
            <p>
              You listen to {comparison.taste_gaps.eras_only_in_a.join(', ')} music that{' '}
              {otherLabel} hasn't touched.
            </p>
          )}
          {comparison.taste_gaps.eras_only_in_b.length > 0 && (
            <p>
              {otherLabel} listens to {comparison.taste_gaps.eras_only_in_b.join(', ')} music that
              you haven't touched.
            </p>
          )}
          {comparison.taste_gaps.eras_only_in_a.length === 0 &&
            comparison.taste_gaps.eras_only_in_b.length === 0 && (
              <p className="text-neutral-500">You listen to the same eras.</p>
            )}
        </div>
        {comparison.taste_gaps.artists_only_in_a.length > 0 && (
          <div className="mt-4">
            <p className="mb-2 text-xs text-neutral-500">Only in your rotation</p>
            <ArtistGrid artists={comparison.taste_gaps.artists_only_in_a} />
          </div>
        )}
        {comparison.taste_gaps.artists_only_in_b.length > 0 && (
          <div className="mt-4">
            <p className="mb-2 text-xs text-neutral-500">Only in {otherLabel}'s rotation</p>
            <ArtistGrid artists={comparison.taste_gaps.artists_only_in_b} />
          </div>
        )}
      </section>

      <section className="mt-10 rounded-xl border border-neutral-800 bg-neutral-900/50 p-6 text-center">
        {playlist ? (
          <a
            href={playlist.spotify_playlist_url}
            target="_blank"
            rel="noreferrer"
            className="inline-block rounded-full bg-emerald-500 px-8 py-3 font-semibold text-black transition hover:bg-emerald-400"
          >
            Open playlist on Spotify ↗
          </a>
        ) : (
          <div>
            <p className="text-sm text-red-400">{playlistError}</p>
            <button
              onClick={retryPlaylist}
              disabled={playlistRetrying}
              className="mt-3 rounded-full bg-emerald-500 px-8 py-3 font-semibold text-black transition hover:bg-emerald-400 disabled:opacity-50"
            >
              {playlistRetrying ? 'Retrying...' : 'Retry playlist generation'}
            </button>
          </div>
        )}
      </section>
    </div>
  )
}
