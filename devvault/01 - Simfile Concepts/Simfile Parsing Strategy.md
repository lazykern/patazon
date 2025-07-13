# Simfile Parsing Strategy

Tags: #concept #simfile #implementation

Parsing a `.dtx` file effectively requires a multi-pass approach to handle its declarative structure. A robust parser can be broken down into a few key phases.

---

## Phase 1: Header & Resource Pass

First, iterate through the file line by line, focusing only on lines that start with `#`.

1.  **Identify Command**: Extract the command (e.g., `TITLE`, `WAV01`, `BPM`).
2.  **Store Data**:
    *   If it's a metadata command ([[Header Commands]]), store the value in a general song properties object.
    *   If it's a resource command ([[Resource Mapping]]), add the entry to a resource table (e.g., a dictionary mapping `01` to `kick.wav`).
    *   If it's a global setting like `#BPM`, store it as the initial value.

At the end of this pass, you should have all the metadata and a complete map of all external assets, but no note data.

## Phase 2: Body & Channel Pass

Now, iterate through the file again. This time, focus on the [[Channel Data]] lines (`#xxxCC: ...`).

1.  **Identify Measure and Channel**: For each line, parse the measure number (`xxx`) and the channel ID (`CC`).
2.  **Parse Objects**: Read the data string. Iterate through it, taking two characters at a time to get the object IDs.
3.  **Create Timed Events**: For each non-`00` object, calculate its precise timestamp within the song. This requires knowing:
    *   The current BPM.
    *   The current measure's length (which can be modified by channel `02`).
    *   The object's position within the measure.
4.  **Store Events**: Store these timed events in a structured list. Each event should contain, at a minimum:
    *   `Timestamp (ms)`
    *   `Channel ID`
    *   `Object ID`
    *   `Resource Path` (looked up from the resource table)

## Data Structures

*   **SongInfo**: A class/struct to hold all metadata (`Title`, `Artist`, etc.).
*   **ResourceTable**: A `Dictionary<string, string>` or `HashMap` for resource mappings.
*   **EventList**: A `List<GameEvent>` where `GameEvent` is a class/struct holding the timed event data.

After these two passes, you will have a clean, ordered list of all game events, ready to be consumed by the [[🎮 Gameplay Engine MOC]] and [[🔊 Audio System MOC]].

---

## Implementation Details & Best Practices

### Internal Tick Resolution

While the channel data string provides a variable grid resolution (e.g., 16th notes, 24th notes), a robust engine converts this to a high, fixed internal resolution for timing calculations. The DTXMania engine converts every measure into **384 ticks**.

When you calculate the beat position (`item_index / resolution`), you should then map this to the 384-tick system to get a precise, scalable timestamp before factoring in BPM and measure length. This avoids floating point inaccuracies and makes time calculations more consistent.

### Character Encoding

Many legacy simfiles, especially those created with Japanese tools, use **Shift_JIS** character encoding. A parser that only supports UTF-8 may fail to read metadata correctly, resulting in garbled text for titles and artist names. When reading the file, it's a safe practice to try parsing with Shift_JIS if UTF-8 fails, or to provide a configuration option for the user.

---

### Related

*   [[🎵 Simfile Parsing MOC]]
