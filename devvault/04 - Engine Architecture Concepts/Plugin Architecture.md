# Plugin Architecture

Tags: #concept #architecture #plugins

A powerful engine can be made extensible through the use of a **plugin architecture**. This allows third-party developers to add new features, custom UI elements, or even entirely new gameplay modes without modifying the core engine's source code.

---

## How It Works: An Interface-Based Approach

The foundation of a plugin system is a set of `interfaces` defined by the core engine. A plugin is a separate library (e.g., a `.dll` on Windows) that contains classes implementing these interfaces.

**Example `IPlugin.cs` in the core engine:**
```csharp
public interface IPlugin
{
    string Name { get; }
    string Author { get; }
    void Initialize(IEngineAccessor engine);
    void Update();
    void Draw();
    void Dispose();
}
```

The `IEngineAccessor` is a crucial, limited interface that exposes parts of the engine (like input state or screen dimensions) to the plugin in a safe way.

### The Loading Process

1.  **Discovery**: On startup, the engine scans a designated `plugins` folder for any compatible library files (`.dll`s).
2.  **Inspection**: It uses reflection to inspect each library, looking for classes that implement the `IPlugin` interface.
3.  **Instantiation**: For each valid plugin class found, the engine creates an instance of it.
4.  **Lifecycle Management**: The engine then manages the plugin's lifecycle, calling its `Initialize`, `Update`, `Draw`, and `Dispose` methods at the appropriate times within the main game loop.

### Plugin Capabilities

A well-designed plugin system should allow plugins to:
*   Draw to the screen.
*   Receive player input.
*   Request **exclusive input control** to implement custom menus or alternate gameplay modes.
*   Access a limited, safe subset of the game's state.
*   Add their own configuration options to the main settings screen.

This architecture fosters a creative community around the engine and allows for features that the original developers may have never envisioned.

---

### Related

*   [[Game State Machine]]
*   [[Input Handling]] 