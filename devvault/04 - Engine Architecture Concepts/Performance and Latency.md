# Performance and Latency

Tags: #concept #architecture #performance #audio #rendering

For a rhythm game, minimizing latency—the delay between a player's action and the feedback they receive—is paramount. A responsive, "tight" feel is a hallmark of a high-quality engine. This requires tuning at both the audio and graphics levels.

---

## Low-Latency Audio Backend

Standard operating system audio mixers add a significant amount of latency, which is unacceptable for a rhythm game. To achieve the lowest possible audio latency, an engine should ideally support low-level audio APIs that bypass the OS mixer and provide a more direct path to the audio hardware.

*   **ASIO (Audio Stream Input/Output)**: A professional standard on Windows, offering extremely low latency.
*   **WASAPI (Windows Audio Session API)**: A modern Windows API that can be used in "exclusive mode" to gain direct access to the audio device, bypassing the system mixer.
*   **CoreAudio (macOS/iOS)** / **Oboe (Android)**: Equivalents for other platforms.

Supporting these backends is critical for reducing the audio portion of input lag.

## GPU Synchronization

Modern operating systems and graphics drivers often buffer rendering commands, creating a delay of one or more frames between when the CPU issues a draw call and when the image actually appears on the monitor. This is a major source of perceived input lag.

To combat this, an engine might use advanced techniques to force the CPU and GPU to synchronize every frame. This can involve:
*   Using specific driver settings (e.g., "ultra-low latency mode").
*   Implementing "GPU flushing" techniques that force the command buffer to be submitted to the hardware immediately at the end of a frame.

While these techniques can be complex to implement, they are essential for ensuring that the visuals on screen are as up-to-date as possible, which is critical for the player's timing.

---

### Related

*   [[🎮 Gameplay Engine MOC]]
*   [[Core Audio Architecture]]
*   [[Master Audio Clock]] 