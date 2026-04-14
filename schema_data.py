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

# schema_data.py
import sqlite3
import os

def build_database(conn):
    """
    Creates four tables in dependency order.
    Must call PRAGMA foreign_keys = ON as first statement.
    Uses CREATE TABLE IF NOT EXISTS for all tables.
    """
    # First statement: enable foreign key enforcement
    conn.execute("PRAGMA foreign_keys = ON;")
    
    cursor = conn.cursor()
    
    # Table 1: Artist (exact specification)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Artist (
        artist_id   INTEGER PRIMARY KEY,
        name        TEXT    NOT NULL,
        genre       TEXT    NOT NULL,
        origin_city TEXT
    )
    ''')
    
    # Table 2: Track (exact specification with inline REFERENCES)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Track (
        track_id         INTEGER PRIMARY KEY,
        title            TEXT    NOT NULL,
        duration_seconds INTEGER NOT NULL,
        artist_id        INTEGER NOT NULL REFERENCES Artist(artist_id)
    )
    ''')
    
    # Table 3: Playlist (exact specification)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Playlist (
        playlist_id   INTEGER PRIMARY KEY,
        playlist_name TEXT    NOT NULL,
        owner_name    TEXT    NOT NULL
    )
    ''')
    
    # Table 4: PlaylistTrack (exact specification)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS PlaylistTrack (
        playlist_id INTEGER NOT NULL REFERENCES Playlist(playlist_id),
        track_id    INTEGER NOT NULL REFERENCES Track(track_id),
        position    INTEGER NOT NULL,
        PRIMARY KEY (playlist_id, track_id)
    )
    ''')
    
    conn.commit()
    print("Tables created successfully (IF NOT EXISTS).")


def seed_database(conn):
    """
    Populates all four tables using conn.executemany().
    Uses INSERT OR IGNORE to allow safe re-runs.
    """
    cursor = conn.cursor()
    
    # ============ ARTISTS (6 artists) ============
    # Columns: artist_id (auto), name, genre, origin_city
    artists = [
        ("The Beatles", "Rock", "Liverpool"),
        ("Taylor Swift", "Pop", "West Reading"),
        ("Queen", "Rock", "London"),
        ("Beyoncé", "R&B", "Houston"),
        ("Drake", "Hip Hop", "Toronto"),
        ("Adele", "Soul", "London"),
    ]
    cursor.executemany("INSERT OR IGNORE INTO Artist (name, genre, origin_city) VALUES (?, ?, ?)", artists)
    print(f"Inserted/ignored {len(artists)} artists.")
    
    # Get artist_id mappings for foreign keys
    cursor.execute("SELECT artist_id, name FROM Artist")
    artist_map = {name: artist_id for artist_id, name in cursor.fetchall()}
    
    # ============ TRACKS (18 tracks) ============
    # Columns: track_id (auto), title, duration_seconds, artist_id
    tracks = [
        # The Beatles (Rock)
        ("Come Together", 259, "The Beatles"),
        ("Hey Jude", 431, "The Beatles"),
        ("Let It Be", 243, "The Beatles"),
        ("Yesterday", 125, "The Beatles"),  # 4th track for The Beatles
        # Taylor Swift (Pop)
        ("Shake It Off", 219, "Taylor Swift"),
        ("Blank Space", 231, "Taylor Swift"),
        ("Love Story", 235, "Taylor Swift"),
        # Queen (Rock)
        ("Bohemian Rhapsody", 354, "Queen"),
        ("We Will Rock You", 122, "Queen"),
        ("We Are the Champions", 179, "Queen"),
        # Beyoncé (R&B)
        ("Halo", 241, "Beyoncé"),
        ("Single Ladies", 200, "Beyoncé"),
        ("Crazy in Love", 236, "Beyoncé"),
        # Drake (Hip Hop)
        ("God's Plan", 198, "Drake"),
        ("Hotline Bling", 264, "Drake"),
        ("In My Feelings", 217, "Drake"),
        # Adele (Soul)
        ("Hello", 295, "Adele"),
        ("Rolling in the Deep", 228, "Adele"),
        ("Someone Like You", 284, "Adele"),
    ]
    
    track_data = []
    for title, duration, artist_name in tracks:
        artist_id = artist_map.get(artist_name)
        if artist_id:
            track_data.append((title, duration, artist_id))
    
    cursor.executemany("INSERT OR IGNORE INTO Track (title, duration_seconds, artist_id) VALUES (?, ?, ?)", track_data)
    print(f"Inserted/ignored {len(track_data)} tracks.")
    
    # Get track_id mappings
    cursor.execute("SELECT track_id, title FROM Track")
    track_map = {title: track_id for track_id, title in cursor.fetchall()}
    
    # ============ PLAYLISTS (4 playlists) ============
    # Columns: playlist_id (auto), playlist_name, owner_name
    playlists = [
        ("Rock Classics", "John"),
        ("Pop Hits", "Sarah"),
        ("Workout Mix", "Mike"),
        ("Chill Vibes", "Emma"),
    ]
    cursor.executemany("INSERT OR IGNORE INTO Playlist (playlist_name, owner_name) VALUES (?, ?)", playlists)
    print(f"Inserted/ignored {len(playlists)} playlists.")
    
    # Get playlist_id mappings
    cursor.execute("SELECT playlist_id, playlist_name FROM Playlist")
    playlist_map = {name: playlist_id for playlist_id, name in cursor.fetchall()}
    
    # ============ PLAYLISTTRACK ASSIGNMENTS (20+ assignments) ============
    # Columns: playlist_id, track_id, position
    playlist_assignments = [
        # Rock Classics playlist (position 1-7)
        ("Rock Classics", "Come Together", 1),
        ("Rock Classics", "Hey Jude", 2),
        ("Rock Classics", "Let It Be", 3),
        ("Rock Classics", "Yesterday", 4),
        ("Rock Classics", "Bohemian Rhapsody", 5),
        ("Rock Classics", "We Will Rock You", 6),
        ("Rock Classics", "We Are the Champions", 7),
        # Pop Hits playlist
        ("Pop Hits", "Shake It Off", 1),
        ("Pop Hits", "Blank Space", 2),
        ("Pop Hits", "Love Story", 3),
        ("Pop Hits", "Single Ladies", 4),
        ("Pop Hits", "Crazy in Love", 5),
        ("Pop Hits", "Hello", 6),
        # Workout Mix playlist
        ("Workout Mix", "God's Plan", 1),
        ("Workout Mix", "Hotline Bling", 2),
        ("Workout Mix", "In My Feelings", 3),
        ("Workout Mix", "We Will Rock You", 4),
        ("Workout Mix", "Single Ladies", 5),
        ("Workout Mix", "Shake It Off", 6),
        # Chill Vibes playlist
        ("Chill Vibes", "Someone Like You", 1),
        ("Chill Vibes", "Hello", 2),
        ("Chill Vibes", "Let It Be", 3),
        ("Chill Vibes", "Halo", 4),
    ]
    
    assignment_data = []
    for playlist_name, track_title, position in playlist_assignments:
        playlist_id = playlist_map.get(playlist_name)
        track_id = track_map.get(track_title)
        if playlist_id and track_id:
            assignment_data.append((playlist_id, track_id, position))
    
    cursor.executemany("INSERT OR IGNORE INTO PlaylistTrack (playlist_id, track_id, position) VALUES (?, ?, ?)", assignment_data)
    print(f"Inserted/ignored {len(assignment_data)} PlaylistTrack assignments.")
    
    # Commit all changes
    conn.commit()
    print("Database seeded successfully.")


if __name__ == "__main__":
    print("=== Phase 2: Author 1 - Database Setup ===\n")
    
    # Step 1: Create an in-memory connection
    memory_conn = sqlite3.connect(":memory:")
    
    # Step 2: Build schema and seed data in memory
    print("Building schema in memory...")
    build_database(memory_conn)
    
    print("\nSeeding database in memory...")
    seed_database(memory_conn)
    
    # Step 3: IntegrityError demonstration
    print("\n=== IntegrityError Demonstration ===")
    print("Attempting to insert a track with non-existent artist_id=9999...")
    try:
        memory_conn.execute(
            "INSERT INTO Track (title, duration_seconds, artist_id) VALUES (?, ?, ?)",
            ("Invalid Track", 180, 9999)
        )
        memory_conn.commit()
        print("ERROR: Insert succeeded when it should have failed!")
    except sqlite3.IntegrityError as e:
        print(f"Referential integrity violation caught: {e}")
        memory_conn.rollback()
    
    # Step 4: Backup to persistent file music.db
    print("\n=== Persistence Backup ===")
    disk_conn = sqlite3.connect("music.db")
    memory_conn.backup(disk_conn)
    disk_conn.close()
    print("Backup complete: music.db has been written to disk.")
    
    # Step 5: Verification
    print("\n=== Verification ===")
    verify_conn = sqlite3.connect("music.db")
    verify_cursor = verify_conn.cursor()
    
    verify_cursor.execute("SELECT COUNT(*) FROM Artist")
    artist_count = verify_cursor.fetchone()[0]
    verify_cursor.execute("SELECT COUNT(*) FROM Track")
    track_count = verify_cursor.fetchone()[0]
    verify_cursor.execute("SELECT COUNT(*) FROM Playlist")
    playlist_count = verify_cursor.fetchone()[0]
    verify_cursor.execute("SELECT COUNT(*) FROM PlaylistTrack")
    assignment_count = verify_cursor.fetchone()[0]
    
    print(f"Artist count: {artist_count}")
    print(f"Track count: {track_count}")
    print(f"Playlist count: {playlist_count}")
    print(f"PlaylistTrack count: {assignment_count}")
    
    verify_conn.close()
    
    print("\n=== Done ===")