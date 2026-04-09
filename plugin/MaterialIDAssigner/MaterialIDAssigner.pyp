"""
MaterialIDAssigner.pyp
Cinema 4D Python Plugin

Purpose:
    Assigns a custom numeric "Material ID" (stored as User Data) to all
    materials that are currently selected in the Material Manager.

Workflow:
    1. Select one or more materials in the C4D Material Manager
    2. Run the plugin via Extensions menu
    3. Enter the desired ID number in the dialog
    4. Confirm with OK — the ID is written to all selected materials

Author:    theafox01
Version:   1.0
Requires:  Cinema 4D R21 or later (Python 3)

Plugin ID: 1060500
    → Placeholder ID for development only.
    → Register a real ID at: https://developers.maxon.net/
    → Replace PLUGIN_ID before publishing/distributing.
"""

import c4d
from c4d import gui, plugins

# ---------------------------------------------------------------------------
# Plugin metadata
# ---------------------------------------------------------------------------
PLUGIN_ID   = 1060500           # PLACEHOLDER — register at developers.maxon.net
PLUGIN_NAME = "Material ID Assigner"
PLUGIN_HELP = "Assigns a numeric Material ID to all selected materials"
PLUGIN_VERSION = "1.0"

# Name of the User Data field that stores the ID on each material
USERDATA_FIELD_NAME = "Material ID"

# ---------------------------------------------------------------------------
# Dialog widget IDs (must be unique within the dialog)
# ---------------------------------------------------------------------------
ID_GROUP_MAIN    = 1001
ID_LABEL         = 1002
ID_ID_FIELD      = 1003
ID_GROUP_BUTTONS = 1004
ID_BTN_OK        = 1005
ID_BTN_CANCEL    = 1006


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def get_selected_materials(doc):
    """
    Returns a list of all materials that are currently selected (active)
    in the Material Manager of the given document.

    Compatible with all Cinema 4D versions that support Python plugins.
    """
    result = []
    mat = doc.GetFirstMaterial()
    while mat:
        if mat.GetBit(c4d.BIT_ACTIVE):
            result.append(mat)
        mat = mat.GetNext()
    return result


def get_or_create_matid_userdata(mat):
    """
    Returns the DescID (UserData ID) of the 'Material ID' User Data field
    on the given material. Creates the field if it does not exist yet.

    The field is of type Long (integer), range 0–99999, not animatable.
    """
    # Search for an existing field with our name
    for uid, bc in mat.GetUserDataContainer():
        if bc[c4d.DESC_NAME] == USERDATA_FIELD_NAME:
            return uid

    # Not found — create it
    bc = c4d.GetCustomDatatypeDefault(c4d.DTYPE_LONG)
    bc[c4d.DESC_NAME]       = USERDATA_FIELD_NAME
    bc[c4d.DESC_SHORT_NAME] = "Mat ID"
    bc[c4d.DESC_MIN]        = 0
    bc[c4d.DESC_MAX]        = 99999
    bc[c4d.DESC_STEP]       = 1
    bc[c4d.DESC_ANIMATE]    = c4d.DESC_ANIMATE_OFF

    return mat.AddUserData(bc)


def assign_id_to_selected_materials(material_id):
    """
    Writes material_id into the 'Material ID' User Data field of every
    selected material in the active document. The operation is undoable.

    Returns the number of materials that were modified (0 if none selected).
    """
    doc = c4d.documents.GetActiveDocument()
    if not doc:
        return 0

    materials = get_selected_materials(doc)
    if not materials:
        return 0

    doc.StartUndo()

    for mat in materials:
        doc.AddUndo(c4d.UNDOTYPE_CHANGE, mat)
        uid = get_or_create_matid_userdata(mat)
        mat[uid] = material_id
        mat.Message(c4d.MSG_UPDATE)

    doc.EndUndo()
    c4d.EventAdd()

    return len(materials)


# ---------------------------------------------------------------------------
# Dialog
# ---------------------------------------------------------------------------

class MaterialIDDialog(gui.GeDialog):
    """
    Modal dialog that lets the user enter the numeric Material ID.
    On OK the ID is applied to all currently selected materials.
    """

    def __init__(self):
        super().__init__()
        self._last_id = 0   # Remembers the last used ID within the session

    def CreateLayout(self):
        self.SetTitle(PLUGIN_NAME)

        # Row: label + number field
        if self.GroupBegin(ID_GROUP_MAIN, c4d.BFH_SCALEFIT | c4d.BFV_FIT, 2, 1, ""):
            self.GroupBorderSpace(8, 8, 8, 8)
            self.AddStaticText(ID_LABEL, c4d.BFH_LEFT, name="Material ID:")
            self.AddEditNumberArrows(ID_ID_FIELD, c4d.BFH_SCALEFIT)
        self.GroupEnd()

        # Separator
        self.AddSeparatorH(0, c4d.BFH_SCALEFIT)

        # Buttons row
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
            # Read the entered ID
            entered_id = self.GetInt32(ID_ID_FIELD)
            self._last_id = entered_id

            # Apply
            count = assign_id_to_selected_materials(entered_id)

            self.Close()

            if count == 0:
                gui.MessageDialog(
                    "Keine Materialien selektiert!\n\n"
                    "Bitte zuerst Materialien im Material Manager auswählen."
                )
            else:
                gui.MessageDialog(
                    f"Material ID {entered_id} wurde erfolgreich\n"
                    f"{count} Material(ien) zugewiesen."
                )

        elif id == ID_BTN_CANCEL:
            self.Close()

        return True


# ---------------------------------------------------------------------------
# Command Plugin
# ---------------------------------------------------------------------------

class MaterialIDAssignerPlugin(plugins.CommandPlugin):
    """
    Registered as a Cinema 4D Command Plugin.
    Appears in the Extensions menu as "Material ID Assigner".
    """

    def Execute(self, doc):
        dlg = MaterialIDDialog()
        dlg.Open(
            dlgtype=c4d.DLG_TYPE_MODAL,
            pluginid=PLUGIN_ID,
            xpos=-2,    # -2 = center on screen
            ypos=-2,
            defaultw=280,
            defaulth=90,
        )
        return True

    def GetState(self, doc):
        # Plugin is always enabled (selection check happens inside the dialog)
        return c4d.CMD_ENABLED


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    plugins.RegisterCommandPlugin(
        id=PLUGIN_ID,
        str=PLUGIN_NAME,
        info=0,
        icon=None,
        help=PLUGIN_HELP,
        dat=MaterialIDAssignerPlugin(),
    )
