# Future Session Prompt — Material ID Assigner

Use this prompt at the start of a new Claude session to quickly brief the AI:

---

## Prompt Template

```
Du arbeitest an einem Cinema 4D Python Plugin namens "Material ID Assigner".

Das Plugin befindet sich im Repository: https://github.com/theafox01/c4d-material-id-assigner

Lies zuerst CLAUDE.md für die vollständige technische Dokumentation.

Kurzbeschreibung des Plugins:
- Typ: Cinema 4D Command Plugin (CommandPlugin)
- Entry Point: plugin/MaterialIDAssigner/MaterialIDAssigner.pyp
- Funktion: Weist allen aktuell selektierten Materialien im Material Manager 
  eine numerische "Material ID" zu, die als User Data auf dem Material gespeichert wird.
- Workflow: Materialien selektieren → Plugin aufrufen → ID eingeben → OK → fertig
- Die Operation ist per Ctrl+Z rückgängig machbar

Architektur (3 Layer):
1. Hilfsfunktionen: get_selected_materials(), get_or_create_matid_userdata(), assign_id_to_selected_materials()
2. Dialog: MaterialIDDialog (GeDialog, modal)
3. Plugin-Klasse: MaterialIDAssignerPlugin (CommandPlugin)

Wichtige Infos:
- Plugin ID 1060500 ist ein Platzhalter → vor Veröffentlichung bei developers.maxon.net registrieren
- Anforderung: Cinema 4D R21+ (Python 3)
- Storage: User Data Feld "Material ID" (DTYPE_LONG) direkt am Material-Objekt

Meine aktuelle Aufgabe: [HIER EINTRAGEN WAS DU MACHEN MÖCHTEST]
```

---

## Checkliste vor Änderungen

- [ ] `CLAUDE.md` gelesen
- [ ] Aktuellen Code in `MaterialIDAssigner.pyp` gelesen
- [ ] Verständnis der 3-Layer-Architektur bestätigt
- [ ] Plugin-ID-Hinweis beachtet (noch Platzhalter)

---

## Typische Erweiterungsaufgaben

| Aufgabe | Stichworte für den Prompt |
|---------|--------------------------|
| Bulk-ID-Zuweisung (Start + Inkrement) | "Füge ein zweites Feld 'Inkrement' hinzu" |
| CSV-Export aller Material-IDs | "Exportiere alle Materialien + IDs als CSV" |
| Letzte ID zwischen Sessions merken | "World Container persistent speichern" |
| Materialien nach ID filtern/auswählen | "Neue CommandPlugin zum Selektieren nach ID" |
| Xpresso-Zugriff dokumentieren | "Zeige wie man die User Data in Xpresso liest" |
