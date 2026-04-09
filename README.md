# Material ID Assigner — Cinema 4D Plugin

Assigns a numeric **Material ID** to all currently selected materials in the Cinema 4D Material Manager.  
The ID is stored as a **User Data field** on each material, making it accessible in scripts, expressions, and external pipelines.

---

## Workflow

1. Select one or more materials in the **Material Manager**
2. Open the plugin via **Extensions → Material ID Assigner**
3. Enter the desired ID number (0 – 99 999)
4. Click **OK** — the ID is written to all selected materials
5. The operation is **undoable** (Ctrl+Z)

---

## Installation

1. Copy the folder `plugin/MaterialIDAssigner/` into your Cinema 4D plugins directory:

   | Platform | Path |
   |----------|------|
   | Windows  | `C:\Users\<User>\AppData\Roaming\Maxon\<C4D version>\plugins\` |
   | macOS    | `~/Library/Preferences/Maxon/<C4D version>/plugins/` |

2. Restart Cinema 4D
3. The plugin appears under **Extensions → Material ID Assigner**

---

## Where is the ID stored?

The ID is saved as **User Data** on the material object:
- Field name: `Material ID`
- Type: Integer (Long), range 0–99 999
- Not animatable

You can read it back in Xpresso, Python scripts, or via any tool that accesses material User Data.

---

## Requirements

- Cinema 4D **R21** or later (Python 3 runtime)
- Works with Standard, Physical, Arnold, Redshift, Octane, and any other renderer  
  (the ID is stored on the material object, renderer-independent)

---

## Plugin ID

The current `PLUGIN_ID = 1060500` is a **placeholder**.  
Before distributing this plugin, register a unique ID at:  
→ https://developers.maxon.net/

---

## Version History

| Version | Date       | Notes            |
|---------|------------|------------------|
| 1.0     | 2026-04-09 | Initial release  |
