# 🎮 Gameplay Engine MOC

Tags: #moc #gameplay

This Map of Content (MOC) outlines the core components of the DTXMania gameplay engine. It covers everything from the overall application structure to the split-second logic of judging a player's performance.

---

## Core Architecture

*   **[[Game State Machine]]**: The high-level structure that manages the flow of the application (e.g., from Title Screen to Song Select to Gameplay).

## Core Gameplay Loop

These concepts define the real-time mechanics of playing a song.

*   **[[Note Rendering and Scrolling]]**: How notes are drawn on the screen and move towards the judgment line.
*   **[[Input Handling]]**: How the engine captures and processes player inputs from drum pads or keyboards.
*   **[[Judgment System]]**: The logic for determining the accuracy of a player's hit (Perfect, Great, etc.).
*   **[[Default Timing Windows and Configuration]]**: The specific timing windows for judgments and how they can be configured.
*   **[[Scoring System]]**: How points are calculated and awarded based on judgment accuracy.
*   **[[Groove Gauge]]**: The player's health bar and the conditions for clearing or failing a song.
*   **[[Advanced Gameplay Mechanics]]**: Features like long notes, wailing, granular auto-play, and other gameplay modifiers.

## Engine Architecture & Tooling

These notes describe high-level architectural patterns that are critical for building a robust and maintainable engine.

*   **[[Skinning System]]**: The system for decoupling game logic from visual assets, allowing for custom themes.
*   **[[Metadata Caching]]**: A caching strategy for fast loading of large song libraries.
*   **[[Plugin Architecture]]**: How to make the engine extensible by third-party developers.
*   **[[Managed vs. Unmanaged Resources]]**: A memory management pattern for handling graphics device resets.
*   **[[Headless Modes]]**: Running the engine without a GUI for automation and development tools.

---

## Related Systems

*   **[[🎵 Simfile Parsing MOC]]**: Provides the note data that this engine consumes.
*   **[[🔊 Audio System MOC]]**: Works in tandem with the gameplay engine to play sounds in sync with on-screen events.
