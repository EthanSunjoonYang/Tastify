import type { Comparison, PlaylistResult, TasteProfile } from '../types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api'

class ApiError extends Error {
  status: number

  constructor(message: string, status: number) {
    super(message)
    this.status = status
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, options)
  if (!response.ok) {
    const body = await response.json().catch(() => null)
    const message = body?.detail ?? `Request failed with status ${response.status}`
    throw new ApiError(message, response.status)
  }
  return response.json() as Promise<T>
}

export function loginUrl(): string {
  return `${API_BASE_URL}/auth/login`
}

export function getProfile(userId: string): Promise<TasteProfile> {
  return request<TasteProfile>(`/profile/me?user_id=${userId}`)
}

export function getComparison(myUserId: string, otherUserId: string): Promise<Comparison> {
  return request<Comparison>(`/compare/${otherUserId}?user_id=${myUserId}`)
}

export function generatePlaylist(
  myUserId: string,
  otherUserId: string,
): Promise<PlaylistResult> {
  return request<PlaylistResult>(`/playlist/generate/${otherUserId}?user_id=${myUserId}`, {
    method: 'POST',
  })
}

export { ApiError }
