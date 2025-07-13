# Groove Gauge

Tags: #concept #gameplay #mechanic #feature

The Groove Gauge is the player's "life bar" or "health meter" during gameplay. It provides immediate feedback on performance and serves as the primary condition for clearing or failing a song.

---

## How It Works

The gauge is a numerical value, typically from 0% to 100%. Its behavior is tied directly to the [[Judgment System]].

*   **Increase**: Hitting notes with good accuracy (`Perfect`, `Great`) increases the gauge. The amount of increase can be weighted, with `Perfect`s rewarding more than `Great`s.
*   **Decrease**: Missing a note or hitting it with poor accuracy (`Poor`, `Miss`) decreases the gauge.
*   **Clear Condition**: To "clear" a song, the player must typically finish with the gauge above a certain threshold (e.g., 80%).
*   **Fail Condition**: If the gauge drops to 0% at any point, the player fails the song immediately ("Stage Failed").

## Configurability and Gameplay Modes

A key feature of a robust engine, as highlighted in the developer guides, is making the gauge's behavior highly configurable. This allows for different difficulty settings and gameplay modes.

*   **Damage Level**: The amount of gauge lost on a `Poor` or `Miss` can be adjusted. A "Hard" or "Expert" setting would feature a much more punishing damage level.
*   **Sudden Death**: A special mode where the gauge starts at 100% and any `Poor` or `Miss` results in an instant Stage Failed.
*   **Risky / Hazard**: A variation of Sudden Death where the player is allowed a small number of mistakes (e.g., 1-10) before failing.
*   **Training / Practice Mode**: A setting can be added to prevent the gauge from decreasing, allowing players to practice a song without fear of failing.

The Groove Gauge is a fundamental system for adding stakes and measuring success in a rhythm game.

---

### Related

*   [[🎮 Gameplay Engine MOC]]
*   [[Judgment System]]
*   [[Scoring System]] 