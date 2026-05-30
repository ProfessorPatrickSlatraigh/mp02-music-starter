import sqlite3

def get_playlist_tracks(conn, playlist_name):
    """Return all tracks on a named playlist ordered by position."""
    query = """
        SELECT  t.title,
                a.name        AS artist_name,
                t.duration_seconds,
                pt.position
        FROM    PlaylistTrack pt
        JOIN    Track    t  ON pt.track_id    = t.track_id
        JOIN    Artist   a  ON t.artist_id    = a.artist_id
        JOIN    Playlist p  ON pt.playlist_id = p.playlist_id
        WHERE   p.playlist_name = ?
        ORDER BY pt.position ASC
    """
    return conn.execute(query, (playlist_name,)).fetchall()


def get_tracks_on_no_playlist(conn):
    """Return all tracks not assigned to any playlist."""
    query = """
        SELECT  t.title,
                a.name AS artist_name
        FROM    Track t
        LEFT JOIN PlaylistTrack pt ON t.track_id = pt.track_id
        JOIN    Artist a ON t.artist_id = a.artist_id
        WHERE   pt.track_id IS NULL
    """
    return conn.execute(query).fetchall()


def get_most_added_track(conn):
    """Return the track appearing on the greatest number of playlists."""
    query = """
        SELECT  t.title,
                a.name AS artist_name,
                COUNT(*) AS count
        FROM    PlaylistTrack pt
        JOIN    Track  t ON pt.track_id  = t.track_id
        JOIN    Artist a ON t.artist_id  = a.artist_id
        GROUP BY pt.track_id
        ORDER BY count DESC
        LIMIT 1
    """
    return conn.execute(query).fetchall()


def get_playlist_durations(conn):
    """Return each playlist's name and total duration in minutes."""
    query = """
        SELECT  p.playlist_name,
                SUM(t.duration_seconds) / 60.0 AS total_minutes
        FROM    Playlist p
        JOIN    PlaylistTrack pt ON p.playlist_id  = pt.playlist_id
        JOIN    Track        t  ON pt.track_id     = t.track_id
        GROUP BY p.playlist_id
        ORDER BY total_minutes DESC
    """
    return conn.execute(query).fetchall()
