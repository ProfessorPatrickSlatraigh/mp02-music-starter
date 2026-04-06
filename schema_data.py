import sqlite3


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
    artists = [
        (1, "Taylor Swift", "Pop", "Nashville"),
        (2, "Rihanna", "Pop", "Saint Michael"),
        (3, "Ariana Grande", "Pop", "Boca Raton"),
        (4, "Katy Perry", "Pop", "Santa Barbara"),
        (5, "The Weeknd", "R&B/Pop", "Toronto"),
        (6, "Harry Styles", "Pop", "Redditch")
    ]

    tracks = [
        (1, "Blank Space", 231, 1),
        (2, "Bad Blood", 211, 1),
        (3, "Style", 231, 1),
        (4, "Umbrella", 275, 2),
        (5, "Diamonds", 225, 2),
        (6, "We Found Love", 215, 2),
        (7, "7 Rings", 178, 3),
        (8, "Thank U, Next", 207, 3),
        (9, "Positions", 172, 3),
        (10, "Last Friday Night", 230, 4),
        (11, "California Gurls", 236, 4),
        (12, "Dark Horse", 215, 4),
        (13, "Heartless", 198, 5),
        (14, "The Hills", 242, 5),
        (15, "Starboy", 230, 5),
        (16, "Watermelon Sugar", 174, 6),
        (17, "Adore You", 207, 6),
        (18, "Satellite", 218, 6)
    ]

    playlists = [
        (1, "Workout Playlist", "Alex"),
        (2, "Car Ride Playlist", "Sam"),
        (3, "Party Mix Playlist", "Jordan"),
        (4, "Chores Playlist", "Taylor")
    ]

    playlist_tracks = [
        (1, 2, 1), (1, 4, 2), (1, 7, 3), (1, 12, 4), (1, 15, 5),
        (2, 1, 1), (2, 5, 2), (2, 9, 3), (2, 14, 4), (2, 16, 5),
        (3, 10, 1), (3, 13, 2), (3, 18, 3), (3, 4, 4), (3, 7, 5),
        (4, 3, 1), (4, 6, 2), (4, 8, 3), (4, 11, 4), (4, 17, 5)
    ]

    conn.executemany(
        "INSERT OR IGNORE INTO Artist (artist_id, name, genre, origin_city) VALUES (?, ?, ?, ?)",
        artists
    )
    conn.executemany(
        "INSERT OR IGNORE INTO Track (track_id, title, duration_seconds, artist_id) VALUES (?, ?, ?, ?)",
        tracks
    )
    conn.executemany(
        "INSERT OR IGNORE INTO Playlist (playlist_id, playlist_name, owner_name) VALUES (?, ?, ?)",
        playlists
    )
    conn.executemany(
        "INSERT OR IGNORE INTO PlaylistTrack (playlist_id, track_id, position) VALUES (?, ?, ?)",
        playlist_tracks
    )

    conn.commit()


if __name__ == "__main__":
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON;")
    build_database(conn)
    seed_database(conn)

    try:
        conn.execute(
            "INSERT INTO Track (track_id, title, duration_seconds, artist_id) VALUES (?, ?, ?, ?)",
            (999, "Ghost Track", 210, 9999)
        )
    except sqlite3.IntegrityError as e:
        print(f"IntegrityError caught: {e}")
        conn.rollback()

    target = sqlite3.connect("music.db")
    conn.backup(target)
    target.close()

    print("Database written to music.db")
    conn.close()