import sqlite3


def build_database(conn):
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



def seed_database(conn):
    artists = [
        (1, "The Weeknd", "Pop", "Toronto"),
        (2, "Michael Jackson", "Funk","Gary"),
	(3, "Drake", "Rap", "Toronto"),
	(4, "Ariana Grande", "R&B", "Boca Raton"),
	(5, "Dua Lipa", "Disco", "London"),
	(6, "Taylor Swift", "Pop", "Pennsylvania")
]

    conn.executemany(
        "INSERT OR IGNORE INTO Artist VALUES (?, ?, ?, ?)",
        artists
    )

    # ── Tracks ───────────────────────────────────────────────────────────────
    # Columns: track_id, title, duration_seconds, artist_id
    # Every artist_id here must exist in the artists list above.
    # duration_seconds: a 3-minute song = 180 seconds.

    tracks = [
        (1, "Monster", 200, 1),
	(2, "The Hills", 170, 1),
	(3, "Save Your Tears", 180, 1),
	(4, "Smooth Criminal", 220, 2),
	(5, "Thriller", 270, 2),
	(6, "Chicago", 190, 2),
	(7, "Take Care", 210, 3),
	(8, "Jimmy Cooks", 185, 3),
	(9, "Find Your Love", 195, 3),
	(10, "Break Free", 236, 4),
	(11, "Love Me Harder", 182, 4),
	(12, "Boyfriend", 160, 4),
	(13, "Levitating", 205, 5),
	(14, "No Lie", 186, 5),
	(15, "New Rules", 193, 5),
	(16, "Shake It Off", 180, 6),
	(17, "You Belong With Me", 220, 6),
	(18, "Blank Space", 233, 6)
    ]

    conn.executemany(
        "INSERT OR IGNORE INTO Track VALUES (?, ?, ?, ?)",
        tracks
    )

    # ── Playlists ────────────────────────────────────────────────────────────

    playlists = [
        # (playlist_id, playlist_name, owner_name),
        (1, "Day Drive", "Shamiur"),
	(2, "Chill", "Nalhanzo"),
	(3, "Study", "Mahi"),
	(4, "Gym","Shamiur"), 
    ]

    conn.executemany(
        "INSERT OR IGNORE INTO Playlist VALUES (?, ?, ?)",
        playlists
    )

    # ── PlaylistTrack ─────────────────────────────────────────────────────────
    # Columns: playlist_id, track_id, position
    # Both playlist_id and track_id must reference rows inserted above.
    # position is the 1-based slot of the track within the playlist.
    # At least one artist must have 3+ tracks appearing across these assignments.

    playlist_tracks = [
        (1, 18, 5),
	(1, 9, 2),
	(1, 14, 3),
	(1 , 2, 1),
	(1, 16 , 4),
	(2, 6 ,2),
	(2, 13, 4),
	(2, 17, 5),
	(2, 11, 3),
	(2, 3, 1),
	(3, 5, 1),
	(3, 12, 3),
	(3, 18, 5),
	(3, 15, 4),
	(3, 7, 2),
	(4, 1, 1),
	(4, 8, 3),
	(4, 10, 4),
	(4, 13, 5),
	(4, 4, 2)
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
    #       Use artist_id = 9999 (or any value you did not insert).
    #       The PRAGMA foreign_keys = ON statement makes SQLite enforce this.
    #       Catch the resulting sqlite3.IntegrityError and print a descriptive message.
    #
    print("\nIntegrityError demonstration:")
    try:
        conn.execute("INSERT INTO Track VALUES (999, 'Ghost Track', 210, 9999)")
        print("  Insert succeeded — did you enable PRAGMA foreign_keys = ON?")
    except sqlite3.IntegrityError as e:
        print(f"  IntegrityError caught: {e}")
        print("  This error confirms that foreign key enforcement is active.")
        conn.rollback()

    # ── 3c — Persist the RAM database to disk with .backup() ─────────────────
    #       to write a permanent copy of the in-memory database to disk.
    #       Print a confirmation message.  Close the target connection when done.
    #
    print("\nPersisting database to music.db ...")
    target_conn = sqlite3.connect("music.db")
    conn.backup(target_conn)
    target_conn.close()
    conn.close()
    print("Database written to music.db")
