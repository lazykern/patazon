# Editor-Specific Commands

Tags: #concept #simfile #implementation #compatibility

When examining simfiles in the wild, you may encounter commands that are not documented in any official format specification. Files saved by the popular editor **DTXCreator**, for example, contain special commands prefixed with `#DTXC_`.

---

## Purpose of Editor Commands

These commands are **editor-specific metadata**. Their purpose is to save the state of the editing environment, allowing a charter to close and re-open their project without losing their setup.

**These commands should be ignored by the game engine's parser.** A robust parser should recognize them as valid lines but simply skip over them without trying to process them as a gameplay feature. Attempting to parse them as standard commands will likely result in errors.

## Common DTXCreator Commands

| Command | Purpose |
|---|---|
| `#DTXC_CHIPPALETTE` | Stores the list of WAV IDs that appear in the editor's chip palette. |
| `#DTXC_LANEBINDEDCHIP`| Binds a specific WAV ID to a drum lane for quick access in the editor UI. |
| `#DTXC_WAVBACKCOLOR` | Stores the background color for a WAV entry in the editor's list. |
| `#DTXC_WAVFORECOLOR` | Stores the foreground (text) color for a WAV entry. |
| `#DTXC_BMP...COLOR` | Same as above, but for BMP list entries. |
| `#DTXC_AVI...COLOR` | Same as above, but for AVI list entries. |

Recognizing these commands is a mark of a mature parser that is resilient to real-world file variations.

---

### Related

*   [[🎵 Simfile Parsing MOC]]
*   [[Simfile Parsing Strategy]] 