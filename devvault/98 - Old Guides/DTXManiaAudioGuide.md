# DTXMania Audio System & Mechanics: A Guide for Rhythm Game Developers

This document deconstructs the sound engine of DTXmaniaNX to provide a blueprint for developers who wish to parse `.dtx` simfiles and replicate their intricate drumming mechanics in a custom rhythm game engine.

The goal is to answer the question: **"What do I need to know to build an audio system that can play DTX drum charts correctly?"**

---

## 1. Core Audio Engine Architecture

At its heart, the DTXMania engine is built for **low-latency, high-precision audio scheduling**. It uses a layered architecture to achieve this.

*   **`CSoundManager` (The Conductor)**: This is the top-level singleton that manages all audio operations. Your engine will need a similar central class to handle sound loading, playback requests, and global settings.

*   **`ISoundDevice` (The Abstraction Layer)**: The manager speaks to an audio device through a common interface. DTXMania ships with three implementations:
    *   `CSoundDeviceWASAPI` (Modern Windows Audio)
    *   `CSoundDeviceASIO` (Low-latency Professional Audio)
    *   `CSoundDeviceDirectSound` (Legacy Windows Audio)
    
    For a new game, targeting a modern low-latency API like WASAPI, CoreAudio (macOS), or Oboe (Android) is recommended. The key is that the device must provide a stable, high-resolution **audio clock**.

*   **BASS (The Low-Level Library)**: DTXMania delegates the difficult tasks of audio decoding, device management, and mixing to the BASS audio library. Using a mature third-party library like BASS, FMOD, or SoLoud is highly advisable.

*   **`CSoundTimer` (The Master Clock)**: The most critical component for synchronization. This is a high-resolution timer (often a busy-wait loop in a dedicated thread) that provides a monotonic "music time" in milliseconds. All on-screen animations and note-triggering logic are synced to this single clock, ensuring that what you see and what you hear are perfectly aligned.

---

## 2. Sound Asset Lifecycle: From File to Playable Voice

A "sound" in DTXMania goes through several stages before it can be played.

1.  **Declaration (in the `.dtx` file)**: The simfile author maps a two-character hexadecimal ID to a sound file.
    ```
    #WAV01: kick.wav
    #WAV02: snare.wav
    ```

2.  **Loading (at Song Load Time)**: Your parser reads these `#WAVxx` tags. For each entry, it should:
    *   Locate the specified audio file (e.g., `kick.wav`).
    *   Use an audio library (like BASS) to decode the file (WAV, OGG, MP3) into a raw PCM audio buffer in memory.
    *   Wrap this buffer in a "sound object" (equivalent to `CSound`). This object holds the audio data and properties like its original sample rate.
    *   Store these sound objects in a map, keyed by their hex ID (e.g., `01`, `02`). `CDTX.listWAV` serves this purpose.

    > **A Note on Data vs. Logic:** It's helpful to understand that the `CDTX` class is primarily a parser and a container for the song's data structure. The real-time logic described in the following sections (e.g., the "Play Loop") is handled by other parts of the application that *use* the `CDTX` object, typically in classes responsible for the gameplay screen (`CStage演奏...`).

3.  **Instantiation (Preparing for Polyphony)**: A single drum pad can be hit many times in quick succession. To handle this, the engine doesn't use the original loaded sound object directly. Instead, it creates multiple **clones** or "voices" for it. This is the foundation of polyphony.
    *   The number of clones is configurable (`nPolyphonicSounds` in `Config.ini`, defaulting to 4).
    *   The `CWAV` class holds an array `CSound[] rSound` for these clones. When a note is triggered, one of these clones is picked to be played.

---

## 3. The Mixing Pipeline: From Individual Hits to Master Output

A single drum hit is just one of many sounds playing simultaneously. The engine uses a multi-stage mixing architecture to manage this.

```
Individual Sound Voice (CSound) ┐
                                ├─► Instrument Sub-Mixer (e.g., Drums) ──┐
Individual Sound Voice (CSound) ┘                                         |
                                                                          ├─► Root Mixer
BGM Track (CSound) ─────────────► Instrument Sub-Mixer (BGM) ────────────┘
                                                                          |
Sound Effect (CSound) ──────────► Instrument Sub-Mixer (SE) ─────────────┘
                                                                          |
                                                                          ▼
                                                                    Master Mixer
                                                                          |
                                                                          ▼
                                                                    Audio Device
```

**Why is this important?** This hierarchy allows for independent volume control. The user can adjust the volume of the "Drums" separately from the "BGM" in the options menu.

*   **Your Implementation**:
    1.  When you create a sound, tag it with a category (`enum EInstType`: `Drums`, `Guitar`, `Bass`, `BGM`, `SE`).
    2.  Create mixer channels/buses for each category.
    3.  When a sound is played, route it to the appropriate category mixer.
    4.  Route all category mixers into a single root mixer.
    5.  The root mixer's volume is your "Master Volume".

---

## 4. Timing and Scheduling: The Heart of the Rhythm Game

This is where the magic happens. A rhythm game is fundamentally about playing the right sound at the right time.

1.  **The Grid**: A `.dtx` file is a grid. A bar is divided into a high-resolution number of "ticks" (DTXMania uses 384). A note is defined by its channel (which pad to hit) and its position on this tick grid.

2.  **From Ticks to Milliseconds**: Your parser must walk this grid and convert every note's tick position into an absolute millisecond timestamp.
    *   The formula is: `PlayTimeMS = TimeAtStartOfBarMS + (TickWithinBar / TicksPerBar) * MillisecondsPerBar`
    *   `MillisecondsPerBar` is calculated from the current BPM (`60000.0 / BPM`) and the bar's length multiplier (from channel `02`).
    *   Store this `PlayTimeMS` value with every single note/chip object.

4.  **Auto-Played Sounds (BGM)**: Note that not all chips in a DTX file are meant to be hit by the player. The format includes specific channels for sounds that should be played automatically by the engine, most importantly the main Background Music track (channel `#01`). Your engine must identify these chips and schedule them for playback without requiring user input.

5.  **The Play Loop**: In your game's main update loop:
    *   Get the current `MusicTimeMS` from your master audio clock.
    *   Iterate through your list of upcoming notes (both playable and automatic).
    *   If `note.PlayTimeMS <= MusicTimeMS`, it's time to play the sound. Trigger the audio playback for that note and mark it as "played".

---

## 5. Essential Drumming Mechanics for DTX Compatibility

To make drum charts feel right, your audio engine **must** implement these mechanics.

### Polyphony

*   **Problem**: A fast snare roll will trigger the same `snare.wav` sample many times before the first hit has finished playing. If you just restart the sample each time, it will sound robotic and cut off.
*   **DTXMania's Solution**: As described in Section 2, each individual WAV has multiple `CSound` clones. This is a **per-sample limit**, not a global one. If `#WAV01` is a kick and `#WAV02` is a snare, each gets its own independent pool of voices. When a note is triggered, the engine picks the next available clone for that *specific sound* in a round-robin fashion.
    ```csharp
    // Simplified logic from CDTX.cs
    int voice_index = (wav.currentlyPlayingVoice + 1) % wav.numberOfVoices;
    CSound voiceToPlay = wav.sound_clones[voice_index];
    voiceToPlay.Play();
    wav.currentlyPlayingVoice = voice_index;
    ```
*   **Your Implementation**: For each loaded sound sample, create a pool of playable "voice" objects. When a hit occurs, find an idle voice in the pool, assign the sample to it, and play it. If no voices are idle, either steal the oldest one or, if your polyphony limit is high enough, this may not be an issue.

    > **Note on DTXMania's Specific Implementation:** The logic described above is a robust, ideal implementation. The actual code in `CDTX.cs` is simpler: when a sound is triggered, it checks the next voice in its sequence. If that voice is busy, it simply advances to the next one and plays it *immediately*, potentially cutting off that sound if the polyphony setting (`nPolyphonicSounds`) is too low for a very dense passage. For 100% faithful replication, this simpler (and slightly less robust) logic is what you would implement.

### Choke Groups (Hi-Hat Muting) - CRITICAL

*   **Problem**: On a real drum kit, hitting the hi-hat pedal to close the cymbals (`Closed Hi-Hat`) instantly stops the ringing sound of an `Open Hi-Hat`. DTX charts are authored with this expectation. Failing to implement this makes many songs sound incorrect and feel unplayable.
*   **DTXMania's Solution**: This is a hard-coded gameplay mechanic. The engine explicitly tracks the state of the hi-hats.
    1.  When a chip on the **Open Hi-Hat channel** (`18`) is played, let its sound ring out.
    2.  When a chip on the **Closed Hi-Hat channel** (`11`) or **Hi-Hat Pedal channel** (`1B`) is played:
        *   **First, immediately find and stop all currently playing Open Hi-Hat sounds.**
        *   Then, play the new Closed Hi-Hat/Pedal sound.
*   **Your Implementation**: You need to create an "exclusive group" or "choke group".
    1.  When playing a sound, check if it belongs to a group that can be "choked" (e.g., Open Hi-Hat).
    2.  When playing a sound that "chokes" another group (e.g., Closed Hi-Hat), iterate through all active voices and immediately stop any that belong to the target group.

---

## 6. Developer's Checklist for DTX Audio Support

To achieve baseline compatibility for playing DTX drum charts, your audio system must support:

*   **[ ] WAV Loading**: Parse `#WAVxx` and load associated sound files.
*   **[ ] Channel Mapping**: Parse the main data grid (`#xxx01: ...`) and map channel numbers (`11`-`1F`, etc.) to their corresponding drum pads.
*   **[ ] Tick-to-MS Conversion**: Accurately calculate the absolute millisecond play time for every note based on `#BPM` changes and bar length (`#02`).
*   **[ ] Master Audio Clock**: A single, high-resolution source of truth for time.
*   **[ ] Polyphony**: A system for playing multiple instances of the same sample concurrently. A pool of at least 4-8 voices per sample is a safe starting point.
*   **[ ] Hi-Hat Choking**: A non-negotiable choke group where playing a sound from the Closed/Pedal Hi-Hat channels immediately stops any playing Open Hi-Hat sounds.
*   **[ ] Volume Control**:
    *   Parse `#VOLUMExx` to set a base volume for each sample.
    *   Implement a master volume control.
    *   (Advanced) Implement per-instrument group mixers (Drums, BGM, etc.).
*   **[ ] Pan Control**: Parse `#PANxx` to set the stereo position of each sample.
*   **[ ] Play Speed Adjustment**: The ability to modify the playback speed of all samples and adjust note scheduling accordingly, as controlled by the user in-game.

By implementing these systems, you will have a robust audio engine capable of faithfully reproducing the core experience of a DTXmania drum chart. 