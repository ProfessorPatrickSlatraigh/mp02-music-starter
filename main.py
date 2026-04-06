"""
main.py
=======
CIS 3120 · MP02 — SQL and Database
Integrator module — application driver

CONTRACT SUMMARY
----------------
Implement the startup sequence, menu loop, and deletion sequence as specified.
This file is the only entry point for the completed application.

REQUIRED (graded):
    ✓ Correct imports from schema_data and queries
    ✓ Startup: open existing music.db OR build + seed + backup on first run
    ✓ Menu loop with options 1–5 and 0 to exit
    ✓ Readable tabular output; durations formatted as M:SS
    ✓ Deletion sequence in correct foreign key order (PlaylistTrack → Track → Artist)
    ✓ IntegrityError caught and displayed if deletion fails

IMPORTANT:
    - Do not define schema or query logic here; import from the Author modules.
    - Do not call build_database() or seed_database() on re-open runs.
    - The menu loop must continue until the user enters 0.
"""

import sqlite3
import os

# ─────────────────────────────────────────────────────────────────────────────
# Imports from Author modules
# ─────────────────────────────────────────────────────────────────────────────

from schema_data import build_database, seed_database
from queries    import (get_playlist_tracks,
                         get_tracks_on_no_playlist,
                         get_most_added_track,
                         get_playlist_durations)


# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

DB_PATH = "music.db"


# ─────────────────────────────────────────────────────────────────────────────
# Output helpers
# ─────────────────────────────────────────────────────────────────────────────

def fmt_duration(total_seconds):
    """Convert a total-seconds value to an M:SS string.

    Parameters
    ----------
    total_seconds : int or float

    Returns
    -------
    str  e.g. 210 → '3:30'
    """
    total_seconds = int(total_seconds)
    mins = total_seconds // 60
    secs = total_seconds % 60
    return f"{mins}:{secs:02d}"


def divider(char="─", width=60):
    """Print a horizontal rule."""
    print(char * width)


# ─────────────────────────────────────────────────────────────────────────────
# Menu option handlers
# ─────────────────────────────────────────────────────────────────────────────

def show_playlist_tracks(conn):
    playlist_name = input("  Enter playlist name: ").strip()
    rows = get_playlist_tracks(conn, playlist_name)
    if not rows:
        print(f"  No tracks found for playlist '{playlist_name}'.")
        return
    print(f"\n  {'Pos':>3}  {'Title':<30}  {'Artist':<22}  {'Duration'}")
    divider()
    for title, artist, duration_sec, position in rows:
        print(f"  {position:>3}  {title:<30}  {artist:<22}  {fmt_duration(duration_sec)}")


def show_tracks_on_no_playlist(conn):
    rows = get_tracks_on_no_playlist(conn)
    if not rows:
        print("  All tracks are assigned to at least one playlist.")
        return
    print(f"\n  {'ID':>4}  {'Title':<30}  {'Artist'}")
    divider()
    for track_id, title, artist in rows:
        print(f"  {track_id:>4}  {title:<30}  {artist}")


def show_most_added_track(conn):
    row = get_most_added_track(conn)
    if row is None:
        print("  No playlist assignments found.")
        return
    title, artist, count = row
    print(f"\n  Most-added track: {title} by {artist}")
    print(f"  Appears on {count} playlist(s).")


def show_playlist_durations(conn):
    rows = get_playlist_durations(conn)
    if not rows:
        print("  No playlist data found.")
        return
    print(f"\n  {'Playlist':<30}  {'Total Duration'}")
    divider()
    for playlist_name, total_minutes in rows:
        total_seconds = total_minutes * 60
        print(f"  {playlist_name:<30}  {fmt_duration(total_seconds)}")


def delete_artist(conn):
    """Menu option 5 — remove an artist and all dependent records.

    Deletion must follow the correct foreign key order:
        Step 1 — delete PlaylistTrack rows for the artist's tracks
        Step 2 — delete Track rows for the artist
        Step 3 — delete the Artist row

    Catches IntegrityError and rolls back if any step fails.
    """

    try:
        artist_id_input = input("  Enter artist ID to delete: ").strip()
        artist_id = int(artist_id_input)
    except ValueError:
        print("  Invalid input — please enter an integer artist ID.")
        return

    row = conn.execute(
        "SELECT name FROM Artist WHERE artist_id = ?", (artist_id,)
    ).fetchone()
    if row is None:
        print(f"  No artist found with ID {artist_id}.")
        return

    artist_name = row[0]
    confirm = input(f"  Delete '{artist_name}' (ID {artist_id}) and all their tracks? [yes/no]: ").strip().lower()
    if confirm != "yes":
        print("  Deletion cancelled.")
        return

    try:
    
        conn.execute("""
            DELETE FROM PlaylistTrack
            WHERE track_id IN (SELECT track_id FROM Track WHERE artist_id = ?)
        """, (artist_id,))


        conn.execute("""
            DELETE FROM Track WHERE artist_id = ?
        """, (artist_id,))

        conn.execute("""
            DELETE FROM Artist WHERE artist_id = ?
        """, (artist_id,))

        conn.commit()
        print(f"  '{artist_name}' and all associated tracks and playlist assignments removed.")

    except sqlite3.IntegrityError as e:
        conn.rollback()
        print(f"  Deletion failed — IntegrityError: {e}")
    except Exception as e:
        conn.rollback()
        print(f"  Deletion failed — {type(e).__name__}: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# Startup
# ─────────────────────────────────────────────────────────────────────────────

def open_or_build_database():
    """Return an open sqlite3 connection to the music database.

    If music.db exists on disk, open it directly and print a re-open message.
    If music.db does not exist, build and seed an in-memory database, back it
    up to music.db, then open music.db for all subsequent operations.

    Returns
    -------
    sqlite3.Connection  pointing to music.db
    """
def open_or_build_database():
    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        conn.execute("PRAGMA foreign_keys = ON;")
        print(f"  Re-opening existing database '{DB_PATH}'.")
        return conn
    else:
        mem_conn = sqlite3.connect(":memory:")
        mem_conn.execute("PRAGMA foreign_keys = ON;")
        build_database(mem_conn)
        seed_database(mem_conn)
        disk_conn = sqlite3.connect(DB_PATH)
        mem_conn.backup(disk_conn)
        disk_conn.close()
        mem_conn.close()
        conn = sqlite3.connect(DB_PATH)
        conn.execute("PRAGMA foreign_keys = ON;")
        print(f"  First-run: built and seeded '{DB_PATH}'.")
        return conn
        
    print("  [open_or_build_database: TODO — implement startup logic]")
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


# ─────────────────────────────────────────────────────────────────────────────
# Menu loop
# ─────────────────────────────────────────────────────────────────────────────

MENU = """
╔══════════════════════════════════════════╗
║      Music Playlist Manager — MP02       ║
╠══════════════════════════════════════════╣
║  1  Show all tracks on a playlist        ║
║  2  Show tracks on no playlist           ║
║  3  Show most-added track                ║
║  4  Show playlist durations              ║
║  5  Delete an artist (and their tracks)  ║
║  0  Exit                                 ║
╚══════════════════════════════════════════╝
"""

HANDLERS = {
    "1": show_playlist_tracks,
    "2": show_tracks_on_no_playlist,
    "3": show_most_added_track,
    "4": show_playlist_durations,
    "5": delete_artist,
}


def run_menu(conn):
    """Display the menu and dispatch user selections until the user exits."""
    while True:
        print(MENU)
        choice = input("Select an option: ").strip()

        if choice == "0":
            print("Goodbye.")
            break

        handler = HANDLERS.get(choice)
        if handler is None:
            print(f"  '{choice}' is not a valid option.  Please enter 0–5.")
            continue

        print()
        handler(conn)
        print()
        input("  Press Enter to return to the menu ...")


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    conn = open_or_build_database()
    try:
        run_menu(conn)
    finally:
        conn.close()
