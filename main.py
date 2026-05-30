# main.py — Integrator: full driver
import sqlite3
import os

from schema_data import build_database, seed_database
from queries import (
    get_playlist_tracks,
    get_tracks_on_no_playlist,
    get_most_added_track,
    get_playlist_durations,
)

DB_PATH = "music.db"


def format_duration(seconds):
    """Convert seconds to mm:ss string."""
    mins = seconds // 60
    secs = seconds % 60
    return f"{mins}:{secs:02d}"


def open_connection():
    """Open or build the database and return a connection."""
    if os.path.exists(DB_PATH):
        print(f"[INFO] Reopening existing database: {DB_PATH}")
        conn = sqlite3.connect(DB_PATH)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    else:
        print("[INFO] First run — building and seeding database...")
        mem_conn = sqlite3.connect(":memory:")
        build_database(mem_conn)
        seed_database(mem_conn)
        target = sqlite3.connect(DB_PATH)
        mem_conn.backup(target)
        target.close()
        mem_conn.close()
        print(f"[INFO] Database saved to {DB_PATH}")
        conn = sqlite3.connect(DB_PATH)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn


def show_playlist_tracks(conn):
    name = input("Enter playlist name: ").strip()
    rows = get_playlist_tracks(conn, name)
    if not rows:
        print("No tracks found for that playlist.")
        return
    print(f"\n{'Pos':<5} {'Title':<35} {'Artist':<20} {'Duration'}")
    print("-" * 70)
    for row in rows:
        title, artist, duration, position = row
        print(f"{position:<5} {title:<35} {artist:<20} {format_duration(duration)}")
    print()


def show_tracks_on_no_playlist(conn):
    rows = get_tracks_on_no_playlist(conn)
    if not rows:
        print("All tracks are on at least one playlist.")
        return
    print(f"\n{'Title':<35} {'Artist'}")
    print("-" * 55)
    for row in rows:
        title, artist = row
        print(f"{title:<35} {artist}")
    print()


def show_most_added_track(conn):
    rows = get_most_added_track(conn)
    if not rows:
        print("No data found.")
        return
    title, artist, count = rows[0]
    print(f"\nMost-added track: {title} by {artist} — appears on {count} playlist(s)\n")


def show_playlist_durations(conn):
    rows = get_playlist_durations(conn)
    if not rows:
        print("No playlists found.")
        return
    print(f"\n{'Playlist':<30} {'Total Duration'}")
    print("-" * 50)
    for row in rows:
        name, total_minutes = row
        total_seconds = int(total_minutes * 60)
        print(f"{name:<30} {format_duration(total_seconds)}")
    print()


def delete_artist(conn):
    try:
        artist_id = int(input("Enter artist_id to delete: ").strip())
    except ValueError:
        print("Invalid input — enter a number.")
        return
    try:
        conn.execute("""
            DELETE FROM PlaylistTrack
            WHERE track_id IN (
                SELECT track_id FROM Track WHERE artist_id = ?
            )""", (artist_id,))
        conn.execute("DELETE FROM Track WHERE artist_id = ?", (artist_id,))
        conn.execute("DELETE FROM Artist WHERE artist_id = ?", (artist_id,))
        conn.commit()
        print(f"Artist {artist_id} and all dependent records removed.")
    except sqlite3.IntegrityError as e:
        conn.rollback()
        print(f"Deletion failed: {e}")


def main():
    conn = open_connection()

    while True:
        print("\n=== Music Playlist App ===")
        print("1. Show all tracks on a playlist")
        print("2. Show tracks on no playlist")
        print("3. Show most-added track")
        print("4. Show playlist durations")
        print("5. Delete an artist and all dependent records")
        print("0. Exit")

        choice = input("Select an option: ").strip()

        if choice == "1":
            show_playlist_tracks(conn)
        elif choice == "2":
            show_tracks_on_no_playlist(conn)
        elif choice == "3":
            show_most_added_track(conn)
        elif choice == "4":
            show_playlist_durations(conn)
        elif choice == "5":
            delete_artist(conn)
        elif choice == "0":
            print("Goodbye!")
            conn.close()
            break
        else:
            print("Invalid option, try again.")


if __name__ == "__main__":
    main()
