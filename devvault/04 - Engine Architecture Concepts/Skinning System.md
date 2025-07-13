# Skinning System

Tags: #concept #architecture #rendering #ui

A skinning system is a crucial architectural component that decouples the game's visual appearance from its underlying logic. It allows the entire user interface—from the main menu to the in-game judgment text—to be customized by artists or the player without requiring any code changes.

---

## How It Works

The core principle is abstraction. Instead of hard-coding asset paths like `"images/judgement.png"`, the code requests assets from the skinning system using a logical name.

```csharp
// Bad: Hard-coded path
var judgementTexture = Texture.LoadFromFile("content/default/images/judgement.png");

// Good: Abstracted request
var judgementTexture = skinManager.GetTexture("judgement.perfect");
```

### The Skin Definition

A "skin" is a directory containing assets and a definition file (e.g., `skin.ini` or `theme.json`). This file maps logical names to actual asset files.

**Example `skin.ini`:**
```ini
[Textures]
judgement.perfect=graphics/perfect.png
judgement.great=graphics/great.png
note.hihat=graphics/note_hihat.png

[Sounds]
sound.don=sounds/hit.wav

[Fonts]
font.main=fonts/main_font.ttf
font.size.main=24
```

### The Lookup Process

When `skinManager.GetTexture("judgement.perfect")` is called:
1.  The manager looks for a `judgement.perfect` key in the current skin's definition file.
2.  It finds the corresponding path: `graphics/perfect.png`.
3.  It resolves the full path relative to the skin's root directory (e.g., `Skins/MyAwesomeSkin/graphics/perfect.png`).
4.  It loads and returns the asset, caching it for future requests.

### Advanced Features

*   **Asset Fallback**: If an asset is not found in the current skin, the system should fall back to a default, built-in skin to prevent crashes.
*   **Per-Song Skins**: A robust engine can support a skin located inside a song's folder. When that song is played, this skin temporarily overrides the user's globally selected skin, allowing charters to provide a completely custom visual experience for their creation.
*   **Metrics and Layout**: The skinning system can also define the position, size, and rotation of UI elements, allowing for complete layout customization.

---

### Related

*   [[🎮 Gameplay Engine MOC]]
*   [[Game State Machine]] 