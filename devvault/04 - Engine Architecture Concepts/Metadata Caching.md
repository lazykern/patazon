# Metadata Caching (Song Database)

Tags: #concept #architecture #performance #database

Loading song information by parsing every single simfile on startup is not scalable. An engine that needs to support a library of thousands of songs requires a **metadata cache**, often called a "song database".

---

## The Problem

A typical simfile contains a lot of information, but only a small subset is needed for the song selection screen (`#TITLE`, `#ARTIST`, `#BPM`, `#DLEVEL`, etc.). Parsing the entire file, especially the lengthy [[Channel Data]] body, just to get this header information is extremely inefficient. Doing this for hundreds or thousands of files would lead to unacceptably long startup times.

## The Solution: Scan Once, Read Fast

A high-performance engine uses a caching strategy:

1.  **First Run Scan**: On the very first run, or when explicitly triggered by the user, the engine performs a full scan of all song folders. It recursively searches for all valid simfiles.
2.  **Build In-Memory Database**: For each file found, it does a single, full parse and extracts all the metadata needed for song selection and sorting. This data is stored in a structured, in-memory list or tree.
3.  **Create Cache File**: The engine then serializes this entire list of metadata into a single, fast-loading binary file (e.g., `song.db`, `cache.dat`).
4.  **Subsequent Runs**: On all subsequent startups, the engine checks for the existence of `song.db`.
    *   If it exists, it loads this single file directly into memory. This is orders of magnitude faster than parsing thousands of text files.
    *   The engine can then perform a quick background check (e.g., by comparing file modification dates) to find any new or changed songs and update the cache accordingly, rather than re-scanning everything from scratch.

### User Data Storage

This database is a good place to store user-specific data, such as high scores, clear lamps (Failed, Clear, Full Combo, etc.), and play counts for each song.

An alternative strategy is to store performance history in separate, small files alongside the original simfiles. This can make the data more portable and easier for users to manage or back up manually, at the cost of slightly slower access compared to a single database file.

---

### Related

*   [[Simfile Parsing Strategy]]
*   [[Game State Machine]] 