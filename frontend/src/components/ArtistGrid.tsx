interface Artist {
  artist_id: string
  name: string
  image_url: string
}

export function ArtistGrid({ artists }: { artists: Artist[] }) {
  if (artists.length === 0) {
    return <p className="text-sm text-neutral-500">None</p>
  }

  return (
    <div className="grid grid-cols-3 gap-4 sm:grid-cols-4 md:grid-cols-5">
      {artists.map((artist) => (
        <div key={artist.artist_id} className="flex flex-col items-center gap-2 text-center">
          {artist.image_url ? (
            <img
              src={artist.image_url}
              alt={artist.name}
              className="h-16 w-16 rounded-full object-cover"
            />
          ) : (
            <div className="h-16 w-16 rounded-full bg-neutral-800" />
          )}
          <span className="line-clamp-2 text-xs text-neutral-300">{artist.name}</span>
        </div>
      ))}
    </div>
  )
}
