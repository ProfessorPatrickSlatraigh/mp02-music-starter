"""
schema_data.py
==============
CIS 3120 · MP02 — SQL and Database
Author 1 module — schema creation and seed data

CONTRACT SUMMARY
----------------
Implement build_database(conn) and seed_database(conn) exactly as specified.
The Integrator's main.py and Author 2's queries.py depend on the table names
and column names defined here.  Do not rename any column.

REQUIRED (graded):
    ✓ build_database(conn)   — creates four tables; PRAGMA foreign_keys = ON first
    ✓ seed_database(conn)    — populates all four tables with executemany; commits
    ✓ IntegrityError demo    — in __main__ block; catches a bad artist_id insert
    ✓ .backup() to music.db  — in __main__ block; prints confirmation
    ✓ INSERT OR IGNORE        — used in all INSERT statements in seed_database()
    ✓ Isolation               — this module must NOT import from queries.py or main.py
"""

import sqlite3
import os


# ─────────────────────────────────────────────────────────────────────────────
# PART 1 — Schema creation
# ─────────────────────────────────────────────────────────────────────────────

def build_database(conn):
    """Create the four-table music schema in the database referenced by conn.

    Requirements (all graded):
      - Call conn.execute("PRAGMA foreign_keys = ON;") as the FIRST statement.
      - Use CREATE TABLE IF NOT EXISTS for every table.
      - Create tables in dependency order so foreign key references resolve:
            Artist  →  Track  →  Playlist  →  PlaylistTrack
      - PlaylistTrack must declare a composite PRIMARY KEY (playlist_id, track_id).
      - Call conn.commit() at the end.

    Parameters
    ----------
    conn : sqlite3.Connection
        An open SQLite connection.  May be :memory: or a file-backed database.

    Returns
    -------
    None
    """
    # Step 1 — enable foreign key enforcement  (DO NOT REMOVE THIS LINE)
    conn.execute("PRAGMA foreign_keys = ON;")

    # Step 2 — Artist table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS Artist (
            artist_id    INTEGER PRIMARY KEY,
            name         TEXT    NOT NULL,
            genre        TEXT    NOT NULL,
            origin_city  TEXT
        )
    """)

    # Step 3 — Track table  (references Artist)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS Track (
            track_id         INTEGER PRIMARY KEY,
            title            TEXT    NOT NULL,
            duration_seconds INTEGER NOT NULL,
            artist_id        INTEGER NOT NULL
                REFERENCES Artist(artist_id)
        )
    """)

    # Step 4 — Playlist table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS Playlist (
            playlist_id    INTEGER PRIMARY KEY,
            playlist_name  TEXT    NOT NULL,
            owner_name     TEXT    NOT NULL
        )
    """)

    # Step 5 — PlaylistTrack junction table  (references both Playlist and Track)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS PlaylistTrack (
            playlist_id  INTEGER NOT NULL REFERENCES Playlist(playlist_id),
            track_id     INTEGER NOT NULL REFERENCES Track(track_id),
            position     INTEGER NOT NULL,
            PRIMARY KEY (playlist_id, track_id)
        )
    """)

    conn.commit()
    print("build_database: schema created successfully.")


# ─────────────────────────────────────────────────────────────────────────────
# PART 2 — Seed data
# ─────────────────────────────────────────────────────────────────────────────

def seed_database(conn):
    """Populate all four tables with realistic music data.

    Requirements (all graded):
      - Use conn.executemany() for every table — no individual execute() inserts.
      - Use INSERT OR IGNORE so this function can be called more than once
        without raising IntegrityError on duplicate primary keys.
      - Insert at minimum:
            6  artists
            18 tracks     (each referencing a valid artist_id)
            4  playlists
            20 PlaylistTrack assignments
      - At least one artist must have three or more tracks assigned to playlists.
      - Call conn.commit() after all inserts.

    Parameters
    ----------
    conn : sqlite3.Connection
        An open, schema-ready SQLite connection.

    Returns
    -------
    None
    """

    # ── Artists ──────────────────────────────────────────────────────────────
    # Columns: artist_id, name, genre, origin_city
    # Replace the placeholder rows below with at least 6 real artists.
    # Choose a genre theme your team agrees on (hip-hop, jazz, Latin, K-pop, etc.)
    # TODO: replace placeholder data with your team's chosen artists

    artists = [
        # (artist_id, name, genre, origin_city),
        #(1, "TODO — Artist Name", "TODO — Genre", "TODO — City"),
        (1, "Rihanna", "Pop", "Barbados"),
        (2, "Eminem", "Hip-Hop", "Detroit"),
        (3, "Sade", "Soul", "London"),
        (4, "Bob Marley", "Reggae", "Kingston"),
        (5, "Beyoncé", "R&B", "Houston"),
        (6, "Whitney Houston", "Pop", "Newark")
        
        # add at least 5 more rows ...
    ]

    conn.executemany(
        "INSERT OR IGNORE INTO Artist VALUES (?, ?, ?, ?)",
        artists
    )

    # ── Tracks ───────────────────────────────────────────────────────────────
    # Columns: track_id, title, duration_seconds, artist_id
    # Every artist_id here must exist in the artists list above.
    # duration_seconds: a 3-minute song = 180 seconds.
    # TODO: replace placeholder data with your team's chosen tracks (minimum 18)

    tracks = [
        # (track_id, title, duration_seconds, artist_id),
        #(1, "TODO — Track Title", 200, 1),
        # add at least 17 more rows ...
        # Rihanna
        (1, "Umbrella", 262, 1),
        (2, "Diamonds", 225, 1),
        (3, "We Found Love", 215, 1),

        #Eminem
        (4, "Lose Yourself", 326, 2),
        (5, "Stan", 404, 2),
        (6, "Without Me", 290, 2),

        #Sade
        (7, "Smooth Operator", 298, 3),
        (8, "No Ordinary Love", 420, 3),
        (9, "By Your Side", 275, 3),

        #Bob Marley
        (10, "No Woman No Cry", 431, 4),
        (11, "One Love", 178, 4),
        (12, "Three Little Birds", 180, 4),

        #Beyonce
        (13, "Halo", 261, 5),
        (14, "Crazy in Love", 235, 5),
        (15, "Single Ladies", 194, 5),

        #Whitney Houston
        (16, "I Will Always Love You", 273, 6),
        (17, "I Wanna Dance with Somebody", 293, 6),
        (18, "Greatest Love of All", 295, 6)
    ]

    conn.executemany(
        "INSERT OR IGNORE INTO Track VALUES (?, ?, ?, ?)",
        tracks
    )

    # ── Playlists ────────────────────────────────────────────────────────────
    # Columns: playlist_id, playlist_name, owner_name
    # TODO: replace placeholder data with your team's chosen playlists (minimum 4)

    playlists = [
        # (playlist_id, playlist_name, owner_name),
        #(1, "TODO — Playlist Name", "TODO — Owner"),
        # add at least 3 more rows ...
        (1, "Throwback Hits", "David"),
        (2, "Soulzzz", "Sarah"),
        (3, "Legends Only", "Alexis"),
        (4, "Top Classics", "Jordan")
    ]

    conn.executemany(
        "INSERT OR IGNORE INTO Playlist VALUES (?, ?, ?)",
        playlists
    )

    # ── PlaylistTrack ─────────────────────────────────────────────────────────
    # Columns: playlist_id, track_id, position
    # Both playlist_id and track_id must reference rows inserted above.
    # (playlist_id, track_id) pairs must be unique — the composite PK enforces this.
    # position is the 1-based slot of the track within the playlist.
    # At least one artist must have 3+ tracks appearing across these assignments.
    # TODO: replace placeholder data with your team's chosen assignments (minimum 20)

    playlist_tracks = [
        # (playlist_id, track_id, position),
        (1, 1, 1),
        # add at least 19 more rows ...
        (1, 4, 2), (1, 7, 3), (1, 10, 4), (1, 13, 5), (2, 1, 6),
        (2, 7, 1), (2, 8, 2), (2, 9, 3), (2, 17, 4), (2, 18, 5),
        (3, 4, 1), (3, 10, 2), (3, 16, 3), (3, 11, 4), (3, 5, 5),
        (4, 2, 1), (4, 6, 2), (4, 12, 3), (4, 14, 4), (4, 15, 5)
    ]

    conn.executemany(
        "INSERT OR IGNORE INTO PlaylistTrack VALUES (?, ?, ?)",
        playlist_tracks
    )

    conn.commit()
    print("seed_database: data inserted successfully.")


# ─────────────────────────────────────────────────────────────────────────────
# PART 3 — Standalone demonstration  (run:  python schema_data.py)
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":

    # 3a — Build and seed a RAM-only database
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON;")
    build_database(conn)
    seed_database(conn)

    # ── Quick sanity check ────────────────────────────────────────────────────
    row_counts = {
        "Artist":       conn.execute("SELECT COUNT(*) FROM Artist").fetchone()[0],
        "Track":        conn.execute("SELECT COUNT(*) FROM Track").fetchone()[0],
        "Playlist":     conn.execute("SELECT COUNT(*) FROM Playlist").fetchone()[0],
        "PlaylistTrack":conn.execute("SELECT COUNT(*) FROM PlaylistTrack").fetchone()[0],
    }
    print("\nRow counts after seeding:")
    for table, count in row_counts.items():
        print(f"  {table:<16} {count:>3} rows")

    # ── 3b — IntegrityError demonstration ─────────────────────────────────────
    # TODO: insert a Track row whose artist_id does NOT exist in the Artist table.
    #       Use artist_id = 9999 (or any value you did not insert).
    #       The PRAGMA foreign_keys = ON statement makes SQLite enforce this.
    #       Catch the resulting sqlite3.IntegrityError and print a descriptive message.
    #
    # Your code here:
    print("\nIntegrityError demonstration:")
    try:
        # TODO: write the INSERT statement that should fail
        conn.execute("INSERT INTO Track VALUES (999, 'Ghost Track', 210, 9999)")
        print("  Insert succeeded — did you enable PRAGMA foreign_keys = ON?")
    except sqlite3.IntegrityError as e:
        # TODO: print a message that identifies which constraint was violated
        print(f"  IntegrityError caught: {e}")
        print("  This error confirms that foreign key enforcement is active.")

    # ── 3c — Persist the RAM database to disk with .backup() ─────────────────
    # TODO: open a connection to "music.db" and call conn.backup(target_conn)
    #       to write a permanent copy of the in-memory database to disk.
    #       Print a confirmation message.  Close the target connection when done.
    #
    # Your code here:
    print("\nPersisting database to music.db ...")
    DB_PATH = "music.db"
    target_conn = sqlite3.connect(DB_PATH)
    conn.backup(target_conn)
    target_conn.close()
    conn.close()
    print(f"  Backup complete.  File size: {os.path.getsize(DB_PATH):,} bytes")
    print(f"  Reopen with:  sqlite3.connect('{DB_PATH}')")
