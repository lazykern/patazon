# Resource Mapping

Tags: #concept #simfile #resources

Resource mapping is the process by which a DTX simfile associates short, two-character hexadecimal IDs with external asset files, such as audio samples and images. This is a critical step in the [[Simfile Parsing Strategy|parsing process]].

---

## Audio Resources (`#WAV`)

The `#WAVxx` command maps a hex ID (`xx`) to a sound file. The engine must load these files into memory to be triggered by [[Channel Data]].

*   **Syntax**: `#WAVxx: <filename.wav>`
*   **Example**: `#WAV01: kick.wav`

Here, the ID `01` is now an alias for `kick.wav`. When channel `11` (Hi-Hat) contains a `01`, the engine knows to play `kick.wav`.

## Image Resources (`#BMP`)

The `#BMPxx` command works identically, but for image files used in background animations ([[BGA and BGI Channels|BGA/BGI]]).

*   **Syntax**: `#BMPxx: <filename.bmp>`
*   **Example**: `#BMP01: background_intro.bmp`

The guide also specifies `#BMPTEXxx`, which is flagged to be loaded as a renderable texture rather than just a simple bitmap.

## Video Resources (`#AVI`)

Similar to other resources, `#AVIxx` maps an ID to a video file.

*   **Syntax**: `#AVIxx: <filename.avi>`
*   **Example**: `#AVI01: intro_movie.avi`

## BPM Change Resources (`#BPM`)

Instead of just changing the BPM directly, the DTX format allows for defining a map of target BPMs. This is the standard way to handle mid-song tempo changes. The ID is then referenced later in the body by channel `08`.

*   **Syntax**: `#BPMxx: <BPM value>`
*   **Example**: `#BPM01: 220.5`

## The Resource Table

A parser should build a data structure—often a dictionary or hash map—to store these mappings. This "resource table" allows for quick lookups during the body parsing phase.

**Example Table:**

| ID  | Type   | Value / File Path |
| --- | ------ | ----------------- |
| `01`| `WAV`  | `kick.wav`        |
| `02`| `WAV`  | `snare.wav`       |
| `A0`| `BMP`  | `intro_image.bmp` |
| `A1`| `AVI`  | `cutscene.avi`    |
| `B1`| `BPM`  | `220.5`           |


This table is essential for translating the abstract IDs in the channel data into concrete assets to be used by the [[🔊 Audio System MOC|audio]] and rendering engines.

---

### Related

*   [[🎵 Simfile Parsing MOC]]
*   [[Header Commands]]
*   [[Channel Data]]
