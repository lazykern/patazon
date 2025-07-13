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

This command sets the default draw size (as a percentage) for the visual note chip associated with sound ID `xx`. It does not affect the sound itself, only its appearance on the screen.

*   **Syntax**: `#SIZExx: <percentage>`
*   **Example**: `#SIZE01: 70` (Sets the note chip for WAV `01` to be drawn at 70% of its normal size)

## Inline Variants

For convenience, the guide also specifies inline versions of these commands, which combine the declaration and property setting into a single line.

*   `#WAVVOLxx: <volume>`
*   `#WAVPANxx: <pan>`

---

### Related

*   [[🎵 Simfile Parsing MOC]]
*   [[Resource Mapping]]
*   [[�� Audio System MOC]] 