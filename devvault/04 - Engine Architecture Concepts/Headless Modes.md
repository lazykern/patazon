# Headless Modes

Tags: #concept #architecture #tools #automation

For development, testing, and automation, it is extremely useful for an engine to be able to run in "headless" modes—that is, without a visible window or any user interaction. This is typically controlled via command-line arguments.

---

## Why Run Headless?

Running without a GUI allows for automated batch processing and integration with other tools, which is invaluable for both developers and content creators.

## Common Headless Modes

### Song Previewer

*   **Command**: `engine.exe --preview "path/to/song.dtx"`
*   **Function**: This mode would launch the engine, load the specified simfile, and render the gameplay screen to a video file or a sequence of images. It might also have **live-reload capabilities**, automatically watching the simfile for changes and re-rendering the preview whenever the charter saves their work.
*   **Use Case**: Allows a charter to quickly see how a pattern looks in-game without having to manually navigate through the menus each time they make a change.

### Batch Audio Exporter

*   **Command**: `engine.exe --export-audio "path/to/song.dtx" --output "song.wav"`
*   **Function**: This mode loads and plays through an entire song internally, capturing all the audio from the [[Mixing and the Rendering Pipeline|master mixer]] (including BGM and auto-played sounds) and saving the result to a single audio file.
*   **Use Case**: Creating high-quality audio previews of charts for sharing online.

### Validation Tool

*   **Command**: `engine.exe --validate "path/to/songfolder/"`
*   **Function**: This mode would parse all the songs in a given folder, checking for common errors like missing resource files, invalid commands, or unsynced notes. It would then generate a report of all issues found.
*   **Use Case**: Essential for content creators to ensure their song packs are well-formed and will not cause issues for players.

Implementing these modes from the start makes an engine a more powerful and versatile tool, not just a game.

---

### Related

*   [[Simfile Parsing Strategy]]
*   [[Game State Machine]] 