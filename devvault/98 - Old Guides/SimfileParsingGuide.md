# How to Parse Rhythm Game Simfiles: A Developer's Guide

This guide provides a developer-focused overview of how to parse a rhythm game simfile, using the DTX format as a primary example. Understanding this process is the first step toward building a game engine that can load and play community-made charts.

## Introduction: What is a Simfile?

A simfile is a text-based file that contains all the information needed to play a song in a rhythm game. This includes:

*   **Metadata**: Song title, artist, difficulty, etc.
*   **Resources**: References to sound files (WAV, OGG), background images (BMP), and videos (AVI).
*   **Chart Data**: The precise timing and placement of every note or event in the game.

The format is typically line-based, with each line representing either a command or a comment.

## The Two Pillars of a Simfile

A DTX file can be conceptually broken down into two main parts:

1.  **The Header**: Defines *what* the song is and *what* resources it uses.
2.  **The Body (Channel Data)**: Defines *when* and *where* notes and events occur.

---

## Part 1: Parsing the Header (Metadata & Resources)

The header consists of lines that follow a `#COMMAND:VALUE` syntax. Your parser's first job is to read these lines and populate your game's data structures.

### Key Metadata Commands

These commands describe the song itself. You'll display this information on the song selection screen.

| Command         | Example Value                 | Purpose                                           |
| --------------- | ----------------------------- | ------------------------------------------------- |
| `#TITLE`        | `My Awesome Song`             | The song's title.                                 |
| `#ARTIST`       | `The Legendary Programmer`    | The song's artist.                                |
| `#BPM`          | `180.5`                       | The initial Beats Per Minute (BPM) of the song.   |
| `#DLEVEL`       | `85`                          | Difficulty level for the Drum chart (0-999).      |
| `#GLEVEL`       | `92`                          | Difficulty level for the Guitar chart.            |
| `#BLEVEL`       | `80`                          | Difficulty level for the Bass chart.              |
| `#PANEL`        | `SongPack01`                  | Group / panel label shown on song-select.         |
| `#PREVIEW`      | `preview.ogg`                 | Audio file used for the preview.                  |
| `#PREIMAGE`     | `jacket.png`                  | Jacket / cover image for the song.                |
| `#STAGEFILE`    | `stage.png`                   | Background shown during gameplay.                 |
| `#BACKGROUND`   | `bg_main.png`                 | Generic background image (fallback/legacy).       |
| `#PATH_WAV`     | `sounds/`                     | Default search folder for WAV resources.          |

### Additional DTXMania-specific Header Commands
| Command | Example Value | Purpose |
| ------- | ------------- | ------- |
| `#PATH` | `assets/` | General fallback path prefix when `PATH_WAV` is absent. |
| `#GENRE` | `Rock` | Genre tag shown on song-select. |
| `#HIDDENLEVEL` | `ON` | Hide difficulty values on UI. |
| `#STAGEFILE` | `stage.png` | Static background displayed during gameplay. |
| `#PREMOVIE` | `intro.avi` | Movie shown on song-select. |
| `#RESULTIMAGExx` / `#RESULTMOVIExx` / `#RESULTSOUNDxx` | `rank_ss.png` | Per-rank result-screen media (xx = SS,S,A,B,C,D,E). |
| `#FORCINGXG` | `ON` | Force 9-lane drum (XG) mode. |
| `#VOL7FTO64` | `ON` | Convert legacy 0-127 volumes to 0-100. |
| `#DTXVPLAYSPEED` | `1.25` | Overrides playback speed in DTXViewer mode. |
| `#IF / #ENDIF`, `#RANDOM` | – | Conditional / randomised chart sections. |

### Key Resource Commands

These commands link an internal ID to an external media file. The ID is a two-character hexadecimal or base-36 value (`00`-`ZZ`).

| Command         | Example Value           | Purpose                                                                |
| --------------- | ----------------------- | ---------------------------------------------------------------------- |
| `#WAVxx`        | `kick.wav`              | Maps the ID `xx` to a sound file. This is the core of the audio system. |
| `#BMPxx`        | `background_layer1.bmp` | Maps the ID `xx` to an image file, used for animations or backgrounds. |
| `#BMPTEXxx`     | `lane_texture.dds`      | Same as `BMPxx` but flagged to load as a texture.                      |
| `#AVIxx`        | `movie_cutscene.avi`    | Maps the ID `xx` to a video file.                                      |
| `#BPMxx`        | `190`                   | Maps the ID `xx` to a specific BPM value for mid-song tempo changes.   |

### WAV Property Commands
| Command | Example | Purpose |
| ------- | ------- | ------- |
| `#SIZExx`    | `70`     | Default chip draw-size (%) for WAV `xx`. |
| `#PANxx`     | `-30`    | Default pan (-100 L … 100 R) for WAV `xx`. |
| `#VOLUMExx`  | `80`     | Default volume 0-100 for WAV `xx`. |
| `#WAVPANxx` / `#WAVVOLxx` | `-40` / `90` | Inline syntax to set pan / volume for WAV `xx`. |

### Suggested Data Structures

To store this information, you might use classes like these in C# (or equivalents in other languages):

```csharp
public class SongMetadata
{
    public string Title { get; set; }
    public string Artist { get; set; }
    public double InitialBpm { get; set; }
    public string PreviewAudioPath { get; set; }
    public string JacketImagePath { get; set; }
}

public class GameResources
{
    // Maps a Base-36 ID (like "01", "1A", "ZZ") to a file path
    public Dictionary<string, string> WavMap { get; } = new Dictionary<string, string>();
    public Dictionary<string, string> BmpMap { get; } = new Dictionary<string, string>();
    
    // Maps a Base-36 ID to a BPM value
    public Dictionary<string, double> BpmChangeMap { get; } = new Dictionary<string, double>();
}
```

---

## Part 2: Parsing the Body (Note & Event Data)

This is the core of the chart. These lines define the timing of every interactive element.

### The Channel Data Syntax: `#XXXCC:DDDDDD...`

*   `#XXX`: A three-digit **bar/measure number**, starting from `001`.
*   `CC`: A two-digit hexadecimal **channel number**. This is the most important part, as it tells you *what kind of event* this line describes.
*   `DDDDDD...`: A long string of two-character **object IDs**. `00` represents a rest. Any other value is an ID that corresponds to a resource defined in the header.

### Understanding Channels (`CC`)

Each channel corresponds to a specific gameplay lane or system event. Here are a few critical examples:

| Channel | Purpose                                         | Example                                                                          |
| ------- | ----------------------------------------------- | -------------------------------------------------------------------------------- |
| `01`    | **Background Music (BGM)**                      | Plays sounds from the `#WAVxx` map that are part of the song, not hit by the player. |
| `02`    | **Measure Length Change**                       | The parameter is a float that scales the measure length (e.g., `0.75` for a 3/4 measure). |
| `03`    | **BPM Change (Integer)**                        | Uses an integer value directly. (Less common).                                  |
| `08`    | **BPM Change (Extended)**                       | Uses an ID from the `#BPMxx` map. This is the standard way to do tempo changes.   |
| `11`-`1F` | **Player-Hittable Notes** (Drums)               | `11`: Hi-Hat, `12`: Snare, `13`: Bass Drum, etc. The specific mapping defines your game's layout. |
| `04`, `07`, `55`-`5B`, `60` | **Layered Background Animations (BGA)** | `04`: layer 1, `07`: layer 2, `55`-`5B`: layers 3-7, `60`: layer 8 |
| `49`-`60` | **Hidden-Note Duplicates** | Copies of drum lanes used to mask or reveal notes dynamically. |
| `...` | `...` | *(See `EChannel.cs` in the DTXMania source for a full list of >200 supported channels.)* |

### Understanding Object Data (`DD...`)

The string of object IDs represents a time grid for the measure.

*   **Resolution**: The number of two-character pairs in the string determines the measure's timing resolution. If there are 16 pairs, the measure is divided into 16th notes. If there are 24, it's 24th notes (triplets).
*   **Timing**: The position of an object ID determines its timing. The 1st pair is on the 1st beat of the grid, the 2nd on the 2nd beat, and so on.
*   **Linking**: When the parser finds a non-`00` object ID (e.g., `1A`), it means "At this exact moment in time, on this specific channel, trigger the event associated with ID `1A`."

**Example:**

```
#WAV01: kick.wav
#WAV02: snare.wav

...

#00213:0100020001000200  // Measure 2, Bass Drum channel
```

This line means:
*   We are in measure #2, on the Bass Drum channel (`13`).
*   The measure is divided into 8 slots (8th note resolution).
*   On the 1st slot, play the sound mapped to `01` (`kick.wav`).
*   On the 3rd slot, play the sound mapped to `02` (`snare.wav`).
*   On the 5th slot, play `kick.wav` again.
*   On the 7th slot, play `snare.wav` again.

---

## A Step-by-Step Parsing Strategy

1.  **File Reading**: Read the file line-by-line. Be mindful of character encoding—**Shift\_JIS** is a safe bet for older Japanese files.

2.  **Initialization**: Create instances of your `SongMetadata`, `GameResources`, and a `List<Measure>` to hold the chart data.

3.  **Primary Loop**: Iterate through each line of the file.
    *   Trim whitespace.
    *   Skip empty lines or lines starting with a semicolon (`;`).
    *   If the line does not start with `#`, ignore it.

4.  **Command & Value Splitting**: For a valid `#` line, find the first colon (`:`).
    *   The text between `#` and `:` is the `command`.
    *   The text after `:` is the `value`.

5.  **Line Processing Logic**:

    ```
    if ( command is a header command like "TITLE", "ARTIST", "WAV01", etc. ) {
        // It's a header line.
        ParseHeader(command, value); 
        // Example: Add "WAV01" and its filename to your WavMap dictionary.
    } 
    else if ( command is a channel data command like "0011A" ) {
        // It's a note data line.
        ParseChannelData(command, value);
    }
    ```

6.  **Parsing Channel Data (In-depth)**:
    *   Extract the measure number (`XXX`) and channel number (`CC`).
    *   Find the `Measure` object for this measure number in your list, or create it if it's the first time you've seen it.
    *   Calculate the timing grid resolution (e.g., `value.Length / 2`).
    *   Iterate through the `value` string, taking two characters at a time (`objectID`).
    *   If `objectID` is not `00`:
        *   Calculate the precise beat position: `beat = (double)item_index / resolution;`
        *   Create a `Note` or `GameEvent` object. Populate it with:
            *   The measure number.
            *   The beat position within the measure.
            *   The channel number (`CC`).
            *   The object ID (`objectID`).
        *   Add this new object to the current `Measure`.

7.  **Post-Processing**: After parsing the whole file, you may want to perform a final step to calculate the absolute timestamp for every note by factoring in the measure lengths and all BPM changes.

By following this structure, you can build a robust parser capable of transforming a simple text file into a rich, playable gameplay experience. 

---

## Appendix A: Internal Resolution & Timing
DTXMania converts every measure into **384 ticks** internally.  After you compute the fraction `slotIndex / totalSlots` from the channel string, multiply by 384 (then by BPM & measure-length scaling) to obtain the exact playback time.

## Appendix B: Full Channel List
The engine recognises a very large set of channels (background layers, hidden lanes, system cues, guitar/bass lanes, etc.).  Refer to `DTXMania/Code/Score,Song/EChannel.cs` for the authoritative enumeration.

## Appendix C: Complete Channel Listing
Below is a comprehensive list of all channels, grouped by function.

### System Channels
These channels control global song properties like timing, playback, and metadata.
| Hex | Dec | Enum Name | Purpose |
|---|---|---|---|
| `01` | 1 | `BGM` | Background Music track. |
| `02` | 2 | `BarLength` | Changes the length of the measure (e.g., `0.75` for a 3/4 bar). |
| `03` | 3 | `BPM` | Changes the BPM using a direct floating-point value. |
| `08` | 8 | `BPMEx` | Changes the BPM using an ID from the `#BPMxx` map. |
| `50` | 80 | `BarLine` | Renders a main bar line. |
| `51` | 81 | `BeatLine` | Renders a sub-division beat line. |
| `C1` | 193 | `BeatLineShift` | Shifts beat line rendering location. |
| `C2` | 194 | `BeatLineDisplay` | Toggles beat line visibility. |
| `EC` | 236 | `Click` | A metronome click sound. |
| `ED` | 237 | `FirstSoundChip` | A non-functional marker for the first audible chip. |
| `EE` | 238 | `MixerAdd` | Adds a sound to an internal mixer for processing. |
| `EF` | 239 | `MixerRemove`| Removes a sound from an internal mixer. |

### Drum Channels
| Hex | Dec | Enum Name | Purpose |
|---|---|---|---|
| `11` | 17 | `HiHatClose` | Closed Hi-Hat |
| `12` | 18 | `Snare` | Snare Drum |
| `13` | 19 | `BassDrum` | Bass Drum |
| `14` | 20 | `HighTom` | High Tom |
| `15` | 21 | `LowTom` | Low Tom |
| `16` | 22 | `Cymbal` | Crash Cymbal (often Right) |
| `17` | 23 | `FloorTom` | Floor Tom |
| `18` | 24 | `HiHatOpen` | Open Hi-Hat |
| `19` | 25 | `RideCymbal` | Ride Cymbal |
| `1A` | 26 | `LeftCymbal` | Left Crash Cymbal |
| `1B` | 27 | `LeftPedal` | Left Pedal / Hi-Hat Pedal |
| `1C` | 28 | `LeftBassDrum` | Left Bass Drum (for double bass) |
| `1F` | 31 | `DrumsFillin` | Marks a fill-in section for drums. |

#### Hidden & Autoplay Drum Channels
*   **Hidden (`31`-`3C`)**: These "ghost note" channels are not shown to the player but are used for score calculation or visual effects.
*   **No-Chip (`B1`-`BE`)**: These channels play sounds automatically without a corresponding hittable note, typically for backing tracks.

### Guitar & Bass Channels
The `xxBxx` notation in a name defines which frets are active (R,G,B,Y,P). `x` means inactive.
| Hex | Dec | Enum Name | Purpose |
|---|---|---|---|
| `20` | 32 | `Guitar_Open` | Open strum (no frets). |
| `21`-`27` | 33-39 | `Guitar_...` | Standard 3-fret (R,G,B) combinations. |
| `93`-`9E` | 147-158 | `Guitar_...` | 5-fret (R,G,B,Y,P) combinations. |
| `A0` | 160 | `Bass_Open` | Bass open strum. |
| `A1`-`A7` | 161-167 | `Bass_...` | Bass 3-fret combinations. |
| `C5`-`D6` | 197-214 | `Bass_...` | Bass 5-fret combinations. |
| `28` / `A8` | 40 / 168 | `Guitar_Wailing` / `Bass_Wailing` | Activates wailing bonus for Guitar/Bass. |
| `2F` | 47 | `Guitar_WailingSound` | The sound to play for wailing. |
| `2C`,`2D` | 44,45 | `Guitar_LongNote`, `Bass_LongNote` | Marks a long (sustain) note. |
| `BA` / `BB` | 186 / 187 | `Guitar_NoChip` / `Bass_NoChip` | Autoplay sounds for Guitar/Bass. |

### Visual Channels (BGA/Movie)
| Hex | Dec | Enum Name | Purpose |
|---|---|---|---|
| `04` | 4 | `BGALayer1` | Background Animation Layer 1 |
| `07` | 7 | `BGALayer2` | Background Animation Layer 2 |
| `55`-`59` | 85-89 | `BGALayer3` - `BGALayer7` | BGA Layers 3-7 |
| `60` | 96 | `BGALayer8` | BGA Layer 8 |
| `C4`, `C7`, `D5`-`DF` | 196,199,213-224 | `..._Swap` | Swaps BGA layers for dynamic effects. |
| `54` | 84 | `Movie` | Plays a movie clip defined in `#AVIxx`. |
| `5A` | 90 | `MovieFull` | Plays a fullscreen movie clip. |

### Sound Effect (SE) Channels
These channels trigger general-purpose sound effects mapped via `#WAVxx`.
| Hex | Dec | Enum Name | Purpose |
|---|---|---|---|
| `61`-`69` | 97-105 | `SE01` - `SE09` | Sound Effects 1-9 |
| `70`-`79` | 112-121 | `SE10` - `SE19` | Sound Effects 10-19 |
| `80`-`89` | 128-137 | `SE20` - `SE29` | Sound Effects 20-29 |
| `90`-`92` | 144-146 | `SE30` - `SE32` | Sound Effects 30-32 |

### Unused/Reserved Channels
These channels are defined in the enum but are either deprecated or reserved for future/other formats.
| Hex | Dec | Enum Name | Purpose |
|---|---|---|---|
| `05`, `06` | 5,6 | `ExObj_nouse`, `MissAnimation_nouse` | Unused |
| `09`, `0A` | 9,10 | `BMS_reserved...` | Reserved for BMS file compatibility. |
| `29`, `30` | 41,48 | `flowspeed_...` | Unused |
| `5B`-`5F`| 91-95 | `nouse_5b` - `nouse_5f` | Unused |
| `52` | 82 | `MIDIChorus` | Likely related to unimplemented SMF playback. |
| `EA`, `EB` | 234,235 | `MixChannel..._unc` | Unused |

## Appendix D: Format Compatibility (GDA & BMS)
The DTXMania engine is capable of parsing more than just the DTX format. It can transparently load and convert several related formats on the fly.

### GDA (Guitar & Drums Archive)
GDA files are very similar to DTX but use a different set of two-character channel codes. The engine maintains an internal conversion table (`stGDAParam`) to map these to the standard `EChannel` enumeration.

| GDA Code | DTX `EChannel` | Purpose |
|---|---|---|
| `HH` | `HiHatClose` | Drums: Hi-Hat |
| `SD` | `Snare` | Drums: Snare |
| `BD` | `BassDrum` | Drums: Bass Drum |
| `G1`-`G7` | `Guitar_...` | Guitar Frets |
| `B1`-`B7` | `Bass_...` | Bass Frets |
| `GW`/`BW`| `..._Wailing` | Wailing Bonus |
| `FI` | `FillIn` | Fill-In Section |
| `TC` | `BPM` | BPM Change |
| `BL` | `BarLength` | Bar Length Change |

### BMS / BME
The engine also contains logic to parse Beatmania (`.bms`) and Beatmania Extended (`.bme`) files, mapping their unique key channels to the corresponding DTX drum channels. This conversion is more complex and happens within `tDTX入力_行解析_チャンネル_BMSチャンネル文字列２桁をチャンネル番号にして返す`.

## Appendix E: DTXCreator-Specific Commands
Files saved by the `DTXCreator` application often contain special commands prefixed with `#DTXC_`. These commands are **editor-specific metadata** and are ignored by the `DTXMania` game engine. Their purpose is to save the state of the editing environment.

| Command | Purpose |
|---|---|
| `#DTXC_CHIPPALETTE` | Stores the list of WAV IDs that appear in the editor's chip palette. |
| `#DTXC_LANEBINDEDCHIP`| Binds a specific WAV ID to a drum lane for quick access in the editor UI. |
| `#DTXC_WAVBACKCOLOR` | Stores the background color for a WAV entry in the editor's list. |
| `#DTXC_WAVFORECOLOR` | Stores the foreground (text) color for a WAV entry. |
| `#DTXC_BMP...COLOR` | Same as above, but for BMP list entries. |
| `#DTXC_AVI...COLOR` | Same as above, but for AVI list entries. | 