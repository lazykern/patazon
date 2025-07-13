# Building a Rhythm Game Engine: A Developer's Guide to Gameplay

This document is the third part of a series on building a DTX-compatible rhythm game. It builds directly on the concepts from the **[Simfile Parsing Guide](SimfileParsingGuide.md)** and the **[Audio System Guide](DTXManiaAudioGuide.md)**.

The goal is to answer the question: **"How do I use my parsed note data and loaded sounds to build an interactive game?"**

---

## 1. The Foundation: Game States and the Main Loop

A rhythm game isn't a single, monolithic block of code. It's a series of distinct states or "screens," each with its own logic. In many engines, these are called **Stages** or **Scenes**.

*   **Startup**: The initial loading screen when the game boots.
*   **Title**: The main title screen.
*   **Song Selection**: The screen where the player chooses a song.
*   **Song Loading**: A temporary screen shown while loading the song's assets.
*   **Performance**: The core gameplay screen where the player actually plays.
*   **Result**: The screen showing the player's score after the song.
*   **End**: The "game over" or "see you next time" screen.

### The State Machine

A game engine needs a **state machine** to manage this flow. A simplified main loop looks like this:

```csharp
// In your main game class
Stage currentStage;

void Initialize() {
    currentStage = new TitleStage();
    currentStage.Activate();
}

void GameLoop() {
    while(true) {
        if (currentStage.IsActive()) {
            currentStage.Progress(); // Handle input and logic for this state
            currentStage.Draw();     // Draw the visuals for this state
        }

        if (currentStage.IsFinished()) {
            Stage nextStage = currentStage.GetNextStage();
            currentStage.Deactivate();
            currentStage = nextStage;
            currentStage.Activate();
        }
    }
}
```
Each stage should have methods for activation (setup), deactivation (cleanup), and frame-by-frame processing.

*   **Developer Takeaway**: Don't put all your logic in one place. Structure your game around a state machine. Each state should be a class responsible for its own input, logic, and rendering.

---

## 2. The Core Gameplay Loop: The Performance Stage

This is where the magic happens. The performance stage contains the most critical logic. It runs every frame and is responsible for everything the player sees and does during a song.

### The Holy Trinity: Time, Notes, and Input

Gameplay is an ongoing interaction between three elements:
1.  **The Master Clock**: A single, high-resolution timer that dictates the tempo of the entire simulation. As explained in the Audio Guide, this should come from your audio device for perfect sync. This is the single source of truth for time.
2.  **The Note Chart**: The list of note objects you created by parsing the simfile. Each note has a pre-calculated musical timestamp (e.g., `playTimeMS`).
3.  **Player Input**: Keystrokes or pad hits from the player. The input system should poll devices once per frame and timestamp each event relative to the master clock.

### Step 1: Note Visualization (Scrolling)

How do you make notes scroll down the screen? It's a simple calculation performed every frame.

*   **Scroll Speed**: A user-configurable value (e.g., `2.5x`) that determines how fast notes move. A higher value means notes are more spaced out.
*   **The Formula**: The on-screen position of a note is a function of its musical time relative to the current time.
    ```csharp
    // Get the current time from the master clock
    long currentTimeMS = masterClock.GetCurrentTime();

    // For each note in the chart...
    if (note.IsVisibleOnScreen(currentTimeMS, scrollSpeed)) {
        // Time until the note should be hit
        long timeDifferenceMS = note.playTimeMS - currentTimeMS;
        
        // PIXELS_PER_MS is a constant you derive from scroll speed
        float y_position = JUDGEMENT_LINE_Y - (timeDifferenceMS * PIXELS_PER_MS); 

        DrawNote(note.Lane, y_position);
    }
    ```

### Step 2: Input Handling & The Judgment System

This is the most important part of any rhythm game. When the player hits a pad, you must determine *how accurately* they hit it.

1.  **Get Input Events**: Your input system should provide a list of pre-timestamped events that have occurred since the last frame.

2.  **Find the Target Note**: For the lane that was hit (e.g., Snare), search your list of un-hit notes on that lane to find the one closest to the input event's timestamp.

3.  **Calculate the Delta**: `long diff = inputEvent.timestamp - targetNote.playTimeMS;`

4.  **Apply the Judgment Window**: Compare the absolute value of `diff` against your game's timing windows. These windows are the heart of your game's "feel."

##### Default Timing Windows and Configuration

While you can define any timing windows you like, a crucial feature of a robust engine is making these values **configurable**. In DTXMania, these settings are loaded from a configuration file, allowing users to adjust the game's difficulty.

The default timing windows in DTXMania are as follows:

*   **Perfect**: ±34ms
*   **Great**: ±67ms
*   **Good**: ±84ms
*   **Poor**: ±117ms

Any hit outside the `Poor` window is considered a `Miss`. This information is essential for developers who want to replicate the feel of the original game or provide similar configuration options to their players.
    ```csharp
    // These values define your game's strictness
    const long PERFECT_WINDOW_MS = 22;
    const long GREAT_WINDOW_MS = 50;
    const long GOOD_WINDOW_MS = 100;
    const long POOR_WINDOW_MS = 150;

    EJudgment judgment;
    if (Math.Abs(diff) <= PERFECT_WINDOW_MS) {
        judgment = EJudgment.Perfect;
    } else if (Math.Abs(diff) <= GREAT_WINDOW_MS) {
        judgment = EJudgment.Great;
    } else if (Math.Abs(diff) <= GOOD_WINDOW_MS) {
        judgment = EJudgment.Good;
    } else if (Math.Abs(diff) <= POOR_WINDOW_MS) {
        judgment = EJudgment.Poor; // Hit, but way off.
    } else {
        // The hit was too far away to be considered for any note. Ignore it.
        return;
    }

    // Process this successful hit!
    ProcessHit(judgment, targetNote);
    targetNote.wasHit = true;
    ```
    *Advanced*: These timing windows can be configurable, or even loaded on a per-song basis to match different styles of music.

### Step 3: Handling Misses (The Auto-Play System)

What happens if the player *doesn't* hit a note? The song can't just go silent.

Every frame, in addition to checking for input, you must also check for notes that have scrolled past the judgment line without being hit.

```csharp
// In the main performance loop...
long currentTimeMS = masterClock.GetCurrentTime();

foreach (var note in all_unhit_notes) {
    // If the note is more than POOR_WINDOW_MS past its time, it's a miss.
    if (currentTimeMS > note.playTimeMS + POOR_WINDOW_MS) {
        ProcessMiss(note);
        note.wasHit = true; // Mark it so we don't process it again.

        // CRITICAL: Play the note's sound anyway!
        // This is often called the "autoplay" or "ghost note" sound.
        // This ensures the song's backing track continues.
        audioSystem.Play(note.soundAsset, isAutoplay: true);
    }
}
```
Failure to play sounds for missed notes is a common mistake that makes a game feel broken and empty. The engine must play the chip sound regardless of whether it was a player hit or an auto-played miss.

---

## 3. Scoring, Combos, and Health (The Gauge)

Gameplay needs stakes. These systems provide them.

*   **Scoring & Skill**: While simple point-based systems work, modern rhythm games often use a **skill-based percentage formula**. This calculates a score (e.g., 98.54%) based on a weighted distribution of judgments, where Perfects and the maximum combo are far more valuable than anything else. This percentage can then be used to calculate a "Song Skill" rating based on the song's difficulty level.

*   **Combo**: A counter that increases with every successful hit (`Good` or better). If the player gets a `Miss`, the combo resets to zero. This rewards consistency.

*   **Groove Gauge (Health Bar)**: This is the player's "life." Its behavior can be made highly configurable to create different gameplay modes:
    *   **Damage Level**: A setting can control how much the gauge decreases on a `Poor` or `Miss`, from lenient to punishing.
    *   **Sudden Death Modes**: A "Risky" or "Hazard" mode can be implemented where the player fails after a set number of misses (e.g., 1-10 misses and you're out).
    *   **Training Features**: An "auto-add gauge" feature can be added to prevent failure, which is useful for practice.
    *   Typically, if the gauge reaches 0%, the player fails the song. If it's above a certain threshold (e.g., 80%) at the end, the player "clears" it.

---

## 4. Advanced Gameplay Mechanics

A robust engine supports features beyond a basic tap-and-score loop.

### Advanced Note Types
Your note data structure should be flexible enough to represent more than just simple taps:
*   **Long Notes (Sustains)**: A note that must be held down, requiring tracking of both a "note on" and a "note off" event.
*   **Special Effect Notes**: Notes that trigger a visual or scoring bonus, like a "Wailing" effect in a guitar game.
*   **Complex Hits**: Notes that require a special input, like an "Open" note hit without holding any frets.

### Lane Modifiers
To add variety and replayability, an engine can alter the note chart in real-time.
*   **Mirror/Random**: These modes shuffle which physical input corresponds to which lane on the screen.
*   **Hyper-Random/Super-Random**: More complex randomization that can shuffle notes within a single chord, completely changing the feel of a pattern.

### Granular Auto-Play
For testing or practice, an auto-play system shouldn't be a single on/off switch. A powerful engine allows individual control over every lane (each drum pad, cymbal, guitar/bass fret, etc.), so a player can practice one part while the computer handles the rest.

### Dynamic Scroll Speed
A quality-of-life feature where the player can change the note scroll speed *during* a song, allowing them to fine-tune readability on the fly.

---

## 5. The Graphics and Audio Engine: Theory

### Skinning and Theming
The entire UI should be skinnable. A **Skinning System** allows artists to completely change the look and feel of the game without touching the code. It works by abstracting asset loading: instead of hard-coding `"images/judgement.png"`, the code asks the skinning system for the `"judgement"` texture, which then finds the correct file in the currently active skin folder.
*Advanced*: The system can support both a global, user-selected skin and a per-song-folder skin, allowing chart creators to provide a custom look for their song pack.

### Resource Lifecycle
To prevent memory leaks and handle graphics device resets (e.g., when a user toggles fullscreen), an engine needs a robust resource management system. A common pattern is to distinguish between two types of resources:
*   **Managed Resources**: Graphics-memory-specific assets like textures, which are lost when the device resets and must be re-created.
*   **Unmanaged Resources**: System-memory assets like loaded sound data or parsed song files, which survive a device reset.

### Performance Tuning
*   **GPU Synchronization**: Modern operating systems can introduce a frame or two of rendering latency. To combat this, an engine might use advanced techniques to force the CPU and GPU to synchronize every frame, ensuring rendering commands are sent to the hardware immediately. This is critical for reducing perceived input lag.
*   **Low-Latency Audio Backend**: To minimize audio latency, an engine should ideally support low-level audio APIs like ASIO (on Windows) or WASAPI in exclusive mode. These bypass the OS mixer and provide a more direct path to the audio hardware.

---

## 6. Beyond Gameplay: Engine Architecture Theory

### The Song Database
Loading song information from thousands of simfiles on startup is too slow. A high-performance engine uses a **metadata cache**.
1.  On first run, the engine scans all song folders and builds a data structure (often a tree) representing the library.
2.  It then saves all the essential metadata (Title, BPM, Level, etc.) into a single, fast-loading binary file (a "song database").
3.  On subsequent startups, it loads this database instantly and only scans for new or changed files to update the cache.
4.  Performance history, high scores, and other per-song user data are typically stored in separate, small files alongside the originals.

### Plugin Architecture
A powerful engine can be extended with plugins. This is achieved by defining an **interface** that a third-party library can implement. The engine loads any assemblies that contain classes implementing this interface. A good plugin system should allow plugins to:
*   Draw to the screen.
*   Receive player input.
*   Request **exclusive input control** to implement custom menus or even alternate gameplay modes.

### Headless Modes
For development and automation, it's useful for the engine to run without a visible window. Common headless modes include:
*   **Song Previewer:** A mode to quickly view a song file being rendered, often with live-reload capabilities.
*   **Batch Audio Exporter:** A mode to automatically play through a song and render the result to a WAV, OGG, or MP3 file.

---

## 7. Developer's Checklist for a Modern Rhythm Game Engine

To build a functioning, feature-rich rhythm game engine based on these principles, you will need to implement the following systems:

*   **[ ] Game State Machine**: A manager that handles transitions between `Title`, `SongSelect`, `Performance`, `Result`, etc.
*   **[ ] Master Game Clock**: A single, high-resolution source of time, synchronized with the audio output.
*   **[ ] Note Scrolling & Rendering System**: A visual component that draws notes on screen based on the master clock and scroll speed.
*   **[ ] Timestamped Input System**: A system that can detect key/pad presses and timestamp them against the master clock.
*   **[ ] Judgment Engine**:
    *   Logic to find the correct note for a given input.
    *   Configurable, per-song timing windows.
    *   Logic to handle misses and trigger autoplay sounds.
    *   Support for long notes, open notes, and other special chip types.
*   **[ ] Scoring & Gauge System**:
    *   A combo counter.
    *   A skill-based score calculator (not just a point sum).
    *   A flexible "Groove Gauge" or health system with multiple failure modes.
*   **[ ] Advanced Gameplay Modifiers**:
    *   Lane randomization (Mirror, Random, etc.).
    *   Live scroll speed changes.
    *   Granular auto-play controls for every lane.
*   **[ ] Robust Asset Management**:
    *   A skinning/theming engine.
    *   A formal resource lifecycle (managed/unmanaged) to handle device loss and prevent leaks.
*   **[ ] Performance & Latency Management**:
    *   Low-level audio API support (ASIO/WASAPI).
    *   GPU flushing or similar techniques to minimize draw latency.
*   **[ ] Metadata Caching**: A system to quickly load song information without parsing every file on every launch.

By building these systems and integrating them with the parsing and audio engines, you will have a complete and robust foundation for creating your own rhythm game. 