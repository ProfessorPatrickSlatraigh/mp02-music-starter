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
        (1, "Drake",            "Hip-Hop", "Toronto"),
        (2, "Bad Bunny",        "Hip-Hop", "San Juan"),
        (3, "Kendrick Lamar",   "Hip-Hop", "Compton"),
        (4, "J. Cole",          "Hip-Hop", "Fayetteville"),
        (5, "Don Toliver",      "Hip-Hop", "Houston"),
        (6, "Eminem",           "Hip-Hop", "Detroit")
    ]

    conn.executemany(
        "INSERT OR IGNORE INTO Artist VALUES (?, ?, ?, ?)",
        artists
    )

    tracks = [
        (1,  "God's Plan",              198, 1),
        (2,  "Hotline Bling",           267, 1),
        (3,  "In My Feelings",          217, 1),
        (4,  "Tití Me Preguntó",        240, 2),
        (5,  "Moscow Mule",             215, 2),
        (6,  "Me Porto Bonito",         210, 2),
        (7,  "HUMBLE.",                 177, 3),
        (8,  "DNA.",                    185, 3),
        (9,  "Alright",                 216, 3),
        (10, "No Role Modelz",          210, 4),
        (11, "Middle Child",            200, 4),
        (12, "Power Trip",              240, 4),
        (13, "After Party",             210, 5),
        (14, "No Idea",                 205, 5),
        (15, "Lemonade",                195, 5),
        (16, "Lose Yourself",           326, 6),
        (17, "The Real Slim Shady",     284, 6),
        (18, "Mockingbird",             250, 6)
    ]

    conn.executemany(
        "INSERT OR IGNORE INTO Track VALUES (?, ?, ?, ?)",
        tracks
    )

    playlists = [
        (1, "Vibes", "Alex"),
        (2, "Workout", "Samuel"),
        (3, "Throwbacks", "Bryan"),
        (4, "Late Night", "Jordan")
    ]

    conn.executemany(
        "INSERT OR IGNORE INTO Playlist VALUES (?, ?, ?)",
        playlists
    )

    playlist_tracks = [
        # Vibes
        (1,  1,  1),
        (1,  3,  2),
        (1, 13,  3),
        (1, 14,  4),
        (1,  6,  5),

        # Workout
        (2,  2,  1),
        (2,  4,  2),
        (2,  8,  3),
        (2, 11,  4),
        (2, 17,  5),

        # Throwbacks
        (3, 16,  1),
        (3, 17,  2),
        (3, 10,  3),
        (3, 12,  4),
        (3,  7,  5),

        # Late Night
        (4,  5,  1),
        (4,  9,  2),
        (4, 15,  3),
        (4, 18,  4),
        (4, 14,  5)
    ]

    conn.executemany(
        "INSERT OR IGNORE INTO PlaylistTrack VALUES (?, ?, ?)",
        playlist_tracks
    )

    conn.commit()

if __name__ == "__main__":
    conn = sqlite3.connect("music.db")   
    build_database(conn)
    seed_database(conn)

    print("Artist count:", conn.execute("SELECT COUNT(*) FROM Artist").fetchone())

    try:
        conn.execute("INSERT INTO Track VALUES (99, 'Fake Track', 200, 9999)")
    except sqlite3.IntegrityError as e:
        print("IntegrityError caught:", e)

    conn.commit()   
    conn.close()

    print("Database saved to music.db")
