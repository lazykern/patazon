# Input Handling

Tags: #concept #gameplay #input

Input handling is the bridge between the player's physical actions and the game's logic. The engine needs a low-latency system to detect when a drum pad is hit and associate that input with a note on the screen.

---

## Input Sources

A robust engine supports multiple input devices:

*   **Keyboard**: Mapping keyboard keys to different drum pads.
*   **MIDI Devices**: Electronic drum kits often send signals as MIDI events.
*   **DirectInput/XInput**: Standard APIs for game controllers and other peripherals.

## The Input Pipeline

1.  **Polling**: Every frame, the engine polls the state of all configured input devices.
2.  **Event Generation**: When a change is detected (e.g., a key is pressed, a MIDI signal arrives), the engine creates an `InputEvent` object.
3.  **Timestamping**: This is the most critical step. The `InputEvent` is timestamped with the current time from the [[Master Audio Clock]]. This precise timestamp is what allows the [[Judgment System]] to determine accuracy.
4.  **Queueing**: The timestamped event is placed into an input queue.

## Processing Inputs

In the main gameplay loop (`tUpdateAndDraw()`), the [[Judgment System]] reads from this input queue. For each input event, it checks if there are any active notes on the corresponding lane that are within the timing windows.

This separation of concerns—capturing input in one thread/subsystem and processing it in another—is key to building a responsive and accurate rhythm game.

---

### Related

*   [[🎮 Gameplay Engine MOC]]
*   [[Judgment System]]
*   [[Master Audio Clock]]
