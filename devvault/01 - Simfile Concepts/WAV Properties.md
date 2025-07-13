# WAV Properties

Tags: #concept #simfile #resources #audio

Beyond simply mapping a sound file to an ID with `#WAVxx`, the DTX format allows charters to specify default properties for that sound. These commands control how a sound is rendered by the audio engine when it's played.

---

## `#VOLUMExx`

This command sets the default volume for the sound associated with ID `xx`. The value is typically an integer from 0 to 100.

*   **Syntax**: `#VOLUMExx: <volume>`
*   **Example**: `#VOLUME01: 85` (Sets the volume for WAV `01` to 85%)

## `#PANxx`

This command sets the default stereo panning for the sound. The value is an integer from -100 (full left) to 100 (full right), with 0 being center.

*   **Syntax**: `#PANxx: <pan>`
*   **Example**: `#PAN02: -30` (Pans WAV `02` slightly to the left)

## `#SIZExx`

Changes the drawing size of the note chip associated with a specific WAV ID. This is a percentage value.

*   **Syntax**: `#SIZExx: <percentage>`
*   **Example**: `#SIZE01: 70` (Sets the note chip for WAV `01` to be drawn at 70% of its normal size)

*(Note: This command is primarily recognized by the DTXMania player engine and may not be supported by all editors.)*

## Aliases

For convenience, some of these commands have aliases:
*   `#WAVVOLxx` is an alias for `#VOLUMExx`.
*   `#WAVPANxx` is an alias for `#PANxx`.

## `#BGMWAV`

This command flags a previously defined WAV resource as background music. It does not define a new sound; it modifies an existing one. Both the player and editor use this to distinguish BGM tracks from playable instrument sounds.

*   **Syntax**: `#BGMWAV: <ID>`
*   **Example**: `#BGMWAV: 01` (Marks WAV `01` as a BGM track)

### Example

Here is a snippet from a real `.dtx` file showing several of these properties being set for different sound IDs.

```dtx
#WAV0C: GAV-CHIHAT1.ogg	;HH Closed Hi-hat
#VOLUME0C: 20
#PAN0C: -25

#WAV0R: GAV-HITOM1.ogg	;HT High Tom 1
#VOLUME0R: 70
#PAN0R: -30

#WAV15: GAV-CYMRIGHT1.ogg	;CY Crash Cymbal 1
#VOLUME15: 25
#PAN15: 30
```

---

### Related

*   [[🎵 Simfile Parsing MOC]]
*   [[Resource Mapping]]
*   [[�� Audio System MOC]] 