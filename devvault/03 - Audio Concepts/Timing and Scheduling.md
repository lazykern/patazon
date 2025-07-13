# Timing and Scheduling

Tags: #concept #audio #timing

While some sounds are played immediately in response to player input, many others—especially background music and auto-played chip notes—must be scheduled to play at precise moments in the future. This is the responsibility of the audio engine's scheduling system.

---

## The Need for Scheduling

When the [[Simfile Parsing Strategy|parser]] processes the simfile, it generates a list of events, each with a precise timestamp. For example, it might determine that a specific BGM sample needs to play at `t=30.542` seconds.

It is not feasible to simply wait until the [[Master Audio Clock]] reaches that time and then try to play the sound. This approach is prone to stutter and inaccuracy due to thread scheduling latency in the OS.

## The Scheduling Process

A better approach is to pre-schedule the sound.

1.  **Event Creation**: During the [[Simfile Parsing Strategy|parsing stage]], the engine converts every note's position into a precise, absolute millisecond timestamp.
    *   **The Grid**: A DTX measure is represented by a high-resolution grid. DTXMania internally converts every measure into **384 ticks**.
    *   **Ticks to Milliseconds**: The parser calculates the timestamp for each note using a formula like:
        `PlayTimeMS = TimeAtStartOfBarMS + (TickWithinBar / 384.0) * MillisecondsPerBar`
        (Where `MillisecondsPerBar` is derived from the current BPM and measure length).
2.  **Submit to Engine**: This event (e.g., `Play sound 'bgm_sample_3' at 30542ms`) is submitted to the `CSoundManager`.
3.  **Queueing**: The `CSoundManager` places the event in a time-ordered queue.
4.  **Real-time Check**: In the audio rendering callback (the same loop that drives the [[Mixing and the Rendering Pipeline|mixer]]), the engine checks the queue. It looks for any scheduled events whose timestamp falls within the small time slice of the audio buffer it is currently rendering.
5.  **Activation**: If a scheduled event's time has arrived, the sound is moved from the queue to the list of currently playing sounds, and the mixer begins including it in the audio output.

This ensures that sounds start playing with sample-accurate timing, perfectly synchronized to the [[Master Audio Clock]].

---

### Related

*   [[🔊 Audio System MOC]]
*   [[Master Audio Clock]]
*   [[Mixing and the Rendering Pipeline]]
