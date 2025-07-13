# Default Timing Windows and Configuration

Tags: #concept #gameplay #configuration

Timing windows are the specific millisecond ranges that define each judgment level in the [[Judgment System]]. A key feature of many rhythm games, including DTXMania, is that these windows are configurable by the user.

---

## Default Values

While configurable, the engine ships with a set of default timing windows. These values represent the acceptable deviation (plus or minus) from a note's exact timestamp.

*   **Perfect**: ±34ms
*   **Great**: ±67ms
*   **Good**: ±84ms
*   **Poor**: ±117ms

A note that is hit outside the `Poor` window, or not hit at all, is considered a `Miss`.

## Configuration

These values are typically stored in a configuration file (e.g., `config.ini`) that is loaded by the engine at startup. This allows players to adjust the game's difficulty and feel to their preference.

**Example `config.ini` section:**

```ini
[TimingWindows]
Perfect=34
Great=67
Good=84
Poor=117
```

The [[Judgment System]] must read these values during initialization and use them for all timing comparisons. If the configuration file is not found, it should fall back to these hardcoded default values.

This configurability is a critical feature for accommodating different hardware setups (which can have varying input latency) and player skill levels.

---

### Related

*   [[🎮 Gameplay Engine MOC]]
*   [[Judgment System]]
