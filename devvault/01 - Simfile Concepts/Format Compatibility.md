# Format Compatibility (GDA, BMS)

Tags: #concept #simfile #implementation #compatibility

A mature rhythm game engine often supports more than just one specific file format. The DTXMania engine is capable of parsing and transparently converting several related formats on the fly, most notably GDA and BMS.

This allows the engine to tap into a wider library of community-made charts without requiring the user to manually convert them.

---

## GDA (Guitar & Drums Archive)

GDA files are structurally very similar to DTX but use a different set of two-character channel codes for drum and guitar notes. A parser can handle this with a simple lookup table that maps GDA codes to the engine's internal [[Channel Data|channel enumeration]].

**Example GDA to DTX Mapping:**

| GDA Code | DTX Channel Purpose |
|---|---|
| `HH` | `HiHatClose` |
| `SD` | `Snare` |
| `BD` | `BassDrum` |
| `G1`-`G7` | `Guitar_...` (3-fret) |
| `B1`-`B7` | `Bass_...` (3-fret) |
| `GW`/`BW`| `..._Wailing` |
| `FI` | `FillIn` |
| `TC` | `BPM` |
| `BL` | `BarLength` |

By pre-processing the channel code through this map, the rest of the parsing logic can remain identical to the DTX parser. In the original DTXMania source, this mapping is handled by a structure named `stGDAParam`.

## BMS / BME (Be-Music Source / Be-Music Extended)

Beatmania files (`.bms`, `.bme`) are another popular format. Parsing these is more complex, as the mapping of keys to instruments can vary.

The engine must contain logic to inspect the BMS file's header to understand its key configuration and then map the note channels to the corresponding DTX drum channels. This conversion is often handled in a dedicated function, such as `tDTX入力_行解析_チャンネル_BMSチャンネル文字列２桁をチャンネル番号にして返す` from the original source, which translates the two-character BMS channel string into the engine's internal channel number.

---

### Related

*   [[🎵 Simfile Parsing MOC]]
*   [[Channel Data]] 