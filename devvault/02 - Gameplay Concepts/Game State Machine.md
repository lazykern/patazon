# Game State Machine

Tags: #concept #gameplay #architecture

At the highest level, DTXMania is structured as a Finite State Machine (FSM). The application moves between distinct "stages" or "scenes," such as the title screen, song select, gameplay, and results screen. This architecture provides a clean and manageable way to handle the application's lifecycle.

---

## The Stage Lifecycle

Each stage in the game (e.g., `CStageTitle`, `CStageSelect`, `CStagePerfDrumsScreen`) adheres to a common lifecycle interface, which typically includes the following methods:

*   **`OnActivate()`**: Called once when the stage becomes active. This is where resources specific to this stage are loaded (e.g., loading song previews in song select).
*   **`OnDeactivate()`**: Called once when the stage is about to be replaced by another. This is where resources are unloaded to free up memory.
*   **`OnManagedCreateResources()`**: Handles the creation of managed resources that can persist between stages.
*   **`OnManagedReleaseResources()`**: Handles the release of managed resources.
*   **`tUpdateAndDraw()`**: Called every frame. This is the main loop for the stage, where all logic updates and rendering calls happen.

A typical flow of stages would be:
`Startup` → `Title` → `Song Selection` → `Song Loading` → `Performance` → `Result` → `End`

## State Transitions

The main application class is responsible for managing the current state and handling transitions. For example, when a player selects a song in the `CStageSelect` stage, the main loop will:

1.  Call `OnDeactivate()` on the current `CStageSelect` instance.
2.  Create a new instance of `CStagePerfDrumsScreen`.
3.  Call `OnActivate()` on the new gameplay stage.
4.  Set the new stage as the active one.

This model ensures that each part of the game is self-contained and only active when it needs to be, which is crucial for managing complexity and resources.

---

### Related

*   [[🎮 Gameplay Engine MOC]]
