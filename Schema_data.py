import sqlite3
import os


def build_database(conn):
    conn.execute("PRAGMA foreign_keys = ON;")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS Artist (
            artist_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            genre TEXT NOT NULL,
            origin_city TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS Track (
            track_id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            duration_seconds INTEGER NOT NULL,
            artist_id INTEGER NOT NULL
                REFERENCES Artist(artist_id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS Playlist (
            playlist_id INTEGER PRIMARY KEY,
            playlist_name TEXT NOT NULL,
            owner_name TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS PlaylistTrack (
            playlist_id INTEGER NOT NULL REFERENCES Playlist(playlist_id),
            track_id INTEGER NOT NULL REFERENCES Track(track_id),
            position INTEGER NOT NULL,
            PRIMARY KEY (playlist_id, track_id)
        )
    """)

    conn.commit()


def seed_database(conn):

    # 🎤 POP ARTISTS (6 required)
    artists = [
        (1, "Taylor Swift", "Pop", "Nashville"),
        (2, "Drake", "Hip-Hop/Pop", "Toronto"),
        (3, "The Weeknd", "R&B/Pop", "Toronto"),
        (4, "Billie Eilish", "Alt Pop", "Los Angeles"),
        (5, "Dua Lipa", "Pop", "London"),
        (6, "Ariana Grande", "Pop", "Florida"),
    ]

    conn.executemany(
        "INSERT OR IGNORE INTO Artist VALUES (?, ?, ?, ?)",
        artists
    )

    # 🎵 TRACKS (18 required)
    tracks = [
        (1, "Love Story", 235, 1),
        (2, "Blank Space", 231, 1),
        (3, "Shake It Off", 219, 1),

        (4, "God's Plan", 198, 2),
        (5, "Hotline Bling", 267, 2),
        (6, "One Dance", 173, 2),

        (7, "Blinding Lights", 200, 3),
        (8, "Starboy", 230, 3),
        (9, "Save Your Tears", 215, 3),

        (10, "Bad Guy", 194, 4),
        (11, "Ocean Eyes", 200, 4),
        (12, "Happier Than Ever", 298, 4),

        (13, "Don't Start Now", 183, 5),
        (14, "Levitating", 203, 5),
        (15, "New Rules", 209, 5),

        (16, "7 rings", 178, 6),
        (17, "thank u, next", 207, 6),
        (18, "Positions", 172, 6),
    ]

    conn.executemany(
        "INSERT OR IGNORE INTO Track VALUES (?, ?, ?, ?)",
        tracks
    )

    # 🎧 PLAYLISTS (4 required)
    playlists = [
        (1, "Pop Hits", "Alex"),
        (2, "Workout Mix", "Sam"),
        (3, "Chill Pop", "Jordan"),
        (4, "Party Vibes", "Taylor"),
    ]

    conn.executemany(
        "INSERT OR IGNORE INTO Playlist VALUES (?, ?, ?)",
        playlists
    )

    # 🔗 PLAYLIST TRACKS (20 required)
    playlist_tracks = [
        (1, 1, 1), (1, 2, 2), (1, 4, 3), (1, 7, 4), (1, 10, 5),

        (2, 3, 1), (2, 5, 2), (2, 6, 3), (2, 8, 4), (2, 13, 5),

        (3, 11, 1), (3, 12, 2), (3, 14, 3), (3, 15, 4), (3, 16, 5),

        (4, 1, 1), (4, 7, 2), (4, 13, 3), (4, 16, 4), (4, 18, 5),
    ]

    conn.executemany(
        "INSERT OR IGNORE INTO PlaylistTrack VALUES (?, ?, ?)",
        playlist_tracks
    )

    conn.commit()


if __name__ == "__main__":

    conn = sqlite3.connect(":memory:")
    build_database(conn)
    seed_database(conn)

    print("\nRow counts:")
    for table in ["Artist", "Track", "Playlist", "PlaylistTrack"]:
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(table, count)

    print("\nIntegrityError test:")
    try:
        conn.execute("INSERT INTO Track VALUES (999, 'Fake Song', 200, 9999)")
    except sqlite3.IntegrityError as e:
        print("IntegrityError caught:", e)

    print("\nSaving database to music.db...")
    target = sqlite3.connect("music.db")
    conn.backup(target)
    target.close()

    print("Done → music.db created")
