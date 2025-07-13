# Hi-Hat Choking

Tags: #concept #audio #mechanic #drumming

Hi-hat choking is a fundamental technique in real drumming and a critical feature for a realistic drum simulator. It refers to the action of an open hi-hat sound being abruptly silenced (choked) by a subsequent closed hi-hat or foot pedal hi-hat hit.

---

## The Mechanic

In a real drum kit, the open and closed hi-hats are the same physical object. You cannot have both an open and closed sound playing at the same time. The DTX format and engine must simulate this behavior.

*   **Open Hi-Hat (Channel `18`)**: When an open hi-hat note is triggered, its sound begins to play, and it will have a natural, long decay.
*   **Closed Hi-Hat (Channel `11`)**: If a closed hi-hat note is triggered while the open hi-hat sound is still playing, the engine must immediately stop the open hi-hat sound.
*   **Foot Pedal (Channel `1B`)**: The foot pedal also chokes the open hi-hat.

## Implementation

This requires coordination between the [[🎮 Gameplay Engine MOC|gameplay logic]] and the [[🔊 Audio System MOC|audio engine]].

1.  **Grouping**: The `CSoundManager` needs a way to group sounds. The Open Hi-Hat, Closed Hi-Hat, and Foot Pedal sounds should all belong to the same "choke group" or "voice group."
2.  **Playback Logic**: When the `CSoundManager` receives a request to play a sound, it checks if that sound belongs to a choke group.
3.  **Choke Check**: If it does, the manager iterates through all other currently playing sounds. If it finds another sound from the same choke group, it immediately stops it before starting the new sound.

This ensures that only one sound from the hi-hat group can be playing at any given time, accurately simulating the behavior of a real hi-hat.

---

### Related

*   [[🔊 Audio System MOC]]
*   [[Advanced Gameplay Mechanics]]
