import re

PLAYLIST_TRACK_LIMIT = 25

# Strips trailing parenthetical/bracketed/dashed suffixes so "Song (Remastered
# 2011)", "Song - Live", and "Song" all normalize to the same dedup key.
_SUFFIX_PATTERN = re.compile(r"\s*[\(\[-].*$")


def _rank_scores(track_ids: list[str]) -> dict[str, float]:
    return {track_id: 1 / (rank + 1) for rank, track_id in enumerate(track_ids)}


def select_shared_artist_tracks(
    top_track_ids_a: list[str],
    top_track_ids_b: list[str],
    track_meta: dict[str, dict],
    shared_artist_ids: set[str],
) -> list[str]:
    """Tier 1: tracks by an artist both users have in their top artists.

    These are the highest-confidence picks -- if you both listen to the
    artist, a track either of you already has in rotation is a safe bet.
    """
    rank_a = _rank_scores(top_track_ids_a)
    rank_b = _rank_scores(top_track_ids_b)
    candidates = set(top_track_ids_a) | set(top_track_ids_b)

    scored = []
    for track_id in candidates:
        meta = track_meta.get(track_id)
        if meta is None or not set(meta.get("artist_ids", [])) & shared_artist_ids:
            continue
        confidence = rank_a.get(track_id, 0.0) + rank_b.get(track_id, 0.0)
        scored.append((track_id, confidence))

    scored.sort(key=lambda pair: -pair[1])
    return [track_id for track_id, _ in scored]


def select_discovery_tracks(
    top_track_ids_a: list[str],
    top_track_ids_b: list[str],
    track_meta: dict[str, dict],
    shared_eras: set[str],
) -> list[str]:
    """Tier 2: tracks from a decade both users listen to, but only one has heard.

    A track already in both pools isn't a discovery for either person, so
    those are excluded here (tier 1 already covers genuine overlap).
    """
    rank_a = _rank_scores(top_track_ids_a)
    rank_b = _rank_scores(top_track_ids_b)
    set_a, set_b = set(top_track_ids_a), set(top_track_ids_b)

    scored = []
    for track_id in set_a - set_b:
        if track_meta.get(track_id, {}).get("decade") in shared_eras:
            scored.append((track_id, rank_a[track_id]))
    for track_id in set_b - set_a:
        if track_meta.get(track_id, {}).get("decade") in shared_eras:
            scored.append((track_id, rank_b[track_id]))

    scored.sort(key=lambda pair: -pair[1])
    return [track_id for track_id, _ in scored]


def _dedup_key(meta: dict) -> tuple[str, str]:
    normalized_name = _SUFFIX_PATTERN.sub("", meta.get("name", "")).strip().lower()
    artist_ids = meta.get("artist_ids") or [""]
    return (normalized_name, artist_ids[0])


def dedupe_and_cap(
    track_ids: list[str], track_meta: dict[str, dict], limit: int = PLAYLIST_TRACK_LIMIT
) -> list[str]:
    seen_keys: set[tuple[str, str]] = set()
    result: list[str] = []
    for track_id in track_ids:
        meta = track_meta.get(track_id)
        if meta is None:
            continue
        key = _dedup_key(meta)
        if key in seen_keys:
            continue
        seen_keys.add(key)
        result.append(track_id)
        if len(result) >= limit:
            break
    return result


def build_playlist_track_ids(
    top_track_ids_a: list[str],
    top_track_ids_b: list[str],
    track_meta_a: dict[str, dict],
    track_meta_b: dict[str, dict],
    shared_artist_ids: set[str],
    shared_eras: set[str],
    limit: int = PLAYLIST_TRACK_LIMIT,
) -> list[str]:
    combined_meta = {**track_meta_b, **track_meta_a}
    tier1 = select_shared_artist_tracks(
        top_track_ids_a, top_track_ids_b, combined_meta, shared_artist_ids
    )
    tier2 = select_discovery_tracks(top_track_ids_a, top_track_ids_b, combined_meta, shared_eras)
    return dedupe_and_cap(tier1 + tier2, combined_meta, limit)
