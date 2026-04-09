# Material ID Assigner — Cinema 4D Plugin

Assigns a numeric **Material ID** to all currently selected materials in the Cinema 4D Material Manager.  
The ID is written directly to the native **Redshift Output node** (`OPTIONS > Material ID`).

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

   **Important:** Copy only the inner `MaterialIDAssigner/` folder — not the outer `plugin/` wrapper.

2. Restart Cinema 4D
3. The plugin appears under **Extensions → Material ID Assigner**

---

## Requirements

| Requirement | Version |
|-------------|---------|
| Cinema 4D   | R2026 or later |
| Redshift    | Any version with node-based RS Standard material |
| Python      | 3.x (included with C4D R2026) |

---

## What gets changed

The plugin sets the **Material ID** parameter on the **Redshift Output node**:

```
Output Node → OPTIONS → Material ID
```

This is the same field visible in the Redshift Node Editor when the Output node is selected.
It is used in Redshift for Cryptomatte, AOV masking and multi-pass compositing workflows.

If no Redshift node graph is found on a material, the ID is stored as **User Data** instead
(fallback for non-node or non-Redshift materials).

---

## Plugin ID

The current `PLUGIN_ID = 1060500` is a **placeholder**.  
Before distributing this plugin, register a unique ID at:  
→ https://developers.maxon.net/

---

## Version History

| Version | Notes |
|---------|-------|
| 1.4 | First fully working release. Correct transaction API (`graph.BeginTransaction()`). |
| 1.3 | Found correct Redshift space + port IDs via diagnostic scripts. |
| 1.2 | Switched to maxon Node Graph API. |
| 1.1 | Attempted description-based parameter search. |
| 1.0 | Initial release — User Data only. |
