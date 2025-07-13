# Mixing and the Rendering Pipeline

Tags: #concept #audio #implementation

The mixing pipeline is where all active sounds in the game are combined into a single stereo audio stream to be sent to the speakers. This process happens in real-time, every few milliseconds, in a tight, performance-critical loop.

---

## The Mixer's Role

The mixer is a central component, often part of the [[Core Audio Architecture|device layer]]. Its job is to:

1.  **Request Audio Data**: Ask the `CSoundManager` for a block of audio samples (e.g., the next 10ms worth of sound).
2.  **Iterate Active Sounds**: The `CSoundManager` keeps a list of all sounds that are currently playing. The mixer iterates through this list.
3.  **Sum Samples**: For each active sound, the mixer reads the next block of samples from its buffer, adjusts its volume, and adds it to a master buffer.
4.  **Clipping Prevention**: After summing all the sounds, the mixer must ensure the final signal does not exceed the maximum amplitude (a phenomenon that causes a harsh distortion called clipping).
5.  **Provide to Device**: The final, mixed buffer is handed to the `ISoundDevice`, which sends it to the hardware.

## The Rendering Callback

This process is typically driven by a callback mechanism. The `ISoundDevice` (e.g., ASIO or WASAPI) will periodically say, "I need more audio data." This triggers the mixer to run its pipeline and produce the next block of sound.

This callback-driven model is highly efficient and is the standard architecture for high-performance audio applications. It ensures that the sound card is never starved for data, which would result in audible clicks or dropouts.

---

## Hierarchical Mixing for Volume Control

While a single master mixer works, a more flexible architecture, as suggested by the developer guides, uses a **hierarchical mixing model**. This is essential for allowing independent volume control (e.g., letting the user turn down the drum sounds but keep the background music loud).

The structure looks like this:

```
Individual Drum Sound ┐
                     ├─► Drums Sub-Mixer ──┐
Individual Drum Sound ┘                     |
                                            ├─► Root Mixer ──► Master Volume
BGM Track ───────────► BGM Sub-Mixer ───────┘
                                            |
Sound Effect ────────► SE Sub-Mixer ────────┘
```

In this model:
1.  When a sound is created, it's assigned a category (e.g., `Drums`, `BGM`, `SE`).
2.  The engine maintains separate "sub-mixer" buses for each category.
3.  When a sound is played, it's routed to the appropriate sub-mixer.
4.  Each sub-mixer has its own volume control, which can be exposed in the game's options menu.
5.  All sub-mixers are then combined in a final "root" or "master" mixer before being sent to the device.

This architecture provides critical flexibility for the end-user and is a hallmark of a feature-rich audio engine.

---

### Related

*   [[🔊 Audio System MOC]]
*   [[Core Audio Architecture]]
*   [[Timing and Scheduling]]
