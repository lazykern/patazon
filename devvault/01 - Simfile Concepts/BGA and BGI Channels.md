# BGA and BGI Channels

Tags: #concept #simfile #video

BGA (Background Animation) and BGI (Background Image) are systems in DTX for displaying visuals that are synchronized with the music. They use dedicated [[Channel Data|channels]] to trigger images defined in the [[Resource Mapping|resource map]].

---

## BGA (Background Animation)

BGA refers to video clips that play during the song. In the DTX format, this is often simulated by sequencing a series of still images.

*   **Channel `04` (BGA Base)**: This is the primary layer for background animations.
*   **Channel `07` (BGA Layer)**: An additional layer for more complex, secondary animations.
*   **Channels `55`-`59` and `60` (BGA Layers 3-8)**: The specification supports up to eight layers of BGA, allowing for highly detailed visual sequences.
*   **Channel `54` (AVI)**: Triggers playback of a video clip mapped to an `#AVIxx` resource.
*   **Channel `5A` (MovieFull)**: Similar to channel `54`, but designates the video to be played in fullscreen.
*   **Channels `C4`, `C7`, `D5`-`DF` (Layer Swapping)**: These special channels allow for dynamic effects by swapping the render order and visibility of the BGA layers.

When a parser encounters an object ID in one of these channels, it instructs the rendering engine to display the corresponding image or video file. The timing is determined by the object's position within the measure's data string.

### Example

Here is how a video is defined and then triggered in a `.dtx` file.

**Resource Definition (in header):**
```dtx
#AVI01: Toe - Goodbye.mp4
```

**Channel Data (in body):**
```dtx
#00354: 01
```

In this example, the resource `01` is mapped to a video file. Then, in measure #003, channel `54` (the AVI channel) has a single event triggering object `01`. This tells the engine to start playing `Toe - Goodbye.mp4` at the beginning of measure 3. *(Note: The example `goodbye-mas.dtx` defines the AVI but does not use channel 54; this is a constructed example for illustration.)*

## BGI (Background Image) and Miss Animations

Originally, some specifications designated channels for static background images or miss animations.

*   **Channel `06` (Miss Animation)**: In modern parsers, this channel is typically considered unused. It was originally intended to trigger an animation when the player missed a note.
*   **Static Backgrounds**: Static, non-animated backgrounds for the entire song are handled by the `#STAGEFILE` command in the header, not by a channel.

## Implementation Notes

A robust engine needs a rendering layer capable of managing multiple visual layers simultaneously. The parser feeds this layer with timed events, just like it feeds the audio engine.

*   The engine must handle loading and unloading of image assets efficiently to avoid performance issues.
*   Transitions between images (e.g., fades) are typically handled by the engine itself, not the simfile format.

---

### Related

*   [[🎵 Simfile Parsing MOC]]
*   [[Channel Data]]
*   [[Resource Mapping]]
