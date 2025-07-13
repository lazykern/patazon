# Simfile Structure Overview

Tags: #concept #simfile

A DTX simfile is a plain text file, typically with a `.dtx` extension, that defines a playable song chart. At its core, the file is composed of two primary sections.

---

### 1. Header Section

The header is located at the top of the file. Every line in this section begins with a `#` character. Its primary responsibilities are:

*   **Metadata**: Defining song information like [[Header Commands|#TITLE, #ARTIST, and #BPM]].
*   **Resource Definitions**: [[Resource Mapping|Mapping sound files (#WAV) and image files (#BMP)]] to two-character hexadecimal IDs (e.g., `01`, `FF`).
*   **Initial Settings**: Defining global gameplay parameters.

### 2. Body Section

The body contains the musical chart data. It consists of a series of channel commands, where each line defines events for a specific measure.

*   **Structure**: The body is made up of measures, identified by a three-digit number (e.g., `#001`, `#002`).
*   **Content**: Each measure contains [[Channel Data|channel definitions]] that specify when notes should be played, which sounds to trigger, and which background videos/images to display.

This separation allows an engine to first parse all metadata and resources before processing the note chart itself, which is covered in [[Simfile Parsing Strategy]].

---

### Related

*   [[🎵 Simfile Parsing MOC]]
