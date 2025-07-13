# Channel Data

Tags: #concept #simfile #mechanic

Channel data forms the body of a `.dtx` file and contains the actual playable chart information. It's a sequence of commands that define events within musical measures.

---

## Structure

Channel data is organized by measure, then by channel.

*   **Measure Identifier**: Each measure is declared with `#xxx`, where `xxx` is a three-digit measure number (e.g., `#001`, `#002`).
*   **Channel Command**: Within a measure, a line follows the format `#xxxCC: [data]`, where:
    *   `xxx` is the measure number.
    *   `CC` is a two-character hexadecimal channel ID.
    *   `[data]` is a string of two-character hexadecimal object IDs from the [[Resource Mapping|resource map]].

## How It Works

The `[data]` string is evenly divided over the time of the measure. For example, if the data string is `01000200`, it represents four beats. The first beat triggers object `01`, the third beat triggers object `02`, and the second and fourth beats are empty (`00`).

**Example:**

```
#00411: 0100020001020102
```

*   `#004`: This is for measure 4.
*   `11`: This is the Hi-Hat channel.
*   `0100020001020102`: This string defines 8 events. If `01` is mapped to `hihat_open.wav` and `02` is mapped to `hihat_closed.wav`, this line defines a sequence of hi-hat hits for measure 4.

This data is consumed by the [[🎮 Gameplay Engine MOC]] to place notes and by the [[🔊 Audio System MOC]] to schedule sounds.

---

## Comprehensive Channel List

The following tables, derived from the developer guides, provide a more complete list of channels recognized by a DTXMania-like engine.

### System Channels
These channels control global song properties like timing, playback, and metadata.
| Hex | Dec | Purpose |
|---|---|---|
| `01` | 1 | Background Music (BGM) track. |
| `02` | 2 | Changes the length of the measure (e.g., `0.75` for a 3/4 bar). |
| `03` | 3 | Changes the BPM using a direct floating-point value. |
| `08` | 8 | Changes the BPM using an ID from the `#BPMxx` map. (Standard method) |
| `50` | 80 | Renders a main bar line. |
| `51` | 81 | Renders a sub-division beat line. |
| `C1` | 193 | Shifts beat line rendering location. |
| `C2` | 194 | Toggles beat line visibility. |
| `EC` | 236 | A metronome click sound. |
| `ED` | 237 | A non-functional marker for the first audible chip. |
| `EE` | 238 | Adds a sound to an internal mixer for processing. |
| `EF` | 239 | Removes a sound from an internal mixer. |

### Drum Channels
| Hex | Dec | Purpose |
|---|---|---|
| `11` | 17 | Closed Hi-Hat |
| `12` | 18 | Snare Drum |
| `13` | 19 | Bass Drum |
| `14` | 20 | High Tom |
| `15` | 21 | Low Tom |
| `16` | 22 | Crash Cymbal (often Right) |
| `17` | 23 | Floor Tom |
| `18` | 24 | Open Hi-Hat (choked by `11` and `1B`) |
| `19` | 25 | Ride Cymbal |
| `1A` | 26 | Left Crash Cymbal |
| `1B` | 27 | Left Pedal / Hi-Hat Pedal |
| `1C` | 28 | Left Bass Drum (for double bass) |
| `1F` | 31 | Marks a fill-in section for drums. |

*   **Hidden & Autoplay Channels**: 
    *   The channels in the range **`31`-`3C`** are "ghost note" channels. They are not shown to the player but are often used for score calculation or to trigger other visual effects.
    *   The channels in the range **`B1`-`BE`** are autoplay channels that play sounds automatically without a corresponding visible note, typically for backing tracks or ambient effects.

### Guitar & Bass Channels
| Hex | Dec | Purpose |
|---|---|---|
| `20` / `A0` | 32 / 160 | Guitar / Bass Open strum. |
| `21`-`27` | 33-39 | Guitar 3-fret (R,G,B) combinations. |
| `93`-`9E` | 147-158 | Guitar 5-fret (R,G,B,Y,P) combinations. |
| `A1`-`A7` | 161-167 | Bass 3-fret combinations. |
| `C5`-`D6` | 197-214 | Bass 5-fret combinations. |
| `28` / `A8` | 40 / 168 | Activates wailing bonus for Guitar/Bass. |
| `2F` | 47 | The sound to play for the wailing effect. |
| `2C` / `2D`| 44 / 45 | Marks a long (sustain) note for Guitar/Bass, respectively. |
| `BA` / `BB` | 186 / 187 | Autoplay sounds for Guitar/Bass (no visible chip). |

### Visual Channels (BGA/Movie)
| Hex | Dec | Purpose |
|---|---|---|
| `04` | 4 | Background Animation Layer 1 |
| `07` | 7 | Background Animation Layer 2 |
| `55`-`59` | 85-89 | BGA Layers 3-7 |
| `60` | 96 | BGA Layer 8 |
| `C4`,`C7`,`D5`-`DF` | 196,199,213-224 | Swaps BGA layers for dynamic effects. |
| `54` | 84 | Plays a movie clip defined in `#AVIxx`. |
| `5A` | 90 | Plays a fullscreen movie clip. |

### Sound Effect (SE) Channels
These channels trigger general-purpose sound effects mapped via `#WAVxx`.
| Hex | Dec | Range |
|---|---|---|
| `61`-`69` | 97-105 | SE01 - SE09 |
| `70`-`79` | 112-121| SE10 - SE19 |
| `80`-`89` | 128-137| SE20 - SE29 |
| `90`-`92` | 144-146| SE30 - SE32 |

### Unused/Reserved Channels
These channels are defined in format specifications but are either deprecated, reserved for other formats like BMS, or not implemented in most modern simulators.
| Hex | Dec | Purpose |
|---|---|---|
| `05`, `06` | 5,6 | Unused (originally for "Extended Object" and "Miss Animation"). |
| `09`, `0A` | 9,10 | Reserved for BMS file compatibility. |
| `29`, `30` | 41,48 | Unused (originally for "Flow Speed"). |
| `52` | 82 | Unused (originally "MIDI Chorus"). |
| `5B`-`5F`| 91-95 | Unused block. |
| `EA`, `EB` | 234,235 | Unused. |

---

### Related

*   [[🎵 Simfile Parsing MOC]]
*   [[Resource Mapping]]
*   [[BGA and BGI Channels]]
*   [[Hi-Hat Choking]]
