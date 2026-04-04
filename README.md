# mp02-music-starter
Starter code for MP02 — SQL and Database · CIS 3120 Programming for Analytics · Baruch College · Three-module SQLite/Python team project with Git workflow

# MP02 — SQL and Database Starter

**CIS 3120 · Programming for Analytics · Baruch College / Zicklin School of Business**

---

## What This Repository Contains

This is the starter repository for **MP02 — SQL and Database**.  
Fork this repository to begin the mini-project.  Do not clone it directly.

| File | Owner | Purpose |
|:-----|:------|:--------|
| `schema_data.py` | Author 1 | Schema creation and seed data |
| `queries.py` | Author 2 | All four query functions |
| `main.py` | Integrator | Driver: startup, menu loop, deletion |
| `README.md` | — | This file |
| `.gitignore` | — | Excludes `music.db` and `__pycache__` |

---

## The Database Schema

The four-table schema below is fixed.  Column names, data types, and constraints
are specified by the assignment.  **Author 1 must implement this schema exactly.**
Author 2's queries and the Integrator's driver depend on these names.

```
Artist
    artist_id    INTEGER PRIMARY KEY
    name         TEXT    NOT NULL
    genre        TEXT    NOT NULL
    origin_city  TEXT

Track
    track_id         INTEGER PRIMARY KEY
    title            TEXT    NOT NULL
    duration_seconds INTEGER NOT NULL
    artist_id        INTEGER NOT NULL  →  Artist(artist_id)

Playlist
    playlist_id    INTEGER PRIMARY KEY
    playlist_name  TEXT    NOT NULL
    owner_name     TEXT    NOT NULL

PlaylistTrack
    playlist_id  INTEGER NOT NULL  →  Playlist(playlist_id)
    track_id     INTEGER NOT NULL  →  Track(track_id)
    position     INTEGER NOT NULL
    PRIMARY KEY (playlist_id, track_id)
```

---

## Team Roles — Quick Reference

| Role | Branch Name | Module |
|:-----|:------------|:-------|
| Integrator | `module/integrator-driver` | `main.py` |
| Author 1   | `module/author1-schema-data` | `schema_data.py` |
| Author 2   | `module/author2-queries` | `queries.py` |

Complete workflow instructions are in the assignment document on Brightspace.

---

## Running the Application

```bash
python main.py
```

On first run, `main.py` builds and seeds the database, backs it up to `music.db`,
then opens a menu.  On subsequent runs it opens the existing `music.db` directly.

To run Author 1's standalone demonstration (IntegrityError + backup):

```bash
python schema_data.py
```

---

## Academic Integrity

Each team member must author their own module.  Instructors may conduct brief oral
reviews of any submitted code.  See the assignment document for the full policy.

# AUTHOR2 UPDATE FIX
