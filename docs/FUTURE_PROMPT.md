# Future Session Prompt — Material ID Assigner

Use this prompt at the start of a new Claude session to quickly get up to speed:

---

## Prompt Template

```
Du arbeitest an einem Cinema 4D Python Plugin: "Material ID Assigner".

Repository: https://github.com/theafox01/c4d-material-id-assigner
Lokaler Pfad: F:\work\My_Plugins&Tools\Cinema 4D\10_C4D_Set selekted Materials Maeteria ID\
Plugin-Pfad: F:\Plugins\C4D\R2026\Used\MaterialIDAssigner\MaterialIDAssigner.pyp

Lies zuerst CLAUDE.md — dort sind alle Lessons Learned dokumentiert.

KURZBESCHREIBUNG:
Command Plugin das allen selektierten Materialien im Material Manager
eine numerische "Material ID" zuweist. Schreibt direkt in den nativen
Redshift Output-Node Port. Fully working seit v1.4.

ARCHITEKTUR:
- set_rs_material_id(mat, value)     → schreibt in RS Node Graph
- set_via_userdata(mat, value)       → Fallback
- assign_id_to_selected_materials()  → Haupt-Loop mit Undo
- MaterialIDDialog(GeDialog)         → Modaler Dialog
- MaterialIDAssignerPlugin(CommandData) → Entry Point

KRITISCHE API-FAKTEN FÜR R2026 (alle getestet):
✅ Space ID:   "com.redshift3d.redshift4c4d.class.nodespace"
✅ Port ID:    "com.redshift3d.redshift4c4d.node.output.materialid"
✅ graph.GetViewRoot()              (nicht GetRoot — deprecated)
✅ maxon.NODE_KIND.INPORT           (nicht PORT — existiert nicht)
✅ graph.BeginTransaction()         (nicht maxon.GraphTransaction(graph) — TypeError)
✅ port.SetDefaultValue(int(value)) (nicht maxon.Int32 — type mismatch)
✅ c4d.plugins.CommandData          (nicht CommandPlugin — in R2026 entfernt)

MEINE AUFGABE: [HIER EINTRAGEN]
```

---

## Diagnose-Tools

Falls API-Probleme auftreten: `docs/debug_material_inspector.py` im
**Script Manager** (Copy-Paste, nicht als Datei öffnen!) ausführen.
Das Script gibt alle Nodes, Ports und Werte des selektierten Materials aus.

---

## Typische Erweiterungsaufgaben

| Aufgabe | Hinweis |
|---------|---------|
| Anderen Renderer unterstützen | Space ID via `nm.GetAllNimbusRefs()` ermitteln |
| Bulk-ID mit Inkrement | Zweites Feld im Dialog + Index * Inkrement |
| ID persistent speichern | `c4d.GetWorldContainerInstance()[ID]` |
| ID zurücklesen | `port.GetPortValue()` (neu seit 2024.4) |
