# CLAUDE.md — AI Developer Documentation

Read this file before making any changes to the plugin.

---

## Project Overview

**Plugin:** Material ID Assigner  
**Language:** Python (Cinema 4D Python Plugin API + maxon Node Graph API)  
**Type:** Cinema 4D Command Plugin (`c4d.plugins.CommandData`)  
**Entry point:** `plugin/MaterialIDAssigner/MaterialIDAssigner.pyp`  
**Version:** 1.4 (first fully working release)  
**Tested on:** Cinema 4D R2026 + Redshift

### What the plugin does
Opens a modal dialog where the user enters a number (0–99 999).
On OK: assigns that number as the **Material ID** to all materials currently
selected in the C4D Material Manager. The ID is written directly to the
native Redshift Output node port — no User Data workaround.
The operation is undoable (Ctrl+Z).

---

## Architecture

```
MaterialIDAssigner.pyp
│
├── set_rs_material_id(mat, value)      # Core: writes to RS node graph
├── set_via_userdata(mat, value)        # Fallback: writes User Data field
├── get_selected_materials(doc)         # Iterates materials, checks BIT_ACTIVE
├── assign_id_to_selected_materials(id) # Loops materials, calls above, handles undo
│
├── class MaterialIDDialog(GeDialog)    # Modal dialog (number input + OK/Cancel)
└── class MaterialIDAssignerPlugin(CommandData)  # Registered command, opens dialog
```

---

## Verified Redshift Node Graph Constants (C4D R2026)

These values were found through an interactive diagnostic session and are confirmed working:

| What | Value |
|------|-------|
| Renderer space ID | `com.redshift3d.redshift4c4d.class.nodespace` |
| Material ID port | `com.redshift3d.redshift4c4d.node.output.materialid` |
| Port lives on | The **Output node** (not the RS Standard node) |

---

## Critical API Rules for C4D R2026 Node Graph

These are **hard-won lessons** from debugging. Do not change these without testing.

### ✅ Correct — what works
```python
# Get graph
graph = nm.GetGraph(maxon.Id("com.redshift3d.redshift4c4d.class.nodespace"))

# Iterate nodes
nodes = []
graph.GetViewRoot().GetChildren(nodes, maxon.NODE_KIND.NODE)  # GetViewRoot, not GetRoot

# Get input ports
ports = []
node.GetInputs().GetChildren(ports, maxon.NODE_KIND.INPORT)   # INPORT, not PORT

# Write value via transaction
with graph.BeginTransaction() as ta:           # graph.BeginTransaction(), NOT maxon.GraphTransaction(graph)
    port.SetDefaultValue(int(value))           # plain Python int, not maxon.Int32()
    ta.Commit()

# Register plugin
class MyPlugin(c4d.plugins.CommandData):       # CommandData, not CommandPlugin
```

### ❌ Wrong — what does NOT work in R2026
```python
graph.GetRoot()                        # deprecated since C4D 2025.0 → use GetViewRoot()
maxon.NODE_KIND.PORT                   # does not exist → use INPORT
maxon.NODE_KIND.ALL                    # does not exist → use ALL_MASK
maxon.GraphTransaction(graph)          # TypeError: wrong type for constructor → use graph.BeginTransaction()
port.SetDefaultValue(maxon.Int32(v))   # type mismatch → use plain int(v)
nm.GetGraph("com.redshift3d.redshift4c4d")          # "Invalid Space" → wrong ID
nm.GetDescIDForNodePort(graph, node, port)           # empty exception, unreliable
nm.GetDescIDForNodePort(port, node)                  # wrong arg order
c4d.plugins.CommandPlugin              # removed in R2026 → use CommandData
```

---

## How set_rs_material_id() Works

```python
def set_rs_material_id(mat, value):
    nm    = mat.GetNodeMaterialReference()         # get node material wrapper
    graph = nm.GetGraph(maxon.Id(RS_SPACE_ID))     # get RS node graph
    
    # Read-only traversal to find the port
    nodes = []; graph.GetViewRoot().GetChildren(nodes, maxon.NODE_KIND.NODE)
    for node in nodes:
        ports = []; node.GetInputs().GetChildren(ports, maxon.NODE_KIND.INPORT)
        for port in ports:
            if str(port.GetId()) == RS_PORT_ID:    # match by full port ID string
                with graph.BeginTransaction() as ta:
                    port.SetDefaultValue(int(value))
                    ta.Commit()
                return True
    return False  # → caller uses User Data fallback
```

---

## Fallback: User Data

If `set_rs_material_id()` returns False (no RS node graph found), the plugin
writes a User Data field named `"Material ID"` (DTYPE_LONG) to the material.
This is the fallback for non-Redshift or non-node materials.

---

## Plugin ID

`PLUGIN_ID = 1060500` — **PLACEHOLDER**  
Register at: https://developers.maxon.net/

---

## File Map

```
.
├── plugin/
│   └── MaterialIDAssigner/
│       └── MaterialIDAssigner.pyp    ← All plugin code (single file)
├── docs/
│   ├── FUTURE_PROMPT.md              ← Prompt template for future AI sessions
│   └── debug_material_inspector.py  ← Script Manager diagnostic (read-only)
├── CLAUDE.md                         ← This file
├── README.md                         ← User-facing documentation
└── .gitignore
```

---

## Extending This Plugin

### Support other renderers (Arnold, Octane, etc.)
1. Find the renderer's space ID: use `debug_material_inspector.py` to call
   `nm.GetAllNimbusRefs()` — prints as list of `(maxon.Id, NimbusBaseRef)` tuples
2. Find the Material ID port ID: run the inspector script, look for port with "id" in name
3. Add space + port as constants and add a second attempt in `set_rs_material_id()`

### Bulk assignment (start ID + increment per material)
Add a second `AddEditNumberArrows` field to `MaterialIDDialog` for the increment.
In `assign_id_to_selected_materials()`: `material_id + (index * increment)`.

### Persistent last-used ID (survives C4D restart)
Store in C4D world container:
```python
c4d.GetWorldContainerInstance()[SOME_UNIQUE_ID] = last_id
```

### Read back the ID in Python
```python
import maxon
nm    = mat.GetNodeMaterialReference()
graph = nm.GetGraph(maxon.Id("com.redshift3d.redshift4c4d.class.nodespace"))
nodes = []; graph.GetViewRoot().GetChildren(nodes, maxon.NODE_KIND.NODE)
for node in nodes:
    ports = []; node.GetInputs().GetChildren(ports, maxon.NODE_KIND.INPORT)
    for port in ports:
        if "output.materialid" in str(port.GetId()):
            print(port.GetPortValue())  # GetPortValue() since C4D 2024.4
```
