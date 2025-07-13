# Managed vs. Unmanaged Resources

Tags: #concept #architecture #resources #rendering

To prevent memory leaks and gracefully handle graphics device events (like a user toggling fullscreen or the OS reclaiming the device), an engine needs a robust resource management system. A common and effective pattern is to distinguish between two types of resources: **managed** and **unmanaged**.

This concept is hinted at in the [[Game State Machine]] lifecycle methods (`OnManagedCreateResources`, `OnManagedReleaseResources`).

---

## Unmanaged Resources

These are standard C# (or Java/C++) objects that live in system memory (RAM) and are managed by the language's garbage collector. The graphics device has no direct knowledge of them.

*   **Examples**:
    *   Loaded audio data (decoded PCM buffers).
    *   Parsed simfile data ([[SongInfo]], [[EventList]]).
    *   The song database cache.
*   **Lifecycle**: They are loaded once (e.g., during the song loading stage) and persist until they are manually disposed of or the garbage collector cleans them up. They **survive** a graphics device reset.

## Managed Resources

These are assets that live primarily in the graphics card's VRAM. They are directly tied to the graphics device context (e.g., DirectX or OpenGL). If that context is lost, these resources become invalid and must be re-created.

*   **Examples**:
    *   Textures (`Texture2D`).
    *   Vertex and Index Buffers.
    *   Shaders.
    *   Render Targets.
*   **Lifecycle**:
    1.  **Creation**: They are created via the `OnManagedCreateResources` method of a [[Game State Machine|stage]].
    2.  **Loss**: When the graphics device is reset (e.g., changing resolution), the engine must call `OnManagedReleaseResources` on all active stages to release the now-invalid resources.
    3.  **Re-creation**: The engine then immediately calls `OnManagedCreateResources` again to reload the assets from disk and re-create the GPU-side resources.

By separating resources into these two categories, the engine can handle device loss gracefully without having to re-load and re-parse all the unmanaged song data, which would be extremely slow.

---

### Related

*   [[Game State Machine]]
*   [[Sound Asset Lifecycle]]
*   [[Skinning System]] 