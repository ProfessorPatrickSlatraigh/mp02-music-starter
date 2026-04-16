def get_playlist_tracks(conn, playlist_name):
    query = """
        SELECT t.title,
               a.name AS artist_name,
               t.duration_seconds,
               pt.position
        FROM PlaylistTrack pt
        JOIN Track t ON pt.track_id = t.track_id
        JOIN Artist a ON t.artist_id = a.artist_id
        JOIN Playlist p ON pt.playlist_id = p.playlist_id
        WHERE p.playlist_name = ?
        ORDER BY pt.position ASC
    """
    return conn.execute(query, (playlist_name,)).fetchall()


def get_tracks_on_no_playlist(conn):
    query = """
        SELECT t.track_id,
               t.title,
               a.name AS artist_name
        FROM Track t
        JOIN Artist a ON t.artist_id = a.artist_id
        LEFT JOIN PlaylistTrack pt ON t.track_id = pt.track_id
        WHERE pt.track_id IS NULL
    """
    return conn.execute(query).fetchall()


def get_most_added_track(conn):
    query = """
        SELECT t.title,
               a.name AS artist_name,
               COUNT(*) AS playlist_count
        FROM PlaylistTrack pt
        JOIN Track t ON pt.track_id = t.track_id
        JOIN Artist a ON t.artist_id = a.artist_id
        GROUP BY pt.track_id
        ORDER BY playlist_count DESC
        LIMIT 1
    """
    return conn.execute(query).fetchone()


def get_playlist_durations(conn):
    query = """
        SELECT p.playlist_name,
               SUM(t.duration_seconds) / 60.0 AS total_minutes
        FROM Playlist p
        JOIN PlaylistTrack pt ON p.playlist_id = pt.playlist_id
        JOIN Track t ON pt.track_id = t.track_id
        GROUP BY p.playlist_id
        ORDER BY total_minutes DESC
    """
    return conn.execute(query).fetchall()