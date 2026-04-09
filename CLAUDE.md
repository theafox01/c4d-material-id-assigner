# CLAUDE.md — AI Developer Documentation

This file is the primary briefing document for the AI assistant (Claude) working on this plugin.  
Read this before making any changes.

---

## Project Overview

**Plugin:** Material ID Assigner  
**Language:** Python (Cinema 4D Python Plugin API)  
**Type:** Cinema 4D Command Plugin (`CommandPlugin`)  
**Entry point:** `plugin/MaterialIDAssigner/MaterialIDAssigner.pyp`

### What the plugin does
Assigns a numeric "Material ID" (stored as User Data) to all materials currently selected in the C4D Material Manager. The user opens a modal dialog, enters a number (0–99 999), and clicks OK. All selected materials receive the ID. The operation is undoable.

---

## Architecture

```
MaterialIDAssigner.pyp
│
├── get_selected_materials(doc)          # Iterates materials, checks BIT_ACTIVE
├── get_or_create_matid_userdata(mat)    # Finds/creates the User Data field on a material
├── assign_id_to_selected_materials(id)  # Wraps the above in StartUndo/EndUndo
│
├── class MaterialIDDialog(GeDialog)     # Modal dialog (input + OK/Cancel)
└── class MaterialIDAssignerPlugin(CommandPlugin)  # Entry point, opens the dialog
```

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| User Data for storage | Renderer-agnostic; accessible from Xpresso, Python, external tools |
| BIT_ACTIVE iteration | Compatible with all C4D R21+ versions (avoids potential API gaps) |
| `doc.StartUndo()` / `doc.EndUndo()` | Makes the operation undoable with a single Ctrl+Z |
| Modal dialog | Simple workflow; no risk of state drift with non-modal |
| `AddEditNumberArrows` | Integer field with +/− arrows, appropriate for ID input |

---

## Cinema 4D SDK Reference Points

- `c4d.BIT_ACTIVE` — flag for selected objects/materials
- `mat.GetUserDataContainer()` — returns `(DescID, BaseContainer)` tuples
- `c4d.GetCustomDatatypeDefault(c4d.DTYPE_LONG)` — creates a Long User Data descriptor
- `mat.AddUserData(bc)` — adds a User Data field, returns the `DescID`
- `c4d.UNDOTYPE_CHANGE` — registers a change for undo purposes
- `c4d.EventAdd()` — triggers a UI refresh after changes
- `gui.GeDialog` — base class for all C4D dialogs
- `plugins.RegisterCommandPlugin(...)` — registers the plugin at startup

---

## Plugin ID

`PLUGIN_ID = 1060500` — **PLACEHOLDER**  
Register a real ID before any distribution at: https://developers.maxon.net/

---

## Extending This Plugin

### Add a "remember last ID" feature across sessions
Store the last ID in the C4D world container:
```python
c4d.GetWorldContainerInstance()[MY_PREF_ID] = last_id
```

### Add a material name preview in the dialog
Read `mat.GetName()` for each selected material and display a list in the dialog using `AddListView`.

### Export all materials with their IDs to CSV
Iterate `doc.GetFirstMaterial()` / `.GetNext()`, read the User Data field, write to file.

### Support for bulk ID assignment (start ID + increment)
Add a second field `ID Increment` to the dialog. Assign `start_id + (index * increment)` per material.

### Read back the ID in Xpresso
- Add a Material node
- Access User Data port named "Material ID"

---

## Common Pitfalls

- **`mat.AddUserData()` creates a new field every time it is called** — always search first with `GetUserDataContainer()` to avoid duplicates. The helper `get_or_create_matid_userdata()` handles this.
- **Do not call `c4d.EventAdd()` inside a StartUndo/EndUndo block** — call it after `EndUndo()`.
- **Plugin ID collisions** — using the placeholder ID in a shared C4D installation can conflict with other plugins. Replace before distributing.

---

## File Map

```
.
├── plugin/
│   └── MaterialIDAssigner/
│       └── MaterialIDAssigner.pyp    ← All plugin code (single file)
├── docs/
│   └── FUTURE_PROMPT.md              ← Prompt template for future AI sessions
├── CLAUDE.md                         ← This file
├── README.md                         ← User-facing documentation
└── .gitignore
```
