# 🔊 Audio System MOC

Tags: #moc #audio

This Map of Content (MOC) details the architecture and mechanics of the audio engine, a critical component for any rhythm game. Low-latency, precisely timed audio is essential for a good player experience.

---

## Core Architecture

*   **[[Core Audio Architecture]]**: A high-level overview of the main components of the sound system, including the device layer and the management layer.
*   **[[Master Audio Clock]]**: The heart of the entire engine. This note explains how a single, high-precision timer drives game time.
*   **[[Sound Asset Lifecycle]]**: How sound assets are loaded, managed in memory, and released.

## Playback and Timing

*   **[[Mixing and the Rendering Pipeline]]**: How individual sounds are combined into a final audio stream that is sent to the speakers.
*   **[[Timing and Scheduling]]**: The process of scheduling sounds to be played at precise future timestamps, which is key to synchronization.
*   **[[Polyphony]]**: The system for managing multiple simultaneous sounds to prevent audio clutter and control resource usage.
*   **[[Hi-Hat Choking]]**: A crucial, drumming-specific audio mechanic for realistic hi-hat sounds.
*   **[[Playback Speed Adjustment]]**: The mechanics of changing song tempo while keeping audio pitch-corrected and notes in sync.

---

## Related Systems

*   **[[🎵 Simfile Parsing MOC]]**: Provides the audio assets and the timestamps for when they should be played.
*   **[[🎮 Gameplay Engine MOC]]**: Triggers sounds in response to player actions and game events.
