# Core Audio Architecture

Tags: #concept #audio #architecture

The audio engine in a game like DTXMania is built in layers to separate low-level hardware interaction from high-level game logic. The architecture can be broken down into two main parts: the device layer and the management layer.

---

## 1. The Device Layer (`ISoundDevice`)

This is the lowest level of the audio engine. It is an abstraction layer that communicates directly with the operating system's audio APIs (like WASAPI, ASIO, or DirectSound). Its sole responsibility is to take a raw buffer of audio data and send it to the sound card.

*   **Interface-based Design**: By using an interface (`ISoundDevice`), the engine can support multiple audio backends. The user can choose the one that provides the lowest latency on their system (e.g., `CAsioSoundDevice`, `CWasapiSoundDevice`).
*   **The Mixer**: The device layer gets its data from the [[Mixing and the Rendering Pipeline|mixer]], which combines all active sounds into a single stream.
*   **Low-Level Libraries**: Engines typically do not implement the entire audio stack from scratch. They delegate difficult tasks like audio decoding, device management, and mixing to a mature third-party library like **BASS**, FMOD, or SoLoud.

## 2. The Management Layer (`CSoundManager`)

This is the high-level interface that the rest of the game interacts with. It is responsible for:

*   **Asset Management**: Loading sounds from files and managing them. See [[Sound Asset Lifecycle]].
*   **Playback Control**: Providing simple methods like `PlaySound()` and `StopSound()`.
*   **The Master Clock**: The `CSoundManager` owns or has a reference to the [[Master Audio Clock]], ensuring all game events can be synchronized to the audio timeline.

This layered design is crucial for maintainability. The gameplay code doesn't need to know about ASIO or WASAPI; it just tells the `CSoundManager` what to do, and the manager handles the low-level details.

---

### Related

*   [[🔊 Audio System MOC]]
*   [[Master Audio Clock]]
*   [[Sound Asset Lifecycle]]
*   [[Mixing and the Rendering Pipeline]]
