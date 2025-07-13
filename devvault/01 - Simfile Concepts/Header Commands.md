# Header Commands

Tags: #concept #simfile #metadata

Header commands are directives in a `.dtx` file that define metadata and global parameters for the song. They always start with a `#` and typically appear at the beginning of the file.

---

## Common Metadata Commands

These commands provide essential information about the song, which is often displayed to the player on the song selection screen.

*   `#TITLE: <song title>`: The title of the song.
*   `#ARTIST: <artist name>`: The name of the artist.
*   `#COMMENT: <comment>`: A description or comment about the chart.
*   `#PANEL: <panel string>`: A string displayed on the loading screen, often used for charter comments or tips.
*   `#GENRE: <genre>`: The genre of the song.

## Core Gameplay Commands

These commands set up the fundamental properties of how the chart will be played.

*   `#BPM: <beats per minute>`: Sets the initial tempo of the song. This can be changed later using the `BPM` channel (`08`).
*   `#DLEVEL: <difficulty level>`: The difficulty value, usually on a scale of 1-100 for the Drum chart. `#PLAYLEVEL` is often used as an alias for this.
*   `#GLEVEL: <difficulty level>`: The difficulty value for the Guitar chart.
*   `#BLEVEL: <difficulty level>`: The difficulty value for the Bass chart.

## Media & Display Commands

These commands link to visual and audio assets used outside of core gameplay, such as on the song selection or results screens.

*   `#PREVIEW: <audio file>`: An audio file to be played as a preview on the song selection screen.
*   `#PREIMAGE: <image file>`: An image (often a "jacket" or "cover art") displayed for the song.
*   `#PREMOVIE: <video file>`: A movie file shown on song-select.
*   `#STAGEFILE: <image file>`: A static background image displayed during gameplay.
*   `#RESULTIMAGExx: <image file>`: An image to be shown on the results screen for a specific rank (e.g., `#RESULTIMAGES: rank_s.png`).
*   `#RESULTMOVIExx: <video file>`: A movie to be shown on the results screen for a specific rank.
*   `#RESULTSOUNDxx: <audio file>`: A sound to be played on the results screen for a specific rank.
*   `#BACKGROUND: <image file>`: A generic background image, often used as a fallback. `#WALL` is a common alias for this command.

## File & Path Commands

*   `#PATH_WAV: <folder path>`: Specifies a default directory where the engine should look for all `#WAVxx` resources. This helps organize song folders.
*   `#PATH: <folder path>`: A more general fallback path prefix when `PATH_WAV` is not specified.

## Gameplay Modifier Commands

These commands act as flags that alter the gameplay experience.

*   `#HIDDENLEVEL: ON`: Instructs the game to hide the difficulty number on the UI.
*   `#FORCINGXG: ON`: Forces the game into a 9-lane (XG) drum mode.
*   `#VOL7FTO64: ON`: A compatibility flag to convert legacy 0-127 volume values to a 0-100 scale.
*   `#DTXVPLAYSPEED: <speed>`: Overrides the default playback speed when the chart is played in a "DTXViewer" or preview mode.

### Example

Here is a snippet from a real-world `.dtx` file header, showing several of these commands in action:

```dtx
#TITLE: グッドバイ -album version-
#ARTIST: Toe
#COMMENT: http://files.pinoypercussionfreaks.com/habble
#PREVIEW: preview.ogg
#PREIMAGE: banner.png
#BPM: 139
#DLEVEL: 88
#GLEVEL: 0
#BLEVEL: 0
```

---

### Related

*   [[🎵 Simfile Parsing MOC]]
*   [[Simfile Structure Overview]]
*   [[Resource Mapping]]
