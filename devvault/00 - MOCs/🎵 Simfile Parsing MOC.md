# 🎵 Simfile Parsing MOC

Tags: #moc #simfile

This Map of Content (MOC) covers all concepts related to parsing and understanding DTX simfiles. It serves as the central hub for navigating the structure, commands, and data within a `.dtx` file.

---

## Core Concepts

These notes break down the fundamental components of a DTX simfile.

*   **[[Simfile Structure Overview]]**: A high-level look at how a `.dtx` file is organized into a header and a body section.
*   **[[Header Commands]]**: Details on metadata commands like `#TITLE`, `#ARTIST`, `#BPM`, and initial gameplay settings.
*   **[[Resource Mapping]]**: How `#WAVxx` and `#BMPxx` commands link short identifiers to actual audio and image files.
*   **[[WAV Properties]]**: How commands like `#VOLUMExx` and `#PANxx` set default properties for audio resources.
*   **[[Channel Data]]**: The heart of the simfile. This explains how note data, background music, and other events are encoded in channels.
*   **[[BGA and BGI Channels]]**: Specifics on how background animations (BGA) and background images (BGI) are timed and displayed.
*   **[[Special Commands]]**: Covers less common but important commands like `#SIZE` and `#RANDOM`.

## Implementation & Compatibility

*   **[[Simfile Parsing Strategy]]**: A guide to implementing a robust parser, including data structures and handling edge cases.
*   **[[Format Compatibility]]**: Notes on parsing related formats like GDA and BMS.
*   **[[Editor-Specific Commands]]**: How to handle non-standard commands from editors like DTXCreator.

---

## Related Systems

*   **[[🔊 Audio System MOC]]**: The audio system consumes the resource map and channel data to play sounds.
*   **[[🎮 Gameplay Engine MOC]]**: The gameplay engine uses the parsed note data to create the playable chart.
