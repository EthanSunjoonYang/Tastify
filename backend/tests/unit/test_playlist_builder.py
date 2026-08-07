from app.services.playlist_builder import (
    build_playlist_track_ids,
    dedupe_and_cap,
    select_discovery_tracks,
    select_shared_artist_tracks,
)


def test_select_shared_artist_tracks_filters_and_ranks_by_combined_confidence():
    top_track_ids_a = ["t1", "t2", "t4"]
    top_track_ids_b = ["t3", "t1"]
    track_meta = {
        "t1": {"name": "A", "artist_ids": ["shared1"], "decade": "2010s"},
        "t2": {"name": "B", "artist_ids": ["onlyA"], "decade": "2010s"},
        "t3": {"name": "C", "artist_ids": ["shared1"], "decade": "2010s"},
        "t4": {"name": "D", "artist_ids": ["shared1"], "decade": "2010s"},
    }

    # t1: rank_a(0)=1.0 + rank_b(1)=0.5 -> 1.5
    # t3: rank_b(0)=1.0 -> 1.0
    # t4: rank_a(2)=1/3 -> 0.333
    # t2 excluded -- its artist isn't shared
    result = select_shared_artist_tracks(top_track_ids_a, top_track_ids_b, track_meta, {"shared1"})

    assert result == ["t1", "t3", "t4"]


def test_select_discovery_tracks_excludes_tracks_known_to_both():
    top_track_ids_a = ["t1", "t2", "t4"]
    top_track_ids_b = ["t5", "t3", "t4"]
    track_meta = {
        "t1": {"name": "A", "artist_ids": ["x"], "decade": "2010s"},
        "t2": {"name": "B", "artist_ids": ["x"], "decade": "1990s"},
        "t3": {"name": "C", "artist_ids": ["x"], "decade": "2010s"},
        "t4": {"name": "D", "artist_ids": ["x"], "decade": "2010s"},
        "t5": {"name": "E", "artist_ids": ["x"], "decade": "2020s"},
    }

    # t4 known to both -> excluded even though its decade is shared
    # t2 not in a shared decade -> excluded
    # t5 not in a shared decade -> excluded
    # t1 (only in a, rank0 -> 1.0) and t3 (only in b, rank1 -> 0.5) remain
    result = select_discovery_tracks(top_track_ids_a, top_track_ids_b, track_meta, {"2010s"})

    assert result == ["t1", "t3"]


def test_dedupe_and_cap_collapses_remaster_and_live_suffixes():
    track_ids = ["t1", "t2", "t3", "t4", "t5"]
    track_meta = {
        "t1": {"name": "Song (Remastered 2011)", "artist_ids": ["a1"]},
        "t2": {"name": "Song", "artist_ids": ["a1"]},  # dup of t1
        "t3": {"name": "Song", "artist_ids": ["a2"]},  # same title, different artist -> kept
        "t4": {"name": "Another Song - Live", "artist_ids": ["a3"]},
        "t5": {"name": "Another Song", "artist_ids": ["a3"]},  # dup of t4
    }

    assert dedupe_and_cap(track_ids, track_meta) == ["t1", "t3", "t4"]


def test_dedupe_and_cap_respects_limit():
    track_ids = ["t1", "t2", "t3"]
    track_meta = {
        "t1": {"name": "A", "artist_ids": ["a1"]},
        "t2": {"name": "B", "artist_ids": ["a2"]},
        "t3": {"name": "C", "artist_ids": ["a3"]},
    }

    assert dedupe_and_cap(track_ids, track_meta, limit=2) == ["t1", "t2"]


def test_build_playlist_track_ids_orders_tier1_before_tier2_and_dedupes():
    top_track_ids_a = ["t1", "t2"]
    # "filler" has no track_meta entry -- pushes t3 to rank 1 (not 0) in b, so
    # t1's tier-1 confidence (1.0) strictly beats t3's (0.5), avoiding a tie.
    top_track_ids_b = ["filler", "t3"]
    track_meta_a = {
        "t1": {"name": "Shared Artist Song", "artist_ids": ["shared"], "decade": "2010s"},
        "t2": {"name": "Discovery Song", "artist_ids": ["onlyA"], "decade": "2010s"},
    }
    track_meta_b = {
        "t3": {"name": "Also Shared Artist Song", "artist_ids": ["shared"], "decade": "2010s"},
    }

    result = build_playlist_track_ids(
        top_track_ids_a,
        top_track_ids_b,
        track_meta_a,
        track_meta_b,
        shared_artist_ids={"shared"},
        shared_eras={"2010s"},
    )

    # t1 and t3 qualify for tier 1 (shared artist); t2 is tier-2 discovery
    assert result == ["t1", "t3", "t2"]
