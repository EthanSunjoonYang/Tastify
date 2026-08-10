export function Avatar({ name, imageUrl }: { name: string; imageUrl?: string | null }) {
  if (imageUrl) {
    return (
      <img
        src={imageUrl}
        alt={name}
        className="h-12 w-12 rounded-full object-cover"
        referrerPolicy="no-referrer"
      />
    )
  }

  const initial = name.trim().charAt(0).toUpperCase() || '?'

  return (
    <div className="flex h-12 w-12 items-center justify-center rounded-full bg-emerald-500/20 text-lg font-semibold text-emerald-300">
      {initial}
    </div>
  )
}
