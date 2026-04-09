"""
MaterialIDAssigner.pyp
Cinema 4D Python Plugin

Purpose:
    Assigns a numeric Material ID to all materials currently selected
    in the Material Manager.

    Strategy (in order of priority):
    1. maxon Node Graph API  — sets the native port on the Output node
       (Redshift RS Standard "OPTIONS > Material ID", R2024+ node materials)
    2. Classic description search  — fallback for non-node materials
    3. User Data  — last resort fallback

Author:    theafox01
Version:   1.2
Requires:  Cinema 4D R2026 + Redshift

Plugin ID: 1060500  (PLACEHOLDER — register at developers.maxon.net)

Changelog:
    1.2 - Rewrote core to use maxon Node Graph API for node-based materials
          (Redshift RS Standard / Output node Material ID port)
    1.1 - Search native renderer Material ID parameter via description
    1.0 - Initial release (User Data only)
"""

import c4d
from c4d import gui

import maxon

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
PLUGIN_ID      = 1060500
PLUGIN_NAME    = "Material ID Assigner"
PLUGIN_HELP    = "Assigns a numeric Material ID to all selected materials"
PLUGIN_VERSION = "1.2"

# Set to True to print all found nodes/ports to the C4D console (for debugging)
DEBUG = False

# Renderer graph space IDs to try (in order)
RENDERER_SPACES = [
    "com.redshift3d.redshift4c4d",   # Redshift
    "com.autodesk.arnold.shader",    # Arnold
    "net.maxon.render.0",            # C4D Standard / Physical
]

# Port name fragments to look for (case-insensitive substring match)
MATID_PORT_FRAGMENTS = ["material_id", "materialid", "matid"]

# Fallback User Data field name
USERDATA_FIELD_NAME = "Material ID"

# ---------------------------------------------------------------------------
# Dialog widget IDs
# ---------------------------------------------------------------------------
ID_GROUP_MAIN    = 1001
ID_LABEL         = 1002
ID_ID_FIELD      = 1003
ID_GROUP_BUTTONS = 1004
ID_BTN_OK        = 1005
ID_BTN_CANCEL    = 1006


# ---------------------------------------------------------------------------
# Core: Node Graph API (maxon)
# ---------------------------------------------------------------------------

def try_set_via_node_graph(mat, value):
    """
    Searches the material's node graph for a port matching one of the
    MATID_PORT_FRAGMENTS and sets its default value.

    Returns True if the value was successfully set.
    """
    try:
        nm = mat.GetNodeMaterialReference()
        if not nm:
            return False

        for spaceStr in RENDERER_SPACES:
            try:
                graph = nm.GetGraph(maxon.Id(spaceStr))
            except Exception:
                continue

            if graph.IsNullValue():
                continue

            if DEBUG:
                print(f"[MatIDAssigner] Found graph: {spaceStr}")

            found = [False]

            with maxon.GraphTransaction(graph) as ta:

                # Collect all nodes
                nodes = []
                graph.GetRoot().GetChildren(nodes, maxon.NODE_KIND.NODE)

                for node in nodes:
                    nodeIdStr = str(node.GetId()).lower()

                    if DEBUG:
                        print(f"[MatIDAssigner]   Node: {nodeIdStr}")

                    # Collect all input ports of this node
                    ports = []
                    node.GetInputs().GetChildren(ports, maxon.NODE_KIND.PORT)

                    for port in ports:
                        portIdStr = str(port.GetId()).lower()

                        if DEBUG:
                            print(f"[MatIDAssigner]     Port: {portIdStr}")

                        if any(frag in portIdStr for frag in MATID_PORT_FRAGMENTS):
                            port.SetDefaultValue(maxon.Int32(value))
                            found[0] = True
                            if DEBUG:
                                print(f"[MatIDAssigner] ✓ Set '{portIdStr}' = {value}")

                ta.Commit()

            if found[0]:
                return True

        return False

    except Exception as e:
        print(f"[MatIDAssigner] Node graph error: {e}")
        return False


# ---------------------------------------------------------------------------
# Fallback: Classic description search
# ---------------------------------------------------------------------------

def try_set_via_description(mat, value):
    """
    Searches the material's classic C4D description for a parameter
    named 'material id' and sets it. Works for non-node legacy materials.
    """
    try:
        desc = mat.GetDescription(0)
        for bc, paramid, groupid in desc:
            if bc is None:
                continue
            name = bc.GetString(c4d.DESC_NAME)
            if name and "material id" in name.strip().lower():
                mat[paramid] = value
                if DEBUG:
                    print(f"[MatIDAssigner] ✓ Set via description: '{name}' = {value}")
                return True
    except Exception as e:
        print(f"[MatIDAssigner] Description search error: {e}")
    return False


# ---------------------------------------------------------------------------
# Fallback: User Data
# ---------------------------------------------------------------------------

def set_via_userdata(mat, value):
    """
    Writes value to a 'Material ID' User Data field on the material.
    Creates the field if it doesn't exist yet.
    """
    for uid, bc in mat.GetUserDataContainer():
        if bc[c4d.DESC_NAME] == USERDATA_FIELD_NAME:
            mat[uid] = value
            return
    # Create new field
    bc = c4d.GetCustomDatatypeDefault(c4d.DTYPE_LONG)
    bc[c4d.DESC_NAME]    = USERDATA_FIELD_NAME
    bc[c4d.DESC_SHORT_NAME] = "Mat ID"
    bc[c4d.DESC_MIN]     = 0
    bc[c4d.DESC_MAX]     = 99999
    bc[c4d.DESC_STEP]    = 1
    bc[c4d.DESC_ANIMATE] = c4d.DESC_ANIMATE_OFF
    uid = mat.AddUserData(bc)
    mat[uid] = value


# ---------------------------------------------------------------------------
# Material selection
# ---------------------------------------------------------------------------

def get_selected_materials(doc):
    result = []
    mat = doc.GetFirstMaterial()
    while mat:
        if mat.GetBit(c4d.BIT_ACTIVE):
            result.append(mat)
        mat = mat.GetNext()
    return result


# ---------------------------------------------------------------------------
# Main assignment logic
# ---------------------------------------------------------------------------

def assign_id_to_selected_materials(material_id):
    """
    Assigns material_id to all selected materials using the best available method.
    Returns (total, native_count, fallback_count).
    """
    doc = c4d.documents.GetActiveDocument()
    if not doc:
        return 0, 0, 0

    materials = get_selected_materials(doc)
    if not materials:
        return 0, 0, 0

    doc.StartUndo()

    native_count   = 0
    fallback_count = 0

    for mat in materials:
        doc.AddUndo(c4d.UNDOTYPE_CHANGE, mat)

        if DEBUG:
            print(f"\n[MatIDAssigner] Processing: {mat.GetName()}")

        # Priority 1: Node graph
        if try_set_via_node_graph(mat, material_id):
            native_count += 1

        # Priority 2: Classic description
        elif try_set_via_description(mat, material_id):
            native_count += 1

        # Priority 3: User Data fallback
        else:
            set_via_userdata(mat, material_id)
            fallback_count += 1

        mat.Message(c4d.MSG_UPDATE)

    doc.EndUndo()
    c4d.EventAdd()

    return len(materials), native_count, fallback_count


# ---------------------------------------------------------------------------
# Dialog
# ---------------------------------------------------------------------------

class MaterialIDDialog(gui.GeDialog):

    def __init__(self):
        super().__init__()
        self._last_id = 0

    def CreateLayout(self):
        self.SetTitle(PLUGIN_NAME)

        if self.GroupBegin(ID_GROUP_MAIN, c4d.BFH_SCALEFIT | c4d.BFV_FIT, 2, 1, ""):
            self.GroupBorderSpace(8, 8, 8, 8)
            self.AddStaticText(ID_LABEL, c4d.BFH_LEFT, name="Material ID:")
            self.AddEditNumberArrows(ID_ID_FIELD, c4d.BFH_SCALEFIT)
        self.GroupEnd()

        self.AddSeparatorH(0, c4d.BFH_SCALEFIT)

        if self.GroupBegin(ID_GROUP_BUTTONS, c4d.BFH_SCALEFIT, 2, 1, ""):
            self.GroupBorderSpace(8, 4, 8, 8)
            self.AddButton(ID_BTN_OK,     c4d.BFH_SCALEFIT, name="OK")
            self.AddButton(ID_BTN_CANCEL, c4d.BFH_SCALEFIT, name="Abbrechen")
        self.GroupEnd()

        return True

    def InitValues(self):
        self.SetInt32(ID_ID_FIELD, self._last_id, min=0, max=99999, step=1)
        return True

    def Command(self, id, msg):
        if id == ID_BTN_OK:
            entered_id = self.GetInt32(ID_ID_FIELD)
            self._last_id = entered_id

            total, native, fallback = assign_id_to_selected_materials(entered_id)
            self.Close()

            if total == 0:
                gui.MessageDialog(
                    "Keine Materialien selektiert!\n\n"
                    "Bitte zuerst Materialien im Material Manager auswählen."
                )
            elif fallback > 0 and native == 0:
                gui.MessageDialog(
                    f"Material ID {entered_id} wurde gesetzt ({total} Material(ien)).\n\n"
                    f"Hinweis: Kein nativer Parameter gefunden — ID als User Data gespeichert.\n"
                    f"→ Aktiviere DEBUG=True im Plugin-Code für Details."
                )
            else:
                gui.MessageDialog(
                    f"Material ID {entered_id} erfolgreich\n"
                    f"{total} Material(ien) zugewiesen. ✓"
                )

        elif id == ID_BTN_CANCEL:
            self.Close()

        return True


# ---------------------------------------------------------------------------
# Plugin
# ---------------------------------------------------------------------------

class MaterialIDAssignerPlugin(c4d.plugins.CommandData):

    def Execute(self, doc):
        dlg = MaterialIDDialog()
        dlg.Open(
            dlgtype=c4d.DLG_TYPE_MODAL,
            pluginid=PLUGIN_ID,
            xpos=-2,
            ypos=-2,
            defaultw=280,
            defaulth=90,
        )
        return True

    def GetState(self, doc):
        return c4d.CMD_ENABLED


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    c4d.plugins.RegisterCommandPlugin(
        id=PLUGIN_ID,
        str=PLUGIN_NAME,
        info=0,
        icon=None,
        help=PLUGIN_HELP,
        dat=MaterialIDAssignerPlugin(),
    )
