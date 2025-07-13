# Master Audio Clock

Tags: #concept #audio #timing #architecture

The Master Audio Clock (often an instance of a class like `CSoundTimer`) is the single most important component for synchronization in a rhythm game. It provides a high-precision, monotonically increasing timestamp that represents the current song time. All other systems synchronize to this clock.

---

## Why It's So Important

Standard system clocks or frame-based timing (delta time) are not suitable for a rhythm game due to their lack of precision and susceptibility to drift and stutter. A dedicated audio clock is essential because:

*   **Synchronization**: It ensures that [[Note Rendering and Scrolling|note rendering]], [[Input Handling|input events]], and audio playback are all perfectly aligned. What you see on screen must match what you hear exactly.
*   **Precision**: It is often based on the audio hardware's own clock, providing a much higher resolution (sub-millisecond) than typical system timers.
*   **Resilience**: It is not affected by fluctuations in frame rate. If the game's rendering stutters, the audio and the internal sense of time continue to advance smoothly.

## How It Works

The clock is typically tied to the audio stream itself. The `ISoundDevice` layer, which sends audio buffers to the hardware, can accurately report how much audio has been played. This value is used to update the master clock's current time.

For maximum precision, this timer is often implemented in a dedicated thread that runs in a tight, high-priority loop (a "busy-wait"), constantly updating its value. This prevents the timing source from being affected by the scheduling latencies of the main game thread.

Every other part of the game that needs to know the current time should query this clock:

*   The **[[Gameplay Engine MOC|gameplay engine]]** uses it to calculate note positions.
*   The **[[Input Handling|input system]]** uses it to timestamp player actions.
*   The **[[Judgment System]]** uses it to compare note times and input times.

Without a reliable master clock, creating a fair and accurate rhythm game is impossible.

---

### Related

*   [[🔊 Audio System MOC]]
*   [[Core Audio Architecture]]
*   [[Timing and Scheduling]]
