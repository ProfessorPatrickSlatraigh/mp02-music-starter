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
    # TODO: write a SELECT query that joins PlaylistTrack, Track, Artist, and Playlist.
    #       Filter by Playlist.playlist_name = ? using a parameterised query.
    #       Order results by PlaylistTrack.position ASC.
    #
    # Hint: start from PlaylistTrack and join outward:
    #   FROM PlaylistTrack pt
    #   JOIN Track    t  ON pt.track_id    = t.track_id
    #   JOIN Artist   a  ON t.artist_id    = a.artist_id
    #   JOIN Playlist p  ON pt.playlist_id = p.playlist_id
    #   WHERE p.playlist_name = ?
    #
    # Your query here:
    # TODO: replace the stub query below with your actual SELECT statement.
    #       The stub returns an empty result set so the function is callable
    #       before implementation.  The ? placeholder must match playlist_name.
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
    # TODO: write a SELECT query using LEFT JOIN between Track and PlaylistTrack.
    #       After the LEFT JOIN, filter rows where PlaylistTrack.track_id IS NULL.
    #       Also join Artist to retrieve the artist name.
    #
    # Hint:
    #   FROM   Track t
    #   JOIN   Artist a          ON t.artist_id = a.artist_id
    #   LEFT JOIN PlaylistTrack pt ON t.track_id = pt.track_id
    #   WHERE  pt.track_id IS NULL
    #
    # Your query here:
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
    # TODO: write a SELECT query that groups PlaylistTrack by track_id,
    #       counts the rows per group, joins Track and Artist for the names,
    #       orders by COUNT(*) DESC, and limits to 1 row.
    #
    # Hint:
    #   SELECT t.title, a.name, COUNT(*) AS playlist_count
    #   FROM   PlaylistTrack pt
    #   JOIN   Track  t ON pt.track_id  = t.track_id
    #   JOIN   Artist a ON t.artist_id  = a.artist_id
    #   GROUP BY pt.track_id
    #   ORDER BY playlist_count DESC
    #   LIMIT 1
    #
    # Your query here:
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
    return conn.execute(query).fetchone()


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
    # TODO: write a SELECT query that:
    #   - joins Playlist, PlaylistTrack, and Track
    #   - groups by Playlist.playlist_id (or playlist_name)
    #   - selects Playlist.playlist_name and SUM(Track.duration_seconds) / 60.0
    #   - orders by the SUM DESC
    #
    # Hint:
    #   SELECT  p.playlist_name,
    #           SUM(t.duration_seconds) / 60.0 AS total_minutes
    #   FROM    Playlist      p
    #   JOIN    PlaylistTrack pt ON p.playlist_id = pt.playlist_id
    #   JOIN    Track         t  ON pt.track_id   = t.track_id
    #   GROUP BY p.playlist_id
    #   ORDER BY total_minutes DESC
    #
    # Your query here:
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
        (1, "Sample Artist A", "Hip-Hop", "New York"),
        (2, "Sample Artist B", "R&B",     "Atlanta"),
    ])
    conn.executemany("INSERT OR IGNORE INTO Track VALUES (?,?,?,?)", [
        (1, "Track One",   210, 1),
        (2, "Track Two",   185, 1),
        (3, "Track Three", 240, 2),
        (4, "Track Four",  195, 2),
        (5, "Orphan Track", 170, 1),  # intentionally not added to any playlist
    ])
    conn.executemany("INSERT OR IGNORE INTO Playlist VALUES (?,?,?)", [
        (1, "Morning Commute", "Student A"),
        (2, "Study Session",   "Student B"),
    ])
    conn.executemany("INSERT OR IGNORE INTO PlaylistTrack VALUES (?,?,?)", [
        (1, 1, 1), (1, 2, 2), (1, 3, 3),
        (2, 1, 1), (2, 4, 2),  # Track 1 appears on both playlists
    ])
    conn.commit()

    # Run each function and print a brief result summary
    print("=" * 60)
    print("Function 1 — get_playlist_tracks('Morning Commute')")
    rows = get_playlist_tracks(conn, "Morning Commute")
    if rows:
        for row in rows:
            print(f"  pos {row[3]:>2} | {row[0]:<20} | {row[1]:<20} | {row[2]}s")
    else:
        print("  (no rows returned — check your query)")

    print()
    print("Function 2 — get_tracks_on_no_playlist()")
    rows = get_tracks_on_no_playlist(conn)
    if rows:
        for row in rows:
            print(f"  id={row[0]}  {row[1]} by {row[2]}")
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
            print(f"  {row[0]:<25} {mins}:{secs:02d}")
    else:
        print("  (no rows returned — check your query)")

    print("=" * 60)
    conn.close()
# AUTHOR2 FINAL FIX
