import { useEffect, useRef, useState } from 'react'
import { Navigate, useNavigate, useParams } from 'react-router-dom'
import { ApiError, getLobby, joinLobby, loginUrl } from '../api/client'
import { Avatar } from '../components/Avatar'
import { ErrorState } from '../components/ErrorState'
import { Spinner } from '../components/Spinner'
import { getMyUserId, setPendingLobbyHost } from '../session'
import type { Lobby as LobbyData } from '../types'

const POLL_INTERVAL_MS = 3000

export function LobbyPage() {
  const myUserId = getMyUserId()
  const { hostUserId: hostParam } = useParams<{ hostUserId?: string }>()
  const navigate = useNavigate()

  const hostUserId = hostParam ?? myUserId ?? undefined
  const isHost = Boolean(myUserId && hostUserId === myUserId)
  const isGuestEntry = Boolean(myUserId && hostUserId && !isHost)

  const [lobby, setLobby] = useState<LobbyData | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)
  const hasJoinedRef = useRef(false)

  useEffect(() => {
    if (!myUserId && hostParam) {
      setPendingLobbyHost(hostParam)
    }
  }, [myUserId, hostParam])

  useEffect(() => {
    if (!myUserId || !hostUserId) return

    let cancelled = false

    async function ensureJoinedThenPoll() {
      try {
        if (isGuestEntry && !hasJoinedRef.current) {
          await joinLobby(hostUserId!, myUserId!)
          hasJoinedRef.current = true
        }
        const data = await getLobby(hostUserId!)
        if (!cancelled) setLobby(data)
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof ApiError ? err.message : 'Failed to load lobby.')
        }
      }
    }

    ensureJoinedThenPoll()
    const intervalId = setInterval(ensureJoinedThenPoll, POLL_INTERVAL_MS)

    return () => {
      cancelled = true
      clearInterval(intervalId)
    }
  }, [myUserId, hostUserId, isGuestEntry])

  if (!myUserId) {
    if (!hostParam) {
      return <Navigate to="/" replace />
    }
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-6 px-6 text-center">
        <p className="text-sm font-medium tracking-wide text-emerald-400 uppercase">
          Taste Comparator
        </p>
        <h1 className="max-w-xl text-3xl font-bold text-white sm:text-4xl">
          Someone wants to compare music taste with you
        </h1>
        <p className="max-w-md text-neutral-400">Log in with Spotify to join their lobby.</p>
        <a
          href={loginUrl()}
          className="mt-4 rounded-full bg-emerald-500 px-8 py-3 font-semibold text-black transition hover:bg-emerald-400"
        >
          Log in with Spotify
        </a>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center px-6">
        <ErrorState message={error} />
      </div>
    )
  }

  if (!lobby) {
    return <Spinner label="Loading lobby..." />
  }

  const otherUserId = isHost ? lobby.guest?.id : lobby.host.id
  const inviteUrl = `${window.location.origin}/lobby/${myUserId}`

  function copyInviteLink() {
    navigator.clipboard.writeText(inviteUrl).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    })
  }

  function createBlend() {
    if (otherUserId) navigate(`/results/${otherUserId}`)
  }

  return (
    <div className="mx-auto max-w-2xl px-6 py-12">
      <h1 className="text-2xl font-bold text-white">
        {isHost ? 'Your Lobby' : `${lobby.host.display_name ?? 'Their'}'s Lobby`}
      </h1>

      {isHost && (
        <section className="mt-6 rounded-xl border border-neutral-800 bg-neutral-900/50 p-6">
          <p className="text-sm font-semibold tracking-wide text-neutral-400 uppercase">
            Invite link
          </p>
          <div className="mt-3 flex gap-2">
            <input
              readOnly
              value={inviteUrl}
              className="flex-1 rounded-lg border border-neutral-700 bg-neutral-950 px-3 py-2 text-sm text-neutral-300"
            />
            <button
              onClick={copyInviteLink}
              className="rounded-lg bg-emerald-500 px-4 py-2 text-sm font-semibold text-black transition hover:bg-emerald-400"
            >
              {copied ? 'Copied!' : 'Copy'}
            </button>
          </div>
        </section>
      )}

      <section className="mt-6">
        <p className="mb-3 text-sm font-semibold tracking-wide text-neutral-400 uppercase">
          Who&apos;s here
        </p>
        <div className="flex flex-col gap-3">
          <div className="flex items-center gap-3 rounded-xl border border-neutral-800 bg-neutral-900/50 p-4">
            <Avatar name={lobby.host.display_name ?? 'Host'} />
            <span className="text-white">
              {lobby.host.display_name ?? 'Host'}
              {isHost && <span className="ml-2 text-xs text-neutral-500">(you)</span>}
            </span>
          </div>
          <div className="flex items-center gap-3 rounded-xl border border-dashed border-neutral-800 bg-neutral-900/20 p-4">
            {lobby.guest ? (
              <>
                <Avatar name={lobby.guest.display_name ?? 'Guest'} />
                <span className="text-white">
                  {lobby.guest.display_name ?? 'Guest'}
                  {!isHost && <span className="ml-2 text-xs text-neutral-500">(you)</span>}
                </span>
              </>
            ) : (
              <span className="text-neutral-500">Waiting for someone to join...</span>
            )}
          </div>
        </div>
      </section>

      <div className="mt-10 text-center">
        <button
          onClick={createBlend}
          disabled={!otherUserId}
          className="rounded-full bg-emerald-500 px-8 py-3 font-semibold text-black transition hover:bg-emerald-400 disabled:cursor-not-allowed disabled:bg-neutral-700 disabled:text-neutral-400"
        >
          Create Blend
        </button>
      </div>
    </div>
  )
}
