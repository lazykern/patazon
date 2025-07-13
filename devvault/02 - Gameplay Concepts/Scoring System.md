# Scoring System

Tags: #concept #gameplay #mechanic

The scoring system translates player performance into a quantitative score. A well-designed system rewards accuracy and consistency.

---

## Basic Scoring Formula

A common approach for scoring is to assign a base point value to each note, which is then multiplied by a factor corresponding to the [[Judgment System|judgment]].

*   **Perfect**: Base Score * 1.0
*   **Great**: Base Score * 0.8
*   **Good**: Base Score * 0.5
*   **Poor**: Base Score * 0.2
*   **Miss**: 0

The `Base Score` is often calculated by dividing a target maximum score (e.g., 1,000,000) by the total number of notes in the chart. This ensures that every song has a similar scoring scale, regardless of its length or density.

`Base Score = 1,000,000 / totalNotes`

## Skill-Based Scoring

While a simple point-based system is easy to implement, a more modern approach is to calculate a **skill percentage**. This score (e.g., 98.54%) is based on a weighted distribution of judgments, where `Perfect`s are significantly more valuable.

This percentage can then be used to calculate a "Song Skill" rating for the player, which is a value derived from the song's difficulty level and the player's performance percentage. This provides a more meaningful metric of achievement than a raw score.

## Combos

Combos are a crucial part of the scoring system, rewarding players for hitting consecutive notes without getting a `Poor` or `Miss`.

*   The **combo count** increments for every `Good` or better hit.
*   The combo **breaks** (resets to zero) on a `Poor` or `Miss`.
*   The current combo count is displayed prominently on screen.

While some games incorporate the combo directly into the score calculation (e.g., by adding a combo bonus), many modern rhythm games keep it as a separate metric of performance, with the final score being primarily determined by judgment accuracy.

## Final Grade

After a song is completed, the final score is used to assign a letter grade (e.g., S, A, B, C, F). The thresholds for these grades are typically based on score ranges (e.g., 950,000+ for an S).

---

### Related

*   [[🎮 Gameplay Engine MOC]]
*   [[Judgment System]]
*   [[Advanced Gameplay Mechanics]]
