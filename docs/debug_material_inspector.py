"""
Material Inspector — Debug Script
Ausführen über: Script Manager in Cinema 4D

Selektiere zuerst ein RS Standard Material, dann dieses Script ausführen.
Gibt alle Nodes und Ports im Node-Graph aus → zeigt den exakten Port-Namen
für die Material ID, den das Plugin dann setzen muss.
"""

import c4d
import maxon

def main():
    doc = c4d.documents.GetActiveDocument()

    # Aktives (selektiertes) Material holen
    mat = doc.GetFirstMaterial()
    while mat:
        if mat.GetBit(c4d.BIT_ACTIVE):
            break
        mat = mat.GetNext()

    if mat is None:
        print("=== FEHLER: Kein Material selektiert! ===")
        return

    print(f"\n{'='*60}")
    print(f"Material: {mat.GetName()}")
    print(f"Type ID:  {mat.GetType()}")
    print(f"{'='*60}")

    # GetNodeMaterialReference prüfen
    if not hasattr(mat, 'GetNodeMaterialReference'):
        print("✗ GetNodeMaterialReference nicht vorhanden!")
        return

    nm = mat.GetNodeMaterialReference()
    print(f"NodeMaterialRef: {nm}")
    print(f"Type: {type(nm)}")

    if nm is None:
        print("✗ Kein Node Material!")
        return

    # Alle bekannten Renderer-Spaces probieren
    spaces = [
        "com.redshift3d.redshift4c4d",
        "net.maxon.render.0",
        "com.autodesk.arnold.shader",
        "com.otoy.octane",
    ]

    for spaceStr in spaces:
        try:
            graph = nm.GetGraph(maxon.Id(spaceStr))
        except Exception as e:
            print(f"\n[{spaceStr}] GetGraph Error: {e}")
            continue

        if graph.IsNullValue():
            print(f"\n[{spaceStr}] → kein Graph (IsNullValue)")
            continue

        print(f"\n{'='*60}")
        print(f"✓ GRAPH GEFUNDEN: {spaceStr}")
        print(f"{'='*60}")

        nodes = []
        graph.GetRoot().GetChildren(nodes, maxon.NODE_KIND.NODE)
        print(f"Anzahl Nodes: {len(nodes)}")

        for node in nodes:
            nodeId = str(node.GetId())
            print(f"\n  NODE: {nodeId}")

            ports = []
            node.GetInputs().GetChildren(ports, maxon.NODE_KIND.PORT)

            if ports:
                print(f"    Input Ports ({len(ports)}):")
                for port in ports:
                    portId   = str(port.GetId())
                    portVal  = ""
                    try:
                        portVal = f" = {port.GetDefaultValue()}"
                    except:
                        pass
                    # Markiere potenzielle Material-ID-Ports
                    marker = " ◄◄◄ MATERIAL ID?" if any(
                        f in portId.lower() for f in ["material_id","materialid","matid","object_id","objectid"]
                    ) else ""
                    print(f"      {portId}{portVal}{marker}")
            else:
                print(f"    (keine Input-Ports)")

    print(f"\n{'='*60}")
    print("Inspector fertig.")
    print(f"{'='*60}\n")

main()
