import sqlite3
import os

from schema_data import build_database, seed_database
from queries import (
    get_playlist_tracks,
    get_tracks_on_no_playlist,
    get_most_added_track,
    get_playlist_durations
)

DB_PATH = "music.db"


def fmt_duration(total_seconds):
    total_seconds = int(total_seconds)
    mins = total_seconds // 60
    secs = total_seconds % 60
    return f"{mins}:{secs:02d}"


def divider(char="-", width=70):
    print(char * width)


def show_playlist_tracks(conn):
    playlist_name = input("Enter playlist name: ").strip()
    rows = get_playlist_tracks(conn, playlist_name)

    if not rows:
        print(f"No tracks found for playlist '{playlist_name}'.")
        return

    print(f"\nTracks on playlist: {playlist_name}")
    print(f"{'Pos':>3}  {'Title':<30}  {'Artist':<20}  {'Duration'}")
    divider()

    for title, artist, duration_sec, position in rows:
        print(f"{position:>3}  {title:<30}  {artist:<20}  {fmt_duration(duration_sec)}")


def show_tracks_on_no_playlist(conn):
    rows = get_tracks_on_no_playlist(conn)

    if not rows:
        print("All tracks are assigned to at least one playlist.")
        return

    print("\nTracks on no playlist")
    print(f"{'ID':>4}  {'Title':<30}  {'Artist'}")
    divider()

    for track_id, title, artist in rows:
        print(f"{track_id:>4}  {title:<30}  {artist}")


def show_most_added_track(conn):
    row = get_most_added_track(conn)

    if row is None:
        print("No playlist assignments found.")
        return

    title, artist, count = row
    print("\nMost-added track")
    divider()
    print(f"Title: {title}")
    print(f"Artist: {artist}")
    print(f"Playlist count: {count}")


def show_playlist_durations(conn):
    rows = get_playlist_durations(conn)

    if not rows:
        print("No playlist data found.")
        return

    print("\nPlaylist durations")
    print(f"{'Playlist':<30}  {'Total Duration'}")
    divider()

    for playlist_name, total_minutes in rows:
        total_seconds = total_minutes * 60
        print(f"{playlist_name:<30}  {fmt_duration(total_seconds)}")


def delete_artist(conn):
    try:
        artist_id = int(input("Enter artist ID to delete: ").strip())
    except ValueError:
        print("Invalid input. Please enter an integer artist ID.")
        return

    row = conn.execute(
        "SELECT name FROM Artist WHERE artist_id = ?",
        (artist_id,)
    ).fetchone()

    if row is None:
        print(f"No artist found with ID {artist_id}.")
        return

    artist_name = row[0]
    confirm = input(
        f"Delete '{artist_name}' (ID {artist_id}) and all dependent records? [yes/no]: "
    ).strip().lower()

    if confirm != "yes":
        print("Deletion cancelled.")
        return

    try:
        conn.execute("""
            DELETE FROM PlaylistTrack
            WHERE track_id IN (
                SELECT track_id
                FROM Track
                WHERE artist_id = ?
            )
        """, (artist_id,))

        conn.execute("""
            DELETE FROM Track
            WHERE artist_id = ?
        """, (artist_id,))

        conn.execute("""
            DELETE FROM Artist
            WHERE artist_id = ?
        """, (artist_id,))

        conn.commit()
        print(f"Artist {artist_id} ({artist_name}) and all dependent records removed.")

    except sqlite3.IntegrityError as e:
        conn.rollback()
        print(f"Deletion failed: {e}")


def open_or_build_database():
    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        conn.execute("PRAGMA foreign_keys = ON;")
        print(f"Re-opened existing database: {DB_PATH}")
        return conn

    print("First run: building and seeding database...")
    mem_conn = sqlite3.connect(":memory:")
    mem_conn.execute("PRAGMA foreign_keys = ON;")

    build_database(mem_conn)
    seed_database(mem_conn)

    target_conn = sqlite3.connect(DB_PATH)
    mem_conn.backup(target_conn)
    target_conn.close()
    mem_conn.close()

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    print(f"Database built and saved to {DB_PATH}")
    return conn


MENU = """
================ Music Playlist Manager ================
1. Show all tracks on a playlist
2. Show tracks on no playlist
3. Show most-added track
4. Show playlist durations
5. Delete an artist and all dependent records
0. Exit
========================================================
"""


HANDLERS = {
    "1": show_playlist_tracks,
    "2": show_tracks_on_no_playlist,
    "3": show_most_added_track,
    "4": show_playlist_durations,
    "5": delete_artist
}


def run_menu(conn):
    while True:
        print(MENU)
        choice = input("Select an option: ").strip()

        if choice == "0":
            print("Goodbye.")
            break

        handler = HANDLERS.get(choice)
        if handler is None:
            print("Invalid option. Please enter 0-5.")
            continue

        print()
        handler(conn)
        print()
        input("Press Enter to return to the menu...")


if __name__ == "__main__":
    conn = open_or_build_database()
    try:
        run_menu(conn)
    finally:
        conn.close()