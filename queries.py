"""
queries.py
==========
CIS 3120 · MP02 — SQL and Database
Author 2 module — all query functions

CONTRACT SUMMARY
----------------
Implement the four functions below exactly as specified.  Every function
accepts a conn argument and returns results as a list of rows (the output
of .fetchall()).  The Integrator's main.py calls these functions and handles
all output formatting — do NOT print inside any of these functions.

REQUIRED (graded):
    ✓ get_playlist_tracks(conn, playlist_name)   — JOIN across 4 tables; ORDER BY position
    ✓ get_tracks_on_no_playlist(conn)             — LEFT JOIN + IS NULL pattern
    ✓ get_most_added_track(conn)                  — GROUP BY + ORDER BY COUNT DESC
    ✓ get_playlist_durations(conn)                — SUM + GROUP BY; result in minutes
    ✓ Isolation  — this module must NOT import from schema_data.py or main.py

IMPORTANT:
    - Do not print anything inside these functions.
    - Do not open a database connection inside these functions.
    - All database access must go through the conn parameter.
    - Column order within each returned row must match the specification below.
"""

import sqlite3


# ─────────────────────────────────────────────────────────────────────────────
# FUNCTION 1 — Playlist track listing
# ─────────────────────────────────────────────────────────────────────────────

def get_playlist_tracks(conn, playlist_name):
    """Return all tracks on the named playlist, ordered by position.

    JOIN pattern required:
        PlaylistTrack  →  Track  →  Artist  →  Playlist

    Each returned row must include the following columns in this order:
        1. track title           (Track.title)
        2. artist name           (Artist.name)
        3. duration in seconds   (Track.duration_seconds)
        4. position on playlist  (PlaylistTrack.position)

    Results must be sorted by PlaylistTrack.position ASC.

    Parameters
    ----------
    conn          : sqlite3.Connection  — open database connection
    playlist_name : str                 — exact value of Playlist.playlist_name

    Returns
    -------
    list of tuples  [(title, artist_name, duration_seconds, position), ...]
    Empty list if the playlist name does not exist.
    """
    query = """
        SELECT t.title,
               a.name AS artist_name,
               t.duration_seconds,
               pt.position
        FROM PlaylistTrack pt
        JOIN Track t ON pt.track_id = t.track_id
        JOIN Artist a ON t.artist_id = a.artist_id
        JOIN Playlist p ON pt.playlist_id = p.playlist_id
        WHERE p.playlist_name = ?
        ORDER BY pt.position ASC
    """
    return conn.execute(query, (playlist_name,)).fetchall()


# ─────────────────────────────────────────────────────────────────────────────
# FUNCTION 2 — Tracks on no playlist
# ─────────────────────────────────────────────────────────────────────────────

def get_tracks_on_no_playlist(conn):
    """Return all tracks that do not appear on any playlist.

    Pattern required: LEFT JOIN between Track and PlaylistTrack, then
    filter WHERE PlaylistTrack.track_id IS NULL.

    Each returned row must include the following columns in this order:
        1. track_id              (Track.track_id)
        2. track title           (Track.title)
        3. artist name           (Artist.name)

    Parameters
    ----------
    conn : sqlite3.Connection  — open database connection

    Returns
    -------
    list of tuples  [(track_id, title, artist_name), ...]
    Empty list if every track belongs to at least one playlist.
    """
    query = """
        SELECT t.track_id,
               t.title,
               a.name AS artist_name
        FROM Track t
        JOIN Artist a ON t.artist_id = a.artist_id
        LEFT JOIN PlaylistTrack pt ON t.track_id = pt.track_id
        WHERE pt.track_id IS NULL
    """
    return conn.execute(query).fetchall()


# ─────────────────────────────────────────────────────────────────────────────
# FUNCTION 3 — Most-added track
# ─────────────────────────────────────────────────────────────────────────────

def get_most_added_track(conn):
    """Return the single track that appears on the greatest number of playlists.

    Pattern required: GROUP BY track_id with COUNT(*), ORDER BY count DESC, LIMIT 1.

    The returned row must include the following columns in this order:
        1. track title           (Track.title)
        2. artist name           (Artist.name)
        3. playlist count        (COUNT of PlaylistTrack rows for this track)

    Parameters
    ----------
    conn : sqlite3.Connection  — open database connection

    Returns
    -------
    One tuple  (title, artist_name, playlist_count)
    None if PlaylistTrack is empty.
    """
    query = """
        SELECT t.title,
               a.name AS artist_name,
               COUNT(*) AS playlist_count
        FROM PlaylistTrack pt
        JOIN Track t ON pt.track_id = t.track_id
        JOIN Artist a ON t.artist_id = a.artist_id
        GROUP BY pt.track_id
        ORDER BY playlist_count DESC
        LIMIT 1
    """
    result = conn.execute(query).fetchone()
    return result


# ─────────────────────────────────────────────────────────────────────────────
# FUNCTION 4 — Playlist total durations
# ─────────────────────────────────────────────────────────────────────────────

def get_playlist_durations(conn):
    """Return each playlist's name and total duration, longest first.

    Pattern required: SUM(Track.duration_seconds) per playlist using GROUP BY,
    then divide by 60.0 to convert to minutes.

    Each returned row must include the following columns in this order:
        1. playlist name         (Playlist.playlist_name)
        2. total duration        (SUM(duration_seconds) / 60.0, as a float)

    Results must be ordered by total duration DESC (longest playlist first).

    Parameters
    ----------
    conn : sqlite3.Connection  — open database connection

    Returns
    -------
    list of tuples  [(playlist_name, total_minutes), ...]
    Empty list if PlaylistTrack is empty.
    """
    query = """
        SELECT p.playlist_name,
               SUM(t.duration_seconds) / 60.0 AS total_minutes
        FROM Playlist p
        JOIN PlaylistTrack pt ON p.playlist_id = pt.playlist_id
        JOIN Track t ON pt.track_id = t.track_id
        GROUP BY p.playlist_id
        ORDER BY total_minutes DESC
    """
    return conn.execute(query).fetchall()


# ─────────────────────────────────────────────────────────────────────────────
# Standalone smoke test  (run:  python queries.py)
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # This block builds a minimal in-memory database so Author 2 can test
    # query functions independently, without depending on schema_data.py.
    # It does NOT replace the integration test in main.py.

    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON;")

    # Minimal schema — matches the required DDL exactly
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS Artist (
            artist_id INTEGER PRIMARY KEY, name TEXT NOT NULL,
            genre TEXT NOT NULL, origin_city TEXT
        );
        CREATE TABLE IF NOT EXISTS Track (
            track_id INTEGER PRIMARY KEY, title TEXT NOT NULL,
            duration_seconds INTEGER NOT NULL,
            artist_id INTEGER NOT NULL REFERENCES Artist(artist_id)
        );
        CREATE TABLE IF NOT EXISTS Playlist (
            playlist_id INTEGER PRIMARY KEY,
            playlist_name TEXT NOT NULL, owner_name TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS PlaylistTrack (
            playlist_id INTEGER NOT NULL REFERENCES Playlist(playlist_id),
            track_id    INTEGER NOT NULL REFERENCES Track(track_id),
            position    INTEGER NOT NULL,
            PRIMARY KEY (playlist_id, track_id)
        );
    """)

    # Minimal seed — enough rows to exercise all four query functions
    conn.executemany("INSERT OR IGNORE INTO Artist VALUES (?,?,?,?)", [
        (1, "Wale", "Hip-Hop", "Washington, D.C."),
        (2, "Travis Scott", "Hip-Hop", "Houston"),
        (3, "Don Toliver", "Hip-Hop", "Houston"),
        (4, "Kenny Mason", "Hip-Hop", "Atlanta"),
        (5, "J. Cole", "Hip-Hop", "Fayetteville"),
        (6, "Freddie Gibbs & Alchemist", "Hip-Hop", "Gary / Beverly Hills"),
        (7, "Westside Gunn", "Hip-Hop", "Buffalo"),
        (8, "Clipse", "Hip-Hop", "Virginia Beach"),
        (9, "Chance The Rapper", "Hip-Hop", "Chicago"),
    ])
    
    conn.executemany("INSERT OR IGNORE INTO Track VALUES (?,?,?,?)", [
        (1, "Power and Problems", 240, 1),
        (2, "goosebumps", 244, 2),
        (3, "STARGAZING", 271, 2),
        (4, "CAN'T SAY Feat. Don Toliver", 198, 2),
        (5, "No Idea", 154, 3),
        (6, "Drugs N Hella Melodies Feat. Kali Uchis", 198, 3),
        (7, "MAMA DON'T KNOW", 192, 4),
        (8, "GIVENCHY BAG", 157, 4),
        (9, "SHELL", 210, 4),
        (10, "Huntin Wabbitz", 162, 5),
        (11, "3001", 158, 5),
        (12, "1995", 289, 6),
        (13, "Mar-A-Lago", 149, 6),
        (14, "God Is Perfect", 239, 6),
        (15, "Why I Do Em Like That feat. Billie Esco", 241, 7),
        (16, "MANDELA", 122, 7),
        (17, "F.I.C.O. Feat. Stove God Cooks", 202, 8),
        (18, "Ride Feat Do or Die", 179, 9),
    ])
    
    conn.executemany("INSERT OR IGNORE INTO Playlist VALUES (?,?,?)", [
        (1, "Workout Mix", "Roy"),
        (2, "Late Night Vibes", "Roy"),
        (3, "Study Mode", "Roy"),
        (4, "Weekend Drive", "Roy"),
    ])
    
    conn.executemany("INSERT OR IGNORE INTO PlaylistTrack VALUES (?,?,?)", [
        (1, 2, 1),
        (1, 3, 2),
        (1, 7, 3),
        (1, 10, 4),
        (1, 12, 5),
        (2, 1, 1),
        (2, 5, 2),
        (2, 6, 3),
        (2, 14, 4),
        (2, 15, 5),
        (3, 8, 1),
        (3, 9, 2),
        (3, 11, 3),
        (3, 13, 4),
        (3, 18, 5),
        (4, 4, 1),
        (4, 12, 2),
        (4, 14, 3),
        (4, 16, 4),
        (4, 17, 5),
    ])
    
    conn.commit()

    # Run each function and print a brief result summary
    print("=" * 60)
    print("Function 1 — get_playlist_tracks('Workout Mix')")
    rows = get_playlist_tracks(conn, "Workout Mix")
    if rows:
        for row in rows:
            print(f"  pos {row[3]:>2} | {row[0]:<35} | {row[1]:<25} | {row[2]}s")
    else:
        print("  (no rows returned — check your query)")

    print()
    print("Function 2 — get_tracks_on_no_playlist()")
    rows = get_tracks_on_no_playlist(conn)
    if rows:
        for row in rows:
            print(f"  id={row[0]} | {row[1]:<35} | {row[2]}")
    else:
        print("  (no rows returned — check your query)")

    print()
    print("Function 3 — get_most_added_track()")
    row = get_most_added_track(conn)
    if row:
        print(f"  {row[0]} by {row[1]} — appears on {row[2]} playlist(s)")
    else:
        print("  (no row returned — check your query)")

    print()
    print("Function 4 — get_playlist_durations()")
    rows = get_playlist_durations(conn)
    if rows:
        for row in rows:
            total_sec = row[1] * 60
            mins = int(total_sec) // 60
            secs = int(total_sec) % 60
            print(f"  {row[0]:<20} | {mins}:{secs:02d} ({row[1]:.2f} minutes)")
    else:
        print("  (no rows returned — check your query)")

    print("=" * 60)
    conn.close()