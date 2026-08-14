export interface TasteProfile {
  user_id: string
  era_vector: Record<string, number>
  top_artist_ids: Record<string, number>
  artist_names: Record<string, string>
  artist_images: Record<string, string>
  top_track_ids: string[]
  computed_at: string
}

export interface SharedArtist {
  artist_id: string
  name: string
  image_url: string
  weight_a: number
  weight_b: number
  combined_weight: number
}

export interface UniqueArtist {
  artist_id: string
  name: string
  image_url: string
  weight: number
}

export interface TasteGaps {
  eras_only_in_a: string[]
  eras_only_in_b: string[]
  artists_only_in_a: UniqueArtist[]
  artists_only_in_b: UniqueArtist[]
}

export interface EraBreakdownRow {
  decade: string
  user_a: number
  user_b: number
}

export interface Comparison {
  user_a_id: string
  user_a_display_name: string | null
  user_b_id: string
  user_b_display_name: string | null
  overall_score: number
  era_score: number
  artist_score: number
  shared_artists: SharedArtist[]
  taste_gaps: TasteGaps
  era_breakdown: EraBreakdownRow[]
  computed_at: string
}

export interface PlaylistResult {
  spotify_playlist_id: string
  spotify_playlist_url: string
  playlist_track_ids: string[]
}

export interface LobbyParticipant {
  id: string
  display_name: string | null
  profile_image_url: string | null
}

export interface Lobby {
  host: LobbyParticipant
  guest: LobbyParticipant | null
  blend_ready: boolean
}
