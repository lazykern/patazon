# Polyphony

Tags: #concept #audio #resources

Polyphony refers to the number of simultaneous sounds (or "voices") that an audio engine can play at once. In a dense drum chart, hundreds of notes might be triggered in a short period, and managing this is critical to prevent audio distortion and high CPU usage.

---

## The Polyphony Limit: Per-Sample Voice Pools

A key architectural detail from the developer guides is that polyphony is **not a global limit**, but a **per-sample limit**.

This means that each individual sound file loaded from a `#WAVxx` definition gets its own independent pool of voices. For example:
*   `kick.wav` (`#WAV01`) gets its own pool of 8 voices.
*   `snare.wav` (`#WAV02`) gets its own pool of 8 voices.

A rapid sequence of kick drum hits will only ever consume voices from the `kick.wav` pool, and will never "steal" a voice from the snare or cymbal pools. This is critical for ensuring that important sounds are not accidentally cut off by other, less important sounds.

When a request comes in to play a sound:
1. The engine looks at the specific sound requested (e.g., `kick.wav`).
2. It checks the voice pool associated *only with that sound*.
3. If a voice is available, it plays the sound.
4. If all voices in that specific pool are busy, a voice-stealing logic is enacted, typically "steal oldest". The engine finds the instance of `kick.wav` that started playing the longest time ago, stops it, and uses that voice for the new hit.

A simplified version of this logic, as seen in the original DTXMania source, is a simple round-robin assignment. This approach is less robust than true "steal oldest" but is fundamental to replicating the original engine's behavior:
```csharp
// Pseudocode for picking the next voice clone
int voice_index = (sound.last_played_voice + 1) % sound.total_voices;
CSound voiceToPlay = sound.clones[voice_index];
voiceToPlay.Play(); // This may cut off the sound previously using this voice
sound.last_played_voice = voice_index;
```

This per-sample approach is fundamental to replicating the audio behavior of the DTXMania engine.

## Why It's Necessary

1.  **Performance**: Mixing a huge number of sounds is computationally expensive. Limiting polyphony keeps the CPU load on the audio thread predictable and stable.
2.  **Clarity**: Playing the same sample over itself hundreds of times can lead to a muddy, distorted sound. Limiting the voices keeps the mix clean.
3.  **Realism**: Real-world instruments have natural polyphony limits. A drummer can't hit the same cymbal 100 times in a second.

The `CSoundManager` is typically responsible for tracking the number of active instances of each sound and enforcing these polyphony rules.

---

### Related

*   [[🔊 Audio System MOC]]
*   [[Sound Asset Lifecycle]]
