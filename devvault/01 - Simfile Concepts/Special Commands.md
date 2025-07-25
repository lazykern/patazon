# Special Commands

Tags: #concept #simfile

Beyond the standard metadata and channel data, DTX files can contain special commands that introduce conditional logic, allowing for chart variations within a single file.

---

## `#RANDOM`

*   **Syntax**: `#RANDOM <number>`
*   **Purpose**: This command is the entry point for creating a randomized or branching section in a chart. The parser should generate a random integer from 1 up to (but not including) `<number>`.

## `#IF`

*   **Syntax**: `#IF <number>`
*   **Purpose**: This command marks the beginning of a conditional block. The commands inside this block are only processed if the number generated by a preceding `#RANDOM` command matches this block's `<number>`.

## `#ENDIF`

*   **Syntax**: `#ENDIF`
*   **Purpose**: This command marks the end of a conditional `#IF` block.

**Example:**

```
#RANDOM 3
#IF 1
  // Commands to execute if random number is 1
#ENDIF
#IF 2
  // Commands to execute if random number is 2
#ENDIF
```

In this example, the engine would generate a random number between 1 and 2 (inclusive). If the number is 1, only the commands inside the `#IF 1` block are parsed. If it's 2, only the commands in the `#IF 2` block are parsed. This allows charters to create different patterns that can change on each playthrough. A parser must implement this conditional logic to correctly interpret the chart.

*(Note: These conditional commands are a feature of the DTXMania player engine and are not supported by all editors. The provided example simfiles also do not use them.)*

---

### Related

*   [[🎵 Simfile Parsing MOC]]
*   [[Header Commands]]
