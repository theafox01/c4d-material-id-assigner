"""
MaterialIDAssigner.pyp
Cinema 4D Python Plugin

Purpose:
    Assigns a numeric Material ID to all materials currently selected
    in the Material Manager.

    Sets the native Redshift Output node port:
    com.redshift3d.redshift4c4d.node.output.materialid

Workflow:
    1. Select one or more materials in the C4D Material Manager
    2. Run the plugin via Extensions menu
    3. Enter the desired ID number in the dialog
    4. Confirm with OK

Author:    theafox01
Version:   1.3
Requires:  Cinema 4D R2026 + Redshift

Plugin ID: 1060500  (PLACEHOLDER — register at developers.maxon.net)

Changelog:
    1.3 - Hardcoded correct Redshift space ID and port ID (found via diagnostics)
          Space:  com.redshift3d.redshift4c4d.class.nodespace
          Port:   com.redshift3d.redshift4c4d.node.output.materialid
          Fixed:  GetRoot() → GetViewRoot() (deprecated since 2025.0)
          Fixed:  NODE_KIND.PORT → NODE_KIND.INPORT
    1.2 - Rewrote core to use maxon Node Graph API
    1.1 - Search native renderer Material ID parameter via description
    1.0 - Initial release (User Data only)
"""

import c4d
from c4d import gui
import maxon

# ---------------------------------------------------------------------------
# Plugin metadata
# ---------------------------------------------------------------------------
PLUGIN_ID      = 1060500
PLUGIN_NAME    = "Material ID Assigner"
PLUGIN_HELP    = "Assigns a numeric Material ID to all selected materials"
PLUGIN_VERSION = "1.3"

# Redshift node graph constants (verified in C4D R2026)
RS_SPACE_ID  = "com.redshift3d.redshift4c4d.class.nodespace"
RS_PORT_ID   = "com.redshift3d.redshift4c4d.node.output.materialid"

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
# Core: Redshift Node Graph
# ---------------------------------------------------------------------------

def set_rs_material_id(mat, value):
    """
    Sets the Material ID on the Redshift Output node of a node-based material.
    Port: com.redshift3d.redshift4c4d.node.output.materialid

    Returns True on success, False if the material has no Redshift node graph.
    """
    try:
        nm = mat.GetNodeMaterialReference()
        if nm is None:
            return False

        graph = nm.GetGraph(maxon.Id(RS_SPACE_ID))
        if graph.IsNullValue():
            return False

        found = [False]

        with maxon.GraphTransaction(graph) as ta:
            nodes = []
            graph.GetViewRoot().GetChildren(nodes, maxon.NODE_KIND.NODE)

            for node in nodes:
                ports = []
                node.GetInputs().GetChildren(ports, maxon.NODE_KIND.INPORT)

                for port in ports:
                    if str(port.GetId()) == RS_PORT_ID:
                        port.SetDefaultValue(maxon.Int32(value))
                        found[0] = True
                        break

                if found[0]:
                    break

            ta.Commit()

        return found[0]

    except Exception as e:
        print(f"[MatIDAssigner] Error: {e}")
        return False


# ---------------------------------------------------------------------------
# Fallback: User Data
# ---------------------------------------------------------------------------

def set_via_userdata(mat, value):
    """Writes value to a 'Material ID' User Data field. Creates it if needed."""
    for uid, bc in mat.GetUserDataContainer():
        if bc[c4d.DESC_NAME] == USERDATA_FIELD_NAME:
            mat[uid] = value
            return

    bc = c4d.GetCustomDatatypeDefault(c4d.DTYPE_LONG)
    bc[c4d.DESC_NAME]       = USERDATA_FIELD_NAME
    bc[c4d.DESC_SHORT_NAME] = "Mat ID"
    bc[c4d.DESC_MIN]        = 0
    bc[c4d.DESC_MAX]        = 99999
    bc[c4d.DESC_STEP]       = 1
    bc[c4d.DESC_ANIMATE]    = c4d.DESC_ANIMATE_OFF
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
# Main assignment
# ---------------------------------------------------------------------------

def assign_id_to_selected_materials(material_id):
    """
    Assigns material_id to all selected materials.
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

        if set_rs_material_id(mat, material_id):
            native_count += 1
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
                    f"Material ID {entered_id} gesetzt ({total} Material(ien)).\n\n"
                    f"Hinweis: Kein Redshift Output-Node gefunden.\n"
                    f"ID wurde als User Data gespeichert."
                )
            else:
                gui.MessageDialog(
                    f"Material ID {entered_id} erfolgreich\n"
                    f"{total} Material(ien) zugewiesen."
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
