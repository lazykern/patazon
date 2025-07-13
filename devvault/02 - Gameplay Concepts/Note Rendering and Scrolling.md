# Note Rendering and Scrolling

Tags: #concept #gameplay #rendering

Once the [[Simfile Parsing Strategy|parser]] has created a list of timed events, the gameplay engine must translate this data into the familiar scrolling notes on the screen. This process involves continuous calculations based on the song's tempo and the game's master clock.

---

## The Note Highway

The "note highway" or "lane" is the area where notes appear and travel towards the judgment line. The engine's rendering logic is responsible for drawing this highway and the notes within it each frame.

## Calculating Note Position

The position of a note at any given moment is a function of:

1.  **The Note's Timestamp**: The precise time (in milliseconds) when the note is meant to be hit.
2.  **The Current Song Time**: The current position of the [[Master Audio Clock]].
3.  **Scroll Speed**: A multiplier that determines how fast notes travel. This is often a configurable setting for the player.

For each active note (a note that is currently visible on screen), the calculation is typically:

```csharp
// The user's setting, e.g., 2.5x
float scrollSpeedMultiplier = userConfig.ScrollSpeed; 

// Convert the multiplier into a concrete pixel velocity
// This constant is something you tune for your game's resolution
const float BASE_PIXELS_PER_MILLISECOND = 0.5f; 
float pixelsPerMs = BASE_PIXELS_PER_MILLISECOND * scrollSpeedMultiplier;

long timeDifference = note.timestamp - masterClock.currentTime;
float positionY = judgmentLineY + (timeDifference * pixelsPerMs);
```

This calculation is performed for every visible note, every single frame, in the `tUpdateAndDraw()` method of the gameplay stage.

## Culling and Optimization

To maintain performance, the engine doesn't draw every note in the song at all times. It only renders notes that are within a certain time window of the current song time. This is known as culling.

*   A note is "activated" when it's a few seconds away from its hit time.
*   It is "deactivated" and removed from the active rendering list after it has been hit or missed.

This ensures that the rendering loop only processes a small subset of the total notes in the chart at any given time.

---

### Related

*   [[🎮 Gameplay Engine MOC]]
*   [[Master Audio Clock]]
*   [[Judgment System]]
