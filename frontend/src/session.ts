const MY_USER_ID_KEY = 'tasteComparator.myUserId'
const COMPARE_WITH_KEY = 'tasteComparator.compareWith'

export function getMyUserId(): string | null {
  return localStorage.getItem(MY_USER_ID_KEY)
}

export function setMyUserId(userId: string): void {
  localStorage.setItem(MY_USER_ID_KEY, userId)
}

export function getPendingCompareWith(): string | null {
  return sessionStorage.getItem(COMPARE_WITH_KEY)
}

export function setPendingCompareWith(userId: string): void {
  sessionStorage.setItem(COMPARE_WITH_KEY, userId)
}

export function clearPendingCompareWith(): void {
  sessionStorage.removeItem(COMPARE_WITH_KEY)
}
