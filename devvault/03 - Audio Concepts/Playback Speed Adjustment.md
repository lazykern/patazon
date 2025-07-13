# Playback Speed Adjustment

Tags: #concept #audio #gameplay #feature

A standard feature in modern rhythm games is the ability for the player to adjust the playback speed of a song. This is not to be confused with [[Note Rendering and Scrolling|Scroll Speed]], which is a purely visual change. Playback speed adjustment changes the actual tempo of the audio and the entire simulation.

---

## How It Works

Adjusting playback speed requires two components of the engine to work in tandem: the [[🔊 Audio System MOC|audio engine]] and the [[🎮 Gameplay Engine MOC|gameplay engine]].

### Audio Pitch and Tempo

When the user sets the speed to, for example, 1.2x, the audio engine must:
1.  **Adjust Tempo**: Play all audio samples (including BGM and note sounds) 20% faster.
2.  **Correct Pitch**: Crucially, speeding up an audio sample also raises its pitch. A good audio engine uses a pitch-shifting algorithm (often built into libraries like BASS or FMOD) to counteract this effect, preserving the original key of the song. Without pitch correction, the music would sound like "chipmunks" at higher speeds.

### Note Scheduling

The gameplay engine must also adjust its timing. If the song is playing 20% faster, the timestamps for all notes must be scaled accordingly.

*   `adjustedTimestamp = originalTimestamp / playbackSpeed`

A note originally scheduled for `10000ms` would be rescheduled to `10000 / 1.2 = 8333ms`.

The [[Master Audio Clock]] itself is not changed; it continues to report the "real" time that has passed. It is the scheduled times of the events themselves that are modified. This ensures that the notes remain perfectly synchronized with the faster audio.

## Use Cases

*   **Practice**: Players can slow down a difficult song to learn complex patterns.
*   **Accessibility**: Allows players to adjust the game's physical demands to their comfort level.
*   **Challenge**: Advanced players might speed up easy songs for an extra challenge.

---

### Related

*   [[🔊 Audio System MOC]]
*   [[Note Rendering and Scrolling]]
*   [[Master Audio Clock]] 