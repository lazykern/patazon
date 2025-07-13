# Simfile Parsing Strategy

Tags: #concept #simfile #implementation

Parsing a `.dtx` file effectively requires handling its declarative structure, where resources like sounds and images might be referenced by channels before they are defined. A common approach is a two-pass system, but the DTXMania engine uses a more complex and efficient single-pass strategy.

---

## Single-Pass Parsing with Forward-Reference Resolution

The parser iterates through the file line by line just once.

1.  **Line-by-Line Analysis**: The engine reads each line and determines if it is a header command, a resource definition, or channel data.

2.  **Immediate Header/Resource Processing**:
    *   Metadata commands (`#TITLE`, `#ARTIST`, etc.) are stored immediately.
    *   Resource definitions (`#WAVxx`, `#BMPxx`, etc.) are added to their respective lists. The engine assigns a unique internal ID to each new resource.

3.  **Chip and Event Handling**:
    *   When channel data (`#xxxCC: ...`) is encountered, the objects are parsed.
    *   For each object, a "chip" is created and added to a master list (`listChip`).
    *   **Forward-Reference Handling**: If a chip references a resource ID (e.g., WAV `01`) that has not been defined yet, the chip is still created. It's temporarily assigned a negative or placeholder internal ID. Later, when the actual `#WAV01` definition is parsed, the engine iterates back through the chip list to update all chips that were waiting for that definition, replacing the placeholder with the correct internal ID.

4.  **Post-Processing**: After the entire file is read, the master chip list is sorted by timestamp. Then, final calculations like precise event timing (factoring in BPM changes) are performed on the complete, ordered list of events.

This single-pass method avoids reading the file multiple times but requires careful management of internal IDs and placeholders to resolve forward references correctly.

## Implementation Details & Best Practices

### Internal Tick Resolution

While the channel data string provides a variable grid resolution (e.g., 16th notes, 24th notes), a robust engine converts this to a high, fixed internal resolution for timing calculations. The DTXMania engine converts every measure into **384 ticks**.

When you calculate the beat position (`item_index / resolution`), you should then map this to the 384-tick system to get a precise, scalable timestamp before factoring in BPM and measure length. This avoids floating point inaccuracies and makes time calculations more consistent.

### Character Encoding

Many legacy simfiles, especially those created with Japanese tools, use **Shift_JIS** character encoding. The `CDTX.cs` implementation explicitly reads files using this encoding. A parser that only supports UTF-8 may fail to read metadata correctly, resulting in garbled text for titles and artist names.

---

### Related

*   [[🎵 Simfile Parsing MOC]]
