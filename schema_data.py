"""
schema_data.py
==============
CIS 3120 · MP02 — SQL and Database
Author 1 module — schema creation and seed data

Team:   Daniel Wang (Integrator), Chinmoy (Author 1), Rahim (Author 2)
Theme:  Hip-Hop

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
            Artist  ->  Track  ->  Playlist  ->  PlaylistTrack
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
    # NOTE: column is named 'title' in schema per spec; queries alias it as track_name
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
    """Populate all four tables with realistic hip-hop music data.

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
    # Agreed artists per team agreement

    artists = [
        # (artist_id, name,           genre,      origin_city)
        (1, "Lil Uzi Vert",  "Hip-Hop/Rap",   "Philadelphia"),
        (2, "Drake",          "Hip-Hop/R&B",   "Toronto"),
        (3, "NAV",            "Hip-Hop/Trap",  "Toronto"),
        (4, "Future",         "Trap/Hip-Hop",  "Atlanta"),
        (5, "Young Thug",     "Trap/Hip-Hop",  "Atlanta"),
        (6, "ASAP Rocky",     "Hip-Hop/Rap",   "New York"),
    ]

    conn.executemany(
        "INSERT OR IGNORE INTO Artist VALUES (?, ?, ?, ?)",
        artists
    )

    # ── Tracks ───────────────────────────────────────────────────────────────
    # Columns: track_id, title, duration_seconds, artist_id
    # Lil Uzi Vert (artist_id=1) has 5 tracks — satisfies the >=3 requirement

    tracks = [
        # (track_id, title,                        duration_seconds, artist_id)
        # Lil Uzi Vert — 5 tracks
        (1,  "XO Tour Llif3",                  177, 1),
        (2,  "Money Longer",                   192, 1),
        (3,  "The Way Life Goes",              214, 1),
        (4,  "Futsal Shuffle 2020",            148, 1),
        (5,  "Bad and Boujee (feat. Migos)",   343, 1),
        # Drake — 4 tracks
        (6,  "God's Plan",                     198, 2),
        (7,  "Hotline Bling",                  267, 2),
        (8,  "One Dance",                      174, 2),
        (9,  "In My Feelings",                 217, 2),
        # NAV — 3 tracks
        (10, "Wanted You",                     193, 3),
        (11, "Tap",                            178, 3),
        (12, "Call Me",                        196, 3),
        # Future — 3 tracks
        (13, "Mask Off",                       206, 4),
        (14, "Life Is Good",                   237, 4),
        (15, "March Madness",                  251, 4),
        # Young Thug — 3 tracks
        (16, "Havana",                         217, 5),
        (17, "Best Friend",                    181, 5),
        (18, "Hot (feat. Gunna)",              195, 5),
        # ASAP Rocky — 2 tracks
        (19, "Praise the Lord",               209, 6),
        (20, "Everyday",                       258, 6),
    ]

    conn.executemany(
        "INSERT OR IGNORE INTO Track VALUES (?, ?, ?, ?)",
        tracks
    )

    # ── Playlists ────────────────────────────────────────────────────────────
    # Columns: playlist_id, playlist_name, owner_name

    playlists = [
        # (playlist_id, playlist_name,      owner_name)
        (1, "Trap Bangers",      "Daniel"),
        (2, "Late Night Cruise", "Chinmoy"),
        (3, "Gym Motivation",    "Rahim"),
        (4, "Chill Trap",        "Daniel"),
    ]

    conn.executemany(
        "INSERT OR IGNORE INTO Playlist VALUES (?, ?, ?)",
        playlists
    )

    # ── PlaylistTrack ─────────────────────────────────────────────────────────
    # Columns: playlist_id, track_id, position
    # Lil Uzi Vert tracks (1-5) spread across playlists — satisfies >=3 requirement

    playlist_tracks = [
        # (playlist_id, track_id, position)
        # Trap Bangers (playlist_id=1) — 6 tracks
        (1,  1,  1),   # XO Tour Llif3         — Lil Uzi Vert
        (1, 13,  2),   # Mask Off               — Future
        (1, 18,  3),   # Hot (feat. Gunna)      — Young Thug
        (1,  6,  4),   # God's Plan             — Drake
        (1, 19,  5),   # Praise the Lord        — ASAP Rocky
        (1,  3,  6),   # The Way Life Goes      — Lil Uzi Vert
        # Late Night Cruise (playlist_id=2) — 4 tracks
        # NOTE: track 5 (Bad and Boujee) and track 20 (Everyday) are intentionally
        # left off all playlists so get_tracks_on_no_playlist() returns results.
        (2,  7,  1),   # Hotline Bling          — Drake
        (2, 10,  2),   # Wanted You             — NAV
        (2, 16,  3),   # Havana                 — Young Thug
        (2,  9,  4),   # In My Feelings         — Drake
        # Gym Motivation (playlist_id=3) — 6 tracks
        (3,  2,  1),   # Money Longer           — Lil Uzi Vert
        (3,  4,  2),   # Futsal Shuffle 2020    — Lil Uzi Vert
        (3, 14,  3),   # Life Is Good           — Future
        (3, 15,  4),   # March Madness          — Future
        (3, 17,  5),   # Best Friend            — Young Thug
        (3, 11,  6),   # Tap                    — NAV
        # Chill Trap (playlist_id=4) — 5 tracks
        (4,  8,  1),   # One Dance              — Drake
        (4, 12,  2),   # Call Me                — NAV
        (4, 19,  3),   # Praise the Lord        — ASAP Rocky
        (4, 16,  4),   # Havana                 — Young Thug
        (4, 10,  5),   # Wanted You             — NAV
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
        "Artist":        conn.execute("SELECT COUNT(*) FROM Artist").fetchone()[0],
        "Track":         conn.execute("SELECT COUNT(*) FROM Track").fetchone()[0],
        "Playlist":      conn.execute("SELECT COUNT(*) FROM Playlist").fetchone()[0],
        "PlaylistTrack": conn.execute("SELECT COUNT(*) FROM PlaylistTrack").fetchone()[0],
    }
    print("\nRow counts after seeding:")
    for table, count in row_counts.items():
        print(f"  {table:<16} {count:>3} rows")

    # ── 3b — IntegrityError demonstration ────────────────────────────────────
    # Attempts to insert a Track row whose artist_id does NOT exist in Artist.
    # artist_id = 9999 was never inserted, so SQLite raises IntegrityError
    # because PRAGMA foreign_keys = ON is active.
    print("\nIntegrityError demonstration:")
    try:
        conn.execute("INSERT INTO Track VALUES (999, 'Ghost Track', 210, 9999)")
        print("  Insert succeeded — did you enable PRAGMA foreign_keys = ON?")
    except sqlite3.IntegrityError as e:
        print(f"  IntegrityError caught: {e}")
        print("  --> artist_id 9999 does not exist in Artist; referential integrity violated.")
        print("  This error confirms that foreign key enforcement is active.")

    # ── 3c — Persist the RAM database to disk with .backup() ─────────────────
    # Opens a connection to music.db and backs up the in-memory database to it.
    print("\nPersisting database to music.db ...")
    DB_PATH = "music.db"
    target_conn = sqlite3.connect(DB_PATH)
    conn.backup(target_conn)
    target_conn.close()
    conn.close()
    print(f"  Backup complete.  File size: {os.path.getsize(DB_PATH):,} bytes")
    print(f"  Reopen with:  sqlite3.connect('{DB_PATH}')")
