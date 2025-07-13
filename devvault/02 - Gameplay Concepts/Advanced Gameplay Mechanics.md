# Advanced Gameplay Mechanics

Tags: #concept #gameplay #mechanic

Beyond the core loop of hitting notes, many rhythm games feature advanced mechanics that add depth and variety to the gameplay experience. These are often implemented as toggles or modifiers that the player can select.

---

## Auto-Play

Auto-play is a mode where the game plays the notes automatically. This is an essential feature for:

*   **Demonstrations**: Showing how a chart is meant to be played.
*   **Debugging**: Verifying that [[Channel Data]] is being parsed and timed correctly by the [[Master Audio Clock]] without requiring perfect player input.
*   **Background Animations**: Allowing players to watch complex [[BGA and BGI Channels|BGAs]] without the distraction of playing.

In this mode, the [[Judgment System]] is bypassed, and every note is treated as a "Perfect."

## Lane Modifiers

These modifiers change how notes appear on the screen.

*   **Hidden**: Notes become invisible partway down the screen.
*   **Sudden**: Notes appear suddenly just before the judgment line.
*   **Mirror**: The note chart is flipped horizontally.
*   **Random**: The lanes for notes are randomized, but their timing remains the same.
*   **Hyper-Random/Super-Random**: More complex randomization that can shuffle notes even within a single chord.

## Advanced Note Types

A robust engine's data structures should support more than simple taps.
*   **Long Notes (Sustains)**: Notes that must be held down, requiring the engine to track both a "note on" and a "note off" event. These are defined by special channels (`2C`, `AD`) in the simfile.
*   **Wailing Bonus**: A special effect, typically in guitar modes, triggered by a specific channel (`28`, `A8`). When active, the player can shake the guitar's whammy bar for bonus points.
*   **Special Effect Notes**: A broader category for any note that triggers a unique visual or scoring effect.
*   **Complex Hits**: Notes that require a special input beyond a simple tap, such as hitting an "Open" note in a guitar game without holding any frets.

## Granular Auto-Play

For practice and testing, a simple on/off auto-play is insufficient. A powerful engine allows **individual control over every lane**. A player should be able to set the Hi-Hat and Snare to auto-play while they practice a difficult kick drum pattern.

## Dynamic Scroll Speed

This is a quality-of-life feature where the player can change the [[Note Rendering and Scrolling|scroll speed]] *during* a song, usually via a key combination. This allows them to fine-tune the readability of the chart on the fly without having to restart.

## Hi-Hat Choking

This is a drumming-specific mechanic. If an Open Hi-Hat note is followed closely by a Closed Hi-Hat note, the sound of the open hi-hat should be cut off ("choked"). This is a critical detail for realistic drum simulation and is handled by the [[Hi-Hat Choking|audio engine]].

---

### Related

*   [[🎮 Gameplay Engine MOC]]
*   [[Scoring System]]
*   [[Hi-Hat Choking]]
