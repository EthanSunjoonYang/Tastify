const MY_USER_ID_KEY = 'tasteComparator.myUserId'
const PENDING_LOBBY_HOST_KEY = 'tasteComparator.pendingLobbyHost'

export function getMyUserId(): string | null {
  return localStorage.getItem(MY_USER_ID_KEY)
}

export function setMyUserId(userId: string): void {
  localStorage.setItem(MY_USER_ID_KEY, userId)
}

export function clearMyUserId(): void {
  localStorage.removeItem(MY_USER_ID_KEY)
}

export function getPendingLobbyHost(): string | null {
  return sessionStorage.getItem(PENDING_LOBBY_HOST_KEY)
}

export function setPendingLobbyHost(hostUserId: string): void {
  sessionStorage.setItem(PENDING_LOBBY_HOST_KEY, hostUserId)
}

export function clearPendingLobbyHost(): void {
  sessionStorage.removeItem(PENDING_LOBBY_HOST_KEY)
}
