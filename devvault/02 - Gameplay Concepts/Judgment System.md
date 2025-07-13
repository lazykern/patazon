# Judgment System

Tags: #concept #gameplay #mechanic

The judgment system is the core logic that evaluates the timing of a player's [[Input Handling|input]] against the expected timestamp of a note. Its decision—Perfect, Great, Good, Poor, or Miss—is the primary feedback mechanism for the player.

---

## The Judgment Process

When a player hits a pad, the following process occurs:

1.  **Receive Input**: An input event, timestamped by the [[Master Audio Clock]], is received.
2.  **Find Target Note**: The system looks for the closest, active (not yet hit) note on the corresponding lane.
3.  **Calculate Difference**: It calculates the time difference between the input event's timestamp and the target note's timestamp.
    *   `delta = input.timestamp - note.timestamp`
4.  **Compare to Windows**: The absolute value of `delta` is compared against the [[Default Timing Windows and Configuration|configured timing windows]].
5.  **Assign Judgment**: The system assigns the best possible judgment for which the `delta` qualifies (e.g., if it's within the Perfect window, it's a Perfect).
6.  **Trigger Feedback**: Based on the judgment, the system triggers several events:
    *   Plays a corresponding sound effect (e.g., a cheer for a Perfect).
    *   Displays a judgment animation on screen.
    *   Updates the [[Scoring System]].
    *   Marks the note as "hit" so it cannot be judged again.

## Handling Misses

If a note's timestamp passes the [[Master Audio Clock|current time]] by more than the `Poor` timing window, the note is marked as a `Miss`. This is typically done in a separate check within the main game loop, independent of player input.

A critical rule, emphasized in the developer guides, is that **the engine must play the note's sound anyway**. This is sometimes called the "ghost note" or "autoplay" sound.

Failing to do this makes the game feel broken, as the song's backing track or melody will have noticeable gaps. The engine must play the chip's sound regardless of whether it was a player hit or an auto-played miss to ensure the song remains musically intact. This also affects the [[Groove Gauge]] and [[Scoring System|combo]].

---

### Related

*   [[🎮 Gameplay Engine MOC]]
*   [[Input Handling]]
*   [[Default Timing Windows and Configuration]]
*   [[Scoring System]]
*   [[Master Audio Clock]]
