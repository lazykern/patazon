# Sound Asset Lifecycle

Tags: #concept #audio #resources

Efficiently managing sound assets is crucial for performance and preventing audio glitches. The sound asset lifecycle covers the process from loading a sound off the disk to releasing it from memory.

---

## 1. Creation and Loading

When the [[Simfile Parsing Strategy|parser]] encounters a `#WAVxx` definition in the simfile header, it instructs the `CSoundManager` to create a sound object.

1.  **Path Resolution**: The manager resolves the relative file path from the simfile.
2.  **Loading**: The sound file (e.g., a `.wav` or `.ogg` file) is read from disk.
3.  **Decoding**: The compressed audio data is decoded into a raw PCM audio buffer.
4.  **Storage**: The decoded buffer is stored in memory (RAM). For very large files like background music, the engine might use streaming instead, where only small chunks are loaded into memory at a time.
5.  **Registration**: The newly created sound object is registered with the `CSoundManager`, associated with its original hex ID from the simfile.

## 2. Instantiation (Preparing for Polyphony)

A single sound asset (like `snare.wav`) is just the raw data. To play it multiple times in quick succession, the engine creates several playable **clones** or "voices" of it.

*   This is the foundation of the [[Polyphony]] system.
*   The number of clones is often configurable (e.g., 4-8 voices per sound).
*   When a request to play the sound comes in, the engine picks one of these clones to play on, leaving the others free to be used for subsequent hits.

## 3. Playback

When a note is hit or a BGM event occurs, the game logic tells the `CSoundManager` to play the sound associated with a specific ID. The manager finds the corresponding sound object and tells the [[Mixing and the Rendering Pipeline|mixer]] to start reading samples from the buffer of one of its instantiated clones.

## 4. Release

When a sound is no longer needed (e.g., when the gameplay stage is deactivated), its resources—both the original decoded buffer and all its clones—must be released to free up memory.

*   The `CSoundManager` receives a command to release the sound.
*   The PCM buffer in memory is deallocated.
*   The sound object is removed from the manager's registry.

This is typically handled by the [[Game State Machine|stage's]] `OnDeactivate()` or `OnManagedReleaseResources()` methods, ensuring that memory usage is cleaned up between songs.

---

### Related

*   [[🔊 Audio System MOC]]
*   [[Core Audio Architecture]]
*   [[Polyphony]]
*   [[CSoundManager]]
